// Content Script - работает только на Funpay.com
(function() {
  'use strict';
  
  // Проверка, что мы на правильном домене
  if (!window.location.hostname.includes('funpay.com')) {
    return;
  }

  // Инициализация расширения
  let extensionInitialized = false;
  let authState = { authenticated: false };
  
  // Загрузка состояния аутентификации
  chrome.runtime.sendMessage({ action: 'checkAuth' }, (response) => {
    if (response && response.authenticated) {
      authState.authenticated = true;
      initializeExtension();
    } else {
      showAuthPrompt();
    }
  });

  function initializeExtension() {
    if (extensionInitialized) return;
    extensionInitialized = true;
    
    // Ждем загрузки DOM
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initFeatures);
    } else {
      initFeatures();
    }
  }

  function showAuthPrompt() {
    const authModal = document.createElement('div');
    authModal.id = 'funpay-pro-auth-modal';
    authModal.innerHTML = `
      <div class="funpay-pro-modal-overlay">
        <div class="funpay-pro-modal-content">
          <h2>FunPay Pro Extension</h2>
          <p>Введите ключ доступа:</p>
          <input type="text" id="funpay-pro-auth-key" placeholder="AUTH-xxxx-xxxx-xxxx" />
          <div class="funpay-pro-modal-buttons">
            <button id="funpay-pro-auth-submit">Войти</button>
            <button id="funpay-pro-auth-cancel">Отмена</button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(authModal);
    
    document.getElementById('funpay-pro-auth-submit').addEventListener('click', () => {
      const key = document.getElementById('funpay-pro-auth-key').value;
      chrome.runtime.sendMessage({ action: 'authenticate', key }, (response) => {
        if (response && response.success) {
          authState.authenticated = true;
          authModal.remove();
          initializeExtension();
        } else {
          alert('Неверный ключ доступа!');
        }
      });
    });
    
    document.getElementById('funpay-pro-auth-cancel').addEventListener('click', () => {
      authModal.remove();
    });
  }

  // Загрузка модулей
  let analyticsManager, autoRaiseManager, multiAccountManager;
  
  async function loadModules() {
    // Загрузка скриптов модулей
    const scripts = [
      chrome.runtime.getURL('utils/analytics.js'),
      chrome.runtime.getURL('utils/autoRaise.js'),
      chrome.runtime.getURL('utils/multiAccount.js')
    ];
    
    for (const src of scripts) {
      const script = document.createElement('script');
      script.src = src;
      script.type = 'text/javascript';
      document.head.appendChild(script);
      await new Promise(resolve => {
        script.onload = resolve;
        script.onerror = resolve;
      });
    }
    
    // Инициализация менеджеров
    if (typeof AnalyticsManager !== 'undefined') {
      analyticsManager = new AnalyticsManager();
      await analyticsManager.init();
    }
    
    if (typeof AutoRaiseManager !== 'undefined') {
      autoRaiseManager = new AutoRaiseManager();
      await autoRaiseManager.init();
    }
    
    if (typeof MultiAccountManager !== 'undefined') {
      multiAccountManager = new MultiAccountManager();
      await multiAccountManager.init();
    }
  }

  // Получение настроек из storage
  async function getSettings() {
    return new Promise((resolve) => {
      chrome.storage.local.get(['settings'], (result) => {
        resolve(result.settings || {});
      });
    });
  }

  // Сохранение настроек
  async function saveSettings(settings) {
    return new Promise((resolve) => {
      chrome.storage.local.set({ settings }, resolve);
    });
  }

  // Кастомизация интерфейса
  async function initCustomization() {
    const settings = await getSettings();
    
    if (settings.theme) {
      applyTheme(settings.theme);
    }
    
    if (settings.cursor) {
      applyCursor(settings.cursor);
    }
    
    if (settings.animations) {
      applyAnimations(settings.animations);
    }
  }

  function applyTheme(themeConfig) {
    const styleId = 'funpay-pro-theme';
    let style = document.getElementById(styleId);
    if (!style) {
      style = document.createElement('style');
      style.id = styleId;
      document.head.appendChild(style);
    }
    
    style.textContent = `
      :root {
        --fp-primary: ${themeConfig.primaryColor || '#007bff'};
        --fp-secondary: ${themeConfig.secondaryColor || '#6c757d'};
        --fp-background: ${themeConfig.backgroundColor || '#ffffff'};
        --fp-text: ${themeConfig.textColor || '#212529'};
      }
      
      body {
        background-color: var(--fp-background) !important;
        color: var(--fp-text) !important;
      }
    `;
  }

  function applyCursor(cursorUrl) {
    document.body.style.cursor = `url(${cursorUrl}), auto`;
  }

  function applyAnimations(enabled) {
    if (enabled) {
      const style = document.createElement('style');
      style.textContent = `
        .lot-card, .game-card {
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .lot-card:hover, .game-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
      `;
      document.head.appendChild(style);
    }
  }

  // Автоподнятие лотов
  async function initAutoRaise() {
    if (autoRaiseManager) {
      await autoRaiseManager.init();
    }
  }

  function raiseLots() {
    if (autoRaiseManager) {
      autoRaiseManager.raiseLots();
    }
  }

  // Аналитика
  function initAnalytics() {
    // Сбор данных о продажах
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === 'collectAnalytics') {
        if (analyticsManager) {
          analyticsManager.trackSales();
          const stats = analyticsManager.getStats();
          sendResponse({ success: true, stats });
        }
      }
      
      if (request.action === 'getAnalytics') {
        if (analyticsManager) {
          const stats = analyticsManager.getStats();
          sendResponse({ success: true, stats });
        }
      }
    });
  }

  // Шаблоны сообщений и автоответы
  async function initMessages() {
    const settings = await getSettings();
    if (settings.autoMessages && settings.autoMessages.enabled) {
      setupAutoMessages(settings.autoMessages);
    }
  }

  function setupAutoMessages(config) {
    // Наблюдение за новыми сообщениями
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1 && node.classList.contains('message')) {
            handleNewMessage(node, config);
          }
        });
      });
    });
    
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
      observer.observe(chatContainer, { childList: true });
    }
  }

  function handleNewMessage(messageElement, config) {
    // Логика автоответа
    const messageText = messageElement.textContent.toLowerCase();
    
    config.templates.forEach(template => {
      if (messageText.includes(template.trigger)) {
        sendAutoReply(template.response);
      }
    });
  }

  function sendAutoReply(text) {
    const input = document.querySelector('.message-input');
    const sendButton = document.querySelector('.send-button');
    
    if (input && sendButton) {
      input.value = text;
      sendButton.click();
    }
  }

  // Мультиаккаунт
  async function initMultiAccount() {
    // Управление несколькими аккаунтами
  }

  // Быстрая торговля
  async function initFastTrade() {
    const settings = await getSettings();
    if (settings.fastTrade && settings.fastTrade.enabled) {
      addFastTradeButtons();
    }
  }

  function addFastTradeButtons() {
    // Добавление кнопок быстрой торговли
  }

  // Панель управления
  function createControlPanel() {
    const panel = document.createElement('div');
    panel.id = 'funpay-pro-panel';
    panel.innerHTML = `
      <div class="funpay-pro-toggle"></div>
      <div class="funpay-pro-menu">
        <button class="fp-btn" data-section="settings">⚙️ Настройки</button>
        <button class="fp-btn" data-section="analytics">📊 Аналитика</button>
        <button class="fp-btn" data-section="messages">💬 Сообщения</button>
        <button class="fp-btn" data-section="automation">🤖 Автоматизация</button>
      </div>
    `;
    document.body.appendChild(panel);
    
    // Переключение меню
    const toggle = panel.querySelector('.funpay-pro-toggle');
    toggle.addEventListener('click', () => {
      panel.classList.toggle('active');
    });
    
    // Открытие popup при клике на настройки
    panel.querySelectorAll('.fp-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        chrome.runtime.sendMessage({ action: 'openPopup' });
      });
    });
  }

  // Обработка сообщений от background
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'raiseLots') {
      raiseLots();
      sendResponse({ success: true });
    }
    
    if (request.action === 'settingsUpdated') {
      const settings = request.settings;
      
      // Обновление кастомизации
      if (settings.theme || settings.primaryColor) {
        initCustomization();
      }
      
      // Обновление автоподнятия
      if (autoRaiseManager && settings.autoRaise) {
        autoRaiseManager.updateSettings(settings.autoRaise);
      }
      
      // Обновление автосообщений
      if (settings.autoMessages) {
        initMessages();
      }
      
      sendResponse({ success: true });
    }
  });

})();
