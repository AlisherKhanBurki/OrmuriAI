/**
 * Ormuri AI Playground — Client Application Logic (v3.2)
 * Full 4-Language Multilingual System: English, Urdu, Pashto, Ormuri (Bargista)
 */

const LANG_META = {
  en: { name: 'English', native: 'English', flag: '🇬🇧', dir: 'ltr' },
  ur: { name: 'اردو', native: 'اردو', flag: '🇵🇰', dir: 'rtl' },
  ps: { name: 'پښتو', native: 'پښتو', flag: '☀️', dir: 'rtl' }
};

const TRANSLATIONS = {
  en: {
    brand_subtitle: 'Endangered Language Generative Engine & Linguistic Playground',
    badge_model: 'Gemini 3.8 Flash (Cached)',
    badge_kb: '📚 866,060 Tokens (2.0M Chars)',
    badge_erg: '⚡ Split Ergativity Active',
    badge_corpus: '📖 11 Primary Works (Unabridged)',
    btn_lexicon: 'Lexicon',
    btn_lexicon_count: '(6,657 Ormuri Words)',
    btn_grammar: 'Grammar & Corpus',
    btn_support: 'Support',
    btn_support_extra: ' Cause',
    prompt_title: 'Prompt Formulation',
    mode_free: 'Free Prompt',
    mode_story: 'Folk Story',
    mode_proverb: 'Proverb',
    mode_dialogue: 'Dialogue',
    mode_ergativity: 'Ergativity Test',
    chips_label: 'Quick Scenarios:',
    prompt_placeholder: "Type your prompt in English, Urdu, or Ormuri...\nE.g., 'Describe the snowfall on Baar Pit mountain and the warmth of traditional hearths in Kaniguram.'",
    temp_label: 'Creativity / Temp:',
    btn_clear: 'Clear',
    btn_generate: 'Generate Ormuri',
    output_title: 'Linguistic Output & Inspector',
    tab_rendered: 'Polished Output',
    tab_scratchpad: 'Morphological Scratchpad',
    tab_scratchpad_badge: 'Verified',
    tab_raw: 'Raw Markdown',
    placeholder_title: 'Ready to Generate',
    placeholder_text: 'Select a scenario chip on the left or write a custom prompt to test Ormuri generation with anti-hallucination verification.',
    loading_title: 'Generating Authentic Ormuri...',
    loading_text: 'Grounding prompt against 866,060 token unabridged corpus (Prechaak 311pp, 1,491 Idioms, 1,029 Proverbs, UDHR, Poetry, 500+ Verbs) with Split Ergativity verification...',
    elapsed_label: 'Elapsed:',
    card_ormuri_tag: 'اُرموړی رسم الخط (Bargista Script)',
    card_phonetic_tag: 'Phonetic Romanization (IPA Guide)',
    card_trans_tag: 'Translation (اردو / English)',
    btn_copy: 'Copy',
    scratchpad_banner_title: 'Anti-Hallucination Guardrail Active',
    scratchpad_banner_text: 'Every sentence below was linguistically decomposed to verify TAM alignment, Wackernagel clitic hosting, and object-verb agreement before surface generation.',
    footer_mission_title: '🏛️ Preservation Mission',
    footer_mission_text: 'Ormuri is critically endangered. Support cloud & API costs to keep this heritage AI engine active.',
    footer_btn_copy: 'Copy Account',
    drawer_title: 'Ormuri Lexicon Explorer',
    search_placeholder: 'Search by Ormuri, English, Urdu, or IPA...',
    pos_all: 'All',
    pos_n: 'Nouns',
    pos_v: 'Verbs',
    pos_adj: 'Adjectives',
    pos_adv: 'Adverbs',
    pos_prn: 'Pronouns/Clitics',
    btn_load_all: 'Load All Words',
    grammar_title: '📐 Ormuri Generative Grammar Cheat Sheet',
    support_title: 'Support Ormuri (Bargista) AI Preservation',
    alert_no_prompt: 'Please type or select a prompt first.',
    copied_toast: 'Copied to clipboard! ✓',
    ormuri_copied_toast: 'Ormuri text copied! ✓',
    account_copied_toast: 'Account details copied: PK62ASCM0001143230003241 (ALI SHER KHAN BURKI) ✓',
    word_inserted: 'Inserted into prompt!',
    btn_keyboard: '⌨️ Virtual Keyboard'
  },
  ur: {
    brand_subtitle: 'نایاب تاریخی زبان کا جنریٹو انجن اور لسانی تجربہ گاہ',
    badge_model: 'جیمینائی 3.8 فلیش (کیشڈ)',
    badge_kb: '📚 866,060 ٹوکن (2.0M حروف)',
    badge_erg: '⚡ ارګیٹیویٹی گارڈریل فعال',
    badge_corpus: '📖 11 بنیادی کتب و متون',
    btn_lexicon: 'جامع لغت',
    btn_lexicon_count: '(6,657 ارموڑی الفاظ)',
    btn_grammar: 'قواعد و متون',
    btn_support: 'مالی تعاون',
    btn_support_extra: ' کریں',
    prompt_title: 'پرامپٹ اور ہدایات',
    mode_free: 'آزاد پرامپٹ',
    mode_story: 'لوک داستان',
    mode_proverb: 'کہاوت / ضرب المثل',
    mode_dialogue: 'روزمرہ مکالمہ',
    mode_ergativity: 'ارګیٹیویٹی ٹیسٹ',
    chips_label: 'فوری نمونہ جات:',
    prompt_placeholder: "اپنا پرامپٹ اردو، انگریزی یا ارموڑی میں لکھیں...\nمثال: 'بار پیٹ پہاڑ پر برفباری اور کانیگرم کے روایتی گھرانوں کے احوال بیان کریں۔'",
    temp_label: 'تخلیقی صلاحیت / ٹمپریچر:',
    btn_clear: 'صاف کریں',
    btn_generate: 'ارموڑی متن بنائیں',
    output_title: 'لسانی آؤٹ پٹ اور تجزیہ',
    tab_rendered: 'تیار شدہ متن',
    tab_scratchpad: 'صرفی و نحوی تجزیہ',
    tab_scratchpad_badge: 'تصدیق شدہ',
    tab_raw: 'خام مارک ڈاؤن',
    placeholder_title: 'متن بنانے کے لیے تیار',
    placeholder_text: 'بائیں جانب سے کوئی نمونہ منتخب کریں یا اپنا پرامپٹ لکھ کر ارموڑی زبان کی تصدیق شدہ تخلیق دیکھیں۔',
    loading_title: 'مستند ارموڑی متن تیار ہو رہا ہے...',
    loading_text: '866,060 ٹوکنز پر مشتمل ذخیرہ (ناول پریچاک، 1,491 محاورے، 1,029 کہاوتیں، انسانی حقوق، شاعری اور افعال) سے تصدیق جاری ہے...',
    elapsed_label: 'صرف شدہ وقت:',
    card_ormuri_tag: 'اُرموړی رسم الخط (بارګِسته)',
    card_phonetic_tag: 'تلفظ اور رومن رسم الخط (IPA)',
    card_trans_tag: 'ترجمہ (اردو / انگریزی)',
    btn_copy: 'کاپی کریں',
    scratchpad_banner_title: 'تحفظِ صحتِ لسانی (گارڈریل) فعال',
    scratchpad_banner_text: 'ہر جملے کو قواعد، فاعلی کلاٹکس (واکرنیگل) اور مفعولی مطابقت کے اصولوں کے تحت جانچا گیا ہے۔',
    footer_mission_title: '🏛️ تحفظِ ورثہ مشن',
    footer_mission_text: 'ارموڑی ایک معدوم ہوتی نایاب زبان ہے۔ کلاؤڈ اور اے پی آئی اخراجات کے لیے تعاون فرمائیں۔',
    footer_btn_copy: 'اکاؤنٹ کاپی کریں',
    drawer_title: 'ارموڑی جامع لغت (Lexicon)',
    search_placeholder: 'ارموڑی، اردو، انگریزی یا تلفظ سے تلاش کریں...',
    pos_all: 'سبھی',
    pos_n: 'اسم (Nouns)',
    pos_v: 'فعل (Verbs)',
    pos_adj: 'صفت (Adjectives)',
    pos_adv: 'متعلق فعل (Adverbs)',
    pos_prn: 'ضمیر / کلاٹک',
    btn_load_all: 'تمام الفاظ لوڈ کریں',
    grammar_title: '📐 ارموڑی قواعد و نحوی رہنمائی',
    support_title: 'ارموڑی (بارګِسته) اے آئی تحفظ کے لیے تعاون',
    alert_no_prompt: 'براہ کرم پہلے پرامپٹ لکھیں یا منتخب کریں۔',
    copied_toast: 'کاپی ہو گیا! ✓',
    ormuri_copied_toast: 'ارموڑی متن کاپی ہو گیا! ✓',
    account_copied_toast: 'اکاؤنٹ تفصیلات کاپی ہو گئیں: PK62ASCM0001143230003241 (علی شیر خان برکی) ✓',
    word_inserted: 'لفظ پرامپٹ میں شامل کر دیا گیا!',
    btn_keyboard: '⌨️ ورچوئل کیبورڈ'
  },
  ps: {
    brand_subtitle: 'د نایابه ژبې د تولید ماشین او د ژبپوهنې ډګر',
    badge_model: 'جیمیناي 3.8 فلیش (کیش شوی)',
    badge_kb: '📚 866,060 ټوکنه (2.0M توري)',
    badge_erg: '⚡ ارګیټیوټي ګارډرییل فعال',
    badge_corpus: '📖 11 اصلي کتابونه او لیکنې',
    btn_lexicon: 'د لغتونو قاموس',
    btn_lexicon_count: '(6,657 ارموړي کلمې)',
    btn_grammar: 'ګرامر او متون',
    btn_support: 'ملاتړ وکړئ',
    btn_support_extra: ' (مرسته)',
    prompt_title: 'د پوښتنې / پرامپټ جوړول',
    mode_free: 'ازاد پرامپټ',
    mode_story: 'ولسي کیسه',
    mode_proverb: 'متل',
    mode_dialogue: 'ورځنۍ خبرې',
    mode_ergativity: 'د ارګیټیوټي آزموینه',
    chips_label: 'سمدستي بېلګې:',
    prompt_placeholder: "خپله پوښتنه په پښتو، اردو، انګلیسي یا ارموړي ولیکئ...\nد بېلګې په توګه: 'د بار پېټ پر غره د واورې اورېدو او د کانیګرم د ولسي حجرو تودوخه بیان کړئ.'",
    temp_label: 'تخلیقي کچه / ټمپریچر:',
    btn_clear: 'پاک کړئ',
    btn_generate: 'ارموړي متن جوړ کړئ',
    output_title: 'ژبنیزې لاسته راوړنې او څېړنه',
    tab_rendered: 'بشپړ متن',
    tab_scratchpad: 'صرفي او نحوي شننه',
    tab_scratchpad_badge: 'تایید شوی',
    tab_raw: 'خام مارک ډاون',
    placeholder_title: 'د تولید لپاره چمتو دی',
    placeholder_text: 'له کیڼ اړخ څخه یوه بېلګه وټاکئ یا خپله پوښتنه ولیکئ ترڅو د ارموړي ژبې باوري تولید وګورئ.',
    loading_title: 'اصلي او کره ارموړي متن جوړېږي...',
    loading_text: 'د 866,060 ټوکن لرونکي ذخیرې (ناول پریچاک، 1,491 اصطلاحات، 1,029 متلونه، د بشري حقونو منشور او افعال) څخه تصدیق روان دی...',
    elapsed_label: 'تېر شوی وخت:',
    card_ormuri_tag: 'اُرموړی رسم الخط (بارګِسته)',
    card_phonetic_tag: 'تلفظ او رومن لیکدود (IPA)',
    card_trans_tag: 'ژباړه (پښتو / انګلیسي / اردو)',
    btn_copy: 'کاپي کړئ',
    scratchpad_banner_title: 'د ژبني سموالي ساتونکی فعال دی',
    scratchpad_banner_text: 'هر تېر شوی جمله د صرفي اصولو، فاعلي کلاټکسونو او د مفعول او فعل د سمون له مخې څېړل شوې ده.',
    footer_mission_title: '🏛️ د ژبې ژغورنې ماموریت',
    footer_mission_text: 'ارموړي یوه نایابه او تاریخي ژبه ده. د کلاوډ او سرور لګښتونو کې مرسته وکړئ.',
    footer_btn_copy: 'اکاونټ کاپي کړئ',
    drawer_title: 'د ارموړي ژبې قاموس',
    search_placeholder: 'په ارموړي، پښتو، اردو، انګلیسي یا فونټیک وپلټئ...',
    pos_all: 'ټول',
    pos_n: 'نومونه (Nouns)',
    pos_v: 'فعلونه (Verbs)',
    pos_adj: 'صفتونه (Adjectives)',
    pos_adv: 'قیدونه (Adverbs)',
    pos_prn: 'ضمائر / کلاټیک',
    btn_load_all: 'ټول کلمات راولئ',
    grammar_title: '📐 د ارموړي ژبې ګرامر او جدولونه',
    support_title: 'د ارموړي (بارګِسته) ژبې له ساتنې سره مرسته',
    alert_no_prompt: 'مهرباني وکړئ لومړی پوښتنه یا پرامپټ ولیکئ.',
    copied_toast: 'کاپي شوه! ✓',
    ormuri_copied_toast: 'ارموړي متن کاپي شو! ✓',
    account_copied_toast: 'د بانکي حساب شمېره کاپي شوه: PK62ASCM0001143230003241 (علي شیر خان برکي) ✓',
    word_inserted: 'کلمه پرامپټ ته واستول شوه!',
    btn_keyboard: '⌨️ مجازی کیبورډ'
  }
};

