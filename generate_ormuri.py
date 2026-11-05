"""
generate_ormuri.py
Official Google GenAI SDK script with Context Caching and In-Context Learning (ICL)
for Ormuri (Bargista / اُرموړی) generation with strict linguistic guardrails.
"""

import os
import sys
import argparse
import time
from typing import Optional, Generator

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

MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
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

You are provided with an authoritative linguistic knowledge base and a dynamically retrieved lexicon in your context.

========================================================================================
CRITICAL SYNTAX & VOCABULARY GUARDRAILS (ABSOLUTE ZERO TOLERANCE FOR DEVIATION):
========================================================================================

1. 🚫 STRICT PROHIBITION OF PASHTO & URDU CODE-SWITCHING:
   - Ormuri is an autonomous Western Iranian language. It is NOT Pashto, and NOT Persian.
   - You MUST NEVER insert Pashto function words or Urdu/Persian vocabulary when composing Ormuri.
   - BANNED TOKENS IN THE ORMURI SECTION (ZERO TOLERANCE):
     * ❌ NEVER USE Pashto 'د' (da) for 'of'. Ormuri uses direct noun juxtaposition (e.g. 'کانیګرام تاک' = stream of Kaniguram) or oblique clitics!
     * ❌ NEVER USE Pashto 'ته' (tə) as a preposition for 'to / towards'. In Ormuri, 'ته' [tə] is strictly the PRONOUN 'YOU' (2SG)! For 'to / for', use 'ال' (al) or postposition 'نر' (nar)!
     * ❌ NEVER USE Pashto 'پاره' (pārə) or 'لپاره' (ləpārə) for purpose in Ormuri script!
     * ❌ NEVER USE Pashto 'په' (pə). In Ormuri, use circumposition 'ته ... نر' (tə ... nar) or preposition 'پا' (pā)!
     * ❌ NEVER USE Pashto 'که' (kə) as a relative pronoun or conjunction!
     * ❌ NEVER USE Pashto 'دی' (day) as a copula ("is"). In Ormuri, 3SG present copula is strictly 'ہۀ' (hʌ) or 'ان' (in)!
     * ❌ NEVER USE Pashto 'دي' (dī) as plural copula ("are"). In Ormuri, 3PL present copula is strictly 'ہین' (hīn) or 'این' (īn)!
     * ❌ NEVER USE Pashto 'کول / کړل' (kawəl / kṛəl). In Ormuri, 'to do' is 'دوک' (dōk) in past, 'کن-' (kan-) in present!
     * ❌ NEVER USE Pashto 'ویل / وویل' (wayəl / wuwayəl). In Ormuri, 'to say' is 'غوېڅوک' (ɣwētsōk) in past, 'غوېڅن' (ɣwētsən) in present!
     * ❌ NEVER USE Pashto 'تلل / تګ' (tləl / tag). In Ormuri, 'to go' is 'څوک' (tsōk) in past, 'څوا' (tswā) in present!
     * ❌ NEVER USE Pashto 'راتلل / راغلل' (rātləl / rāɣləl). In Ormuri, 'to come' is 'بیوک' (byōk) in past, 'با' (bā) in present!
     * ❌ NEVER USE Pashto 'څښل' (tsəx̌əl). In Ormuri, 'to drink' is 'تتک' (tətək) in past, 'ترون' (trōn) in present!
     * ❌ NEVER USE Pashto 'خوړل' (xwāṛəl). In Ormuri, 'to eat' is 'خوراک' (xwārāk) in past, 'خورا' (xwarā) in present!
     * ❌ NEVER USE Pashto 'کتل / لیدل' (katəl / līdəl). In Ormuri, 'to see' is 'بوک' (bōk) in past, 'بین-' (bīn-) in present!
     * ❌ NEVER USE Pashto 'څنګه' (tsənga). In Ormuri, 'how' is 'چونَګ' (čōnak) or 'کِشَن' (kišan)!
     * ❌ NEVER USE Pashto 'ولې' (walē). In Ormuri, 'why' is 'چيرا' (čērā)!
     * ❌ NEVER USE 'دیو' (dyō) for language! In Ormuri, 'دیو' strictly means the NUMBER TWO (2). Language is strictly 'زبان' (zbān) / 'ورمړو زبان' (Warmaṛō zbān)!
     * ❌ NEVER USE Arabic/Urdu/Pashto meta-linguistic labels ('مذکر', 'اسم', 'مؤنث', 'اصیل نام', 'بڼه', 'معنی') inside the Ormuri section!

