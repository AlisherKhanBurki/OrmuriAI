# Ormuri AI (Bargista / اُرموړی)

An open-source digital preservation and AI generative linguistics engine for **Ormuri (Bargista)**, a critically endangered Western Iranian language historically spoken in Kaniguram (South Waziristan, Pakistan) and Baraki Barak (Logar, Afghanistan).

![License](https://img.shields.io/badge/License-MIT-emerald.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![Google Gemini](https://img.shields.io/badge/Model-Gemini%203.5%20Flash-cyan.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)
![Languages](https://img.shields.io/badge/Languages-English%20%7C%20Urdu%20%7C%20Pashto%20%7C%20Ormuri-orange.svg)

---

## 🌟 Key Features

### 1. 100% Unabridged Generative Knowledge Base (`ormuri_core_kb.md`)
Synthesizes **100% of all primary linguistic works** unabridged without omitting a single page or verse: **866,000+ tokens and 450,000+ characters**:
- **Complete Novel *Prechaak* (پرېچاک)**: All 311 pages in full by Rozi Khan Burki.
- **Complete Gospel of Luke (لُوقا 1–24)**: All 24 chapters in full (869 verses/paragraphs).
- **Complete *Warmaṛo Muhāwari* (Idioms & Phrases)**: All authentic idioms cleanly demarcated starting from Idiom #1 with literal glosses and figurative meanings by Farah Naz Burki.
- **Complete *Warmaṛo Matali* (Proverbs Collection)**: All authentic proverbs cleanly demarcated starting from Proverb #1 with cultural commentaries by Farhana Burki.
- **Complete Ormuri Folk Stories (*Matalay aw Khesay*)**: Traditional oral tales (*Shwaxay Khekany*, *Zargatay*, etc.).
- **Complete Ormuri Poetry Anthology (*Warmaṛo Shāirī*)**: Classical and contemporary verse.
- **Universal Declaration of Human Rights (UDHR)**: Translated in full into authentic Ormuri.
- **Infinitive Verbs System**: Comprehensive paradigms covering Category-A irregulars and all 466+ Category-B verbs.
- **Ormuri Primer 2 (*Dweyam Kitab*)**: Pedagogical grammar, vigesimal numbers, and reading drills.
- **Linguistic Abbreviations & Symbols**: Standardized orthographic and dialectological conventions (Kanigrami vs Logari).
- **Consolidated Dictionary**: 6,657 structured lexical entries available in [`lexicon.json`](file:///c:/Users/IMRAN/Downloads/Ormuri%20AI/Ormuri%20Data/lexicon.json).

---

### 2. In-Browser 10-Work Primary Corpus Reader (`frontend/corpus_data.js`)
- **Direct Interactive Access**: Read all 10 authentic works directly inside the web interface under the **Primary Corpus Archive** tab.
- **Instant Sub-Tab Navigation**: Jump smoothly between Novel, Luke, Idioms, Proverbs, Stories, Poetry, UDHR, Verbs, Primer, and Abbreviations.
- **Full-Text Real-Time Search**: Search any Ormuri word, romanized term, Urdu gloss, or English concept across the entire archive instantly.
- **Sequential Demarcation**: Idioms and Proverbs follow clean, intuitive consecutive numbering (#1, #2, #3...) for seamless academic reference.

---

### 3. Simplified & Advanced Generative Controls
- **Lay-User Friendly**: Replaced intimidating raw statistical labels (`Creativity / Temp: 0.2`) with an elegant, unobtrusive button:
  - English: `⚙️ Advanced [0.2]`
  - Urdu: `⚙️ جدید ترتیبات [0.2]`
  - Pashto: `⚙️ پرمختللي ترتیبات [0.2]`
- **Dedicated Advanced Settings Popover**:
  - **Quick Select Presets**: One-click chips for `0.0 (Strict)`, `0.2 (Optimal)`, `0.5 (Balanced)`, and `0.8 (Creative)`.
  - **Direct Numeric Input Box**: Enter any exact float value (`0.0`–`1.0`) directly.
  - **Synchronized Fine-Tuning Slider**: Bi-directionally synchronized with number input and preset chips.

---

### 4. Resilient Multi-Key Round-Robin Rotation Pool
- `generate_ormuri.py` and `server.py` feature an automated key pool manager (`KeyPool`).
- Automatically balances load across multiple Google Gemini API keys via round-robin dispatch, ensuring uninterrupted generation even during quota and rate limits.
- Supports both single key (`GEMINI_API_KEY`) and multi-key lists (`GEMINI_API_KEYS` / comma-separated strings).

---

### 5. Strict Morphological Scratchpad & Anti-Hallucination Guardrails
- **Morphological Scratchpad Protocol**: Before surface generation, the engine deconstructs every clause in `<morphological_scratchpad>` tags, enforcing:
  - Split-ergativity in past transitive constructions.
  - Wackernagel second-position pronominal clitics (*-am*, *-at*, *-a/yē*, *-an*, *-at-an*, *-a-wē*).
  - Accurate vocabulary disambiguation (e.g., 'Language' = *زبان* [zbān] / *زبنَّی* [zbənni]; *دیو* [dyō] strictly means the number 'two').
- **Dual Script Output**: Surfaces authentic Ormuri Arabic-based script (*Bargista*) alongside standardized International Phonetic Alphabet (IPA) Romanization and dual Urdu/English translations.

---

### 6. Trilingual Interface & On-Screen Virtual Keyboard
- **Full Localization**: Seamless switching between English, Urdu, and Pashto with complete Right-to-Left (RTL) typography.
- **Integrated Virtual Keyboard**: On-screen keyboard with tabs for Ormuri special characters (ݪ, ݫ, ݭ, ړ, ږ, ښ, etc.), Pashto, and Urdu.
- **Live Lexicon Explorer**: Search 6,657 words with Part-of-Speech filtering and one-click insertion into the prompt.

---

## 📂 Repository Structure

```
OrmuriAI/
├── frontend/
│   ├── index.html                  # Responsive modern web testing UI
│   ├── style.css                   # High-aesthetic dark design system with RTL support
│   ├── app.js                      # Client application logic, popover controls, & localization
│   └── corpus_data.js              # In-browser unabridged 10-work primary corpus dataset
├── build_corpus_data.py            # Corpus extraction and JSON/JS dataset generator
├── extract_full_corpus.py          # Master extraction pipeline covering 100% of all corpus files
├── generate_ormuri.py              # GenAI SDK engine with key rotation pool & CLI
├── server.py                       # Multithreaded local server with API endpoints (:8080)
├── lexicon.json                    # 6,657 structured lexical entries
├── ormuri_core_kb.md               # Master unabridged linguistic knowledge base
├── kaniguram_verification.md       # Verified descriptive passage & grammatical proofs
├── .env.example                    # Environment template for Gemini API key(s)
└── README.md                       # Documentation and setup guide
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11 or higher
- One or more Google Gemini API Keys

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/AlisherKhanBurki/OrmuriAI.git
cd OrmuriAI
pip install google-genai pypdf
```

### 3. Configure API Key(s)
Set your Gemini API key in your environment or in a `.env` file:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your_api_key_here"

# For multi-key rotation pool:
$env:GEMINI_API_KEYS="key_1,key_2,key_3"

# Linux / macOS
export GEMINI_API_KEY="your_api_key_here"
```

### 4. Launch the Web Playground
Start the local server:
```bash
python server.py
```
Open your browser at:
👉 **`http://localhost:8080`**

---

## 💻 CLI & Interactive Mode

You can also run generation directly from your terminal:

```bash
# Interactive conversation shell
python generate_ormuri.py --interactive

# Custom one-off prompt
python generate_ormuri.py --prompt "Write an authentic Ormuri proverb about hospitality and honor"

# Custom temperature setting
python generate_ormuri.py --prompt "Compose a greeting dialogue" --temperature 0.2
```

---

## 📜 Morphological Scratchpad Protocol

Every generated text is preceded by a linguistic reasoning scratchpad:
```markdown
<morphological_scratchpad>
Sentence 1:
- Intent: Kaniguram is truly the paradise town of this world.
- Alignment: Nominative-Accusative (Nominal Copular Sentence).
- Subject: کانیګرام [Kānīgrām] + Referential/Focus Clitic 'يې' [yē].
- Predicate: ته دنیا هۀ جنت ا شور [tə dunyā hʌ jannat a šōr].
- Roots: کانیګرام (Kaniguram), يې (clitic), ته (prep: in), دنیا (world), هۀ (copula 3sg), جنت (paradise), ا (izafat linker), شور (town).
</morphological_scratchpad>
```

---

## 🤝 Citation & Preservation Credits

Compiled under the aegis of the **Committee for the Preservation of Ormuri Language** (*کمیٹی برائے تحفظ زبانِ ارمڑی*), Pashto Academy Peshawar, and regional linguists:
- Rozi Khan Burki (روزی خان برکی)
- Dr. Nasrullah Jan Wazir (ڈاکٹر نصراللہ جان وزیر)
- Dr. Muhammad Kamal Khan (ڈاکٹر محمد کمال خان)
- Farhana Burki (فرحانہ برکی)
- Farahnaz Burki (فرح ناز برکی)
- Hikmat Yar Burki (حکمت یار برکی)

---

## 📄 License
This project is licensed under the MIT License.