const CHIP_PROMPTS = {
  en: {
    prechaak: {
      label: '📖 Novel Prechaak',
      prompt: "Translate and explain in authentic Ormuri using vocabulary from the novel Prechaak: 'In the cold winter of Kaniguram, the tribal elders gathered in the council house to resolve the blood dispute.'"
    },
    folk: {
      label: '🏔️ Folk Stories',
      prompt: "Narrate a traditional Ormuri folk story about the ancient iron-smiths (اوستاکار) of Kaniguram and the heritage of Baar Pit mountain."
    },
    udhr: {
      label: '🕊️ Human Rights (UDHR)',
      prompt: "Translate into formal civic Ormuri (following the Charter of Human Rights): 'All human beings are born free and equal in dignity and rights.'"
    },
    proverb: {
      label: '📜 Proverbs (1,029)',
      prompt: "Present an authentic Ormuri proverb about hospitality (مېلمۀ) and honor (ننګ), with literal word breakdown, cultural meaning, and practical moral lesson."
    },
    idiom: {
      label: '💡 Idioms (1,491)',
      prompt: "Present an authentic Ormuri idiom about courage and steadfastness from the Ormuri Idioms collection, with word gloss and idiomatic meaning."
    },
    dialogue: {
      label: '🗣️ Daily Greetings',
      prompt: "Write a natural conversational dialogue between two Ormuri speakers meeting in the morning, greeting each other, asking about health, family, and sheep grazing."
    },
    ergativity: {
      label: '⚡ Ergativity Test',
      prompt: "Translate and linguistically explain: 'Asima took Asim to the mountain, but the boy gave the bread to his mother' (verify past transitive object agreement vs agentive clitic al)."
    }
  },
  ur: {
    prechaak: {
      label: '📖 ناول پریچاک',
      prompt: "ناول پریچاک کے مستند ذخیرہ الفاظ کے ساتھ ارموڑی میں ترجمہ کریں: 'کانیگرم کے سرد موسم سرما میں قبائلی عمائدین خون کے جھگڑے کو سلجھانے کے لیے بیٹھک میں جمع ہوئے۔'"
    },
    folk: {
      label: '🏔️ لوک کہانیاں',
      prompt: "کانیگرم کے قدیم لوہاروں (اوستاکار) اور بار پیٹ پہاڑ کی روایت پر ایک روایتی ارموڑی لوک کہانی بیان کریں۔"
    },
    udhr: {
      label: '🕊️ انسانی حقوق (UDHR)',
      prompt: "انسانی حقوق کے عالمی منشور کے مطابق ارموڑی میں ترجمہ کریں: 'تمام انسان پیدائشی طور پر آزاد اور وقار و حقوق میں برابر ہیں۔'"
    },
    proverb: {
      label: '📜 ضرب الامثال (1,029)',
      prompt: "مہمان نوازی (مېلمۀ) اور ننگ و ناموس پر ایک مستند ارموڑی کہاوت پیش کریں جس میں لفظ بہ لفظ تجزیہ اور اخلاقی درس شامل ہو۔"
    },
    idiom: {
      label: '💡 محاورات (1,491)',
      prompt: "ارموڑی محاورات کے ذخیرے سے بہادری اور ثابت قدمی پر ایک مستند محاورہ پیش کریں بمع مفہوم و لغوی تشریح۔"
    },
    dialogue: {
      label: '🗣️ روزمرہ مکالمہ',
      prompt: "صبح کے وقت ملنے والے دو ارموڑی بولنے والوں کے درمیان فطری گفتگو لکھیں جس میں خیریت، اہل خانہ اور بھیڑ بکریاں چرانے کا احوال ہو۔"
    },
    ergativity: {
      label: '⚡ ارګیٹیویٹی ٹیسٹ',
      prompt: "ارموڑی میں ترجمہ اور لسانی تصدیق کریں: 'عاصمہ عاصم کو پہاڑ لے گئی، مگر لڑکے نے روٹی اپنی ماں کو دی۔' (ماضی متعدی مفعولی مطابقت اور فاعلی کلاٹک 'ال' کی تصدیق کریں)"
    }
  },
  ps: {
    prechaak: {
      label: '📖 ناول پریچاک',
      prompt: "د پریچاک ناول له مستندې ذخیرې څخه په ګټې اخیستنې په ارموړي ژباړه وکړئ: 'د کانیګرم په یخ ژمي کې قومي مشران په حجره کې د وینې د شخړې د هواري لپاره راټول شول.'"
    },
    folk: {
      label: '🏔️ ولسي کیسې',
      prompt: "د کانیګرم د پخوانیو اوسپنو جوړوونکو (اوستاکار) او د بار پېټ د غره په اړه یوه دودیزه ارموړي ولسي کیسه بیان کړئ."
    },
    udhr: {
      label: '🕊️ بشري حقونه (UDHR)',
      prompt: "د بشري حقونو د نړیوال منشور پر بنسټ رسمي ارموړي ته وژباړئ: 'ټول انسانان ازاد پیدا شوي او په حقوقو او کرامت کې سره مساوي دي.'"
    },
    proverb: {
      label: '📜 متلونه (1,029)',
      prompt: "د مېلمستیا (مېلمۀ) او ننګ په اړه یو مستند ارموړی متل د ټکي په ټکي مانا او اخلاقي درس سره وړاندې کړئ."
    },
    idiom: {
      label: '💡 اصطلاحات (1,491)',
      prompt: "د ارموړي اصطلاحاتو له ټولګې څخه د مېړانې او زړورتیا په هکله یوه مستنده اصطلاح له تشریح سره ولیکئ."
    },
    dialogue: {
      label: '🗣️ ورځنۍ خبرې اترې',
      prompt: "د دوو ارموړي ژبو ترمنځ چې سهار وختي یو بل سره ویني، د روغتیا، کورنۍ او رمو پوښتنه کوي، یوه روانه مکالمه ولیکئ."
    },
    ergativity: {
      label: '⚡ د ارګیټیوټي آزموینه',
      prompt: "په ارموړي کې ژباړه او صرفي تحلیل وکړئ: 'عاصمې عاصم غره ته بوته، خو هلک خپله ډوډۍ مور ته ورکړه.' (په تېر مهال کې د مفعولي مطابقت او فاعلي کلاټک ال تصدیق)"
    }
  }
};

