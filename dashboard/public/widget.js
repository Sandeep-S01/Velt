(function () {
  class SmartSearchWidget {
    constructor(storeId, apiBase) {
      this.storeId = storeId;
      this.apiBase = apiBase;
      this.config = {
        theme: 'light',
        primary_color: '#4F46E5',
        position: 'bottom-right',
        placeholder_text: 'Search for products...',
        show_filters: true,
        show_price: true,
        show_rating: true,
        enable_autocomplete: true
      };
      this.isOpen = false;
      this.currentQueryLogId = null;
      this.debounceTimeout = null;

      this.init();
    }

    async init() {
      try {
        await this.loadConfig();
        this.injectStyles();
        this.renderElements();
        this.bindEvents();
      } catch (err) {
        console.error('SmartSearch Widget: Initialization failed', err);
      }
    }

    async loadConfig() {
      const resp = await fetch(`${this.apiBase}/widget/config/${this.storeId}`);
      if (resp.ok) {
        const remoteConfig = await resp.json();
        this.config = { ...this.config, ...remoteConfig };
      }
    }

    injectStyles() {
      const css = `
        /* SmartSearch Floating Action Button */
        #ss-widget-fab {
          position: fixed;
          bottom: 24px;
          width: 52px;
          height: 52px;
          border-radius: 50%;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          box-shadow: 0 4px 14px rgba(0, 0, 0, 0.16);
          z-index: 99999;
          transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s;
        }
        #ss-widget-fab:hover {
          transform: scale(1.05);
          box-shadow: 0 6px 20px rgba(0, 0, 0, 0.24);
        }
        #ss-widget-fab svg {
          width: 22px;
          height: 22px;
          fill: none;
          stroke: currentColor;
          stroke-width: 2.5;
        }

        /* SmartSearch Search Modal Overlay */
        #ss-search-overlay {
          position: fixed;
          inset: 0;
          background: rgba(17, 24, 37, 0.6);
          backdrop-filter: blur(8px);
          -webkit-backdrop-filter: blur(8px);
          z-index: 999999;
          display: flex;
          align-items: flex-start;
          justify-content: center;
          padding: 60px 24px 24px 24px;
          opacity: 0;
          pointer-events: none;
          transition: opacity 0.25s ease-out;
        }
        #ss-search-overlay.ss-open {
          opacity: 1;
          pointer-events: auto;
        }

        /* Modal Container */
        .ss-modal {
          background: ${this.config.theme === 'dark' ? '#111827' : '#FFFFFF'};
          color: ${this.config.theme === 'dark' ? '#F9FAFB' : '#111827'};
          width: 100%;
          max-width: 600px;
          border-radius: 16px;
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
          border: 1px solid ${this.config.theme === 'dark' ? '#374151' : '#E5E7EB'};
          overflow: hidden;
          transform: translateY(-20px);
          transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }
        #ss-search-overlay.ss-open .ss-modal {
          transform: translateY(0);
        }

        /* Modal Header (Search Input Zone) */
        .ss-header {
          display: flex;
          align-items: center;
          padding: 16px;
          border-b: 1px solid ${this.config.theme === 'dark' ? '#374151' : '#F3F4F6'};
          gap: 12px;
        }
        .ss-search-icon {
          color: #9CA3AF;
          width: 20px;
          height: 20px;
          stroke: currentColor;
          stroke-width: 2.5;
          fill: none;
        }
        .ss-input {
          flex: 1;
          border: none;
          background: transparent;
          font-family: system-ui, -apple-system, sans-serif;
          font-size: 16px;
          color: inherit;
          outline: none;
          padding: 4px 0;
        }
        .ss-input::placeholder {
          color: #9CA3AF;
        }
        .ss-close-btn {
          background: transparent;
          border: none;
          color: #9CA3AF;
          cursor: pointer;
          padding: 6px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background 0.15s, color 0.15s;
        }
        .ss-close-btn:hover {
          background: ${this.config.theme === 'dark' ? '#1F2937' : '#F3F4F6'};
          color: ${this.config.primary_color};
        }
        .ss-close-btn svg {
          width: 18px;
          height: 18px;
          stroke: currentColor;
          stroke-width: 2.5;
          fill: none;
        }

        /* Suggestions Drop Panel */
        .ss-autocomplete-panel {
          border-bottom: 1px solid ${this.config.theme === 'dark' ? '#374151' : '#F3F4F6'};
          background: ${this.config.theme === 'dark' ? '#1F2937' : '#FAFBFB'};
          max-height: 200px;
          overflow-y: auto;
          display: none;
        }
        .ss-autocomplete-panel.ss-active {
          display: block;
        }
        .ss-suggestion-item {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 10px 16px;
          cursor: pointer;
          font-size: 13px;
          font-weight: 500;
          color: ${this.config.theme === 'dark' ? '#D1D5DB' : '#4B5563'};
          transition: background 0.15s;
        }
        .ss-suggestion-item:hover {
          background: ${this.config.theme === 'dark' ? '#374151' : '#F3F4F6'};
        }
        .ss-suggestion-item span.ss-bulb {
          color: ${this.config.primary_color};
          font-size: 14px;
        }

        /* Results Catalog Container */
        .ss-results-area {
          max-height: 400px;
          overflow-y: auto;
          padding: 8px 0;
        }
        .ss-results-empty {
          padding: 40px 24px;
          text-align: center;
          color: #9CA3AF;
          font-size: 14px;
        }
        .ss-card {
          display: flex;
          padding: 16px;
          gap: 16px;
          cursor: pointer;
          border-bottom: 1px solid ${this.config.theme === 'dark' ? '#1F2937' : '#F9FAFB'};
          transition: background 0.15s;
          text-decoration: none;
          color: inherit;
        }
        .ss-card:hover {
          background: ${this.config.theme === 'dark' ? '#1F2937' : '#F9FAFB'};
        }
        .ss-card-img {
          width: 80px;
          height: 80px;
          border-radius: 8px;
          object-cover: cover;
          border: 1px solid ${this.config.theme === 'dark' ? '#374151' : '#E5E7EB'};
          background: ${this.config.theme === 'dark' ? '#374151' : '#F3F4F6'};
        }
        .ss-card-fallback-img {
          width: 80px;
          height: 80px;
          border-radius: 8px;
          background: ${this.config.theme === 'dark' ? '#1F2937' : '#F3F4F6'};
          border: 1px dashed ${this.config.theme === 'dark' ? '#374151' : '#D1D5DB'};
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
        }
        .ss-card-details {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .ss-card-title {
          font-weight: 700;
          font-size: 15px;
          line-height: 1.35;
          margin: 0;
        }
        .ss-card-price {
          font-weight: 700;
          font-size: 14px;
          color: ${this.config.primary_color};
        }
        .ss-card-desc {
          font-size: 12px;
          color: #9CA3AF;
          line-height: 1.45;
          margin: 2px 0 0 0;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        .ss-card-match {
          align-self: flex-start;
          display: inline-flex;
          font-size: 9px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          padding: 2px 6px;
          border-radius: 4px;
          margin-top: 4px;
          background: ${this.config.primary_color}12;
          color: ${this.config.primary_color};
          border: 1px solid ${this.config.primary_color}25;
        }

        /* Loading Spinner */
        .ss-loader {
          display: none;
          align-items: center;
          justify-content: center;
          padding: 40px;
        }
        .ss-loader.ss-active {
          display: flex;
        }
        .ss-spinner {
          width: 28px;
          height: 28px;
          border: 3px border-white/20;
          border-radius: 50%;
          border-top: 3px solid ${this.config.primary_color};
          animation: ss-spin 0.8s linear infinite;
        }
        @keyframes ss-spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `;

      const styleSheet = document.createElement('style');
      styleSheet.type = 'text/css';
      styleSheet.innerText = css;
      document.head.appendChild(styleSheet);
    }

    renderElements() {
      // 1. Create Floating Button
      const fab = document.createElement('div');
      fab.id = 'ss-widget-fab';
      fab.style.backgroundColor = this.config.primary_color;
      
      // Position config
      if (this.config.position === 'bottom-left') {
        fab.style.left = '24px';
      } else {
        fab.style.right = '24px';
      }

      fab.innerHTML = `
        <svg viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
      `;
      document.body.appendChild(fab);

      // 2. Create Search Overlay Modal
      const overlay = document.createElement('div');
      overlay.id = 'ss-search-overlay';
      overlay.innerHTML = `
        <div class="ss-modal">
          <div class="ss-header">
            <svg class="ss-search-icon" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input type="search" class="ss-input" placeholder="${this.config.placeholder_text}" autocomplete="off" />
            <button class="ss-close-btn">
              <svg viewBox="0 0 24 24">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
          <div class="ss-autocomplete-panel"></div>
          <div class="ss-loader">
            <div class="ss-spinner"></div>
          </div>
          <div class="ss-results-area">
            <div class="ss-results-empty">Type something to search by meaning...</div>
          </div>
        </div>
      `;
      document.body.appendChild(overlay);

      // Save Element References
      this.fabEl = fab;
      this.overlayEl = overlay;
      this.inputEl = overlay.querySelector('.ss-input');
      this.closeBtnEl = overlay.querySelector('.ss-close-btn');
      this.autocompleteEl = overlay.querySelector('.ss-autocomplete-panel');
      this.loaderEl = overlay.querySelector('.ss-loader');
      this.resultsEl = overlay.querySelector('.ss-results-area');
    }

    bindEvents() {
      // Toggle Modal
      this.fabEl.addEventListener('click', () => this.openSearch());
      this.closeBtnEl.addEventListener('click', () => this.closeSearch());
      
      // Close on backdrop click
      this.overlayEl.addEventListener('click', (e) => {
        if (e.target === this.overlayEl) {
          this.closeSearch();
        }
      });

      // Hotkey (Cmd+K or Ctrl+K)
      window.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
          e.preventDefault();
          this.isOpen ? this.closeSearch() : this.openSearch();
        }
        if (e.key === 'Escape' && this.isOpen) {
          this.closeSearch();
        }
      });

      // Typing debounced autocomplete suggestions / search trigger
      this.inputEl.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        this.handleQueryChange(query);
      });

      this.inputEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          const query = e.target.value.trim();
          this.executeSearch(query);
        }
      });
    }

    openSearch() {
      this.isOpen = true;
      this.overlayEl.classList.add('ss-open');
      setTimeout(() => this.inputEl.focus(), 50);
    }

    closeSearch() {
      this.isOpen = false;
      this.overlayEl.classList.remove('ss-open');
      this.inputEl.value = '';
      this.resultsEl.innerHTML = '<div class="ss-results-empty">Type something to search by meaning...</div>';
      this.autocompleteEl.classList.remove('ss-active');
      this.autocompleteEl.innerHTML = '';
      this.currentQueryLogId = null;
    }

    handleQueryChange(query) {
      if (this.debounceTimeout) {
        clearTimeout(this.debounceTimeout);
      }

      if (!query) {
        this.autocompleteEl.classList.remove('ss-active');
        this.autocompleteEl.innerHTML = '';
        return;
      }

      if (!this.config.enable_autocomplete) return;

      this.debounceTimeout = setTimeout(async () => {
        try {
          const resp = await fetch(
            `${this.apiBase}/widget/autocomplete?store_id=${this.storeId}&query=${encodeURIComponent(query)}`
          );
          if (resp.ok) {
            const data = await resp.json();
            this.renderSuggestions(data.suggestions, query);
          }
        } catch (err) {
          console.error('Autocomplete request failed', err);
        }
      }, 150);
    }

    renderSuggestions(suggestions, originalQuery) {
      if (!suggestions || suggestions.length === 0) {
        this.autocompleteEl.classList.remove('ss-active');
        this.autocompleteEl.innerHTML = '';
        return;
      }

      this.autocompleteEl.innerHTML = suggestions
        .map(
          (s) => `
            <div class="ss-suggestion-item" data-value="${s}">
              <span class="ss-bulb">💡</span>
              <span>${s.replace(new RegExp(originalQuery, 'gi'), (m) => `<strong>${m}</strong>`)}</span>
            </div>
          `
        )
        .join('');
      
      this.autocompleteEl.classList.add('ss-active');

      // Add click listeners to items
      this.autocompleteEl.querySelectorAll('.ss-suggestion-item').forEach((item) => {
        item.addEventListener('click', () => {
          const val = item.getAttribute('data-value');
          this.inputEl.value = val;
          this.autocompleteEl.classList.remove('ss-active');
          this.executeSearch(val);
        });
      });
    }

    async executeSearch(query) {
      if (!query) return;

      this.autocompleteEl.classList.remove('ss-active');
      this.loaderEl.classList.add('ss-active');
      this.resultsEl.innerHTML = '';
      this.currentQueryLogId = null;

      try {
        const response = await fetch(`${this.apiBase}/widget/search`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            store_id: this.storeId,
            query: query,
            limit: 5
          })
        });

        if (!response.ok) throw new Error('Search failed');

        // Extract query log ID from CORS response headers for click conversion attribution
        this.currentQueryLogId = response.headers.get('X-Query-Log-ID');

        const products = await response.json();
        this.renderResults(products);
      } catch (err) {
        this.resultsEl.innerHTML = `<div class="ss-results-empty" style="color: #EF4444">Error loading results. Please try again.</div>`;
      } finally {
        this.loaderEl.classList.remove('ss-active');
      }
    }

    renderResults(products) {
      if (!products || products.length === 0) {
        this.resultsEl.innerHTML = `
          <div class="ss-results-empty">
            <div style="font-size: 24px; margin-bottom: 8px;">🔍</div>
            No results found. Try searching for something else.
          </div>
        `;
        return;
      }

      this.resultsEl.innerHTML = products
        .map((p) => {
          const scorePercent = Math.round((1 - p.score) * 100);
          const showPrice = this.config.show_price && p.price !== null;
          
          return `
            <a href="${p.product_url || '#'}" class="ss-card" data-product-id="${p.id}">
              ${p.image_url 
                ? `<img src="${p.image_url}" alt="${p.title}" class="ss-card-img" />`
                : `<div class="ss-card-fallback-img">📦</div>`
              }
              <div class="ss-card-details">
                <h4 class="ss-card-title">${p.title}</h4>
                ${showPrice ? `<span class="ss-card-price">$${p.price.toFixed(2)}</span>` : ''}
                ${p.description ? `<p class="ss-card-desc">${p.description}</p>` : ''}
                <span class="ss-card-match">${scorePercent}% Match</span>
              </div>
            </a>
          `;
        })
        .join('');

      // Add click tracking event listeners to search cards
      this.resultsEl.querySelectorAll('.ss-card').forEach((card) => {
        card.addEventListener('click', (e) => {
          const productId = card.getAttribute('data-product-id');
          this.trackClick(productId);
        });
      });
    }

    async trackClick(productId) {
      if (!this.currentQueryLogId) return;

      try {
        await fetch(`${this.apiBase}/analytics/click`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            query_log_id: parseInt(this.currentQueryLogId, 10),
            clicked_product_id: productId
          })
        });
      } catch (err) {
        console.error('Click conversion tracking failed', err);
      }
    }
  }

  // Expose to window
  window.SmartSearchWidget = SmartSearchWidget;
})();
