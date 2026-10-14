"""
generate_ormuri.py
Official Google GenAI SDK script with Context Caching and In-Context Learning (ICL)
for Ormuri (Bargista / اُرموړی) generation with strict linguistic guardrails.
"""

import os
import sys
import argparse
import time
from typing import Optional

# Ensure UTF-8 stdout and line buffering on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
except Exception:
    pass

from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError

import hashlib
import json
import threading

# Load .env file if present
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    with open(_env_path, "r", encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY", "")
_keys_str = os.environ.get("GEMINI_API_KEYS", "") or DEFAULT_API_KEY
ALL_API_KEYS = [k.strip() for k in _keys_str.split(",") if k.strip()]
if not ALL_API_KEYS and DEFAULT_API_KEY:
    ALL_API_KEYS = [DEFAULT_API_KEY]

MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
CACHE_TTL = "86400s"  # 24-hour TTL

class ApiKeyPool:
    """Manages pool of free/paid Gemini API keys with automatic round-robin dispatch and rate-limit cooldowns."""
    def __init__(self, keys: list[str]):
        self.keys = [k.strip() for k in keys if k and k.strip()]
        self.current_idx = 0
        self._lock = threading.Lock()
        self.clients = {}
        self.cooldowns = {}  # key_idx -> timestamp until which it is on cooldown

    def has_keys(self) -> bool:
        if self.keys:
            return True
        env_single = os.environ.get("GEMINI_API_KEY", "").strip()
        env_multi = os.environ.get("GEMINI_API_KEYS", "").strip()
        return bool(env_single or env_multi)

    def get_client(self, round_robin: bool = True) -> tuple[genai.Client, str, int]:
        """Dispatch next available API key using thread-safe round-robin load balancing."""
        with self._lock:
            if not self.keys:
                env_single = os.environ.get("GEMINI_API_KEY", "").strip()
                env_multi = os.environ.get("GEMINI_API_KEYS", "").strip()
                combined = [k.strip() for k in f"{env_single},{env_multi}".split(",") if k.strip()]
                if combined:
                    self.keys = combined

            if not self.keys:
                raise ValueError("No Gemini API key provided. Please set GEMINI_API_KEY or GEMINI_API_KEYS.")

            now = time.time()
            n = len(self.keys)
            
            # Find next non-cooled key
            for offset in range(n):
                idx = (self.current_idx + offset) % n
                if self.cooldowns.get(idx, 0) <= now:
                    if round_robin:
                        self.current_idx = (idx + 1) % n
                    key = self.keys[idx]
                    if key not in self.clients:
                        self.clients[key] = genai.Client(api_key=key)
                    print(f"[KEY-DISPATCH] Round-Robin: Dispatched Key #{idx + 1} of {n} for request")
                    return self.clients[key], key, idx
            
            # If all are in cooldown, pick the one whose cooldown expires soonest
            soonest_idx = min(range(n), key=lambda i: self.cooldowns.get(i, 0))
            if round_robin:
                self.current_idx = (soonest_idx + 1) % n
            key = self.keys[soonest_idx]
            if key not in self.clients:
                self.clients[key] = genai.Client(api_key=key)
            print(f"[KEY-DISPATCH] All keys active; dispatched Key #{soonest_idx + 1} of {n}")
            return self.clients[key], key, soonest_idx

    def mark_rate_limited(self, idx: int, duration_sec: float = 60.0):
        """Put a key into cooldown for 60s when a 429 quota is encountered."""
        with self._lock:
            self.cooldowns[idx] = time.time() + duration_sec
            print(f"[KEY-COOLDOWN] Key #{idx + 1} put in cooldown for {duration_sec}s due to rate limit.")

    def rotate(self, reason: str = "") -> tuple[genai.Client, str, int]:
        return self.get_client(round_robin=True)

KEY_POOL = ApiKeyPool(ALL_API_KEYS)

SYSTEM_GUARDRAIL_PROMPT = """You are the world's foremost computational linguist and native speaker specialist for Ormuri (Bargista / اُرموړی), an endangered Western Iranian language spoken in Kaniguram, South Waziristan.

You are given a comprehensive, authoritative linguistic knowledge base in your context.

CRITICAL GENERATIVE CONSTRAINTS (ZERO TOLERANCE FOR DEVIATION):
1. ZERO PASHTO / PERSIAN FALLBACK:
   - You must NEVER insert Pashto function words (e.g. 'da', 'kawəl', 'de', 'stāso', 'ham') or Urdu/Persian vocabulary when composing Ormuri.
   - Every lexical root, affix, and particle MUST be authentic Ormuri as codified in the knowledge base.
   - If a specific modern term is missing, paraphrase using native Ormuri compounds (e.g., 'town of paradise', 'iron-stone knife', 'clear water').

2. EXACT SPLIT ERGATIVITY ALGEBRA:
   - Present / Future / Imperfective:
     * Alignment is Nominative-Accusative.
     * Subject is in Direct Case (az, tu, o, max, tyos, ay).
     * Verb agrees with the SUBJECT in person/number via finite suffixes (-m, -yen, -Ø, -ay, -y, -in).
     * Marker is 'بُو' (bu) for present/habitual and 'سُو' (su) for future/modal.
   - Past Transitive:
     * Alignment is ERGATIVE-ABSOLUTIVE.
     * The Agent is marked by an enclitic (-m, -t, -wə/-l, -n) hosted on the first constituent (clitic host) or 'ال' (al).
     * The Verb MUST agree in GENDER and NUMBER with the OBJECT (Patient), NOT the subject.
     * Verb stems: Masculine past (tsalyek, řūk, dōk, byōk) vs Feminine past (tsələk, dāk, buk) vs Plural (da-kin, řūk-bukin).

3. STRICT CLITIC SYNTAX (WACKERNAGEL 2P POSITION):
   - Enclitics (-m, -t, -wə, -nyē, -n) and particles ('يې' yē, 'ال' al, 'دې' dē) must attach to the right edge of the first constituent.

4. MANDATORY MORPHOLOGICAL SCRATCHPAD & ORMURI EXAMPLE SENTENCE ENFORCEMENT:
   For every generated passage, explanation, translation, or answer, you MUST first produce a `<morphological_scratchpad>`.
   
   CRITICAL REQUIREMENT (STRICTLY ENFORCED):
   In BOTH the Morphological Scratchpad (inspected in the "Morphological Scratchpad Verified" tab) AND in the Raw Markdown / explanatory output:
   Whenever an example sentence is given, referenced, or analyzed (for sentence-by-sentence decomposition, grammar demonstrations, verb conjugations, idioms, proverbs, or word usage):
   - You MUST ALWAYS write the exact, complete example sentence in authentic Ormuri script right there:
     `- Example Sentence in Ormuri: [اُرموړی متن - in authentic Perso-Arabic script with all letters ݫ, ݭ, ڒ, څ, ځ, ګ]`
   - You MUST include its Phonetic Romanization:
     `- Phonetic Romanization: [IPA/Roman transcription]`
   - You MUST include its English Intent / Meaning:
     `- Intent / Meaning: [English explanation]`
   - Followed by Alignment Type, Subject & Clitic Host, Object & Verb Agreement, and Exact Roots/Affixes.
   
   NEVER present an example in English alone or abstract grammatical breakdown without providing the full corresponding sentence in authentic Ormuri right beside it!
   
   After the scratchpad, output the full structured response:
   ### Polished Ormuri (Bargista / اُرموړی) Text
   [STRICT RELEVANCE REQUIREMENT:
    - This section MUST be the DIRECT answer, lesson content, or composition specifically requested by the user, in authentic Ormuri script.
    - DO NOT generate unrelated generic poetry, random Kaniguram praises, or disconnected folk stories when the user asked a specific question or requested a lesson!
    - If the user asks "What is X in Ormuri?", this section MUST directly state the term, its grammatical class, and authentic example sentences using X in Ormuri.
    - If the user asks for a lesson, this section MUST contain the exact lesson sentences/dialogue being taught.
    - Every sentence here must directly resolve the user's inquiry.]
   
   ### Phonetic Romanization
   [Phonetic Romanization with IPA symbols in strict 1-to-1 sentence alignment with the Ormuri text above]
   
   ### Translation & Notes
   [Direct sentence-by-sentence translation and analytical explanation of the EXACT Ormuri text above:
    - If the user asked or prompted in Urdu (اردو), write this section entirely in Urdu (اردو).
    - If the user asked or prompted in Pashto (پښتو), write this section entirely in Pashto (پښتو).
    - If the user prompted in English, write in English.
    - Ensure 100% mutual semantic correspondence: this section must directly translate and explain the Ormuri text above, with zero divergence.]

5. STRICT CANONICAL VOCABULARY ENFORCEMENT:
   - "Language" in Ormuri is strictly **زبان** [zbān] (Plural: **زبنَّی** [zbənni]) or the compound autonym **ورمړو زبان** [Warmaṛō zbān] / **ورمړو** [Warmaṛō].
   - CRITICAL WARNING: NEVER use "دیو" (dyō) for "language"! In authentic Ormuri, "دیو" [dyō] strictly means the numeral "TWO" (2 / دو / binary pair). "Language" is ALWAYS **زبان** [zbān].

6. MULTILINGUAL ADAPTATION & DIRECT RELEVANCE DIRECTIVES:
   - In Q/A Mode: Answer the question directly in Ormuri. The Ormuri text must state the facts, terminology, or rules in Ormuri itself, supplemented by the translation box.
   - In Teaching Mode: The Ormuri text must contain the exact target vocabulary, grammatical patterns, and dialogue being taught.
   - Strict 1-to-1 Alignment: Never let the Ormuri text discuss one topic while the translation discusses a different topic. Both sections must be 100% synchronized.
   - Language Matching: Inquiries in Urdu receive Urdu explanations & translations; inquiries in Pashto receive Pashto explanations & translations.
"""

def load_knowledge_base(kb_path: str) -> str:
    """Load the compiled ormuri_knowledge_base.md or ormuri_core_kb.md document."""
    if not os.path.exists(kb_path):
        raise FileNotFoundError(f"Knowledge base file not found at: {kb_path}")
    with open(kb_path, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"[OK] Loaded Knowledge Base ({len(content)} characters, ~{len(content.split())} words from {os.path.basename(kb_path)})")
    return content

def get_or_create_cache(client: genai.Client, kb_content: str, model_name: str = MODEL_NAME) -> Optional[str]:
    """
    Attempt to create an explicit Gemini Context Cache with 24h TTL.
    If the account's tier does not allocate server-side cache storage (limit=0),
    gracefully return None so the script seamlessly uses direct in-context injection.
    """
    print(f"[*] Attempting to create explicit Context Cache with {model_name} (TTL: {CACHE_TTL})...")
    try:
        cache = client.caches.create(
            model=model_name,
            config=types.CreateCachedContentConfig(
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=kb_content)]
                    )
                ],
                system_instruction=SYSTEM_GUARDRAIL_PROMPT,
                ttl=CACHE_TTL,
                display_name="ormuri_linguistics_kb"
            )
        )
        print(f"[SUCCESS] Context Cache Created: {cache.name}")
        print(f"          Expire Time: {cache.expire_time}")
        return cache.name
    except ClientError as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            print(f"[INFO] Free tier active: Persistent server-side cache storage has limit=0 tokens.")
            print(f"       Proceeding with direct In-Context Learning (ICL) inside {model_name}'s window.")
            return None
        print(f"[WARNING] Cache creation encountered ClientError: {e}")
        return None
    except Exception as e:
        print(f"[WARNING] Cache creation error: {e}. Falling back to direct ICL.")
        return None

