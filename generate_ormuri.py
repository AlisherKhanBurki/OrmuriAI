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

# Ensure UTF-8 stdout on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError

# Default API Key provided by the user
DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBWcJEdFIP0zP5p2MWlXCCoVBocjUeRqq8")
MODEL_NAME = "gemini-3.8-flash"
CACHE_TTL = "86400s"  # 24-hour TTL

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

4. MANDATORY MORPHOLOGICAL SCRATCHPAD:
   For every generated passage or sentence, you MUST first produce a `<morphological_scratchpad>` detailing:
   - Sentence Number & Intent
   - Alignment Type (Nominative-Accusative vs Ergative-Absolutive)
   - Subject & Clitic Host
   - Object & Gender/Number Verb Agreement
   - Exact Ormuri Roots & Affixes Used
   
   After the scratchpad, output the polished Ormuri text in the standard Perso-Arabic script with all authentic letters (ݫ, ݭ, ڒ, څ, ځ, ګ), followed by phonetic Romanization and an English translation.
"""

def load_knowledge_base(kb_path: str) -> str:
    """Load the compiled ormuri_knowledge_base.md document."""
    if not os.path.exists(kb_path):
        raise FileNotFoundError(f"Knowledge base file not found at: {kb_path}")
    with open(kb_path, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"[OK] Loaded Knowledge Base ({len(content)} characters, ~{len(content.split())} words)")
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
            print(f"       Proceeding with direct In-Context Learning (ICL) inside {model_name}'s 1M-token window.")
            return None
        print(f"[WARNING] Cache creation encountered ClientError: {e}")
        return None
    except Exception as e:
        print(f"[WARNING] Cache creation error: {e}. Falling back to direct ICL.")
        return None

def generate_ormuri(
    client: genai.Client,
    prompt: str,
    cache_name: Optional[str] = None,
    kb_content: Optional[str] = None,
    model_name: str = MODEL_NAME,
    temperature: float = 0.2
) -> str:
    """Execute generation with anti-hallucination scratchpad verification and robust retry."""
    print(f"\n[*] Generating Ormuri response with {model_name} (temperature={temperature})...")
    
    models_to_try = [model_name]
    if "3.8" in model_name:
        models_to_try.append("gemini-3.7-flash")
    
    last_error = None
    for current_model in models_to_try:
        for attempt in range(1, 4):
            try:
                if cache_name and current_model == model_name:
                    response = client.models.generate_content(
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
                    response = client.models.generate_content(
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
                print(f"[RETRY] Model {current_model} attempt {attempt}/3 returned error: {e}")
                time.sleep(3 * attempt)
            except Exception as e:
                last_error = e
                print(f"[RETRY] Unexpected error on {current_model}: {e}")
                time.sleep(3 * attempt)
    
    raise RuntimeError(f"Failed to generate after retrying models {models_to_try}: {last_error}")

def main():
    parser = argparse.ArgumentParser(description="Ormuri AI Generative Linguistics Engine")
    parser.add_argument("--prompt", type=str, help="Prompt for generation")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive session")
    parser.add_argument("--kb", type=str, default="ormuri_knowledge_base.md", help="Path to knowledge base file")
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
