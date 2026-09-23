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

# Force UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from generate_ormuri import (
    load_knowledge_base,
    get_or_create_cache,
    generate_ormuri,
    DEFAULT_API_KEY,
    MODEL_NAME
)
from google import genai

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
KB_PATH = os.path.join(BASE_DIR, "ormuri_knowledge_base.md")
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

# Initialize GenAI Client
CLIENT = genai.Client(api_key=DEFAULT_API_KEY)
CACHE_NAME = get_or_create_cache(CLIENT, KB_CONTENT, model_name=MODEL_NAME)


def parse_ormuri_output(raw_text: str) -> Dict[str, Any]:
    """Parse output into scratchpad, ormuri text, romanization, and translation."""
    # Replace all '*' symbols in the model's response with a space ' '
    raw_text = raw_text.replace('*', ' ')

    scratchpad = ""
    scratchpad_m = re.search(r'<morphological_scratchpad>(.*?)</morphological_scratchpad>', raw_text, re.DOTALL | re.IGNORECASE)
    if scratchpad_m:
        scratchpad = scratchpad_m.group(1).replace('*', ' ').strip()
    
    # Remove scratchpad from remaining text
    content_after = re.sub(r'<morphological_scratchpad>.*?</morphological_scratchpad>', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()
    
    # Try extracting sections
    ormuri_text = ""
    romanization = ""
    translation = ""
    
    # Section matching (handles English "Ormuri", "Bargista", and Arabic "اُرموړی", "ارموړی", "اورموړی", "Perso-Arabic")
    sec_ormuri = re.search(r'(?:###?\s*(?:Polished\s*)?(?:Ormuri|Bargista|[\u0600-\u06FF]+|Perso-Arabic).*?\n)(.*?)(?=(?:###?\s*(?:Phonetic|Romanization|Roman|IPA|English|Translation)|$))', content_after, re.DOTALL | re.IGNORECASE)
    sec_roman = re.search(r'(?:###?\s*(?:Phonetic\s*)?(?:Romanization|Roman|IPA).*?\n)(.*?)(?=(?:###?\s*(?:English|Translation|Literal)|$))', content_after, re.DOTALL | re.IGNORECASE)
    sec_trans = re.search(r'(?:###?\s*(?:English\s*)?(?:Translation|Meaning).*?\n)(.*?)(?=$)', content_after, re.DOTALL | re.IGNORECASE)
    
    if sec_ormuri:
        ormuri_text = sec_ormuri.group(1).strip()
    if sec_roman:
        romanization = sec_roman.group(1).strip()
    if sec_trans:
        translation = sec_trans.group(1).strip()
    
    # Fallback if ormuri_text was not matched by heading
    if not ormuri_text:
        # 1. Try text before romanization/translation
        before_roman = re.split(r'###?\s*(?:Phonetic|Romanization|English|Translation)', content_after, flags=re.IGNORECASE)[0].strip()
        # Clean any remaining markdown header lines
        cleaned_before = re.sub(r'^#+.*?\n', '', before_roman).strip()
        if cleaned_before and len(cleaned_before) > 5:
            ormuri_text = cleaned_before
        else:
            # 2. Extract any paragraphs with Arabic characters
            arabic_blocks = []
            for p in content_after.split('\n\n'):
                p_clean = p.strip()
                if not p_clean:
                    continue
                arabic_count = len(re.findall(r'[\u0600-\u06FF]', p_clean))
                if arabic_count >= 5:
                    arabic_blocks.append(p_clean)
            if arabic_blocks:
                ormuri_text = '\n\n'.join(arabic_blocks)

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
                "kb_tokens": 866060,
                "lexicon_entries": len(LEXICON_DATA)
            })
            return

        elif path == "/api/lexicon":
            search_query = query.get("q", [""])[0].strip().lower()
            pos_filter = query.get("pos", [""])[0].strip().lower()
            limit = int(query.get("limit", [50])[0])

            results = []
            for item in LEXICON_DATA:
                match = True
                hw = item.get("headword", item.get("word", ""))
                ipa = item.get("ipa", "")
                meaning = item.get("meaning", item.get("gloss", ""))
                if search_query:
                    text_corpus = f"{hw} {ipa} {meaning}".lower()
                    if search_query not in text_corpus:
                        match = False
                if pos_filter and match:
                    if pos_filter not in item.get("pos", "").lower():
                        match = False
                if match:
                    # Provide uniform keys for frontend
                    results.append({
                        "word": hw,
                        "headword": hw,
                        "ipa": ipa,
                        "pos": item.get("pos", ""),
                        "gloss": meaning,
                        "meaning": meaning
                    })
                    if len(results) >= limit:
                        break

            self.send_json({
                "query": search_query,
                "total_matches": len(results),
                "results": results
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
                mode = data.get("mode", "free")

                if not prompt:
                    self.send_json({"error": "Prompt cannot be empty"}, status=400)
                    return

                # Enrich prompt based on mode
                full_prompt = prompt
                if mode == "story":
                    full_prompt = f"Compose a rich traditional story in authentic Ormuri:\n{prompt}"
                elif mode == "proverb":
                    full_prompt = f"Provide and analyze authentic Ormuri proverbs regarding:\n{prompt}"
                elif mode == "dialogue":
                    full_prompt = f"Write an authentic conversational dialogue between native Ormuri speakers:\n{prompt}"
                elif mode == "grammar_check":
                    full_prompt = f"Linguistically analyze and translate this sentence into authentic Ormuri, strictly enforcing split-ergativity and clitic rules:\n{prompt}"

                print(f"[API] Generating for prompt ({len(prompt)} chars, mode={mode})...")
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
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, PlaygroundHandler)
    print(f"\n==================================================================")
    print(f"  🚀 Ormuri AI Playground Server running at http://localhost:{port}")
    print(f"  📂 Serving Frontend from: {FRONTEND_DIR}")
    print(f"  🧠 Model: {MODEL_NAME} | KB Tokens: 866,060 | Lexicon: {len(LEXICON_DATA)}")
    print(f"==================================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    port = PORT
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port)