def generate_ormuri(
    client: Optional[genai.Client] = None,
    prompt: str = "",
    cache_name: Optional[str] = None,
    kb_content: Optional[str] = None,
    model_name: str = MODEL_NAME,
    temperature: float = 0.2
) -> str:
    """Execute generation with live anti-hallucination scratchpad and seamless key rotation."""
    print(f"\n[*] Generating Ormuri response with {model_name} (temperature={temperature})...")
    
    models_to_try = [model_name]
    for alt in ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.7-flash", "gemini-3.8-flash", "gemini-flash-latest"]:
        if alt not in models_to_try:
            models_to_try.append(alt)

    last_error = None
    max_key_rotations = max(1, len(KEY_POOL.keys))

    for key_turn in range(max_key_rotations):
        active_client, active_key, key_idx = KEY_POOL.get_client()

        for current_model in models_to_try:
            for attempt in range(1, 3):
                try:
                    if cache_name and current_model == model_name:
                        response = active_client.models.generate_content(
                            model=current_model,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                cached_content=cache_name,
                                temperature=temperature,
                            )
                        )
                    else:
                        # In-Context Learning: Provide prompt alongside the knowledge base
                        full_prompt = (
                            f"{SYSTEM_GUARDRAIL_PROMPT}\n\n"
                            f"# ORMURI REFERENCE KNOWLEDGE BASE\n\n{kb_content}\n\n"
                            f"---\n\n"
                            f"USER GENERATION TASK:\n{prompt}"
                        )
                        response = active_client.models.generate_content(
                            model=current_model,
                            contents=[
                                types.Content(role="user", parts=[types.Part.from_text(text=full_prompt)])
                            ],
                            config=types.GenerateContentConfig(
                                temperature=temperature,
                            )
                        )
                    
                    return response.text

                except (ClientError, APIError) as e:
                    last_error = e
                    err_lower = str(e).lower()
                    is_quota = any(w in err_lower for w in ["429", "resource_exhausted", "quota", "rate limit"])
                    is_unavailable = any(w in err_lower for w in ["503", "unavailable", "high demand", "overloaded"])
                    is_not_found = any(w in err_lower for w in ["404", "not_found", "not found", "no longer available"])
                    
                    if is_unavailable or is_not_found:
                        print(f"[MODEL-FALLBACK] Model {current_model} is {('not available (404)' if is_not_found else 'experiencing high demand (503)')}. Trying fallback model...")
                        break  # Try next model in models_to_try
                    elif is_quota:
                        print(f"[QUOTA-LIMIT] Key #{key_idx + 1} reached quota limit (429). Rotating to next API key...")
                        KEY_POOL.mark_rate_limited(key_idx, 60.0)
                        active_client, active_key, key_idx = KEY_POOL.rotate(reason="429 Rate Limit")
                        break  # Try next model/key
                    else:
                        print(f"[RETRY] Key #{key_idx + 1} Model {current_model} attempt {attempt}/2 returned error: {e}")
                        time.sleep(1.0 * attempt)
                except Exception as e:
                    last_error = e
                    print(f"[RETRY] Key #{key_idx + 1} Unexpected error on {current_model}: {e}")
                    time.sleep(1.0 * attempt)

    raise RuntimeError(f"Failed to generate after trying {max_key_rotations} API keys: {last_error}")


