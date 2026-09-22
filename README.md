# Ormuri AI (Bargista / اُرموړی)

An open-source digital preservation and AI generative linguistics engine for **Ormuri (Bargista)**, a critically endangered Western Iranian language historically spoken in Kaniguram (South Waziristan, Pakistan) and Baraki Barak (Logar, Afghanistan).

![License](https://img.shields.io/badge/License-MIT-emerald.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![Google Gemini](https://img.shields.io/badge/Model-Gemini%203.8%20Flash-cyan.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

---

## 🌟 Key Features

1. **53K-Token Generative Knowledge Base (`ormuri_knowledge_base.md`)**:
   - Comprehensive codification of **TAM Split Ergativity** (Nominative-Accusative for Present/Future; Ergative-Absolutive for Past Transitive).
   - **Wackernagel (2P) Clitic Syntax** and placement rules (`-m`, `-t`, `-wə/-l`, `-n`, `يې`, `ال`, `دې`).
   - Full verbal paradigms (Class 1 `-oak`/`-ək` vs Class 2 `-aek`/`-yæk`; verbal nouns in `-tsən` vs `-aw`).
   - Exhaustive consolidated lexicon of **6,900+ words** with IPA phonetic transcriptions, grammatical categories, and English/Urdu glosses.

2. **In-Context Learning & Context Caching Engine (`generate_ormuri.py`)**:
   - Powered by the official **Google GenAI SDK** (`google-genai`) and `gemini-3.8-flash`.
   - Explicit Context Caching with 24-hour TTL (`ttl="86400s"`).
   - **Anti-Hallucination Cage**: Zero Pashto/Persian fallback, ensuring 100% authentic Ormuri roots.
   - **Mandatory Morphological Scratchpad**: Deconstructs every clause, verifying TAM alignment, clitic hosting, and object-verb agreement before surface generation.

3. **Interactive Testing Playground & Web UI (`server.py` & `frontend/`)**:
   - Multithreaded local server with fast JSON API endpoints.
   - High-aesthetic dark mode interface with glassmorphism and Noto Nastaliq Urdu / Amiri typography.
   - 1-click quick scenarios (Kaniguram folklore, knife-making history, proverbs with moral lessons, daily greetings).
   - **Live Lexicon Explorer**: Real-time searchable dictionary of 6,900+ words with part-of-speech filtering.
   - **Grammar Cheat Sheet**: Interactive formula modal for split ergativity and clitic matrices.

---

## 📂 Repository Structure

```
OrmuriAI/
├── frontend/
│   ├── index.html                  # Responsive modern web testing UI
│   ├── style.css                   # High-aesthetic dark design system
│   └── app.js                      # Client application logic & lexicon explorer
├── Ormuri Data/
│   ├── WORD/                       # Primary manuscripts (Dictionary, Proverbs, Stories, Luke)
│   └── PDF/                        # Verified grammar and poetry publications
├── ormuri_knowledge_base.md        # 53K-token authoritative generative grammar & lexicon
├── generate_ormuri.py              # GenAI SDK engine with caching & CLI
├── build_knowledge_base.py         # Automated extraction pipeline from raw corpus
├── server.py                       # Local API backend and static web server (:8080)
├── lexicon.json                    # 6,930 structured lexical entries (1.3 MB)
├── kaniguram_verification.md       # Verified 3-paragraph descriptive passage
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