2. 🛡️ MANDATORY ORMURI FUNCTION WORD & COPULA MATRIX:
   - 1SG Subject: 'از' (az) | Enclitic: '-م' (-m)
   - 2SG Subject: 'تو' (tu) | Oblique: 'تہ' (tə) | Enclitic: '-ت' (-t)
   - 3SG Subject: 'او' (ō) / 'آ' (ā) | Oblique: 'فۀ' (fə) | Enclitic: '-وۀ' (-wə) / '-ل' (-l)
   - 1PL Subject: 'ماخ' (māx) | Enclitic: '-ماخ' (-māx)
   - 2PL Subject: 'توس' (tyōs) | Enclitic: '-توس' (-tyōs)
   - 3PL Subject: 'ای' (ay) | Enclitic: '-ن' (-n)
   - Present/Habitual Marker: 'بُو' (bu) [precedes or attaches to verb]
   - Future/Modal Marker: 'سُو' (su)
   - 3SG Present Copula ("is"): strictly 'ہۀ' (hʌ) or 'ان' (in)
   - 3PL Present Copula ("are"): strictly 'ہین' (hīn) or 'این' (īn)
   - Negation: 'نۀ' (nə) / 'نَک' (nak)
   - Negative Copula ("is not"): 'نیسْت' (nēst) / 'نۀ هۀ' (nə hʌ)
   - Focus / Topicalizer: 'يې' (yē)
   - "In / inside": 'ته ... نر' (tə ... nar) or 'نره' (narə)
   - "Upon / on": 'پا ... زر' (pā ... zar) or 'زر' (zar)
   - "With": 'سۀ' (sə) or 'سټ' (saṭ)
   - "To / towards": 'ال' (al) or postposition 'نر' (nar)
   - "And": 'او' (aw)
   - "Very": 'زُت' (zut)
   - "Good / fine": 'ښه' (xša) / 'جَم' (ǰam)

3. ⚖️ EXACT SPLIT ERGATIVITY ALGEBRA:
   - Present / Future Tenses (Nominative-Accusative):
     * Subject is in Direct Case (az, tu, o, max, tyos, ay).
     * Verb agrees in person/number with the SUBJECT via finite suffixes (-m, -yen, -Ø, -ay, -y, -in).
     * Marker is 'بُو' (bu) for present and 'سُو' (su) for future.
     * Example: 'از بُو وک تروم۔' (Az bu wək trōm - "I drink water.")
     * Example: 'څاک وک بُو تاک نر څوا۔' (Tsāk wək bu tāk nar tswā - "Cold water flows in the stream.")
   - Past Transitive Tenses (ERGATIVE-ABSOLUTIVE):
     * The Agent takes enclitic (-m, -t, -wə, -n) or particle 'ال' (al).
     * The Verb MUST agree in GENDER and NUMBER with the OBJECT (Patient), NEVER the subject!
     * Masculine Past Verb: stem + -ək/-ūk (e.g. 'تتک' drank masc, 'دوک' did masc, 'خوراک' ate masc).
     * Feminine Past Verb: stem + -ak/-uk (e.g. 'داک' did fem, 'بُک' was fem).
     * Plural Past Verb: stem + -in/-kin (e.g. 'بُکِن' were pl, 'داکین' did pl).
     * Example: 'از ال څاک وک تتک۔' (Az al tsāk wək tətək - "I drank cold water." Agent=az al, Object=wək [masc], Verb=tətək [masc]).
     * Example: 'او وه ډُوډی خوراک۔' (O wə ḍūḍī xwārāk - "He ate bread.")

