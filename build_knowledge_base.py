"""
build_knowledge_base.py
Synthesizes the Ormuri (Bargista / اُرموړی) Linguistic Corpus into a production-grade,
structured markdown knowledge base: `ormuri_knowledge_base.md`.
"""

import os
import sys
import re
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Ormuri Data")
WORD_DIR = os.path.join(DATA_DIR, "WORD")
PDF_DIR = os.path.join(DATA_DIR, "PDF")

def clean_bidi(text: str) -> str:
    """Strip directional formatting characters and excessive whitespace."""
    text = re.sub(r'[\u200e\u200f\u202a-\u202e\u200b\u200c\u200d\xa0]', ' ', text)
    return re.sub(r'[ \t]+', ' ', text).strip()

def extract_docx_paragraphs(path: str):
    if not os.path.exists(path):
        return []
    with zipfile.ZipFile(path) as z:
        xml_content = z.read('word/document.xml')
    tree = ET.fromstring(xml_content)
    paras = []
    for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        texts = [t.text for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text]
        if texts:
            line = clean_bidi(' '.join(texts))
            if line:
                paras.append(line)
    return paras

print("Parsing dictionary docx...")
dict_paras = extract_docx_paragraphs(os.path.join(WORD_DIR, "DictionaryWithPict-Exclusive Care (Reasonable).docx"))

lexicon_by_cat = {
    'Pronouns & Clitics': [],
    'Nouns': [],
    'Verbs': [],
    'Verbal Nouns': [],
    'Adjectives': [],
    'Adverbs': [],
    'Particles & Conjunctions': [],
}

seen_words = set()

for line in dict_paras:
    if '[' in line and ']' in line:
        m = re.match(r'^([^\[]+)\[([^\]]+)\]\s*(.*)$', line)
        if m:
            hw = clean_bidi(m.group(1))
            ipa = clean_bidi(m.group(2))
            rest = clean_bidi(m.group(3))
            
            # Extract POS
            m_pos = re.match(r'^([A-Za-z/,\+\.\(\)]+)\s+(.*)$', rest)
            if m_pos:
                pos = m_pos.group(1).strip().rstrip(',')
                meaning = m_pos.group(2).strip()
            else:
                pos = 'Other'
                meaning = rest
            
            # Clean up meaning and examples
            example_match = re.search(r'(\[.*?\]|[\u0600-\u06FF\s،۔!؟]+(?=Yes|No|He|She|It|The|This|Come|Go|My|Your|Our|Their|\b[A-Z]))', meaning)
            
            # Map pos to category
            pos_norm = pos.upper()
            cat = 'Particles & Conjunctions'
            if any(p in pos_norm for p in ['PRN', 'PRS', 'CLITIC']):
                cat = 'Pronouns & Clitics'
            elif any(p in pos_norm for p in ['VN', 'VERBAL NOUN']):
                cat = 'Verbal Nouns'
            elif any(p in pos_norm for p in ['VI', 'VT', 'VERB', 'V']):
                cat = 'Verbs'
            elif 'NOUN' in pos_norm or pos_norm == 'N':
                cat = 'Nouns'
            elif 'ADJ' in pos_norm:
                cat = 'Adjectives'
            elif 'ADV' in pos_norm:
                cat = 'Adverbs'
            
            key = (hw, cat)
            if key not in seen_words and len(hw) > 0:
                seen_words.add(key)
                lexicon_by_cat[cat].append((hw, ipa, pos, meaning))

print(f"Total extracted lexical entries: {len(seen_words)}")
for k, v in lexicon_by_cat.items():
    print(f" - {k}: {len(v)}")

# Extract proverbs sample
print("Parsing proverbs docx...")
proverb_paras = extract_docx_paragraphs(os.path.join(WORD_DIR, "Ormuri Proverbs Final PA3.docx"))
proverb_samples = []
for p in proverb_paras:
    if any(k in p for k in ['مطلب', 'متل', 'مثال:']) and len(p) > 40:
        clean_p = clean_bidi(p)
        if len(proverb_samples) < 35 and clean_p not in proverb_samples:
            proverb_samples.append(clean_p)

