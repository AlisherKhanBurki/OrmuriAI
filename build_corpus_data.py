"""
build_corpus_data.py
Extracts the 10 Unabridged Works of the Ormuri Primary Corpus Archive
from ormuri_knowledge_base.md (excluding Gospel of Luke)
and generates frontend/corpus_data.js
"""

import sys
import os
import re
import json

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(BASE_DIR, "ormuri_knowledge_base.md")
OUT_JS_PATH = os.path.join(BASE_DIR, "frontend", "corpus_data.js")

with open(KB_PATH, "r", encoding="utf-8") as f:
    full_text = f.read()

parts = full_text.split("## PART ")
print(f"Total parts in KB: {len(parts)-1}")

works = {}

# ----------------------------------------------------
# 1. Novel Prechaak (پرېچاک) by Rozi Khan Burki (311 pages)
# ----------------------------------------------------
prechaak_raw = parts[1]
prechaak_split = re.split(r'###\s*Prechaak\s*—\s*Page\s*(\d+)', prechaak_raw)
prechaak_items = []
for i in range(1, len(prechaak_split), 2):
    p_num = prechaak_split[i]
    p_content = prechaak_split[i+1].strip()
    if p_content:
        prechaak_items.append({
            'id': f'prechaak-p{p_num}',
            'title': f'Page {p_num}',
            'text': p_content
        })

works['prechaak'] = {
    'id': 'prechaak',
    'icon': '📖',
    'title': 'Novel Prechaak (پرېچاک)',
    'author': 'Rozi Khan Burki (روزی خان برکي)',
    'badge': f'{len(prechaak_items)} Pages Complete',
    'genre': 'Historical Novel & Classical Dialect Prose',
    'desc': 'The first complete novel written entirely in authentic Ormuri (Bargista). A 311-page literary epic chronicling Kaniguram social history, clan relationships, blood disputes, tribal assemblies, and dialect dialogue.',
    'items': prechaak_items
}

# ----------------------------------------------------
# 2. Ormuri Idioms & Phrases (وَرمَړو محاوري) by Farah Naz Burki
# ----------------------------------------------------
idiom_items = []
idiom_docx_path = os.path.join(BASE_DIR, "Ormuri Data", "WORD", "ORMURI IDIOMS AND PHRASES-3 - Copy.docx")

sections_set = {
    'پیوز', 'نِنی', 'نګُشت/ نګُشتی', 'پِټ', 'څمی/ څوم', 'دِست/ دِستی', 
    'پاړی', 'ګویٛ', 'سر', 'بیان', 'سینۀ', 'ګګېل', 'زلی', 'زبان',
    'ګس/  ګݭی', 'مُخ', 'مړمند', 'لیکيے', 'متفرق',
    'نګُشت/نګُشتی', 'څمی/څوم', 'دِست/دِستی', 'ګس/ګݭی'
}

def is_idiom_meaning_line(t):
    return any(t.startswith(k) for k in [
        'مطلب', 'ته په', 'ته پۀ', 'لفظي معنۀ', 'محاورۀ', 'محاورتاً', 'محاوتاً', 
        'او محاورۀ', 'او متل', 'يعني', 'یعنی', 'اصل مطلب', 'اصل مطلبه'
    ]) or any(k in t[:30] for k in ['مطلب', 'لفظي معنۀ', 'محاورتاً', 'محاوتاً'])

def is_idiom_example_line(t):
    return t.startswith('مثال') or t.startswith('مثاله') or 'مثال:' in t[:10]