4. 🔬 MANDATORY MORPHOLOGICAL SCRATCHPAD REQUIREMENT:
   - Before outputting ANY surface sections, you MUST open a `<morphological_scratchpad>` block.
   - Inside `<morphological_scratchpad>`, you must systematically pass EVERY planned Ormuri sentence through the 5 morphological verification guardrails:
     * Sentence [N]: "[English / planned meaning]"
       - Tense / Aspect / Mood: [Present habitual ('بُو' bu) | Future ('سُو' su) | Past Transitive (Ergative) | Past Intransitive]
       - Split Ergativity & Case Alignment: [Direct nominative subject (az, tu, o, max, tyos, ay) OR Ergative agent with enclitic (-m, -t, -wə, -n) or 'ال' (al)]
       - Object-Verb Agreement Check: [In Past Transitive: Verb agrees in gender and number with the OBJECT (Patient), NEVER the subject! (Masc: -ək/-ūk, Fem: -ak/-uk, Pl: -in/-kin)]
       - Enclitics & Particles: [Host - Clitic alignment (-m, -t, -wə, -n, yē, al), Postpositions ('نر' nar, 'زر' zar), Prepositions ('پا' pā, 'سۀ' sə)]
       - Lexical & Anti-Pashto Audit: [Confirm every root word is sourced from 'Module 6: TARGETED RELEVANT LEXICON'; verify ZERO Pashto/Urdu intrusion (no 'د', 'دی', 'کول', 'ته' as preposition, etc.)]
   - Close the scratchpad with `</morphological_scratchpad>` before emitting '### Polished Ormuri (Bargista / اُرموړی) Text'.

5. 🎯 SECTION FORMULATION RULES:
   - '### Polished Ormuri (Bargista / اُرموړی) Text':
     * For vocabulary questions or translations: State the target Ormuri word/phrase clearly, followed by 2–3 AUTHENTIC, NATURAL DAILY-LIFE EXAMPLE SENTENCES in Ormuri script showing how native speakers use the word.
     * NEVER try to explain grammar or linguistics using Arabic/Urdu/Pashto words inside this section!
     * Every sentence here must be 100% pure authentic Ormuri dialogue or statement.
   - '### Phonetic Romanization':
     * 1-to-1 IPA romanization matching the Ormuri section sentence by sentence.
   - '### Translation & Notes':
     * Provide comprehensive explanations, translations, morphological breakdowns, gender/number classifications, and answers in the user's requested language (English, Urdu, or Pashto).

6. 📖 LEXICAL FIDELITY (ZERO HALLUCINATION & GROUND-TRUTH SOURCING):
   - You MUST strictly use the authentic Ormuri words provided in the 'TARGETED RELEVANT LEXICON' and 'CORE FUNCTION MATRIX'.
   - NEVER invent pseudo-Ormuri words:
     * Milk is strictly 'شیپی' [šīpī] — NEVER invent fake words like 'ورمه'!
     * Village / Town is strictly 'ښار' [šār], 'شور' [šōr], or 'کانیګرام' [Kānīgrām] — NEVER use Pashto 'کلی' [kəlay]!
     * Cow / Cattle is strictly 'ګوَئ' [ɡwəy] or 'ګیویٛ' [ɡyōy] — NEVER use Pashto 'غوا'!
     * Goat is strictly 'وزۀ' [wzəʰ] (Plural: 'وݫي' [wʑī]), or 'بُز' [buz] (he-goat), or 'څرووک' [tsərwōk]!
     * Grass / Grazing fodder is strictly 'غواݭی' [ɣwāɕī] or 'وښه' [wəxa] — ('خور' strictly means sister, not fodder)!
     * Strong / Healthy is strictly 'ټینګ' [ṭīng] or 'زورَوَر' [zōrawar] — NEVER Pashto 'تکړه'!
     * To graze is 'څوا' [tswā] or 'چرَؤ' [čarʌw]!
     * To milk is 'دُسیېک' [dusyæk] / 'دُسؤ' [dussʌw]!
   - NATIVE SENTENCE PATTERNS: The dictionary entries contain authentic example sentences in brackets '[...]' (e.g. 'نر ګیویٛ ان يې دُسيېک' = He milked the cow; 'ا سپئے ا شیپی توتک' = The bitch drank the milk; 'ا څرووک بُو ګړديې شیو بُغيېک' = The goat was bleating the whole night). Adapt these authentic patterns directly!
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

