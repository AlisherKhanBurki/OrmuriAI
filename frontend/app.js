/**
 * Ormuri AI Playground — Client Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const promptInput = document.getElementById('promptInput');
  const tempSlider = document.getElementById('tempSlider');
  const tempValue = document.getElementById('tempValue');
  const btnGenerate = document.getElementById('btnGenerate');
  const btnClear = document.getElementById('btnClear');
  const btnSpinner = document.getElementById('btnSpinner');
  const modeSelector = document.getElementById('modeSelector');
  const quickChips = document.querySelectorAll('.chip');

  // Output Elements
  const outputPlaceholder = document.getElementById('outputPlaceholder');
  const outputLoading = document.getElementById('outputLoading');
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

  // Grammar Modal Elements
  const btnOpenGrammar = document.getElementById('btnOpenGrammar');
  const btnCloseGrammar = document.getElementById('btnCloseGrammar');
  const grammarModal = document.getElementById('grammarModal');

  let currentMode = 'free';
  let currentTab = 'rendered';
  let timerInterval = null;
  let lexiconDebounce = null;
  let activePosFilter = '';

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
    promptInput.focus();
  });

  // 5. Output Tabs Switching
  outputTabs.addEventListener('click', (e) => {
    const btn = e.target.closest('.tab-btn');
    if (!btn) return;
    outputTabs.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentTab = btn.dataset.tab;

    // Switch visible tab
    tabRendered.classList.add('hidden');
    tabScratchpad.classList.add('hidden');
    tabRaw.classList.add('hidden');

    if (currentTab === 'rendered') {
      tabRendered.classList.remove('hidden');
    } else if (currentTab === 'scratchpad') {
      tabScratchpad.classList.remove('hidden');
    } else if (currentTab === 'raw') {
      tabRaw.classList.remove('hidden');
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
      alert('Please type or select a prompt first.');
      promptInput.focus();
      return;
    }

    // Set Loading State
    btnGenerate.disabled = true;
    btnSpinner.classList.add('active');
    outputPlaceholder.classList.add('hidden');
    tabRendered.classList.add('hidden');
    tabScratchpad.classList.add('hidden');
    tabRaw.classList.add('hidden');
    outputLoading.classList.remove('hidden');

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
        throw new Error(data.error || 'Server generation error');
      }

      const parsed = data.parsed || {};
      
      // Render Content
      renderOrmuriOutput(parsed);

      // Restore UI State
      outputLoading.classList.add('hidden');
      if (currentTab === 'rendered') {
        tabRendered.classList.remove('hidden');
      } else if (currentTab === 'scratchpad') {
        tabScratchpad.classList.remove('hidden');
      } else {
        tabRaw.classList.remove('hidden');
      }

    } catch (err) {
      clearInterval(timerInterval);
      outputLoading.classList.add('hidden');
      outputPlaceholder.classList.remove('hidden');
      alert(`Generation Failed: ${err.message}`);
    } finally {
      btnGenerate.disabled = false;
      btnSpinner.classList.remove('active');
    }
  }

  function renderOrmuriOutput(parsed) {
    // 1. Ormuri Text
    ormuriText.innerHTML = formatProse(parsed.ormuri_text || 'No text extracted');

    // 2. Romanization
    if (parsed.romanization) {
      romanText.innerHTML = formatProse(parsed.romanization);
      cardRomanization.style.display = 'block';
    } else {
      cardRomanization.style.display = 'none';
    }

    // 3. Translation
    if (parsed.translation) {
      transText.innerHTML = formatProse(parsed.translation);
      cardTranslation.style.display = 'block';
    } else {
      cardTranslation.style.display = 'none';
    }

    // 4. Scratchpad
    scratchpadContent.textContent = parsed.scratchpad || 'No morphological scratchpad found.';

    // 5. Raw output
    rawContent.textContent = parsed.raw_text || '';
  }

  function formatProse(text) {
    return text.split('\n\n')
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
      showToast('Copied to clipboard! ✓');
    }).catch(err => {
      console.error('Copy failed:', err);
    });
  };

  document.getElementById('btnCopyText').addEventListener('click', () => {
    const activeText = ormuriText.innerText;
    if (activeText) {
      navigator.clipboard.writeText(activeText).then(() => {
        showToast('Ormuri text copied! ✓');
      });
    }
  });

  function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: #10B981;
      color: #03201c;
      font-weight: 600;
      padding: 0.65rem 1.25rem;
      border-radius: 8px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      z-index: 999;
      font-size: 0.85rem;
      transition: opacity 0.3s;
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 2000);
  }

  // 9. Lexicon Explorer Drawer
  btnOpenLexicon.addEventListener('click', () => {
    lexiconDrawer.classList.add('open');
    if (!lexiconResults.children.length) {
      fetchLexicon('');
    }
    lexiconSearchInput.focus();
  });

  btnCloseLexicon.addEventListener('click', () => {
    lexiconDrawer.classList.remove('open');
  });

  lexiconSearchInput.addEventListener('input', (e) => {
    clearTimeout(lexiconDebounce);
    lexiconDebounce = setTimeout(() => {
      fetchLexicon(e.target.value.trim());
    }, 200);
  });

  posFilters.addEventListener('click', (e) => {
    if (e.target.classList.contains('pos-chip')) {
      posFilters.querySelectorAll('.pos-chip').forEach(c => c.classList.remove('active'));
      e.target.classList.add('active');
      activePosFilter = e.target.dataset.pos;
      fetchLexicon(lexiconSearchInput.value.trim());
    }
  });

  async function fetchLexicon(query) {
    lexiconResults.innerHTML = '<div style="color: #64748B; padding: 1rem; text-align: center;">Searching lexicon...</div>';
    try {
      const url = `/api/lexicon?q=${encodeURIComponent(query)}&pos=${encodeURIComponent(activePosFilter)}&limit=60`;
      const res = await fetch(url);
      const data = await res.json();
      renderLexiconResults(data.results || []);
    } catch (e) {
      lexiconResults.innerHTML = `<div style="color: #EF4444; padding: 1rem;">Failed to load words: ${e.message}</div>`;
    }
  }

  function renderLexiconResults(items) {
    if (!items.length) {
      lexiconResults.innerHTML = '<div style="color: #64748B; padding: 1rem; text-align: center;">No words match your search.</div>';
      return;
    }

    lexiconResults.innerHTML = items.map(item => `
      <div class="lexicon-item" onclick="insertWordToPrompt('${escapeHtml(item.word)}')">
        <div class="lex-top">
          <span class="lex-word">${item.word}</span>
          <span class="lex-ipa">[${item.ipa || ''}]</span>
          <span class="lex-pos">${item.pos || 'N/A'}</span>
        </div>
        <div class="lex-gloss">${escapeHtml(item.gloss || '')}</div>
      </div>
    `).join('');
  }

  window.insertWordToPrompt = (word) => {
    promptInput.value += ` ${word} `;
    showToast(`Inserted "${word}" into prompt!`);
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

});