if os.path.exists(idiom_docx_path):
    import docx
    i_doc = docx.Document(idiom_docx_path)
    curr_sec = 'پیوز'
    curr_i = None
    curr_im = []
    curr_ie = []
    parsed_idioms = []
    
    for idx_p, p_obj in enumerate(i_doc.paragraphs[47:]):
        t = p_obj.text.strip()
        if not t: continue
        if 'کمیٹی برائے تحفظ زبان ارمڑی' in t: break
        
        if t in sections_set or any(s == t.replace(' ', '') for s in sections_set):
            curr_sec = t
            continue
        
        has_num = bool(re.match(r'^\(?\d+[\.\)]\s*', t))
        if is_idiom_example_line(t):
            curr_ie.append(t)
        elif is_idiom_meaning_line(t) or t.startswith('ته ݭکوړیته لفظ کی'):
            curr_im.append(t)
        else:
            is_new = False
            if has_num or p_obj.style.name == 'List Paragraph' or curr_ie or curr_im or not curr_i:
                is_new = True
            
            if is_new:
                if curr_i:
                    parsed_idioms.append((curr_sec, curr_i, curr_im, curr_ie))
                curr_i = t
                curr_im = []
                curr_ie = []
            else:
                curr_im.append(t)
                
    if curr_i:
        parsed_idioms.append((curr_sec, curr_i, curr_im, curr_ie))
        
    start_idiom_num = 1
    for offset, (sec, phrase, m_lines, e_lines) in enumerate(parsed_idioms):
        idiom_num = start_idiom_num + offset
        body_parts = [f"【{sec}】", phrase]
        if m_lines:
            body_parts.append("\n".join(m_lines))
        if e_lines:
            body_parts.append("\n".join(e_lines))
        idiom_items.append({
            'id': f'idiom-{idiom_num}',
            'num': idiom_num,
            'title': f'Idiom #{idiom_num}',
            'text': "\n\n".join(body_parts)
        })

works['idioms'] = {
    'id': 'idioms',
    'icon': '💡',
    'title': 'Ormuri Idioms & Phrases (وَرمَړو محاوري)',
    'author': 'Farah Naz Burki (فرح ناز برکي)',
    'badge': f'{len(idiom_items):,} Complete Idioms',
    'genre': 'Idiomatic Phrases, Metaphors & Cultural Speech',
    'desc': 'Complete compendium of authentic Ormuri idiomatic phrases collected across Kaniguram and D. I. Khan, correctly demarcated with full literal explanations and colloquial usage examples.',
    'items': idiom_items
}

# ----------------------------------------------------
# 3. Ormuri Proverbs Collection (وَرمَړو متلي) by Farhana Burki
# ----------------------------------------------------
proverb_items = []
proverb_docx_path = os.path.join(BASE_DIR, "Ormuri Data", "WORD", "Ormuri Proverbs Final PA3.docx")

if os.path.exists(proverb_docx_path):
    import docx
    p_doc = docx.Document(proverb_docx_path)
    curr_p = None
    curr_m = []
    curr_e = []
    parsed_proverbs = []
    
    for p in p_doc.paragraphs[31:]:
        t = p.text.strip()
        if not t: continue
        if t == 'خاتمه': break
        is_new = False
        if p.style.name == 'List Paragraph':
            is_new = True
        elif any(t.startswith(f'{n})') or t.startswith(f'({n}') or f'({n}' in t for n in range(300, 365)):
            is_new = True
        if is_new:
            if curr_p:
                parsed_proverbs.append((curr_p, curr_m, curr_e))
            curr_p = t
            curr_m = []
            curr_e = []
        else:
            if t.startswith('مثال') or 'مثال:' in t or t.startswith('مثاله'):
                curr_e.append(t)
            else:
                curr_m.append(t)
    if curr_p:
        parsed_proverbs.append((curr_p, curr_m, curr_e))
        
    start_proverb_num = 1
    for offset, (prov, m_lines, e_lines) in enumerate(parsed_proverbs):
        proverb_num = start_proverb_num + offset
        body_parts = [prov]
        if m_lines:
            body_parts.append("\n".join(m_lines))
        if e_lines:
            body_parts.append("\n".join(e_lines))
        proverb_items.append({
            'id': f'proverb-{proverb_num}',
            'num': proverb_num,
            'title': f'Proverb #{proverb_num}',
            'text': "\n\n".join(body_parts)
        })

works['proverbs'] = {
    'id': 'proverbs',
    'icon': '📜',
    'title': 'Ormuri Proverbs Collection (وَرمَړو متلي)',
    'author': 'Farhana Burki (فرحانه برکي)',
    'badge': f'{len(proverb_items):,} Complete Proverbs',
    'genre': 'Oral Lore, Traditional Tribal Wisdom & Adages',
    'desc': 'Complete collection of authentic Ormuri proverbs (Warmaṛo Matali), correctly demarcated with full literal explanations and practical moral usage examples.',
    'items': proverb_items
}

