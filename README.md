# Ormuri AI (Bargista / اُرموړی)

An open-source digital preservation and AI generative linguistics engine for **Ormuri (Bargista)**, a critically endangered Western Iranian language historically spoken in Kaniguram (South Waziristan, Pakistan) and Baraki Barak (Logar, Afghanistan).

![License](https://img.shields.io/badge/License-MIT-emerald.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![Google Gemini](https://img.shields.io/badge/Model-Gemini%203.8%20Flash-cyan.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

---

## 🌟 Key Features

1. **100% Unabridged Generative Knowledge Base (`ormuri_knowledge_base.md`)**:
   - Synthesizes **100% of all 11 primary works** unabridged without omitting a single page or verse: **2,001,849 characters, 424,448 words, and 866,060 Gemini tokens**.
   - **Complete Novel *Prechaak* (پرېچاک)**: All 311 pages in full by Rozi Khan Burki (416,828 characters).
   - **Complete Gospel of Luke (لُوقا 1- 24)**: All 24 chapters in full (869 paragraphs, 132,807 characters).
   - **Complete *Warmaṛo Muhāwari***: All 1,491 paragraphs and 1,199 idioms by Farah Naz Burki (104,969 characters).
   - **Complete *Warmaṛo Matali***: All 1,029 paragraphs and 1,012 proverbs with cultural commentaries by Farhana Burki (102,788 characters).
   - **Complete Ormuri Folk Stories**: All 623 paragraphs of traditional oral tales (*Shwaxay Khekany*, *Zargatay*, etc.).
   - **Complete Ormuri Poetry Anthology**: All 52 pages of classical and contemporary verse (67,827 characters).
   - **Complete Universal Declaration of Human Rights**: All 155 paragraphs translated into Ormuri.
   - **Complete 10 Ormuri Infinitive Verbs**: All 47 pages containing all Category-A irregulars and all 466+ Category-B verbs.
   - **Complete Ormuri Primer 2**: All 109 pages of pedagogical grammar, vigesimal numbers, and reading drills.
   - **Complete Linguistic Abbreviations**: Dialectology distinctions (Kanigrami vs Logari).
   - **Complete Illustrated Dictionary**: All 7,025 entries consolidated in [`lexicon.json`](file:///c:/Users/IMRAN/Downloads/Ormuri%20AI/Ormuri%20Data/lexicon.json).

2. **In-Context Learning & Context Caching Engine (`generate_ormuri.py`)**:
   - Powered by the official **Google GenAI SDK** (`google-genai`) and `gemini-3.8-flash`.
   - Explicit persistent server-side Context Caching with 24-hour TTL (`ttl="86400s"`).
   - **Anti-Hallucination Guardrails**: Zero Pashto/Persian fallback.
   - **Mandatory Morphological Scratchpad**: Deconstructs every clause, verifying TAM alignment, clitic hosting, and object-verb agreement.

3. **Interactive Testing Playground & Web UI (`server.py` & `frontend/`)**:
   - Multithreaded local server with fast JSON API endpoints (`/api/generate`, `/api/lexicon`, `/api/status`).
   - High-aesthetic dark mode interface with glassmorphism and Noto Nastaliq Urdu / Amiri typography.
   - Quick scenarios: Universal Declaration of Human Rights, Kaniguram knife craftsmanship, Proverbs, and Greetings.
   - **Live Lexicon Explorer**: Real-time searchable dictionary of 6,650+ words with POS filtering.
   - **Grammar Formula Modal**: Visual reference for split ergativity and clitic syntax.

---

## 📂 Repository Structure

```
OrmuriAI/
├── frontend/
│   ├── index.html                  # Responsive modern web testing UI
│   ├── style.css                   # High-aesthetic dark design system
│   └── app.js                      # Client application logic & lexicon explorer
├── Ormuri Data/
│   ├── WORD/                       # Primary manuscripts (Dictionary, Proverbs, Stories, Luke, UDHR, Idioms)
│   └── PDF/                        # Verified verb books, primers, poetry, and novel Prechaak
├── ormuri_knowledge_base.md        # Complete 13-module master linguistic knowledge base (215K chars)
├── generate_ormuri.py              # GenAI SDK engine with caching & CLI
├── extract_full_corpus.py          # Master extraction pipeline covering 100% of all 11 corpus files
├── build_knowledge_base.py         # Secondary extraction utility
├── server.py                       # Local API backend and static web server (:8080)
├── lexicon.json                    # 6,652 structured lexical entries (1.3 MB)
├── kaniguram_verification.md       # Verified 3-paragraph descriptive passage
├── .env.example                    # Environment template for Gemini API key
└── README.md                       # Documentation and setup guide
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11 or higher
- A Google Gemini API Key

### 2. Installation
Clone the repository and install required packages:
```bash
git clone https://github.com/AlisherKhanBurki/OrmuriAI.git
cd OrmuriAI
pip install google-genai pypdf
```

### 3. Configure API Key
Set your Gemini API key:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your_api_key_here"

# Linux / macOS
export GEMINI_API_KEY="your_api_key_here"
```

### 4. Launch the Playground UI
Start the multithreaded server:
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
python generate_ormuri.py --prompt "Write an authentic Ormuri proverb about mountains and streams"

# Run default Kaniguram verification
python generate_ormuri.py
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