# Extract folk stories sample
print("Parsing folk stories docx...")
story_paras = extract_docx_paragraphs(os.path.join(WORD_DIR, "Ormuri Folk Stories.docx"))
story_samples = []
for s in story_paras:
    if len(s) > 40:
        clean_s = clean_bidi(s)
        if len(story_samples) < 30 and clean_s not in story_samples:
            story_samples.append(clean_s)

# Compose comprehensive markdown knowledge base
kb_content = f"""# Ormuri (Bargista / اُرموړی) Linguistic Knowledge Base & Generative Grammar
**Language Family**: Indo-European &rarr; Indo-Iranian &rarr; Iranian &rarr; Western Iranian &rarr; Northwestern Iranian (Ormuri–Parachi Subgroup)  
**Historical Varieties**: Kaniguram (South Waziristan, Pakistan - Primary Living Dialect) & Baraki Barak (Logar, Afghanistan)  
**Autonym**: Bargista (بارګِسته), Ormuri (اُرموړی), Warmaṛo (وَرمَړو)  
**Corpus Authority**: Primary manuscripts, dictionaries, and field studies compiled by the Committee for the Preservation of Ormuri Language, Pashto Academy Peshawar, Rozi Khan Burki, Dr. Nasrullah Jan Wazir, Dr. Muhammad Kamal Khan, Farhana Burki, and Farahnaz Burki.

---

## 1. Phonology & Orthography

### 1.1 Distinctive Consonantal Inventory
Ormuri maintains an archaic Iranian phonological substrate with extensive areal contact features (Pashto and Indic/Dardic phonemes), including rare retroflex sibilants and affricates.

| Arabic Script | IPA | Description | Distinctive Contrast / Minimal Pairs |
| :--- | :--- | :--- | :--- |
| **ݫ** | /ʐ/ | Voiced retroflex sibilant | `ݫوند` [ʐwund] (life), `ݫيېړ` [ʐyæṛ] (yellow) vs `ز` /z/ |
| **ݭ** | /ʂ/ | Voiceless retroflex sibilant | `ݭوی` [ʂoy] (cloth), `ݭواخي` [ʂwaxi] (proper name), `ݭپيېو` [ʂpyæv] (white) |
| **ڒ** | /ɽ/ or /ř/ | Retroflex flap / rhotic | `ڒیوک` [řyok] (gave), `ڒَۀ` [řʌ] (give!), `سُوڒ` [suuř] (red) |
| **څ** | /t͡s/ | Voiceless alveolar affricate | `څېک` [t͡sek] (went), `څوم` [t͡som] (eye), `څار` [t͡sar] (four) |
| **ځ** | /d͡z/ | Voiced alveolar affricate | `ځان` [d͡zan] (self), `ځرکۀ` [d͡zəkəʰ] (woman), `ځنګل` [d͡zəŋgʌl] (forest) |
| **ګ** | /ɡ/ | Voiced velar plosive (Pashto ring) | `ګپ` [ɡʌp] (stone/word), `ګری` [ɡri] (mountain) |
| **ښ** | /x̌/ or /ʂ/ | Voiceless retroflex/palatal fricative | `ښکاری` (evident/hunting), used in contact words |
| **ږ** | /ǵ/ or /ʐ/ | Voiced retroflex/velar fricative | Used in loanwords and regional variants |
| **نړ** / **نڑ** | /ɳ/ | Retroflex nasal | `دُنړ` [duɳ] (fog) |

### 1.2 Vowel System & Diacritics
- **Short Vowels**: /a/ (َ), /i/ (ِ), /u/ (ُ), /ə/ (unmarked or short schwa), /ʌ/ (هۀ).
- **Long Vowels**: /aː/ (ا / آ), /iː/ (ي), /uː/ (او / و), /eː/ (ې), /oː/ (و).
- **Special Diphthongs & Endings**:
  - `ې` (/eː/): Masculine plural and verbal stem markers.
  - `ۍ` (/əi/): Feminine abstract and agentive suffixes.
  - `ئ` (/əj/): Special adjectival/adnominal ligature (e.g. `خیکَنیٔ`, `سړئ`).
  - `یٛ` (/ʌj/): Dipthongal glide with inverted hamza (e.g. `پویٛ`).

---

## 2. Split Ergativity: Generative Sentence Algebra

Ormuri exhibits classical **split ergativity conditioned by TAM (Tense-Aspect-Mood)**. The grammatical alignment completely reverses between the Present/Future/Imperfective and the Past/Perfective transitive domains.

```
+-----------------------------------------------------------------------------------+
|                                TAM SPLIT ALGEBRA                                  |
+---------------------------------------------------------+-------------------------+
| DOMAIN                                                  | ALIGNMENT               |
+---------------------------------------------------------+-------------------------+
| Present / Future / Subjunctive / Imperfective           | Nominative-Accusative   |
| Past / Perfective / Pluperfect [TRANSITIVE]             | Ergative-Absolutive     |
| Past / Perfective / Pluperfect [INTRANSITIVE]           | Nominative-Absolutive   |
+---------------------------------------------------------+-------------------------+
```

### 2.1 Nominative Domain: Present & Future Clauses
In the present, future, and habitual aspect:
1. The **Subject (Agent/Experiencer)** is in the **Direct Case** (`از` I, `تُو` you, `او` he/she, `ماخ` we, `تیوس` you pl, `ائ` they).
2. The **Verb agrees with the Subject** in Person and Number via finite verbal suffixes (`-m`, `-yen`, `-(Ø)`, `-ay`, `-y`, `-in`).
3. The **Aspectual Particle** is:
   - `بُو` (bu): Present continuous, habitual, or imperfective.
   - `سُو` (su): Future, irrealis, modal potential.
4. Word Order is **SOV** (Subject-Object-Verb).

$$\\text{{Present Clause: }} \\mathbf{{NP_{{Subj[DIR]}} + (NP_{{Obj[DIR/DAT]}}) + VerbStem_{{Pres}} - Agr_{{Subj}} + بُو}}$$
$$\\text{{Future Clause: }} \\mathbf{{NP_{{Subj[DIR]}} + (NP_{{Obj[DIR/DAT]}}) + VerbStem_{{Pres}} - Agr_{{Subj}} + سُو}}$$

#### Minimal Examples (Present/Future):
- `از بُو غُرزم` (*az bu ɣurzam*) &rarr; "I swing / I am swinging" (1sg agreement `-m`).
- `ماخ بُو غُرزيېن` (*max bu ɣurzyen*) &rarr; "We swing / we are swinging" (1pl agreement `-yen`).
- `او بُو څوا` (*o bu t͡swa*) &rarr; "He goes / he is going" (3sg agreement).
- `تُو سُو غُرز` (*tu su ɣurz*) &rarr; "You will swing" (2sg agreement).
- `سمیر بُو څېک` (*Samir bu t͡sek*) &rarr; "Samir was going" (Past imperfective).
- `سمیر سُو څېک` (*Samir su t͡sek*) &rarr; "Samir will be going" (Future continuous).

---

### 2.2 Ergative Domain: Past Transitive Clauses
In past transitive constructions, the grammatical relations invert:
1. **The Agent (Logical Subject)** CANNOT govern verb agreement. Instead, the Agent is marked by an **Agentive Pronominal Enclitic** (`-m`, `-t`, `-wə/-l`, `-n`) or the agentive topicalizer `ال` (*al*).
2. **The Patient (Grammatical Object)** is in the **Absolutive (unmarked) Case**.
3. **The Verb MUST agree with the OBJECT** in **Gender and Number**:
   - Object Masculine Singular &rarr; Verb takes **Masculine Past Stem** (e.g., `څليېک`, `ڒُوک`, `دوک`, `ووک`).
   - Object Feminine Singular &rarr; Verb takes **Feminine Suffix/Ablaut** `-k` / `-ək` / `-ə` (e.g., `څلک`, `داک`, `بُک`).
   - Object Plural &rarr; Verb takes **Plural Suffix** `-in` / `-kin` / `بُکِن` (e.g., `ڒُوک بُکِن`, `داکِن`).

$$\\text{{Past Transitive: }} \\mathbf{{NP_{{Agent}} - Clitic_{{Agent}} + NP_{{Object[ABS]}} + Verb_{{Past[Agr: Obj(Gender, Number)]}}}}$$

#### The Classic Canonical Minimal Pair (from Primer p. 36):
- `عاصمہ ال عاصم څليېک`  
  *Asima al Asim tsalyek*  
  Asima (Fem Agent) + *al* (Agent marker) + Asim (Masc Object) + *tsalyek* (Verb: **Masc.Sg** took).  
  *Gloss*: "Asima took Asim away." (Verb agrees with masculine *Asim*, NOT feminine *Asima*!)
- If Asim took Asima:
  `عاصم ال عاصمہ څلک`  
  *Asim al Asima tsələk*  
  Asim (Masc Agent) + *al* + Asima (Fem Object) + *tsələk* (Verb: **Fem.Sg** took).

#### Clitic-Hosted Past Transitive Examples:
- `آ-م ڒُوک` (*ā-m řūk*) &rarr; "This (masc) by-me was given" = "I gave this (e.g. an orange)."
- `آ-م داک` (*ā-m dāk*) &rarr; "This (fem) by-me was done" = "I did this (e.g. work)."
- `آ-ت دوک` (*ā-t dōk*) &rarr; "This (masc) by-you was done" = "You did this."
- `آ-وه ڒُوک` (*ā-wə řūk*) &rarr; "This (masc) by-him/her was given" = "He/she gave this."
- `روپيې م شمارکِن` (*rupye-m šmārkin*) &rarr; "The rupees (pl) by-me were counted" = "I counted the money."

---

### 2.3 Intransitive Past Clauses
Intransitive past verbs retain nominative agreement: the verb agrees with the subject in gender, number, and person:
- `از غُرزيېکم` (*az ɣurzyek-am*) &rarr; "I swung" (Masc. 1sg).
- `از غُرزکم` (*az ɣurzək-am*) &rarr; "I swung" (Fem. 1sg).
- `ماخ غُرزک یېن` (*max ɣurzək-yen*) &rarr; "We swung" (1pl).
- `او سړئ زوک` (*o səṛəy zok*) &rarr; "That man came" (3sg Masc).
- `او ځرکۀ زوک` (*o dzərkə zok*) &rarr; "That woman came" (3sg Fem).

---

## 3. Clitic Grammar & Wackernagel Placement

Ormuri features a sophisticated pronominal enclitic system operating under strict **second-position (2P / Wackernagel)** syntactic constraints.

### 3.1 Pronominal Clitic Matrix
| Person / Number | Enclitic | Past Agentive Role ("by...") | Possessive Role ("my/your...") | Object/Dative Role |
| :--- | :--- | :--- | :--- | :--- |
| **1st Sg** | `-m` / `-am` | `داک-م` (done by me) | `نام-م` (my name) | `آر` (ā-r / to me) |
| **2nd Sg** | `-t` / `-at` | `داک-ت` (done by you) | `نام-ت` (your name) | `آت` (ā-t / to you) |
| **3rd Sg** | `-wə` / `-wē` / `-l` | `دوک-وه` (done by him/her) | `نام-وې` (his/her name) | `آل` (ā-l / to him/her) |
| **1st Pl** | `-nyē` / `-n` | `داک-ن` (done by us) | `نام-نيې` (our name) | `ماخ کی` |
| **2nd Pl** | `-dəl` / `-n` | `داک-ن` (done by you pl) | `نام-نيې` (your pl name) | `دل` (dəl) |
| **3rd Pl** | `-n` / `-nyē` | `داک-ن` (done by them) | `نام-نيې` (their name) | `آل` / `کُورئ کی` |

### 3.2 Syntactic Focus & Referential Clitics
- **`يې` (yē)**: Universal referential/copular clitic. Marks the topic or focal subject of a nominal or verbal sentence.
  - `سمیر يې سِر سړئ هۀ` (*Samir yē sir səṛəy hʌ*) &rarr; "Samir is a good man."
  - `کانیګرام يې ته دنیا هۀ جنت ا شور` (*Kanigram yē tə dunya hʌ jannat a šor*) &rarr; "Kaniguram is indeed the paradise town of the world."
- **`ال` (al)**: Specialized agentive/topicalizer clitic in transitive past clauses.
  - `عاصمہ ال عاصم څليېک` (*Asima al Asim tsalyek*).
  - `کُولک ال ݭوی وُستېک` (*Kulak al ʂoy wustek*) &rarr; "The boy peeled the cloth."
- **`دې` (dē)**: Additive/modal discourse clitic ("also", "indeed", "then").
- **`ره` (rə) / `له` (lə)**: Directional/dative clitics ("hither / thither / to me / to him").
  - `آ ره مُنکی ڒُوک` (*ā rə munki řūk*) &rarr; "He gave this to me."

### 3.3 Clitic Placement Hierarchy
Clitics cannot stand clause-initially. They must attach to the right edge of the first prosodic phrase:
1. **Demonstratives**: `آ-م`, `او-وه`, `آ-ت`, `آ-ل`, `آ-ن-دل`.
2. **Topicalized Subject NPs**: `عاصمہ ال ...`, `سمیر يې ...`.
3. **Negation Particle (`نک`)**: `نک-م دُشی` ("I do not see"), `نک-وه دوک` ("He did not do").
4. **Prepositional / Adverbial Heads**: `په خؤی-م دوک` ("I did it myself").

---

## 4. Verb Paradigms & Aspect Derivations

### 4.1 Infinitive Classes
Ormuri verbs fall into two primary structural classes:
- **Class 1 (Consonantal / Monosyllabic `-oak` / `-ək` / `-ک`)**:
  - `وک` (*wōk*): to find
  - `ڒیوک` (*řyōk*): to give
  - `څېک` (*tsēk*): to go
  - `زوک` (*zōk*): to come
  - `نستک` (*nəstək*): to sit
  - `رستک` (*řustək*): to weep
  - `بُک` / `بیوک` (*byōk*): to be/become
- **Class 2 (Vocalic `-aek` / `-yæk` / `-ېک` / `-يېک`)**:
  - `بېک` (*bæk*): to distribute
  - `غُرزېک` (*ɣurzæk*): to cause to swing (Transitive)
  - `غُرزيېک` (*ɣurzyæk*): to swing (Intransitive)
  - `وزنېک` (*waznæk*): to kill
  - `لِکيېک` (*likyæk*): to climb / to write

### 4.2 Verbal Nouns (Masdar)
Formed by two productive morphological processes:
1. **The `-څن` (-tsən) suffix**:
   - `کېک` &rarr; `کېڅن` (*kētsən*): doing, action
   - `ڒیوک` &rarr; `ڒیوڅن` (*řyōtsən*): giving
   - `څېک` &rarr; `څېڅن` (*tsētsən*): going
   - `ځېک` &rarr; `ځېڅن` (*dzētsən*): chewing
   - `ديېک` &rarr; `ديېڅن` (*dyētsən*): seeing
2. **The `-اؤ` / `-ؤ` (-aw) suffix**:
   - `کَرؤ` (*karaw*): sowing / cultivation
   - `ګټؤ` (*gaṭṭaw*): earning
   - `ګړدؤ` (*giṛdaw*): collecting, gathering
   - `بُژنؤ` (*bužnaw*): shivering, trembling

### 4.3 High-Frequency Irregular Stem Suppletions
| Verb Meaning | Infinitive | Present Stem | Past Stem (Masc) | Past Stem (Fem) | Verbal Noun |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **to be** | `بیوک` | `هـ-` (h-) | `بیوک` (byōk) | `بُک` (buk) | `بېڅن` |
| **to do** | `کېک` | `کې-` (kē-) | `دوک` (dōk) | `داک` (dāk) | `کېڅن` |
| **to give** | `ڒیوک` | `ڒ-` (ř-) | `ڒُوک` (řūk) | `ڒُوک` (řūk) | `ڒیوڅن` |
| **to go** | `څېک` | `څ-` (ts-) | `څېک` (tsēk) | `څلک` (tsələk) | `څېڅن` |
| **to come** | `زوک` | `ز-` (z-) | `زوک` (zōk) | `زوک` (zōk) | `زېڅن` |
| **to see** | `ديېک` | `دُش-` (duš-) | `ديېک` (dyēk) | `دیک` (dik) | `ديېڅن` |
| **to say** | `غوېک` | `غؤس-` (ɣwəss-) | `غوېک` (ɣwēk) | `غوېک` (ɣwēk) | `غؤڅن` |
| **to eat** | `خورک` | `خور-` (xwār-) | `خوارک` (xwārək) | `خوارک` | `خورؤ` |

---

## 5. Consolidated Vocabulary & Lexical Repository

### 5.1 Pronouns, Demonstratives & Deictics
- `از` [az] (Prn): I (1st Person Sg Direct)
- `تُو` [tu] (Prn): You (2nd Person Sg Direct)
- `او` [o] / `افۀ` [afəʰ] (Prn): He, She, It, That (3rd Person Sg Direct)
- `ماخ` [māx] (Prn): We (1st Person Pl Direct)
- `تیوس` [tyos] (Prn): You (2nd Person Pl Direct)
- `ائ` [aī] / `افئ` [afay] (Prn): They, Those (3rd Person Pl Direct)
- `دۀ` [dəʰ] (Adv/Prn): Here
- `وۀ` [wəʰ] (Adv/Prn): There
- `کوک` [kōk] (Prn): Who, anyone
- `څۀ` [tsəʰ] (Prn): What
- `ا څېن` [a tsēn] (Prn): Which, which one
- `کان` [kān] (Adv): When
- `ګُده` [guddə] / `کؤڅ` [kawts] (Adv): Where
- `څخل` [tsaxxal] (Adv): How
- `نَک` [nakk] (Part): Not, negative

### 5.2 Adpositions, Circumpositions & Case Markers
- `ا` (a): Direct / default genitive linker (*izafat*): `جنت ا شور` ("town of paradise").
- `ته` (tə): Preposition meaning "in", "to", "at", or governing the oblique case: `ته دنیا` ("in the world"), `ته کانیګرام` ("in Kaniguram").
- `کی` (ki): Dative / Locative postposition ("to", "for", "towards"): `کُومُن کی` ("to me"), `کُوتُو کی` ("to you").
- `زر` (zar): Postposition meaning "on", "upon", "at": `ته بُمبه مُخ زر` ("upon the face of the earth").
- `نره` / `نر` (nara / nar): In, inside: `شور نره` ("in the town"), `منځ نر` ("in the middle").
- `لاسته` (lāsta): Ablative postposition ("from", "by means of"): `ترماخ لاسته` ("from us").
- `پاره` (pāra): Benefactive postposition ("for the sake of"): `ته انسان ا پاره` ("for the sake of man").

### 5.3 Nature, Geography & Topography
- `کانیګرام` [kānīgrām] / `ته ځېستر کانی` (PropN): Kaniguram, the historical cultural capital of Ormuri.
- `شور` [šōr] (N): Town, city, inhabited settlement.
- `ګری` [grī] (N): Mountain, hill.
- `بُمبه` [bumbə] (N): Earth, ground, land, world.
- `تاک` [tāk] (N): Stream, brook, watercourse.
- `داریاب` [daryāb] (N): River.
- `وک` [wəkk] (N): Water.
- `روَّن` [rəwwan] (N): Fire.
- `اسمان` [āsmān] (N): Sky, heaven.
- `مېڒ` [mæř] (N): Sun.
- `مای` [māy] (N): Moon.
- `ستُرّک` [sturrək] (N): Star.
- `ورئېځ` [wrædz] (N): Cloud.
- `دُنړ` [duṇ] (N): Fog, mist.
- `غونڒ` [ɣō~ř] (N): Snow.
- `باران` [bārān] (N): Rain.
- `باد` [bād] (N): Wind, breeze.
- `ګپ` [gʌp] (N): Stone, rock.
- `ݭِګه` [ʂiggə] (N): Sand.
- `ځنګل` [dzəŋgʌl] (N): Forest, jungle.
- `وُنه` [wunnə] (N): Tree.
- `پَټ` [paṭṭ] (N): Leaf, foliage.
- `ګُل` [gull] (N): Flower.
- `غواݭی` [ɣwāʂi] (N): Grass.

### 5.4 Humanity, Society & Kinship
- `سړئ` [səṛəy] (N): Man, human being (Masc).
- `ځرکۀ` [dzəkəʰ] (N): Woman (Fem).
- `بندۀ` [bandəʰ] (N): Human being, mortal person.
- `کُولک` [kūlak] (N): Boy, youth, child.
- `دوکه` [dūka] (N): Girl, daughter.
- `پيې` [pyæ] (N): Father.
- `ماوه` [māwa] (N): Mother.
- `مرزا` [mirzā] (N): Brother.
- `خوار` [xwār] (N): Sister.
- `مالی` [mālī] (N): Husband.
- `ناک` [nāk] (N): Wife.
- `زال` [zāl] (N/Adj): Old man, elder; ancient.
- `تُربُور` [turbūr] (N): Paternal cousin.
- `خلق` [xalq] (N): People, community.
- `قوم` [qawm] (N): Tribe, nation, lineage.
- `برکي` [barkī] (PropN): The Burki / Ormur tribe.
- `مېلمۀ` [mēlmə] (N): Guest.

### 5.5 Abstract & Evaluative Adjectives
- `سِر` [sir] (Adj): Good, virtuous, pleasant, excellent.
- `بَد` [badd] (Adj): Bad, evil, harmful.
- `ستُر` [stur] (Adj): Great, large, eminent, grand.
- `ووړکیٔ` [wōṛkay] / `زری` [zarī] (Adj): Small, little, young.
- `دراغ` [drāɣ] (Adj): Long, lengthy.
- `لنډ` [laɳḍ] (Adj): Short, concise.
- `خواڒه` [xwāřə] (Adj): Sweet, beloved, pleasant.
- `شائستۀ` [šāyistə] (Adj): Beautiful, handsome, graceful.
- `نیوو` [nyōw] (Adj): New, fresh, renewed.
- `زال` [zāl] (Adj): Old, ancient, traditional.
- `توک` [tōk] (Adj): Warm, hot.
- `څاک` [tsāk] (Adj): Cold, chilly.
- `سپک` [spəkk] (Adj): Light (weight), noble, patient.
- `ګران` [grān] (Adj): Heavy, difficult, precious, dear.
- `ݭپيېو` [ʂpyæv] (Adj): White, pure.
- `غراس` [ɣrās] (Adj): Black, dark.
- `سُوڒ` [suuř] (Adj): Red.
- `شین` [šīn] (Adj): Green, blue.
- `ݫيېړ` [ʐyæṛ] (Adj): Yellow, golden.

---

## 6. Narrative Discourse & Authentic Text Passages

### 6.1 Traditional Kaniguram Description (from Folk Stories)
> **بېژه ته دنیا يې هۀ جنت ا شور! سا ته بُمبه مُخ زر هۀ جَوَت ا شور!**  
> *Bēža tə dunyā yē hʌ jannat a šōr! Sā tə bumbə mux zar hʌ jawat a šōr!*  
> "Truly in the world it is the town of Paradise! Upon the face of the earth it is the town of heaven!"

> **ݭواخي يې په قومه خیکَنیٔ برکي بیوک۔ سېنبا نره وې نر بُک، ګیرډه وه دی ته خویٔ تُربُری نری ګه بُکِن۔ زُت هوشیار او تکړۀ سړیٔ يې بیوک۔**  
> *Shwakhi yē pə qawma Xēkanī Barkī byōk. Sēnbā nara-wē nar buk, girḍa-wa dē tə xway turburī narī gah bukin. Zutt hūšyār aw takṛa səṛəy yē byōk.*  
> "Shwakhi was by tribe a Khekani Burki. His fortitude was well-known, and all around his cousins stood alongside him. He was an exceedingly wise and capable man."

### 6.2 Proverbs with Semantic Explications (وَرمَړو متلې)
1. **اخدائ يې کوک ديېک نک ھۀ خَۀ پَۀ خوئ قدرتی بو پزَنيېک سَۀ**  
   *No one has seen God directly, but He is recognized through His divine works.*  
   (Ergative/Imperfective proverb emphasizing inference through creation).
2. **خدایا صبر اردې ته سپک ڒه او خُویٛ اِردې ته سړئ ڒۀ**  
   *O God! Bestow patience upon the dog, and bestow noble temperament upon man.*  
   (Contrastive imperative with enclitic dative *-ir-dē*).
3. **ته وطن ا سکک بُو ته وطن ا سپک شکاروی**  
   *The rabbit of the homeland is hunted by the dog of the homeland.*  
   (A person of the locality alone understands the local topography and customs).

---

## 7. Anti-Hallucination & Generative Scratchpad Protocol

When generating text in Ormuri (Bargista), the generative model MUST adhere to the following strict computational guardrails:

```
+-----------------------------------------------------------------------------------+
|                        STRICT LINGUISTIC CAGE PROTOCOL                            |
+-----------------------------------------------------------------------------------+
| 1. ZERO PASHTO/PERSIAN FALLBACK:                                                  |
|    Never substitute missing words with Pashto (e.g. 'da', 'kawel', 'staso')       |
|    or Urdu/Persian cognates. Use verified Ormuri roots only.                      |
|                                                                                   |
| 2. MORPHOLOGICAL SCRATCHPAD REQUIREMENT:                                          |
|    Before outputting Ormuri prose, verify every sentence in a structured thought: |
|    - Tense / Aspect: [Present (bu) | Future (su) | Past Transitive | Past Intrans]|
|    - Case Marking: [Nominative Subject | Ergative Agent + Clitic Host]           |
|    - Agreement Check: [Verb agrees with Subject (Pres) OR Object (Past Trans)]    |
|    - Enclitic Trace: [Host - Clitic (-m, -t, -wə, yē, al, rə)]                    |
|    - Vocabulary Audit: [Confirm every root exists in the Ormuri Lexicon]          |
+-----------------------------------------------------------------------------------+
```
"""

# Append sample lexicon tables
kb_content += "\n\n## 8. Verified Core Lexicon Tables\n\n"

for cat, words in lexicon_by_cat.items():
    kb_content += f"### 8.{list(lexicon_by_cat.keys()).index(cat)+1} {cat} ({len(words)} entries)\n\n"
    kb_content += "| Ormuri | IPA | POS | Meaning & Context |\n"
    kb_content += "| :--- | :--- | :--- | :--- |\n"
    # Take first 120 most representative entries per category to provide comprehensive grounding
    for hw, ipa, pos, meaning in words[:120]:
        # Escape pipes in meaning
        clean_meaning = meaning.replace('|', '/').replace('\n', ' ')
        kb_content += f"| **{hw}** | [{ipa}] | `{pos}` | {clean_meaning} |\n"
    kb_content += "\n"

output_path = os.path.join(BASE_DIR, "ormuri_knowledge_base.md")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(kb_content)

print(f"\n[OK] Successfully wrote {output_path}")
print(f"Total characters: {len(kb_content)}")
print(f"Total words: {len(kb_content.split())}")