# ----------------------------------------------------
# 4. Traditional Folk Stories & Lore (ولسي کیسې)
# ----------------------------------------------------
stories_raw = parts[5]
story_lines = [l.strip() for l in stories_raw.split('\n') if l.strip() and not l.startswith('**') and not l.startswith('V:')]
story_items = []
chunk_size = 20
for i in range(0, len(story_lines), chunk_size):
    chunk = story_lines[i:i+chunk_size]
    episode_num = (i // chunk_size) + 1
    # Check for notable title in chunk
    first_line = chunk[0]
    t_label = f"Folk Lore Episode {episode_num}"
    if 'ݭِواخي' in first_line:
        t_label = "Legend of Shwakhi Khekani (ݭِواخي خیکَنئ)"
    elif 'زرګتئی' in first_line:
        t_label = "Folk Tale of Zargat'ay (زرګتئی)"
    elif 'اوستاکار' in first_line:
        t_label = "The Iron-Smiths of Baar Pit (اوستاکار)"

    story_items.append({
        'id': f'story-{episode_num}',
        'title': t_label,
        'text': '\n'.join(chunk)
    })

works['stories'] = {
    'id': 'stories',
    'icon': '🏔️',
    'title': 'Traditional Folk Stories & Lore (ولسي کیسې)',
    'author': 'Oral Tradition & Folk Historians of Kaniguram',
    'badge': f'{len(story_items)} Narrative Episodes ({len(story_lines)} Paragraphs)',
    'genre': 'Folk Tales, Legends & Oral Narratives',
    'desc': 'Ancient oral stories passed down through generations in Kaniguram, depicting the legendary iron-smiths of Baar Pit, mountain spirits, and tribal heroics.',
    'items': story_items
}

# ----------------------------------------------------
# 5. Charter of Human Rights (UDHR)
# ----------------------------------------------------
udhr_raw = parts[7]
udhr_lines = [l.strip() for l in udhr_raw.split('\n') if l.strip() and not l.startswith('**') and not l.startswith('VII:')]
udhr_items = []

# Preamble: lines 5 to 30
preamble_lines = []
curr_art_title = "Preamble (مقدمۀ د منشور)"
curr_art_lines = []

ordinal_names = [
    'اول (Article 1)', 'دیم (Article 2)', 'ڒیم (Article 3)', 'څرُم (Article 4)',
    'پِنځُم (Article 5)', 'شهُم (Article 6)', 'وووُم (Article 7)', 'هنشتُم (Article 8)',
    'نهُم (Article 9)', 'دسُم (Article 10)', 'سندسُم (Article 11)', 'دواسُم (Article 12)',
    'ڒیسُم (Article 13)', 'څارسُم (Article 14)', 'پندزسُم (Article 15)', 'شپاسُم (Article 16)',
    'اووسُم (Article 17)', 'هنشتسُم (Article 18)', 'نسُم (Article 19)', 'جستُم (Article 20)',
    'سه ویزر جستو (Article 21)', 'دیو ویزر جستو (Article 22)', 'ڒی ویزر جستو (Article 23)',
    'څار ویزر جستو (Article 24)', 'پینځ ویزر جستو (Article 25)', 'شپږ ویزر جستو (Article 26)',
    'اوو ویزر جستو (Article 27)', 'هنشت ویزر جستو (Article 28)', 'نه ویزر جستو (Article 29)',
    'دس ویزر جستو (Article 30)'
]

art_idx = 0
for line in udhr_lines[2:]:
    is_art_start = False
    for ord_prefix in ['اول :', 'دیم :', 'ڒیم :', 'څرُم :', 'پِنځُم :', 'شهُم :', 'وووُم :', 'هنشتُم :', 'نهُم :', 'دسُم :', 'سندسُم :', 'دواسُم :', 'ڒیسُم :', 'څارسُم :', 'پندزسُم :', 'شپاسُم :', 'اووسُم :', 'هنشتسُم :', 'نسُم :', 'جستُم :']:
        if line.startswith(ord_prefix):
            is_art_start = True
            break
    
    if is_art_start:
        if curr_art_lines:
            udhr_items.append({
                'id': f'udhr-{len(udhr_items)+1}',
                'title': curr_art_title,
                'text': '\n'.join(curr_art_lines)
            })
        art_idx += 1
        label = ordinal_names[art_idx - 1] if art_idx <= len(ordinal_names) else f"Article {art_idx}"
        curr_art_title = f"مادۀ {label}"
        curr_art_lines = [line]
    else:
        curr_art_lines.append(line)

if curr_art_lines:
    udhr_items.append({
        'id': f'udhr-{len(udhr_items)+1}',
        'title': curr_art_title,
        'text': '\n'.join(curr_art_lines)
    })

works['udhr'] = {
    'id': 'udhr',
    'icon': '🕊️',
    'title': 'Charter of Human Rights (د بشري حقونو نړیواله اعلامیه)',
    'author': 'Universal Declaration of Human Rights (UDHR)',
    'badge': f'{len(udhr_items)} Articles & Preamble',
    'genre': 'Civic, Legal & Human Rights Register',
    'desc': 'Official Ormuri translation of all 30 Articles of the Universal Declaration of Human Rights, demonstrating the expressive precision and legal register of modern Bargista.',
    'items': udhr_items
}

# ----------------------------------------------------
# 6. Ormuri Poetry Anthology (بارګِسته شاعري)
# ----------------------------------------------------
poetry_raw = parts[6]
poetry_split = re.split(r'###\s*Poetry\s*—\s*Page\s*(\d+)', poetry_raw)
poetry_items = []
for i in range(1, len(poetry_split), 2):
    p_num = poetry_split[i]
    p_content = poetry_split[i+1].strip()
    if p_content:
        poetry_items.append({
            'id': f'poetry-p{p_num}',
            'title': f'Verse Anthology Page {p_num}',
            'text': p_content
        })

works['poetry'] = {
    'id': 'poetry',
    'icon': '🎭',
    'title': 'Ormuri Poetry Anthology (بارګِسته شاعري)',
    'author': 'Classical & Contemporary Burki Poets',
    'badge': f'{len(poetry_items)} Pages of Verse',
    'genre': 'Ormuri Verse, Meter, Ghazals & Rhymes',
    'desc': 'Complete 52-page poetic anthology reflecting traditional meters, rhyming schemes, nature imagery of South Waziristan, and deep emotional resonance in the Ormuri mother tongue.',
    'items': poetry_items
}

# ----------------------------------------------------
# 7. 10 Infinitive Verbs & Conjugation Paradigms
# ----------------------------------------------------
verbs_raw = parts[8]
verb_split = re.split(r'###\s*Verb Book\s*—\s*Page\s*(\d+)', verbs_raw)
verb_items = []
for i in range(1, len(verb_split), 2):
    p_num = verb_split[i]
    p_content = verb_split[i+1].strip()
    if p_content:
        verb_items.append({
            'id': f'verb-p{p_num}',
            'title': f'Verb Paradigm Page {p_num}',
            'text': p_content
        })

works['verbs'] = {
    'id': 'verbs',
    'icon': '⚡',
    'title': '10 Infinitive Verbs & Conjugation Paradigms',
    'author': 'Linguistic Documentation Archive',
    'badge': f'{len(verb_items)} Pages of Paradigms',
    'genre': 'Morphological Stems & Verb Conjugations',
    'desc': 'Comprehensive 47-page grammatical record covering 500+ inflected forms, ablaut stems, past/present transitive-intransitive polarity, and agentive agreement markers.',
    'items': verb_items
}

# ----------------------------------------------------
# 8. Ormuri Primer 2 (ارمڑی پرائمر) by Rozi Khan Burki
# ----------------------------------------------------
primer_raw = parts[9]
primer_split = re.split(r'###\s*Primer 2\s*—\s*Page\s*(\d+)', primer_raw)
primer_items = []
for i in range(1, len(primer_split), 2):
    p_num = primer_split[i]
    p_content = primer_split[i+1].strip()
    if p_content:
        primer_items.append({
            'id': f'primer-p{p_num}',
            'title': f'Primer Lesson Page {p_num}',
            'text': p_content
        })

works['primer'] = {
    'id': 'primer',
    'icon': '📘',
    'title': 'Ormuri Primer 2 (ارمڑی پرائمر)',
    'author': 'Rozi Khan Burki (روزی خان برکي)',
    'badge': f'{len(primer_items)} Primer Pages',
    'genre': 'Orthography, Phonology & Foundational Lessons',
    'desc': 'Authoritative 109-page textbook officially sanctioned by the KP Government and Pashto Academy Peshawar University, containing the 48-letter alphabet, IPA phonetic tables, and conversational drills.',
    'items': primer_items
}

# ----------------------------------------------------
# 9. Linguistic Abbreviations & Dialectology
# ----------------------------------------------------
abbrev_raw = parts[10]
abbrev_split = re.split(r'###\s*Abbreviations\s*—\s*Page\s*(\d+)', abbrev_raw)
abbrev_items = []
for i in range(1, len(abbrev_split), 2):
    p_num = abbrev_split[i]
    p_content = abbrev_split[i+1].strip()
    if p_content:
        abbrev_items.append({
            'id': f'abbrev-p{p_num}',
            'title': f'Linguistic Notes Page {p_num}',
            'text': p_content
        })

works['abbrev'] = {
    'id': 'abbrev',
    'icon': '🔍',
    'title': 'Linguistic Abbreviations & Dialectology',
    'author': 'Linguistic Fieldwork & Grammatical Analysis',
    'badge': f'{len(abbrev_items)} Reference Pages',
    'genre': 'Grammatical Standards, Notations & Case Syntax',
    'desc': 'Essential grammatical key detailing standard phonetic symbols, case declensions, circumpositions, and Wackernagel clitic hosting positions.',
    'items': abbrev_items
}

# ----------------------------------------------------
# 10. Comprehensive Dictionary Corpus Overview
# ----------------------------------------------------
works['dict'] = {
    'id': 'dict',
    'icon': '🏛️',
    'title': 'Ormuri Illustrated Dictionary Corpus (قاموس / ډکشنري)',
    'author': 'Rozi Khan Burki (روزی خان برکي)',
    'badge': '6,657 Headwords Complete',
    'genre': 'Unabridged Dictionary with IPA, POS & Urdu Glosses',
    'desc': 'The complete 6,657-word unabridged Ormuri dictionary, including all nouns, verbs, adjectives, cultural terms, and Kaniguram idioms. Full database is accessible via the Dictionary viewer.',
    'items': [
        {
            'id': 'dict-summary-1',
            'title': 'Dictionary Overview & Corpus Statistics',
            'text': 'The unabridged Ormuri Dictionary Corpus contains 6,657 headwords with exact International Phonetic Alphabet (IPA) transcriptions, Part of Speech tags, and Urdu/English definitions. It covers archaic Western Iranian cognates, Kaniguram iron-smithing terms, floral and fauna names, and full verbal paradigms.'
        },
        {
            'id': 'dict-summary-2',
            'title': 'Living Lexical Preservation Status',
            'text': 'Preserved from Rozi Khan Burki\'s monumental lexicographical fieldwork. Every single headword is fully indexed in the interactive Dictionary drawer with search and part-of-speech filtering (Nouns, Verbs, Adjectives, Adverbs, Pronouns/Clitics).'
        }
    ]
}

# Output to JavaScript file
js_content = "/**\n * Unabridged Primary Corpus Archive Data\n * 10 Authentic Primary Works of Kaniguram Ormuri (Bargista)\n */\n"
js_content += "window.CORPUS_DATA = " + json.dumps(works, ensure_ascii=False, indent=2) + ";\n"

with open(OUT_JS_PATH, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"[OK] Generated {OUT_JS_PATH} ({os.path.getsize(OUT_JS_PATH)/1024:.1f} KB)")