def generate_ormuri_stream(
    client: Optional[genai.Client] = None,
    prompt: str = "",
    cache_name: Optional[str] = None,
    kb_content: Optional[str] = None,
    model_name: str = MODEL_NAME,
    temperature: float = 0.2
) -> Generator[str, None, None]:
    """Execute streaming generation yielding chunks token-by-token with automatic key rotation and fallback."""
    print(f"\n[*] Generating streaming Ormuri response with {model_name} (temperature={temperature})...")
    
    models_to_try = [model_name]
    for alt in ["gemini-3.5-flash", "gemini-3.6-flash"]:
        if alt not in models_to_try:
            models_to_try.append(alt)

    last_error = None
    max_key_rotations = max(1, len(KEY_POOL.keys))

    for key_turn in range(max_key_rotations):
        active_client, active_key, key_idx = KEY_POOL.get_client()

        for current_model in models_to_try:
            for attempt in range(1, 3):
                has_yielded = False
                try:
                    if cache_name and current_model == model_name:
                        response_stream = active_client.models.generate_content_stream(
                            model=current_model,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                cached_content=cache_name,
                                temperature=temperature,
                            )
                        )
                    else:
                        full_prompt = (
                            f"{SYSTEM_GUARDRAIL_PROMPT}\n\n"
                            f"# ORMURI REFERENCE KNOWLEDGE BASE\n\n{kb_content}\n\n"
                            f"---\n\n"
                            f"USER GENERATION TASK:\n{prompt}"
                        )
                        response_stream = active_client.models.generate_content_stream(
                            model=current_model,
                            contents=[
                                types.Content(role="user", parts=[types.Part.from_text(text=full_prompt)])
                            ],
                            config=types.GenerateContentConfig(
                                temperature=temperature,
                            )
                        )

                    for chunk in response_stream:
                        chunk_text = chunk.text
                        if chunk_text:
                            has_yielded = True
                            yield chunk_text

                    return

                except (ClientError, APIError) as e:
                    last_error = e
                    if has_yielded:
                        # Stream was broken mid-way, re-raise so caller knows
                        raise e

                    err_lower = str(e).lower()
                    is_quota = any(w in err_lower for w in ["429", "resource_exhausted", "quota", "rate limit"])
                    is_unavailable = any(w in err_lower for w in ["503", "unavailable", "high demand", "overloaded"])
                    is_not_found = any(w in err_lower for w in ["404", "not_found", "not found", "no longer available"])

                    if is_not_found:
                        print(f"[MODEL-FALLBACK] Model {current_model} is not available (404). Trying fallback model...")
                        break
                    elif is_unavailable:
                        print(f"[MODEL-BUSY] Model {current_model} experiencing high demand (503) on Key #{key_idx + 1} (attempt {attempt}/2).")
                        if attempt == 1:
                            time.sleep(1.0)
                            active_client, active_key, key_idx = KEY_POOL.rotate(reason="503 High Demand")
                            continue
                        else:
                            print(f"[MODEL-FALLBACK] Switching to fallback model...")
                            break
                    elif is_quota:
                        print(f"[QUOTA-LIMIT] Key #{key_idx + 1} reached quota limit (429). Rotating to next API key...")
                        KEY_POOL.mark_rate_limited(key_idx, 60.0)
                        active_client, active_key, key_idx = KEY_POOL.rotate(reason="429 Rate Limit")
                        break
                    else:
                        print(f"[RETRY] Key #{key_idx + 1} Model {current_model} attempt {attempt}/2 returned error: {e}")
                        time.sleep(1.0 * attempt)
                except Exception as e:
                    last_error = e
                    if has_yielded:
                        raise e
                    print(f"[RETRY] Key #{key_idx + 1} Unexpected error on {current_model}: {e}")
                    time.sleep(1.0 * attempt)

    raise RuntimeError(f"Failed to generate after trying {max_key_rotations} API keys: {last_error}")


