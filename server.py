"""
server.py
Lightweight, multithreaded backend server for the Ormuri AI Playground.
Serves static frontend files and exposes API endpoints for prompt generation,
scratchpad extraction, lexicon lookup, and system status.
"""

import os
import sys
import json
import re
import urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Any

# Force UTF-8 and immediate line buffering on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
except Exception:
    pass

from generate_ormuri import (
    load_knowledge_base,
    get_or_create_cache,
    generate_ormuri,
    DEFAULT_API_KEY,
    MODEL_NAME,
    KEY_POOL
)
from google import genai

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
CORE_KB_PATH = os.path.join(BASE_DIR, "ormuri_core_kb.md")
KB_PATH = CORE_KB_PATH if os.path.exists(CORE_KB_PATH) else os.path.join(BASE_DIR, "ormuri_knowledge_base.md")
LEXICON_PATH = os.path.join(BASE_DIR, "lexicon.json")

PORT = int(os.environ.get("PORT", 8080))

# Preload resources
print("[*] Initializing Ormuri AI Playground Server...")
KB_CONTENT = load_knowledge_base(KB_PATH)

print("[*] Loading Lexicon Database...")
LEXICON_DATA = []
if os.path.exists(LEXICON_PATH):
    with open(LEXICON_PATH, "r", encoding="utf-8") as f:
        LEXICON_DATA = json.load(f)
print(f"[OK] Loaded {len(LEXICON_DATA)} lexicon entries.")

# Initialize GenAI Client using Key Pool (failsafe if no API key is yet configured in Render)
CLIENT = None
ACTIVE_KEY = None
KEY_IDX = -1
CACHE_NAME = None

if KEY_POOL.has_keys():
    try:
        CLIENT, ACTIVE_KEY, KEY_IDX = KEY_POOL.get_client()
        print(f"[*] Initialized GenAI Client with Key #{KEY_IDX + 1} of {len(KEY_POOL.keys)}.", flush=True)
        CACHE_NAME = get_or_create_cache(CLIENT, KB_CONTENT, model_name=MODEL_NAME)
    except Exception as exc:
        print(f"[WARNING] Could not initialize Gemini client at startup: {exc}", flush=True)
else:
    print("[WARNING] No Gemini API key detected in environment.", flush=True)
    print("          Server will start and serve frontend, corpus archive, and lexicon.", flush=True)
    print("          To enable generation, configure GEMINI_API_KEY in Render Environment Variables.", flush=True)


def clean_section(text: str) -> str:
    """Clean markdown artifacts, dividers, and trailing delimiters from extracted section."""
    if not text:
        return ""
    # Strip leading/trailing horizontal rules (---, ___, ***)
    text = re.sub(r'^\s*[-=_*]{3,}\s*', '', text)
    text = re.sub(r'\s*[-=_*]{3,}\s*$', '', text)
    # Strip any leading heading line left inside section
    text = re.sub(r'^\s*#{1,4}\s+[^\n]+\n+', '', text)
    return text.strip()


