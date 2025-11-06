/**
 * FunPay Ultimate Pro - Main Content Script
 * Главный скрипт для внедрения на страницы FunPay
 */

(function() {
  'use strict';

  // Проверка, что мы на FunPay
  if (!window.location.hostname.includes('funpay')) {
    return;
  }

  FunPayUtils.log('FunPay Ultimate Pro загружен');

  // Инициализация всех модулей
  class FunPayExtension {
    constructor() {
      this.modules = {};
      this.initialized = false;
      this.init();
    }

    async init() {
      if (this.initialized) return;

      FunPayUtils.log('Инициализация расширения...');

      // Загрузка настроек
      await this.loadSettings();

      // Инициализация модулей
      await this.initModules();

      // Добавление UI элементов
      this.injectUI();

      // Регистрация обработчиков
      this.registerEventHandlers();

      // Синхронизация с background
      this.syncWithBackground();

      this.initialized = true;
      FunPayUtils.log('Расширение инициализировано');

      // Уведомление
      if (notificationManager) {
        notificationManager.notify(
          'FunPay Pro активировано',
          'Все системы работают',
          'success'
        );
      }
    }

    async loadSettings() {
      const settings = await FunPayStorage.settings.getAll();
      this.settings = settings;
    }

    async initModules() {
      // Модули будут инициализированы автоматически при загрузке их скриптов
      this.modules = {
        autoResponder: typeof autoResponder !== 'undefined' ? autoResponder : null,
        priceManager: typeof priceManager !== 'undefined' ? priceManager : null,
        lotBooster: typeof lotBooster !== 'undefined' ? lotBooster : null,
        orderAutomation: typeof orderAutomation !== 'undefined' ? orderAutomation : null,
        autoPurchase: typeof autoPurchase !== 'undefined' ? autoPurchase : null,
        priceMonitor: typeof priceMonitor !== 'undefined' ? priceMonitor : null,
        competitorTracker: typeof competitorTracker !== 'undefined' ? competitorTracker : null,
        autoComplaints: typeof autoComplaints !== 'undefined' ? autoComplaints : null,
        salesAnalytics: typeof salesAnalytics !== 'undefined' ? salesAnalytics : null,
        scamDetector: typeof scamDetector !== 'undefined' ? scamDetector : null,
        notificationManager: typeof notificationManager !== 'undefined' ? notificationManager : null
      };

      FunPayUtils.log('Модули инициализированы:', Object.keys(this.modules));
    }

    injectUI() {
      // Добавление панели управления
      this.createControlPanel();

      // Добавление быстрых кнопок
      this.createQuickActions();

      // Добавление индикатора статуса
      this.createStatusIndicator();

      // Добавление кастомных стилей
      this.injectStyles();
    }

    createControlPanel() {
      const panel = document.createElement('div');
      panel.id = 'funpay-pro-panel';
      panel.style.cssText = `
        position: fixed;
        top: 50%;
        right: 0;
        transform: translateY(-50%);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px;
        border-radius: 10px 0 0 10px;
        box-shadow: -2px 0 10px rgba(0,0,0,0.3);
        z-index: 9999;
        transition: right 0.3s;
        min-width: 50px;
      `;

      panel.innerHTML = `
        <div style="text-align: center;">
          <div style="font-weight: bold; margin-bottom: 10px; font-size: 14px;">FP Pro</div>
          <button id="fp-toggle-auto-responder" class="fp-panel-btn" title="Автоответчик">📱</button>
          <button id="fp-toggle-auto-purchase" class="fp-panel-btn" title="Автозакупка">🛒</button>
          <button id="fp-open-dashboard" class="fp-panel-btn" title="Дашборд">📊</button>
          <button id="fp-open-settings" class="fp-panel-btn" title="Настройки">⚙️</button>
        </div>
      `;

      document.body.appendChild(panel);

      // Обработчики кнопок
      document.getElementById('fp-toggle-auto-responder')?.addEventListener('click', () => {
        if (this.modules.autoResponder) {
          if (this.modules.autoResponder.enabled) {
            this.modules.autoResponder.stop();
          } else {
            this.modules.autoResponder.start();
          }
        }
      });

      document.getElementById('fp-toggle-auto-purchase')?.addEventListener('click', () => {
        if (this.modules.autoPurchase) {
          if (this.modules.autoPurchase.enabled) {
            this.modules.autoPurchase.stop();
          } else {
            this.modules.autoPurchase.start();
          }
        }
      });

      document.getElementById('fp-open-dashboard')?.addEventListener('click', () => {
        chrome.runtime.sendMessage({ action: 'openDashboard' });
      });

      document.getElementById('fp-open-settings')?.addEventListener('click', () => {
        chrome.runtime.sendMessage({ action: 'openSettings' });
      });
    }

    createQuickActions() {
      // Добавление быстрых действий на элементы страницы
      domObserver.onElementAdded('.tc-item, .offer-list-item', (element) => {
        this.addQuickActionsToElement(element);
      });

      // Обработка существующих элементов
      document.querySelectorAll('.tc-item, .offer-list-item').forEach(element => {
        this.addQuickActionsToElement(element);
      });
    }

    addQuickActionsToElement(element) {
      if (element.querySelector('.fp-quick-actions')) return;

      const actions = document.createElement('div');
      actions.className = 'fp-quick-actions';
      actions.style.cssText = `
        position: absolute;
        top: 5px;
        left: 5px;
        display: flex;
        gap: 5px;
        z-index: 10;
      `;

      // Кнопка мониторинга цены
      const monitorBtn = this.createActionButton('👁️', 'Мониторить цену', () => {
        const itemId = element.getAttribute('data-id');
        const title = element.querySelector('.tc-title')?.textContent;
        const price = FunPayUtils.parsePrice(element.querySelector('.tc-price')?.textContent || '0');
        
        if (this.modules.priceMonitor) {
          this.modules.priceMonitor.addMonitoredItem({ id: itemId, title, currentPrice: price });
          notificationManager?.notify('Добавлено в мониторинг', title, 'success');
        }
      });

      // Кнопка добавления в избранное
      const favoriteBtn = this.createActionButton('⭐', 'В избранное', () => {
        // Логика добавления в избранное
      });

      actions.appendChild(monitorBtn);
      actions.appendChild(favoriteBtn);

      element.style.position = 'relative';
      element.appendChild(actions);
    }

    createActionButton(icon, title, onClick) {
      const btn = document.createElement('button');
      btn.textContent = icon;
      btn.title = title;
      btn.style.cssText = `
        background: rgba(255,255,255,0.9);
        border: none;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        cursor: pointer;
        font-size: 14px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: transform 0.2s;
      `;
      btn.onmouseover = () => btn.style.transform = 'scale(1.1)';
      btn.onmouseout = () => btn.style.transform = 'scale(1)';
      btn.onclick = (e) => {
        e.stopPropagation();
        onClick();
      };
      return btn;
    }

    createStatusIndicator() {
      const indicator = document.createElement('div');
      indicator.id = 'fp-status-indicator';
      indicator.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: white;
        padding: 10px 15px;
        border-radius: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 9998;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 13px;
      `;

      indicator.innerHTML = `
        <div style="width: 8px; height: 8px; border-radius: 50%; background: #2ecc71;"></div>
        <span>FunPay Pro активен</span>
      `;

      document.body.appendChild(indicator);

      // Обновление статуса каждые 5 секунд
      setInterval(() => this.updateStatus(indicator), 5000);
    }

    async updateStatus(indicator) {
      const stats = await FunPayStorage.stats.getAll();
      const activeModules = Object.values(this.modules).filter(m => m && m.enabled).length;
      
      indicator.querySelector('span').textContent = 
        `FP Pro | Модули: ${activeModules} | Всего действий: ${stats.totalActions || 0}`;
    }

    injectStyles() {
      const style = document.createElement('style');
      style.textContent = `
        .fp-panel-btn {
          display: block;
          width: 40px;
          height: 40px;
          margin: 5px 0;
          background: rgba(255,255,255,0.2);
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-size: 20px;
          transition: all 0.3s;
        }
        .fp-panel-btn:hover {
          background: rgba(255,255,255,0.3);
          transform: scale(1.1);
        }
        .fp-panel-btn:active {
          transform: scale(0.95);
        }
      `;
      document.head.appendChild(style);
    }

    registerEventHandlers() {
      // Обработка сообщений от background
      chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        this.handleMessage(message, sender, sendResponse);
        return true;
      });

      // Обработка горячих клавиш
      document.addEventListener('keydown', (e) => {
        this.handleKeyPress(e);
      });

      // Обработка видимости страницы
      document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
          FunPayUtils.log('Страница скрыта');
        } else {
          FunPayUtils.log('Страница видима');
          this.syncWithBackground();
        }
      });
    }

    handleMessage(message, sender, sendResponse) {
      FunPayUtils.log('Получено сообщение:', message);

      switch (message.action) {
        case 'getStatus':
          sendResponse({ 
            status: 'active',
            modules: Object.keys(this.modules),
            settings: this.settings
          });
          break;

        case 'toggleModule':
          const module = this.modules[message.module];
          if (module) {
            if (module.enabled) {
              module.stop();
            } else {
              module.start();
            }
            sendResponse({ success: true, enabled: module.enabled });
          }
          break;

        case 'updateSettings':
          this.settings = message.settings;
          sendResponse({ success: true });
          break;
      }
    }

    handleKeyPress(event) {
      // Ctrl+Shift+A - Переключение автоответчика
      if (event.ctrlKey && event.shiftKey && event.key === 'A') {
        event.preventDefault();
        if (this.modules.autoResponder) {
          this.modules.autoResponder.enabled 
            ? this.modules.autoResponder.stop() 
            : this.modules.autoResponder.start();
        }
      }

      // Ctrl+Shift+D - Открытие дашборда
      if (event.ctrlKey && event.shiftKey && event.key === 'D') {
        event.preventDefault();
        chrome.runtime.sendMessage({ action: 'openDashboard' });
      }
    }

    syncWithBackground() {
      chrome.runtime.sendMessage({
        action: 'sync',
        data: {
          url: window.location.href,
          pageType: FunPayUtils.getPageType(),
          timestamp: Date.now()
        }
      });
    }
  }

  // Инициализация при загрузке DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      new FunPayExtension();
    });
  } else {
    new FunPayExtension();
  }

})();