ENGLISH_GROUNDING_PROMPT = """You are a computational linguist and master lexicographer preparing a high-fidelity translation and linguistic answer for Ormuri (Bargista / اُرموړی), an endangered Western Iranian language.

YOUR SOLE MISSION IN THIS STAGE:
Provide a comprehensive English semantic response, target concepts, and natural English conversational sentences that directly answer the user's inquiry.

CRITICAL INSTRUCTIONS:
1. Write ENTIRELY in English.
2. Do NOT fabricate or guess Ormuri words in this stage; the unabridged 6,657-word Ormuri dictionary will supply the exact Ormuri vocabulary in Stage 2.
3. Structure your response into these 3 sections:

### 1. English Direct Answer & Conceptual Explanation:
Provide a clear, detailed English explanation answering the user's inquiry. Explain the primary meanings, cultural context (pastoral life in Kaniguram, South Waziristan), and grammatical characteristics (e.g. noun gender, verb aspect).

### 2. Conversational English Sentences (to translate into Ormuri):
Provide 2 to 3 natural, authentic daily-life English sentences that illustrate the answer or demonstrate the words in natural context (e.g. daily chores, mountain life, family, livestock, food, greetings).

### 3. Key English Lexical Keywords:
List 15 to 25 single-word English nouns, verbs, adjectives, and related concepts separated by commas (e.g. cow, heifer, calf, milk, graze, grass, pasture, mountain, morning, fresh, eat, give, butter, herd, barn).
"""

def generate_english_grounding(
    prompt: str,
    mode: str = "qa_general",
    prompt_lang: str = "en",
    model_name: str = MODEL_NAME
) -> str:
    """
    Stage 1: Generate an English semantic response, conceptual breakdown, and target sentences.
    This English response serves as the ground-truth input for Dynamic Lexicon RAG, allowing RAG
    to retrieve 100% of the corresponding relevant Ormuri words from the 6,657-word lexicon.
    """
    full_prompt = (
        f"{ENGLISH_GROUNDING_PROMPT}\n\n"
        f"USER INQUIRY: {prompt}\n"
        f"MODE: {mode} | USER INPUT LANGUAGE: {prompt_lang}"
    )
    
    models_to_try = [model_name]
    for alt in ["gemini-3.5-flash", "gemini-3.6-flash"]:
        if alt not in models_to_try:
            models_to_try.append(alt)

    max_key_rotations = max(1, len(KEY_POOL.keys))
    last_error = None

    for key_turn in range(max_key_rotations):
        active_client, active_key, key_idx = KEY_POOL.get_client()

        for current_model in models_to_try:
            for attempt in range(1, 3):
                try:
                    response = active_client.models.generate_content(
                        model=current_model,
                        contents=[
                            types.Content(role="user", parts=[types.Part.from_text(text=full_prompt)])
                        ],
                        config=types.GenerateContentConfig(
                            temperature=0.2,
                        )
                    )
                    if response.text and response.text.strip():
                        return response.text.strip()
                except (ClientError, APIError) as e:
                    last_error = e
                    err_lower = str(e).lower()
                    is_quota = any(w in err_lower for w in ["429", "resource_exhausted", "quota", "rate limit"])
                    is_unavailable = any(w in err_lower for w in ["503", "unavailable", "high demand", "overloaded"])
                    is_not_found = any(w in err_lower for w in ["404", "not_found", "not found", "no longer available"])

                    if is_not_found:
                        break
                    elif is_unavailable:
                        if attempt == 1:
                            time.sleep(1.0)
                            active_client, active_key, key_idx = KEY_POOL.rotate(reason="503 High Demand")
                            continue
                        else:
                            break
                    elif is_quota:
                        KEY_POOL.mark_rate_limited(key_idx, 60.0)
                        active_client, active_key, key_idx = KEY_POOL.rotate(reason="429 Rate Limit")
                        break
                    else:
                        time.sleep(1.0 * attempt)
                except Exception as e:
                    last_error = e
                    time.sleep(1.0 * attempt)

    # Failsafe fallback: return user prompt if English grounding generation encounters API limits
    print(f"[WARNING] English grounding failed ({last_error}), falling back to direct prompt RAG.")
    return prompt


def generate_ormuri(
    client: Optional[genai.Client] = None,
    prompt: str = "",
    cache_name: Optional[str] = None,
    kb_content: Optional[str] = None,
    model_name: str = MODEL_NAME,
    temperature: float = 0.2
) -> str:
    """Execute non-streaming generation by consuming generate_ormuri_stream."""
    chunks = []
    for chunk in generate_ormuri_stream(
        client=client,
        prompt=prompt,
        cache_name=cache_name,
        kb_content=kb_content,
        model_name=model_name,
        temperature=temperature
    ):
        chunks.append(chunk)
    return "".join(chunks)


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