def parse_ormuri_output(raw_text: str) -> Dict[str, Any]:
    """Parse output into scratchpad, ormuri text, romanization, and translation with ultra-robust failsafes."""
    # Replace all '*' symbols in the model's response with a space ' '
    raw_text = raw_text.replace('*', ' ')

    scratchpad = ""
    scratchpad_m = re.search(r'<morphological_scratchpad>(.*?)</morphological_scratchpad>', raw_text, re.DOTALL | re.IGNORECASE)
    if scratchpad_m:
        scratchpad = scratchpad_m.group(1).replace('*', ' ').strip()
    
    # Remove scratchpad from remaining text
    content_after = re.sub(r'<morphological_scratchpad>.*?</morphological_scratchpad>', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()
    content_after = re.sub(r'^```(?:markdown)?', '', content_after).strip()
    content_after = re.sub(r'```$', '', content_after).strip()
    
    ormuri_text = ""
    romanization = ""
    translation = ""
    
    # 1. Flexible Heading Matching (handles levels # to ####, bold headers, numbered lists, and multilingual titles)
    sec_ormuri = re.search(
        r'(?:^|\n)\s*(?:#{1,4}|\*{2,3}|\d+[\.\)])\s*.*?(?:Ormuri|Bargista|[\u0600-\u06FF]+|Perso-Arabic|Script).*?\n+(.*?)(?=\n\s*(?:#{1,4}|\*{2,3}|\d+[\.\)])|\Z)',
        content_after, re.DOTALL | re.IGNORECASE
    )
    sec_roman = re.search(
        r'(?:^|\n)\s*(?:#{1,4}|\*{2,3}|\d+[\.\)])\s*.*?(?:Phonetic|Romanization|Roman|IPA|Transliteration).*?\n+(.*?)(?=\n\s*(?:#{1,4}|\*{2,3}|\d+[\.\)])|\Z)',
        content_after, re.DOTALL | re.IGNORECASE
    )
    sec_trans = re.search(
        r'(?:^|\n)\s*(?:#{1,4}|\*{2,3}|\d+[\.\)])\s*.*?(?:Translation|Meaning|Notes|Gloss|Vocabulary|Dialogue|Explanation|Breakdown|Analysis|ترجمہ|معنی|تشریح|وضاحت|ژباړه|معنا|توضیحات).*?\n+(.*?)(?=\n\s*(?:#{1,4}|\*{2,3}|\d+[\.\)])|\Z)',
        content_after, re.DOTALL | re.IGNORECASE
    )
    
    if sec_ormuri:
        ormuri_text = clean_section(sec_ormuri.group(1))
    if sec_roman:
        romanization = clean_section(sec_roman.group(1))
    if sec_trans:
        translation = clean_section(sec_trans.group(1))
    
    # Sanity check: Ensure translation isn't mistakenly holding the Ormuri heading
    if translation and re.match(r'^\s*#{0,4}\s*Polished\s*Ormuri', translation, re.IGNORECASE):
        translation = ""

    # 2. Structural Guarantee:
    # In standard response structure, whatever follows the Romanization section until the end IS the Translation, Gloss & Notes
    if romanization and not translation and sec_roman:
        roman_end = sec_roman.end()
        remaining = content_after[roman_end:].strip()
        # Clean any leading markdown heading or divider like '---' or '### Translation'
        remaining = re.sub(r'^(?:[\s\-\*#]+\n+)+', '', remaining).strip()
        remaining = re.sub(r'^\s*#{1,4}\s+[^\n]+\n+', '', remaining).strip()
        if remaining and not re.match(r'^\s*#{0,4}\s*Polished\s*Ormuri', remaining, re.IGNORECASE):
            translation = clean_section(remaining)

    # 3. Comprehensive Paragraph Fallback
    if not (ormuri_text and romanization and translation):
        raw_paragraphs = [p.strip() for p in content_after.split('\n\n') if p.strip()]
        valid_paragraphs = []
        for p in raw_paragraphs:
            # Skip if paragraph is purely a markdown heading or divider
            if re.match(r'^(?:#{1,4}\s+.*|[-=_*]{3,})$', p.strip()):
                continue
            cleaned_p = re.sub(r'^(?:#{1,4}\s+.*?\n+|[-=_*]{3,}\n+)', '', p).strip()
            if cleaned_p and not re.match(r'^Polished\s*Ormuri', cleaned_p, re.IGNORECASE):
                valid_paragraphs.append(cleaned_p)

        trans_paragraphs = []
        for p in valid_paragraphs:
            arb_chars = len(re.findall(r'[\u0600-\u06FF]', p))
            lat_chars = len(re.findall(r'[A-Za-z]', p))
            
            if arb_chars > lat_chars and arb_chars >= 3 and not ormuri_text:
                ormuri_text = clean_section(p)
            elif lat_chars > arb_chars:
                has_ipa = any(c in p for c in 'əʌɪʊšžřɕʑčǰāēīōūḍṭṇṛ')
                if (has_ipa or not romanization) and not romanization:
                    romanization = clean_section(p)
                else:
                    trans_paragraphs.append(clean_section(p))
            else:
                trans_paragraphs.append(clean_section(p))
        
        if not translation and trans_paragraphs:
            translation = clean_section('\n\n'.join(trans_paragraphs))

    return {
        "scratchpad": scratchpad.replace('*', ' ').strip(),
        "ormuri_text": ormuri_text.replace('*', ' ').strip(),
        "romanization": romanization.replace('*', ' ').strip(),
        "translation": translation.replace('*', ' ').strip(),
        "raw_text": raw_text.replace('*', ' ').strip()
    }


class PlaygroundHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def end_headers(self):
        if self.path.startswith("/sw.js"):
            self.send_header("Service-Worker-Allowed", "/")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        elif self.path.startswith("/manifest.json"):
            self.send_header("Content-Type", "application/manifest+json")
        else:
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/status":
            self.send_json({
                "status": "online",
                "model": MODEL_NAME,
                "cached": bool(CACHE_NAME),
                "cache_name": CACHE_NAME or "Direct In-Context Learning",
                "kb_characters": len(KB_CONTENT),
                "kb_tokens": int(len(KB_CONTENT.split()) * 1.3),
                "lexicon_entries": len(LEXICON_DATA),
                "active_key_count": len(KEY_POOL.keys)
            })
            return

        elif path == "/api/lexicon":
            search_query = query.get("q", [""])[0].strip().lower()
            pos_filter = query.get("pos", [""])[0].strip().lower()
            try:
                offset = max(0, int(query.get("offset", [0])[0]))
            except (ValueError, TypeError):
                offset = 0
            try:
                limit = int(query.get("limit", [100])[0])
            except (ValueError, TypeError):
                limit = 100

            matched = []
            for item in LEXICON_DATA:
                hw = item.get("headword", item.get("word", ""))
                ipa = item.get("ipa", "")
                meaning = item.get("meaning", item.get("gloss", ""))
                
                # Filter by search query across headword, IPA, and meaning
                if search_query:
                    text_corpus = f"{hw} {ipa} {meaning}".lower()
                    if search_query not in text_corpus:
                        continue
                
                # Filter by Part of Speech
                if pos_filter:
                    if pos_filter not in item.get("pos", "").lower():
                        continue
                
                matched.append({
                    "word": hw,
                    "headword": hw,
                    "ipa": ipa,
                    "pos": item.get("pos", ""),
                    "gloss": meaning,
                    "meaning": meaning
                })

            total_matches = len(matched)
            if limit > 0:
                paged = matched[offset:offset + limit]
            else:
                paged = matched[offset:]

            self.send_json({
                "query": search_query,
                "pos": pos_filter,
                "total_matches": total_matches,
                "offset": offset,
                "limit": limit,
                "has_more": (offset + len(paged)) < total_matches,
                "results": paged
            })
            return

        # Default static file serving
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/generate":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            
            try:
                data = json.loads(post_data)
                prompt = data.get("prompt", "").strip()
                temperature = float(data.get("temperature", 0.2))
                mode = data.get("mode", "qa")
                prompt_lang = data.get("prompt_lang", "auto")

                if not prompt:
                    self.send_json({"error": "Prompt cannot be empty"}, status=400)
                    return

                # Detect user prompt language
                has_ps = any(c in prompt for c in ['ښ', 'ږ', 'ڼ', 'ۍ', 'ې', 'ئ', 'څ', 'ځ']) or any(w in prompt for w in ['څنګه', 'ولې', 'پښتو', 'کې', 'سره', 'ژبه', 'زده'])
                has_ur = any(c in prompt for c in ['ں', 'ے', 'ٹ', 'ڈ', 'ڑ', 'ہ', 'ھ']) or any(w in prompt for w in ['کیا', 'ہے', 'ہیں', 'تھا', 'تھی', 'میں', 'اردو', 'بتائیں', 'سکھائیں', 'کیوں'])
                
                detected_lang = prompt_lang
                if detected_lang not in ["ur", "ps", "en"]:
                    if has_ps:
                        detected_lang = "ps"
                    elif has_ur:
                        detected_lang = "ur"
                    else:
                        arb = len(re.findall(r'[\u0600-\u06FF]', prompt))
                        lat = len(re.findall(r'[A-Za-z]', prompt))
                        detected_lang = "ur" if arb > lat else "en"

                # Enrich prompt based on mode
                if mode in ["qa_general", "qa", "free", "general", ""]:
                    full_prompt = (
                        f"CRITICAL SYSTEM DIRECTIVE — MASTER QUESTION ANSWERING & KNOWLEDGE ENGINE:\n"
                        f"You are the world's foremost computational linguist and native AI authority on the Ormuri (Bargista / اُرموړی) language, its history, literature, culture, and linguistics. "
                        f"Your primary mission in this default mode is to provide the MOST ACCURATE, COMPLETE, INTELLIGENT, AND DIRECT ANSWER to any question the user asks.\n\n"
                        f"USER QUESTION: {prompt}\n\n"
                        f"MANDATORY REQUIREMENTS BY SECTION:\n"
                        f"1. '### Polished Ormuri (Bargista / اُرموړی) Text':\n"
                        f"   - This section MUST DIRECTLY formulate the authentic answer in Ormuri (Bargista) script.\n"
                        f"   - If the user asks a factual, historical, linguistic, or conversational question, state the direct, factual, and informative answer in articulate, grammatically authentic Ormuri sentences.\n"
                        f"   - If the user asks for translations, vocabulary, or grammar structures, provide the exact target Ormuri formulation.\n"
                        f"   - NEVER generate generic poetry, random Kaniguram praises, or unrelated folk lines. Every Ormuri sentence must directly resolve the user's inquiry.\n\n"
                        f"2. '### Phonetic Romanization':\n"
                        f"   - Provide the exact IPA-based Romanization strictly matching the Ormuri text above sentence-by-sentence.\n\n"
                        f"3. '### Translation & Notes':\n"
                        f"   - Deliver the most comprehensive, authoritative, and direct answer to the user's question.\n"
                        f"   - Provide the 1-to-1 sentence translation of the Ormuri answer, followed by thorough explanation, linguistic analysis, historical context, and any specific details needed to completely answer the user's question.\n"
                        f"   - Answer ALL parts of the user's query thoroughly."
                    )
                elif mode == "qa_context":
                    full_prompt = (
                        f"CRITICAL SYSTEM DIRECTIVE — CORPUS & HISTORICAL CONTEXT Q/A:\n"
                        f"Answer the user's inquiry strictly and explicitly based on the primary historical Ormuri texts, Grierson 1929 records, Efimov 1986 grammar, and the unabridged dictionary in your knowledge base.\n\n"
                        f"USER QUESTION: {prompt}\n\n"
                        f"The '### Polished Ormuri (Bargista / اُرموړی) Text' must directly present the relevant Ormuri terms or sentences cited from the corpus, with 1-to-1 Romanization and Translation with historical citations."
                    )
                elif mode == "teach":
                    full_prompt = (
                        f"CRITICAL REQUIREMENT FOR '### Polished Ormuri (Bargista / اُرموړی) Text':\n"
                        f"This section MUST contain the EXACT target Ormuri vocabulary, sentences, and conversation being taught for this lesson topic.\n"
                        f"DO NOT generate unrelated stories. Every Ormuri sentence must be a direct part of the lesson.\n\n"
                        f"LESSON TOPIC: {prompt}\n\n"
                        f"The '### Translation & Notes' section must systematically break down the lesson (Vocabulary, Grammar Rules, Usage tips, Practice drill) matching the Ormuri text 1-to-1."
                    )
                elif mode == "story":
                    full_prompt = f"Compose a rich traditional story in authentic Ormuri directly addressing:\n{prompt}"
                elif mode == "dialogue":
                    full_prompt = f"Write an authentic conversational dialogue between native Ormuri speakers directly about:\n{prompt}"
                elif mode == "grammar_check":
                    full_prompt = f"Linguistically analyze and translate this sentence into authentic Ormuri, strictly enforcing split-ergativity and clitic rules:\n{prompt}"
                else:
                    full_prompt = prompt

                # Strict language matching directive
                if detected_lang == "ur":
                    full_prompt += "\n\n(TARGET LANGUAGE REQUIREMENT: The user wrote in Urdu. You MUST write the '### Translation & Notes' section and all explanations, breakdowns, and definitions entirely in URDU (اردو). Do NOT use English for the translation section.)"
                elif detected_lang == "ps":
                    full_prompt += "\n\n(TARGET LANGUAGE REQUIREMENT: The user wrote in Pashto. You MUST write the '### Translation & Notes' section and all explanations, breakdowns, and definitions entirely in PASHTO (پښتو). Do NOT use English for the translation section.)"
                else:
                    full_prompt += "\n\n(TARGET LANGUAGE REQUIREMENT: The user wrote in English. Provide the '### Translation & Notes' section in English.)"

                full_prompt += "\n\n(CRITICAL INSTRUCTIONS: 1. You MUST always output all three sections with their standard markdown headings in this exact order: '### Polished Ormuri (Bargista / اُرموړی) Text', '### Phonetic Romanization', and '### Translation & Notes'. Put all dialogue translations, word-by-word glosses, and vocabulary notes inside the '### Translation & Notes' section. Never omit the translation section. 2. In both the <morphological_scratchpad> and Raw Markdown, whenever an example is given or analyzed, you MUST always provide the complete example sentence in authentic Ormuri script along with Romanization. 3. Accurate Ormuri vocabulary: 'Language' is زبان [zbān] / زبنَّی [zbənni]; 'دیو' [dyō] strictly means the number 'two'.)"

                if not KEY_POOL.has_keys():
                    self.send_json({
                        "success": False,
                        "error": "No GEMINI_API_KEY configured in server environment. Please set GEMINI_API_KEY in your Render dashboard under 'Environment Variables'.",
                        "is_quota_limit": False
                    }, status=200)
                    return

                print(f"[API] Generating for prompt ({len(prompt)} chars, mode={mode})...", flush=True)
                result_text = generate_ormuri(
                    CLIENT,
                    full_prompt,
                    cache_name=CACHE_NAME,
                    kb_content=KB_CONTENT,
                    model_name=MODEL_NAME,
                    temperature=temperature
                )

                parsed_output = parse_ormuri_output(result_text)
                self.send_json({
                    "success": True,
                    "prompt": prompt,
                    "mode": mode,
                    "model": MODEL_NAME,
                    "detected_lang": detected_lang,
                    "parsed": parsed_output
                })

            except Exception as exc:
                err_msg = str(exc)
                print(f"[ERROR] API generation failed: {err_msg}")
                is_quota = any(w in err_msg.lower() for w in [
                    "429", "quota", "resource_exhausted", "rate", "limit", "cost", "credit", "exceeded", "exhausted", "billing"
                ])
                self.send_json({
                    "success": False,
                    "error": err_msg,
                    "is_quota_limit": is_quota
                }, status=200)
            return

        self.send_response(404)
        self.end_headers()

    def send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)


def run_server(port: int = PORT):
    os.makedirs(FRONTEND_DIR, exist_ok=True)
    server_address = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(server_address, PlaygroundHandler)
    print(f"\n==================================================================", flush=True)
    print(f"  🚀 Ormuri AI Playground Server running at http://0.0.0.0:{port}", flush=True)
    print(f"  📂 Serving Frontend from: {FRONTEND_DIR}", flush=True)
    print(f"  🧠 Model: {MODEL_NAME} | KB Tokens: 866,060 | Lexicon: {len(LEXICON_DATA)}", flush=True)
    print(f"==================================================================\n", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down server...", flush=True)
        httpd.server_close()


if __name__ == "__main__":
    port = PORT
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port)
