/**
 * Ormuri AI Playground — Client Application Logic (v3.0)
 */

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

  // Grammar Modal Elements
  const btnOpenGrammar = document.getElementById('btnOpenGrammar');
  const btnCloseGrammar = document.getElementById('btnCloseGrammar');
  const grammarModal = document.getElementById('grammarModal');

  // Support / Donation Modal Elements
  const btnOpenSupport = document.getElementById('btnOpenSupport');
  const btnCloseSupport = document.getElementById('btnCloseSupport');
  const supportModal = document.getElementById('supportModal');

  let currentMode = 'free';
  let currentTab = 'rendered';
  let hasGenerated = false;
  let timerInterval = null;
  let lexiconDebounce = null;
  let activePosFilter = '';

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
      alert('Please type or select a prompt first.');
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

  // Support / Account Copying
  window.copySupportAccount = () => {
    const iban = "PK62ASCM0001143230003241";
    navigator.clipboard.writeText(iban).then(() => {
      showToast('Account details copied: PK62ASCM0001143230003241 (ALI SHER KHAN BURKI) ✓');
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
    toast.style.cssText = `
      position: fixed;
      bottom: 4rem;
      right: 2rem;
      background: #10B981;
      color: #03201c;
      font-weight: 600;
      padding: 0.75rem 1.4rem;
      border-radius: 8px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      z-index: 9999;
      font-size: 0.88rem;
      transition: opacity 0.3s;
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 2500);
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

  // 12. Dynamic System Status Sync
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
        lexiconBtnText.textContent = `Lexicon (${countFmt} Words)`;
      }

      const lexiconTotalPill = document.getElementById('lexiconTotalPill');
      if (lexiconTotalPill && data.lexicon_entries) {
        const countFmt = Number(data.lexicon_entries).toLocaleString();
        lexiconTotalPill.textContent = `${countFmt} Words`;
      }
    } catch (err) {
      console.warn('Could not sync status:', err);
    }
  }

  // Initial State Setup
  showOutputState('placeholder');
  fetchSystemStatus();

});
