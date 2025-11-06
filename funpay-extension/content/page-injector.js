/**
 * FunPay Ultimate Pro - Page Injector
 * Внедрение скриптов и модификация страницы
 */

(function() {
  'use strict';

  class PageInjector {
    constructor() {
      this.injected = false;
      this.init();
    }

    init() {
      if (this.injected) return;

      // Внедрение дополнительных элементов UI
      this.injectEnhancements();

      // Модификация существующих элементов
      this.modifyExistingElements();

      // Добавление полезных функций
      this.addUtilityFeatures();

      this.injected = true;
      FunPayUtils.log('Page Injector: инъекции выполнены');
    }

    injectEnhancements() {
      // Улучшенная навигация
      this.enhanceNavigation();

      // Быстрые фильтры
      this.addQuickFilters();

      // Статистика на странице
      this.addPageStats();

      // Дополнительная информация о товарах
      this.enhanceProductInfo();
    }

    enhanceNavigation() {
      const nav = document.querySelector('nav, .navigation, header');
      if (!nav) return;

      const enhancedNav = document.createElement('div');
      enhancedNav.className = 'fp-enhanced-nav';
      enhancedNav.style.cssText = `
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 10px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
      `;

      enhancedNav.innerHTML = `
        <div style="display: flex; gap: 15px;">
          <a href="#" class="fp-nav-link" data-action="dashboard">📊 Дашборд</a>
          <a href="#" class="fp-nav-link" data-action="analytics">📈 Аналитика</a>
          <a href="#" class="fp-nav-link" data-action="settings">⚙️ Настройки</a>
        </div>
        <div id="fp-quick-stats" style="font-size: 13px; opacity: 0.9;">
          Загрузка статистики...
        </div>
      `;

      // Вставка перед основной навигацией
      nav.parentNode.insertBefore(enhancedNav, nav);

      // Обработчики
      enhancedNav.querySelectorAll('.fp-nav-link').forEach(link => {
        link.style.cssText = 'color: white; text-decoration: none; padding: 5px 10px; border-radius: 5px; transition: background 0.3s;';
        link.addEventListener('mouseover', () => link.style.background = 'rgba(255,255,255,0.2)');
        link.addEventListener('mouseout', () => link.style.background = 'transparent');
        link.addEventListener('click', (e) => {
          e.preventDefault();
          const action = link.getAttribute('data-action');
          chrome.runtime.sendMessage({ action: `open${action.charAt(0).toUpperCase() + action.slice(1)}` });
        });
      });

      // Обновление быстрой статистики
      this.updateQuickStats();
      setInterval(() => this.updateQuickStats(), 10000);
    }

    async updateQuickStats() {
      const statsEl = document.getElementById('fp-quick-stats');
      if (!statsEl) return;

      const stats = await FunPayStorage.stats.getAll();
      statsEl.textContent = `📦 Заказы: ${stats.totalOrders || 0} | 💰 Продажи: ${stats.totalSales || 0} | 🔔 Уведомления: ${stats.notifications || 0}`;
    }

    addQuickFilters() {
      const listingContainer = document.querySelector('.tc-list, .offers-list, [class*="list"]');
      if (!listingContainer) return;

      const filtersPanel = document.createElement('div');
      filtersPanel.className = 'fp-quick-filters';
      filtersPanel.style.cssText = `
        background: white;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        align-items: center;
      `;

      filtersPanel.innerHTML = `
        <span style="font-weight: bold;">Быстрые фильтры:</span>
        <button class="fp-filter-btn" data-filter="price-low">💰 Дешевые</button>
        <button class="fp-filter-btn" data-filter="price-high">💎 Дорогие</button>
        <button class="fp-filter-btn" data-filter="new">🆕 Новые</button>
        <button class="fp-filter-btn" data-filter="popular">🔥 Популярные</button>
        <button class="fp-filter-btn" data-filter="discount">🎁 Со скидкой</button>
        <input type="text" id="fp-quick-search" placeholder="Быстрый поиск..." style="
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 5px;
          flex: 1;
          min-width: 200px;
        ">
        <button class="fp-filter-btn" data-filter="reset" style="background: #e74c3c;">↺ Сброс</button>
      `;

      listingContainer.parentNode.insertBefore(filtersPanel, listingContainer);

      // Стили для кнопок
      filtersPanel.querySelectorAll('.fp-filter-btn').forEach(btn => {
        btn.style.cssText = `
          padding: 8px 15px;
          border: none;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border-radius: 5px;
          cursor: pointer;
          font-size: 13px;
          transition: transform 0.2s;
        `;
        btn.addEventListener('mouseover', () => btn.style.transform = 'scale(1.05)');
        btn.addEventListener('mouseout', () => btn.style.transform = 'scale(1)');
      });

      // Обработчики фильтров
      this.setupFilterHandlers(filtersPanel, listingContainer);
    }

    setupFilterHandlers(filtersPanel, listingContainer) {
      filtersPanel.addEventListener('click', (e) => {
        if (e.target.classList.contains('fp-filter-btn')) {
          const filter = e.target.getAttribute('data-filter');
          this.applyFilter(listingContainer, filter);
        }
      });

      const searchInput = document.getElementById('fp-quick-search');
      if (searchInput) {
        searchInput.addEventListener('input', FunPayUtils.debounce((e) => {
          this.applySearch(listingContainer, e.target.value);
        }, 300));
      }
    }

    applyFilter(container, filter) {
      const items = container.querySelectorAll('.tc-item, .offer-list-item');
      
      items.forEach(item => {
        item.style.display = 'block';
        item.style.order = '0';
      });

      switch (filter) {
        case 'price-low':
          const sortedLow = Array.from(items).sort((a, b) => {
            const priceA = FunPayUtils.parsePrice(a.querySelector('.tc-price, .price')?.textContent || '0');
            const priceB = FunPayUtils.parsePrice(b.querySelector('.tc-price, .price')?.textContent || '0');
            return priceA - priceB;
          });
          sortedLow.forEach((item, index) => item.style.order = index);
          break;

        case 'price-high':
          const sortedHigh = Array.from(items).sort((a, b) => {
            const priceA = FunPayUtils.parsePrice(a.querySelector('.tc-price, .price')?.textContent || '0');
            const priceB = FunPayUtils.parsePrice(b.querySelector('.tc-price, .price')?.textContent || '0');
            return priceB - priceA;
          });
          sortedHigh.forEach((item, index) => item.style.order = index);
          break;

        case 'new':
          items.forEach(item => {
            if (!item.querySelector('.badge-new, .new')) {
              item.style.display = 'none';
            }
          });
          break;

        case 'popular':
          // Логика для популярных товаров
          break;

        case 'discount':
          items.forEach(item => {
            if (!item.querySelector('.discount, .sale')) {
              item.style.display = 'none';
            }
          });
          break;

        case 'reset':
          items.forEach(item => {
            item.style.display = 'block';
            item.style.order = '0';
          });
          const searchInput = document.getElementById('fp-quick-search');
          if (searchInput) searchInput.value = '';
          break;
      }
    }

    applySearch(container, query) {
      const items = container.querySelectorAll('.tc-item, .offer-list-item');
      const lowerQuery = query.toLowerCase();

      items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(lowerQuery) ? 'block' : 'none';
      });
    }

    addPageStats() {
      const pageType = FunPayUtils.getPageType();
      
      if (pageType === 'orders' || pageType === 'lots') {
        this.addStatsBanner();
      }
    }

    async addStatsBanner() {
      const banner = document.createElement('div');
      banner.className = 'fp-stats-banner';
      banner.style.cssText = `
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        margin: 20px 0;
        border-radius: 10px;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
      `;

      const stats = await this.getPageStats();
      
      Object.entries(stats).forEach(([key, value]) => {
        const statCard = document.createElement('div');
        statCard.style.cssText = `
          text-align: center;
          padding: 10px;
          background: rgba(255,255,255,0.1);
          border-radius: 8px;
        `;
        statCard.innerHTML = `
          <div style="font-size: 24px; font-weight: bold; margin-bottom: 5px;">${value}</div>
          <div style="font-size: 13px; opacity: 0.9;">${key}</div>
        `;
        banner.appendChild(statCard);
      });

      const container = document.querySelector('.content, main, .container');
      if (container) {
        container.insertBefore(banner, container.firstChild);
      }
    }

    async getPageStats() {
      const pageType = FunPayUtils.getPageType();
      const stats = {};

      if (pageType === 'orders') {
        const orders = document.querySelectorAll('.order-item, [data-order-id]');
        stats['Всего заказов'] = orders.length;
        stats['Активных'] = document.querySelectorAll('.order-active, [data-status="active"]').length;
        stats['Завершенных'] = document.querySelectorAll('.order-completed, [data-status="completed"]').length;
      } else if (pageType === 'lots') {
        const lots = document.querySelectorAll('.tc-item, .lot-item');
        stats['Всего лотов'] = lots.length;
        stats['В наличии'] = document.querySelectorAll('.in-stock, [data-stock="available"]').length;
        stats['Просмотров'] = '---'; // Здесь должна быть логика подсчета
      }

      return stats;
    }

    enhanceProductInfo() {
      domObserver.onElementAdded('.tc-item, .product-item, .offer-list-item', (item) => {
        this.addProductEnhancements(item);
      });

      // Обработка существующих товаров
      document.querySelectorAll('.tc-item, .product-item, .offer-list-item').forEach(item => {
        this.addProductEnhancements(item);
      });
    }

    addProductEnhancements(item) {
      if (item.querySelector('.fp-enhanced')) return;

      const enhancement = document.createElement('div');
      enhancement.className = 'fp-enhanced';
      enhancement.style.cssText = `
        margin-top: 10px;
        padding: 10px;
        background: #f8f9fa;
        border-radius: 5px;
        font-size: 12px;
      `;

      const price = FunPayUtils.parsePrice(item.querySelector('.tc-price, .price')?.textContent || '0');
      const priceHistory = this.getPriceHistory(item);

      enhancement.innerHTML = `
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
          <span>💹 История цен:</span>
          <span style="color: ${priceHistory.trend === 'down' ? 'green' : 'red'};">
            ${priceHistory.trend === 'down' ? '↓' : '↑'} ${Math.abs(priceHistory.change)}%
          </span>
        </div>
        <div style="display: flex; justify-content: space-between;">
          <span>📊 Рыночная цена:</span>
          <span>${FunPayUtils.formatPrice(priceHistory.average)}</span>
        </div>
      `;

      item.appendChild(enhancement);
    }

    getPriceHistory(item) {
      // Здесь должна быть реальная логика получения истории цен
      return {
        trend: Math.random() > 0.5 ? 'up' : 'down',
        change: Math.floor(Math.random() * 20),
        average: Math.random() * 1000
      };
    }

    modifyExistingElements() {
      // Улучшение кнопок
      this.enhanceButtons();

      // Улучшение форм
      this.enhanceForms();

      // Добавление подсказок
      this.addTooltips();
    }

    enhanceButtons() {
      document.querySelectorAll('button, .btn, input[type="submit"]').forEach(btn => {
        if (btn.hasAttribute('data-fp-enhanced')) return;
        btn.setAttribute('data-fp-enhanced', 'true');

        btn.style.transition = 'all 0.3s ease';
        btn.addEventListener('mouseover', () => {
          btn.style.transform = 'translateY(-2px)';
          btn.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
        });
        btn.addEventListener('mouseout', () => {
          btn.style.transform = 'translateY(0)';
          btn.style.boxShadow = '';
        });
      });
    }

    enhanceForms() {
      document.querySelectorAll('input, textarea, select').forEach(field => {
        if (field.hasAttribute('data-fp-enhanced')) return;
        field.setAttribute('data-fp-enhanced', 'true');

        // Автосохранение для textarea
        if (field.tagName === 'TEXTAREA') {
          field.addEventListener('input', FunPayUtils.debounce(async (e) => {
            await FunPayStorage.cache.set(`form_${field.name}`, e.target.value);
          }, 1000));

          // Восстановление сохраненного значения
          FunPayStorage.cache.get(`form_${field.name}`).then(value => {
            if (value && !field.value) {
              field.value = value;
            }
          });
        }
      });
    }

    addTooltips() {
      // Добавление подсказок к элементам
      document.querySelectorAll('[data-tooltip]').forEach(el => {
        el.addEventListener('mouseover', (e) => {
          this.showTooltip(e.target, e.target.getAttribute('data-tooltip'));
        });
        el.addEventListener('mouseout', () => {
          this.hideTooltip();
        });
      });
    }

    showTooltip(element, text) {
      const tooltip = document.createElement('div');
      tooltip.id = 'fp-tooltip';
      tooltip.textContent = text;
      tooltip.style.cssText = `
        position: fixed;
        background: #333;
        color: white;
        padding: 8px 12px;
        border-radius: 5px;
        font-size: 13px;
        z-index: 10000;
        pointer-events: none;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
      `;

      document.body.appendChild(tooltip);

      const rect = element.getBoundingClientRect();
      tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
      tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
    }

    hideTooltip() {
      const tooltip = document.getElementById('fp-tooltip');
      if (tooltip) tooltip.remove();
    }

    addUtilityFeatures() {
      // Копирование текста по клику
      this.addCopyOnClick();

      // Быстрый переход наверх
      this.addScrollToTop();

      // Кнопка экспорта данных
      this.addExportButton();
    }

    addCopyOnClick() {
      document.addEventListener('dblclick', (e) => {
        const text = window.getSelection().toString();
        if (text) {
          FunPayUtils.copyToClipboard(text);
          notificationManager?.notify('Скопировано', 'Текст скопирован в буфер обмена', 'success');
        }
      });
    }

    addScrollToTop() {
      const btn = document.createElement('button');
      btn.id = 'fp-scroll-top';
      btn.innerHTML = '⬆';
      btn.style.cssText = `
        position: fixed;
        bottom: 80px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        font-size: 24px;
        cursor: pointer;
        z-index: 9997;
        opacity: 0;
        transition: opacity 0.3s;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
      `;

      btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });

      document.body.appendChild(btn);

      window.addEventListener('scroll', () => {
        btn.style.opacity = window.scrollY > 300 ? '1' : '0';
      });
    }

    addExportButton() {
      // Кнопка экспорта будет добавлена в дашборд
    }
  }

  // Инициализация
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      new PageInjector();
    });
  } else {
    new PageInjector();
  }

})();