def main():
    parser = argparse.ArgumentParser(description="Ormuri AI Generative Linguistics Engine")
    parser.add_argument("--prompt", type=str, help="Prompt for generation")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive session")
    core_kb = "ormuri_core_kb.md" if os.path.exists("ormuri_core_kb.md") else "ormuri_knowledge_base.md"
    parser.add_argument("--kb", type=str, default=core_kb, help="Path to knowledge base file")
    parser.add_argument("--model", type=str, default=MODEL_NAME, help="Gemini Model ID")
    parser.add_argument("--temp", type=float, default=0.2, help="Sampling temperature")
    parser.add_argument("--api-key", type=str, default=DEFAULT_API_KEY, help="Google Gemini API Key")
    parser.add_argument("--output", type=str, help="Optional file to save generated text")
    args = parser.parse_args()

    kb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.kb)
    kb_content = load_knowledge_base(kb_path)

    client = genai.Client(api_key=args.api_key)

    # Attempt Context Cache
    cache_name = get_or_create_cache(client, kb_content, model_name=args.model)

    if args.interactive:
        print("\n=== Interactive Ormuri Generation Mode ===")
        print("Type your generation request in English or Urdu (e.g. 'Write a story about Kaniguram').")
        print("Type 'exit' or 'quit' to end.\n")
        while True:
            try:
                user_input = input("Ormuri AI> ").strip()
                if not user_input or user_input.lower() in ["exit", "quit"]:
                    break
                result = generate_ormuri(client, user_input, cache_name=cache_name, kb_content=kb_content, model_name=args.model, temperature=args.temp)
                print("\n" + "="*70)
                print(result)
                print("="*70 + "\n")
            except (KeyboardInterrupt, EOFError):
                break
    elif args.prompt:
        result = generate_ormuri(client, args.prompt, cache_name=cache_name, kb_content=kb_content, model_name=args.model, temperature=args.temp)
        print("\n" + "="*70)
        print(result)
        print("="*70 + "\n")
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"[OK] Saved output to {args.output}")
    else:
        # Default test run: 3-paragraph descriptive passage in Ormuri about Kaniguram
        default_prompt = (
            "Write a rich 3-paragraph descriptive passage in authentic Ormuri (Bargista) about Kaniguram (کانیګرام), "
            "the ancestral homeland of the Burki people in South Waziristan.\n"
            "- Paragraph 1: The geography, climate, towering mountains (ګری), cold streams (تاک), and ancient beauty of the town.\n"
            "- Paragraph 2: The historical craftsmanship of the Burki people, their famous iron-forging and knife-making (بټخِنړئ ګپ لاسته ا رو جدا کېک), "
            "and their resilience.\n"
            "- Paragraph 3: The spirit of hospitality (مېلمۀ), community solidarity, and prayers for the peace and enduring life of the Ormuri language.\n"
            "Strictly follow the morphological scratchpad requirement for every sentence before presenting the final Ormuri text."
        )
        print("[*] No prompt specified. Running Stage 3 Verification prompt...")
        result = generate_ormuri(client, default_prompt, cache_name=cache_name, kb_content=kb_content, model_name=args.model, temperature=args.temp)
        print("\n" + "="*70)
        print(result)
        print("="*70 + "\n")
        with open("kaniguram_verification.md", "w", encoding="utf-8") as f:
            f.write(result)
        print("[OK] Verification output saved to kaniguram_verification.md")

if __name__ == "__main__":
    main()