/**
 * On-Screen Virtual Keyboard Layouts
 * Includes authentic 48-letter Ormuri (Rozi Khan Burki orthography), Pashto, and Urdu layouts
 */
const KEYBOARD_LAYOUTS = {
  oru: {
    name: 'بارګِسته (Ormuri)',
    rows: [
      ['۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹', '۰', 'َ', 'ِ', 'ُ', 'ّ', 'ْ', 'ً'],
      ['ض', 'ص', 'ث', 'ق', 'ف', 'غ', 'ع', 'ه', 'خ', 'ح', 'ج', 'چ', 'څ', 'ځ'],
      ['ش', 'ݭ', 'س', 'ی', 'ي', 'ې', 'ۍ', 'ئ', 'یٛ', 'ب', 'پ', 'ل', 'ا', 'آ', 'ت', 'ټ', 'ن', 'ڼ', 'م', 'ک', 'ګ'],
      ['ظ', 'ط', 'ز', 'ݫ', 'ژ', 'ږ', 'ر', 'ڒ', 'ړ', 'ذ', 'د', 'ډ', 'و', 'ں', 'ے', 'ء']
    ],
    specials: ['ڒ', 'ݫ', 'ݭ', 'یٛ', 'څ', 'ځ', 'ټ', 'ډ', 'ړ', 'ګ', 'ڼ', 'ې', 'ۍ', 'ي']
  },
  ps: {
    name: 'پښتو (Pashto)',
    rows: [
      ['۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹', '۰', 'َ', 'ِ', 'ُ', 'ً', 'ّ', 'ْ'],
      ['ض', 'ص', 'ث', 'ق', 'ف', 'غ', 'ع', 'ه', 'خ', 'ح', 'ج', 'چ', 'څ', 'ځ'],
      ['ش', 'ښ', 'س', 'ی', 'ي', 'ې', 'ۍ', 'ئ', 'ب', 'پ', 'ل', 'ا', 'آ', 'ت', 'ټ', 'ن', 'ڼ', 'م', 'ک', 'ګ'],
      ['ظ', 'ط', 'ز', 'ژ', 'ږ', 'ر', 'ړ', 'ذ', 'د', 'ډ', 'و', 'ۀ', 'ء']
    ],
    specials: ['ښ', 'ږ', 'څ', 'ځ', 'ڼ', 'ګ', 'ې', 'ۍ', 'ي', 'ئ', 'ۀ', 'ټ', 'ډ', 'ړ']
  },
  ur: {
    name: 'اردو (Urdu)',
    rows: [
      ['۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹', '۰', 'َ', 'ِ', 'ُ', 'ً', 'ٍ', 'ٌ', 'ّ', 'ْ'],
      ['ض', 'ص', 'ث', 'ق', 'ف', 'غ', 'ع', 'ہ', 'ھ', 'خ', 'ح', 'ج', 'چ'],
      ['ش', 'س', 'ی', 'ب', 'پ', 'ل', 'ا', 'آ', 'ت', 'ٹ', 'ن', 'ں', 'م', 'ک', 'گ'],
      ['ظ', 'ط', 'ز', 'ژ', 'ر', 'ڑ', 'ذ', 'د', 'ڈ', 'و', 'ے', 'ء', 'ئ', 'ؤ', 'ۂ']
    ],
    specials: ['ٹ', 'ڈ', 'ڑ', 'ں', 'ے', 'ھ', 'ہ', 'گ', 'پ', 'چ', 'ژ', 'ۂ']
  }
};

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements - Prompt & Inputs
  const promptInput = document.getElementById('promptInput');
  const tempSlider = document.getElementById('tempSlider');
  const tempValue = document.getElementById('tempValue');
  const btnGenerate = document.getElementById('btnGenerate');
  const btnClear = document.getElementById('btnClear');
  const btnSpinner = document.getElementById('btnSpinner');
  const modeSelector = document.getElementById('modeSelector');
  const quickChips = document.querySelectorAll('.chip');

  // Output Elements & States
  const outputPanel = document.getElementById('outputPanel');
  const outputWrapper = document.querySelector('.output-content-wrapper');
  const outputPlaceholder = document.getElementById('outputPlaceholder');
  const outputLoading = document.getElementById('outputLoading');
  const outputQuotaError = document.getElementById('outputQuotaError');
  const timerText = document.getElementById('timerText');
  const outputTabs = document.getElementById('outputTabs');
  const tabRendered = document.getElementById('tabRendered');
  const tabScratchpad = document.getElementById('tabScratchpad');
  const tabRaw = document.getElementById('tabRaw');

  const ormuriText = document.getElementById('ormuriText');
  const romanText = document.getElementById('romanText');
  const transText = document.getElementById('transText');
  const cardRomanization = document.getElementById('cardRomanization');
  const cardTranslation = document.getElementById('cardTranslation');
  const scratchpadContent = document.getElementById('scratchpadContent');
  const rawContent = document.getElementById('rawContent');

  // Lexicon Drawer Elements
  const btnOpenLexicon = document.getElementById('btnOpenLexicon');
  const btnCloseLexicon = document.getElementById('btnCloseLexicon');
  const lexiconDrawer = document.getElementById('lexiconDrawer');
  const lexiconSearchInput = document.getElementById('lexiconSearchInput');
  const posFilters = document.getElementById('posFilters');
  const lexiconResults = document.getElementById('lexiconResults');
  const lexiconTotalPill = document.getElementById('lexiconTotalPill');
  const btnLoadAllLexicon = document.getElementById('btnLoadAllLexicon');
  const lexStatusText = document.getElementById('lexStatusText');

  // Grammar Modal Elements
  const btnOpenGrammar = document.getElementById('btnOpenGrammar');
  const btnCloseGrammar = document.getElementById('btnCloseGrammar');
  const grammarModal = document.getElementById('grammarModal');

  // Support / Donation Modal Elements
  const btnOpenSupport = document.getElementById('btnOpenSupport');
  const btnCloseSupport = document.getElementById('btnCloseSupport');
  const supportModal = document.getElementById('supportModal');

  // Language Modal & Switcher Elements
  const langModal = document.getElementById('langModal');
  const btnOpenLang = document.getElementById('btnOpenLang');
  const btnCloseLang = document.getElementById('btnCloseLang');
  const navLangFlag = document.getElementById('navLangFlag');
  const navLangName = document.getElementById('navLangName');
  const langCards = document.querySelectorAll('.lang-card');

  // Virtual Keyboard Elements
  const btnToggleKeyboard = document.getElementById('btnToggleKeyboard');
  const btnCloseKeyboard = document.getElementById('btnCloseKeyboard');
  const virtualKeyboardPanel = document.getElementById('virtualKeyboardPanel');
  const vkTabs = document.getElementById('vkTabs');
  const vkKeysContainer = document.getElementById('vkKeysContainer');
  let activeVkLang = 'oru';

  let currentLanguage = 'en';
  let currentMode = 'free';
  let currentTab = 'rendered';
  let hasGenerated = false;
  let timerInterval = null;
  let lexiconDebounce = null;
  let activePosFilter = '';

  /**
   * Child-Friendly Language Switcher & Application Localization
   */
  function openLanguageModal() {
    if (langModal) {
      langCards.forEach(c => {
        c.classList.toggle('active', c.getAttribute('data-lang') === currentLanguage);
      });
      langModal.classList.remove('hidden');
    }
  }

  function closeLanguageModal() {
    if (langModal) {
      langModal.classList.add('hidden');
    }
  }

  function applyLanguage(lang, showNotification = true) {
    if (!TRANSLATIONS[lang]) lang = 'en';
    currentLanguage = lang;
    localStorage.setItem('ormuri_app_lang', lang);

    const meta = LANG_META[lang];
    document.documentElement.dir = meta.dir;
    document.documentElement.lang = lang;

    // Update navbar button
    if (navLangFlag) navLangFlag.textContent = meta.flag;
    if (navLangName) navLangName.textContent = meta.name;

    // Update all text nodes with data-i18n
    const dict = TRANSLATIONS[lang];
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (dict[key] !== undefined) {
        el.textContent = dict[key];
      }
    });

    // Update all input placeholders with data-i18n-ph
    document.querySelectorAll('[data-i18n-ph]').forEach(el => {
      const key = el.getAttribute('data-i18n-ph');
      if (dict[key] !== undefined) {
        el.setAttribute('placeholder', dict[key]);
      }
    });

    // Update quick launch scenario chips
    if (CHIP_PROMPTS[lang]) {
      Object.keys(CHIP_PROMPTS[lang]).forEach(chipKey => {
        const btn = document.querySelector(`.chip[data-chip="${chipKey}"]`);
        if (btn) {
          const info = CHIP_PROMPTS[lang][chipKey];
          btn.textContent = info.label;
          btn.setAttribute('data-prompt', info.prompt);
          btn.dataset.prompt = info.prompt;
        }
      });
    }

    // Highlight active card in modal
    langCards.forEach(card => {
      const cLang = card.getAttribute('data-lang');
      card.classList.toggle('active', cLang === lang);
    });

    // Sync default keyboard layout with language
    if (lang === 'ps') {
      activeVkLang = 'ps';
    } else if (lang === 'ur') {
      activeVkLang = 'ur';
    } else {
      activeVkLang = 'oru';
    }
    if (virtualKeyboardPanel && !virtualKeyboardPanel.classList.contains('hidden')) {
      renderVirtualKeyboard(activeVkLang);
    }

    if (showNotification) {
      const switchMessages = {
        en: 'Switched to English 🇬🇧',
        ur: 'اردو زبان منتخب ہو گئی 🇵🇰',
        ps: 'پښتو ژبه وټاکل شوه ☀️'
      };
      showToast(switchMessages[lang] || `Language set to ${meta.name}`);
    }
  }

  /**
   * Virtual Keyboard Typing & Layout Engine (Pashto, Ormuri, Urdu)
   */
  function insertTextAtCursor(inputEl, text) {
    if (!inputEl) return;
    const startPos = inputEl.selectionStart !== undefined ? inputEl.selectionStart : inputEl.value.length;
    const endPos = inputEl.selectionEnd !== undefined ? inputEl.selectionEnd : inputEl.value.length;
    const textBefore = inputEl.value.substring(0, startPos);
    const textAfter = inputEl.value.substring(endPos);
    inputEl.value = textBefore + text + textAfter;
    const newPos = startPos + text.length;
    inputEl.selectionStart = inputEl.selectionEnd = newPos;
    inputEl.focus();
    inputEl.dispatchEvent(new Event('input', { bubbles: true }));
  }

  function backspaceAtCursor(inputEl) {
    if (!inputEl) return;
    const startPos = inputEl.selectionStart;
    const endPos = inputEl.selectionEnd;
    if (startPos !== endPos) {
      const textBefore = inputEl.value.substring(0, startPos);
      const textAfter = inputEl.value.substring(endPos);
      inputEl.value = textBefore + textAfter;
      inputEl.selectionStart = inputEl.selectionEnd = startPos;
    } else if (startPos > 0) {
      const textBefore = inputEl.value.substring(0, startPos - 1);
      const textAfter = inputEl.value.substring(endPos);
      inputEl.value = textBefore + textAfter;
      inputEl.selectionStart = inputEl.selectionEnd = startPos - 1;
    }
    inputEl.focus();
    inputEl.dispatchEvent(new Event('input', { bubbles: true }));
  }

  function renderVirtualKeyboard(langKey) {
    if (!KEYBOARD_LAYOUTS[langKey]) langKey = 'oru';
    activeVkLang = langKey;

    if (vkTabs) {
      vkTabs.querySelectorAll('.vk-tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-vk-lang') === langKey);
      });
    }

    if (!vkKeysContainer) return;
    vkKeysContainer.innerHTML = '';

    const layout = KEYBOARD_LAYOUTS[langKey];
    const isSpecialClass = `vk-special-${langKey}`;

    layout.rows.forEach(rowKeys => {
      const rowDiv = document.createElement('div');
      rowDiv.className = 'vk-row';
      rowKeys.forEach(char => {
        const keyBtn = document.createElement('button');
        keyBtn.type = 'button';
        keyBtn.className = 'vk-key';
        keyBtn.textContent = char;
        keyBtn.setAttribute('data-char', char);

        if (layout.specials && layout.specials.includes(char)) {
          keyBtn.classList.add(isSpecialClass);
        } else if (['َ', 'ِ', 'ُ', 'ً', 'ٍ', 'ٌ', 'ّ', 'ْ', 'ۂ'].includes(char)) {
          keyBtn.classList.add('vk-diacritic');
        }

        keyBtn.addEventListener('click', (e) => {
          e.preventDefault();
          insertTextAtCursor(promptInput, char);
        });
        rowDiv.appendChild(keyBtn);
      });
      vkKeysContainer.appendChild(rowDiv);
    });
  }

  function toggleVirtualKeyboard() {
    if (!virtualKeyboardPanel) return;
    const isHidden = virtualKeyboardPanel.classList.toggle('hidden');
    if (btnToggleKeyboard) {
      btnToggleKeyboard.classList.toggle('active', !isHidden);
    }
    if (!isHidden) {
      renderVirtualKeyboard(activeVkLang);
      promptInput.focus();
    }
  }

  // Quick characters strip (one-tap instant insertion)
  document.querySelectorAll('.q-char').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const char = btn.getAttribute('data-char');
      if (char) {
        insertTextAtCursor(promptInput, char);
      }
    });
  });

  // Action keys (space, backspace, enter, clear)
  document.querySelectorAll('.vk-action-key').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const action = btn.getAttribute('data-action');
      if (action === 'space') {
        insertTextAtCursor(promptInput, ' ');
      } else if (action === 'backspace') {
        backspaceAtCursor(promptInput);
      } else if (action === 'enter') {
        insertTextAtCursor(promptInput, '\n');
      } else if (action === 'clear') {
        promptInput.value = '';
        promptInput.focus();
        promptInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
    });
  });

  if (btnToggleKeyboard) {
    btnToggleKeyboard.addEventListener('click', toggleVirtualKeyboard);
  }
  if (btnCloseKeyboard) {
    btnCloseKeyboard.addEventListener('click', () => {
      if (virtualKeyboardPanel) {
        virtualKeyboardPanel.classList.add('hidden');
        if (btnToggleKeyboard) btnToggleKeyboard.classList.remove('active');
      }
    });
  }

  if (vkTabs) {
    vkTabs.addEventListener('click', (e) => {
      const tabBtn = e.target.closest('.vk-tab-btn');
      if (tabBtn) {
        const lang = tabBtn.getAttribute('data-vk-lang');
        if (lang) renderVirtualKeyboard(lang);
      }
    });
  }

  /**
   * Universal State Switcher for Output View
   * Directly sets inline display and toggles classes to guarantee instant, 
   * cache-immune replacement of "Ready to Generate".
   */
  function showOutputState(stateName) {
    const states = {
      placeholder: outputPlaceholder,
      loading: outputLoading,
      quota: outputQuotaError,
      rendered: tabRendered,
      scratchpad: tabScratchpad,
      raw: tabRaw
    };

    Object.keys(states).forEach(key => {
      const el = states[key];
      if (!el) return;
      if (key === stateName) {
        el.style.display = 'flex';
        el.classList.remove('hidden');
      } else {
        el.style.display = 'none';
        el.classList.add('hidden');
      }
    });

    if (outputWrapper && (stateName === 'rendered' || stateName === 'scratchpad' || stateName === 'raw')) {
      outputWrapper.scrollTop = 0;
    }
  }

  // Helper: Strip all '*' symbols and replace with a space
  function cleanAsterisks(str) {
    if (!str) return '';
    return str.replaceAll('*', ' ');
  }

  // 1. Temperature Slider
  tempSlider.addEventListener('input', (e) => {
    tempValue.textContent = Number(e.target.value).toFixed(2);
  });

  // 2. Mode Selector
  modeSelector.addEventListener('click', (e) => {
    if (e.target.classList.contains('mode-btn')) {
      modeSelector.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
      e.target.classList.add('active');
      currentMode = e.target.dataset.mode;
    }
  });

  // 3. Quick Chips
  quickChips.forEach(chip => {
    chip.addEventListener('click', () => {
      promptInput.value = chip.dataset.prompt;
      promptInput.focus();
    });
  });

  // 4. Clear Button
  btnClear.addEventListener('click', () => {
    promptInput.value = '';
    hasGenerated = false;
    showOutputState('placeholder');
    promptInput.focus();
  });

  // 5. Output Tabs Switching
  outputTabs.addEventListener('click', (e) => {
    const btn = e.target.closest('.tab-btn');
    if (!btn) return;
    outputTabs.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentTab = btn.dataset.tab;

    // Only switch tabs if model output has been generated
    if (hasGenerated) {
      showOutputState(currentTab);
    }
  });

  // 6. Keyboard Shortcut: Ctrl + Enter
  promptInput.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      triggerGeneration();
    }
  });

  btnGenerate.addEventListener('click', triggerGeneration);

  // 7. Generation Trigger
  async function triggerGeneration() {
    const prompt = promptInput.value.trim();
    if (!prompt) {
      const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
      showToast(dict.alert_no_prompt || 'Please type or select a prompt first.');
      promptInput.focus();
      return;
    }

    // Set Loading State: replaces "Ready to Generate" with the loading indicator
    btnGenerate.disabled = true;
    btnSpinner.classList.add('active');
    showOutputState('loading');

    // Auto-scroll to output panel if on smaller/stacked screens
    if (outputPanel && (window.innerWidth <= 1024 || outputPanel.getBoundingClientRect().top > 80)) {
      outputPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    let startTime = Date.now();
    timerInterval = setInterval(() => {
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      timerText.textContent = `${elapsed}s`;
    }, 100);

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt,
          temperature: parseFloat(tempSlider.value),
          mode: currentMode
        })
      });

      const data = await response.json();
      clearInterval(timerInterval);

      if (!data.success) {
        // Check for Quota / Rate limit / Cost errors
        const isQuota = data.is_quota_limit || 
          (data.error && /429|quota|resource_exhausted|rate|limit|cost|credit|exhausted|billing/i.test(data.error));
        
        if (isQuota) {
          showOutputState('quota');
          if (outputPanel && window.innerWidth <= 1024) {
            outputPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
          return;
        }
        throw new Error(data.error || 'Server generation error');
      }

      const parsed = data.parsed || {};
      
      // Render Content with clean asterisks
      renderOrmuriOutput(parsed);

      // DIRECTLY REPLACE "Ready to Generate" where it was written
      showOutputState(currentTab);

      // Smooth scroll viewport to output panel if on stacked layout
      if (outputPanel && window.innerWidth <= 1024) {
        outputPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }

    } catch (err) {
      clearInterval(timerInterval);
      const isQuotaErr = /429|quota|resource_exhausted|rate|limit|cost|credit|exhausted|billing/i.test(err.message);
      if (isQuotaErr) {
        showOutputState('quota');
        if (outputPanel && window.innerWidth <= 1024) {
          outputPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      } else {
        showOutputState('placeholder');
        alert(`Generation Failed: ${err.message}`);
      }
    } finally {
      btnGenerate.disabled = false;
      btnSpinner.classList.remove('active');
    }
  }

  function renderOrmuriOutput(parsed) {
    hasGenerated = true;

    // Replace all '*' symbols in the model's response with a space
    const cleanedOrmuri = cleanAsterisks(parsed.ormuri_text || 'No text extracted');
    const cleanedRoman = cleanAsterisks(parsed.romanization || '');
    const cleanedTrans = cleanAsterisks(parsed.translation || '');
    const cleanedScratchpad = cleanAsterisks(parsed.scratchpad || 'No morphological scratchpad found.');
    const cleanedRaw = cleanAsterisks(parsed.raw_text || '');

    // 1. Ormuri Text
    ormuriText.innerHTML = formatProse(cleanedOrmuri);

    // 2. Romanization
    if (cleanedRoman) {
      romanText.innerHTML = formatProse(cleanedRoman);
      cardRomanization.style.display = 'block';
    } else {
      cardRomanization.style.display = 'none';
    }

    // 3. Translation
    if (cleanedTrans) {
      transText.innerHTML = formatProse(cleanedTrans);
      cardTranslation.style.display = 'block';
    } else {
      cardTranslation.style.display = 'none';
    }

    // 4. Scratchpad
    scratchpadContent.textContent = cleanedScratchpad;

    // 5. Raw output
    rawContent.textContent = cleanedRaw;
  }

  function formatProse(text) {
    if (!text) return '';
    return cleanAsterisks(text)
      .split('\n\n')
      .map(p => p.trim())
      .filter(p => p.length > 0)
      .map(p => `<p>${escapeHtml(p)}</p>`)
      .join('');
  }

  function escapeHtml(str) {
    return str.replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  // 8. Copy to Clipboard Utility
  window.copyCard = (elementId) => {
    const el = document.getElementById(elementId);
    if (!el) return;
    const textToCopy = el.innerText;
    navigator.clipboard.writeText(textToCopy).then(() => {
      const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
      showToast(dict.copied_toast || 'Copied to clipboard! ✓');
    }).catch(err => {
      console.error('Copy failed:', err);
    });
  };

  document.getElementById('btnCopyText').addEventListener('click', () => {
    const activeText = ormuriText.innerText;
    if (activeText) {
      navigator.clipboard.writeText(activeText).then(() => {
        const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
        showToast(dict.ormuri_copied_toast || 'Ormuri text copied! ✓');
      });
    }
  });

  // Support / Account Copying
  window.copySupportAccount = () => {
    const iban = "PK62ASCM0001143230003241";
    navigator.clipboard.writeText(iban).then(() => {
      const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
      showToast(dict.account_copied_toast || 'Account details copied: PK62ASCM0001143230003241 (ALI SHER KHAN BURKI) ✓');
    }).catch(() => {
      prompt("Copy Account Number / IBAN:", iban);
    });
  };

  window.resetToPlaceholder = () => {
    hasGenerated = false;
    showOutputState('placeholder');
    promptInput.focus();
  };

  function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('toast-fadeout');
      setTimeout(() => toast.remove(), 300);
    }, 2500);
  }

  // 9. Lexicon Explorer Drawer
  // 9. Lexicon Explorer Drawer (Full 6,657-Word Database with Infinite Scroll & Instant Search)
  let lexiconOffset = 0;
  const lexiconLimit = 100;
  let lexiconTotal = 0;
  let lexiconHasMore = false;
  let lexiconLoading = false;
  let currentLexiconQuery = '';
  let loadedCount = 0;

  btnOpenLexicon.addEventListener('click', () => {
    lexiconDrawer.classList.add('open');
    if (!loadedCount) {
      fetchLexicon('', true);
    }
    lexiconSearchInput.focus();
  });

  btnCloseLexicon.addEventListener('click', () => {
    lexiconDrawer.classList.remove('open');
  });

  lexiconSearchInput.addEventListener('input', (e) => {
    clearTimeout(lexiconDebounce);
    lexiconDebounce = setTimeout(() => {
      fetchLexicon(e.target.value.trim(), true);
    }, 250);
  });

  posFilters.addEventListener('click', (e) => {
    if (e.target.classList.contains('pos-chip')) {
      posFilters.querySelectorAll('.pos-chip').forEach(c => c.classList.remove('active'));
      e.target.classList.add('active');
      activePosFilter = e.target.dataset.pos;
      fetchLexicon(lexiconSearchInput.value.trim(), true);
    }
  });

  if (btnLoadAllLexicon) {
    btnLoadAllLexicon.addEventListener('click', () => {
      loadAllRemainingLexicon();
    });
  }

  // Infinite Scroll on Lexicon Drawer
  lexiconResults.addEventListener('scroll', () => {
    if (lexiconLoading || !lexiconHasMore) return;
    const threshold = 350;
    if (lexiconResults.scrollTop + lexiconResults.clientHeight >= lexiconResults.scrollHeight - threshold) {
      fetchLexicon(currentLexiconQuery, false);
    }
  });

  window.loadMoreLexicon = () => {
    fetchLexicon(currentLexiconQuery, false);
  };

  async function fetchLexicon(query, reset = false) {
    if (lexiconLoading) return;
    lexiconLoading = true;

    if (reset) {
      lexiconOffset = 0;
      loadedCount = 0;
      currentLexiconQuery = query;
      lexiconResults.innerHTML = '<div style="color: #64748B; padding: 2rem; text-align: center;"><div class="lex-spinner-sm" style="margin: 0 auto 0.75rem;"></div>Searching full database (6,657 words)...</div>';
      lexiconResults.scrollTop = 0;
      if (lexStatusText) lexStatusText.textContent = 'Searching full dictionary...';
      if (btnLoadAllLexicon) btnLoadAllLexicon.classList.add('hidden');
    } else {
      updateSentinel(true);
    }

    try {
      const url = `/api/lexicon?q=${encodeURIComponent(query)}&pos=${encodeURIComponent(activePosFilter)}&offset=${lexiconOffset}&limit=${lexiconLimit}`;
      const res = await fetch(url);
      const data = await res.json();

      lexiconTotal = data.total_matches || 0;
      lexiconHasMore = Boolean(data.has_more);
      const results = data.results || [];
      lexiconOffset += results.length;
      loadedCount += results.length;

      if (reset) {
        lexiconResults.innerHTML = '';
      }

      renderLexiconChunk(results, reset);

      // Update Status Bar
      if (lexStatusText) {
        if (lexiconTotal === 0) {
          lexStatusText.innerHTML = `No words found matching <strong>"${escapeHtml(query)}"</strong>`;
        } else if (lexiconTotal <= loadedCount) {
          lexStatusText.innerHTML = `Showing all <strong>${lexiconTotal.toLocaleString()}</strong> words`;
        } else {
          lexStatusText.innerHTML = `Showing <strong>${loadedCount.toLocaleString()}</strong> of <strong>${lexiconTotal.toLocaleString()}</strong> words`;
        }
      }

      if (btnLoadAllLexicon) {
        if (lexiconHasMore && (lexiconTotal - loadedCount) <= 2500) {
          btnLoadAllLexicon.textContent = `Load All (${(lexiconTotal - loadedCount).toLocaleString()} more)`;
          btnLoadAllLexicon.classList.remove('hidden');
        } else {
          btnLoadAllLexicon.classList.add('hidden');
        }
      }

      updateSentinel(false);

    } catch (e) {
      if (reset) {
        lexiconResults.innerHTML = `<div style="color: #EF4444; padding: 1.5rem; text-align: center;">Failed to load words: ${e.message}</div>`;
      }
      updateSentinel(false);
    } finally {
      lexiconLoading = false;
    }
  }

  function renderLexiconChunk(items, isReset) {
    if (!items.length) {
      if (isReset) {
        lexiconResults.innerHTML = '<div style="color: #64748B; padding: 2.5rem 1rem; text-align: center;"><div style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</div>No words match your search or filter.</div>';
      }
      return;
    }

    const html = items.map(item => `
      <div class="lexicon-item" onclick="insertWordToPrompt('${escapeHtml(item.word)}')">
        <div class="lex-top">
          <span class="lex-word">${item.word}</span>
          <span class="lex-ipa">[${item.ipa || ''}]</span>
          <span class="lex-pos">${item.pos || 'N/A'}</span>
        </div>
        <div class="lex-gloss">${escapeHtml(item.gloss || item.meaning || '')}</div>
      </div>
    `).join('');

    lexiconResults.insertAdjacentHTML('beforeend', html);
  }

  function updateSentinel(isLoading) {
    let sentinel = document.getElementById('lexSentinel');
    if (!sentinel) {
      sentinel = document.createElement('div');
      sentinel.id = 'lexSentinel';
      sentinel.className = 'lex-bottom-sentinel';
      lexiconResults.appendChild(sentinel);
    }

    if (isLoading) {
      sentinel.innerHTML = '<div class="lex-spinner-sm"></div><span>Loading more words...</span>';
      sentinel.style.display = 'flex';
    } else if (lexiconHasMore) {
      sentinel.innerHTML = `
        <button class="btn-load-more" onclick="window.loadMoreLexicon()">
          Load More Words (${loadedCount} of ${lexiconTotal.toLocaleString()})
        </button>
      `;
      sentinel.style.display = 'flex';
    } else {
      if (loadedCount > 0) {
        sentinel.innerHTML = `<span>✓ All ${lexiconTotal.toLocaleString()} words loaded</span>`;
        sentinel.style.display = 'flex';
      } else {
        sentinel.style.display = 'none';
      }
    }
  }

  async function loadAllRemainingLexicon() {
    if (lexiconLoading || !lexiconHasMore) return;
    lexiconLoading = true;
    updateSentinel(true);

    try {
      const remainingLimit = lexiconTotal - loadedCount + 50;
      const url = `/api/lexicon?q=${encodeURIComponent(currentLexiconQuery)}&pos=${encodeURIComponent(activePosFilter)}&offset=${lexiconOffset}&limit=${remainingLimit}`;
      const res = await fetch(url);
      const data = await res.json();

      const results = data.results || [];
      lexiconOffset += results.length;
      loadedCount += results.length;
      lexiconHasMore = false;

      renderLexiconChunk(results, false);

      if (lexStatusText) {
        lexStatusText.innerHTML = `Showing all <strong>${loadedCount.toLocaleString()}</strong> words`;
      }
      if (btnLoadAllLexicon) {
        btnLoadAllLexicon.classList.add('hidden');
      }

      updateSentinel(false);
    } catch (e) {
      showToast(`Error loading remaining words: ${e.message}`);
      updateSentinel(false);
    } finally {
      lexiconLoading = false;
    }
  }

  window.insertWordToPrompt = (word) => {
    promptInput.value += ` ${word} `;
    const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
    showToast(`"${word}" ${dict.word_inserted || 'inserted into prompt!'}`);
    promptInput.focus();
  };

  // 10. Grammar Cheat Sheet Modal
  btnOpenGrammar.addEventListener('click', () => {
    grammarModal.classList.remove('hidden');
  });

  btnCloseGrammar.addEventListener('click', () => {
    grammarModal.classList.add('hidden');
  });

  grammarModal.addEventListener('click', (e) => {
    if (e.target === grammarModal) {
      grammarModal.classList.add('hidden');
    }
  });

  // 11. Support & Donation Modal
  if (btnOpenSupport && supportModal) {
    btnOpenSupport.addEventListener('click', () => {
      supportModal.classList.remove('hidden');
    });

    if (btnCloseSupport) {
      btnCloseSupport.addEventListener('click', () => {
        supportModal.classList.add('hidden');
      });
    }

    supportModal.addEventListener('click', (e) => {
      if (e.target === supportModal) {
        supportModal.classList.add('hidden');
      }
    });
  }

  // 12. Language Selection Modal Listeners
  if (btnOpenLang) {
    btnOpenLang.addEventListener('click', openLanguageModal);
  }
  if (btnCloseLang) {
    btnCloseLang.addEventListener('click', closeLanguageModal);
  }
  if (langModal) {
    langModal.addEventListener('click', (e) => {
      if (e.target === langModal) closeLanguageModal();
    });
  }

  langCards.forEach(card => {
    card.addEventListener('click', () => {
      const selectedLang = card.getAttribute('data-lang');
      if (selectedLang) {
        applyLanguage(selectedLang, true);
        sessionStorage.setItem('ormuri_lang_chosen_session', '1');
        closeLanguageModal();
      }
    });
  });

  // 13. Dynamic System Status Sync
  async function fetchSystemStatus() {
    try {
      const res = await fetch('/api/status');
      if (!res.ok) return;
      const data = await res.json();
      
      const badgeModel = document.getElementById('badgeModel');
      if (badgeModel && data.model) {
        badgeModel.textContent = `${data.model} (Cached)`;
      }

      const badgeKb = document.getElementById('badgeKb');
      if (badgeKb && data.kb_tokens) {
        const tokensFmt = Number(data.kb_tokens).toLocaleString();
        const charsFmt = data.kb_characters ? `${(data.kb_characters / 1000000).toFixed(1)}M Chars` : '2.0M Chars';
        badgeKb.textContent = `📚 ${tokensFmt} Tokens (${charsFmt})`;
      }

      const lexiconBtnText = document.getElementById('lexiconBtnText');
      if (lexiconBtnText && data.lexicon_entries) {
        const countFmt = Number(data.lexicon_entries).toLocaleString();
        const dict = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
        const wordLabel = currentLanguage === 'ps' ? 'کلمې' : (currentLanguage === 'ur' ? 'الفاظ' : 'Words');
        lexiconBtnText.innerHTML = `<span class="btn-label" data-i18n="btn_lexicon">${dict.btn_lexicon}</span> <span class="btn-count">(${countFmt} ${wordLabel})</span>`;
      }

      const lexiconTotalPill = document.getElementById('lexiconTotalPill');
      if (lexiconTotalPill && data.lexicon_entries) {
        const countFmt = Number(data.lexicon_entries).toLocaleString();
        const wordLabel = currentLanguage === 'ps' ? 'کلمې' : (currentLanguage === 'ur' ? 'الفاظ' : 'Words');
        lexiconTotalPill.textContent = `${countFmt} ${wordLabel}`;
      }
    } catch (err) {
      console.warn('Could not sync status:', err);
    }
  }

  // Initial State Setup
  showOutputState('placeholder');

  // Language Setup & First-time Auto-Open Modal
  const savedLang = localStorage.getItem('ormuri_app_lang');
  const sessionChosen = sessionStorage.getItem('ormuri_lang_chosen_session');

  if (savedLang && TRANSLATIONS[savedLang]) {
    applyLanguage(savedLang, false);
  } else {
    applyLanguage('en', false);
  }

  fetchSystemStatus();

  // Child-friendly auto-open modal whenever opening the application
  if (!sessionChosen) {
    setTimeout(() => {
      openLanguageModal();
    }, 200);
  }

});
