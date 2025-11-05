// Content script для работы на странице Funpay.com
(function() {
  'use strict';

  let autoBuyEnabled = false;
  let autoSellEnabled = false;
  let autoRefreshEnabled = false;
  let refreshInterval = 10;
  let refreshTimer = null;

  // Инициализация
  async function init() {
    console.log('Funpay Trading Helper активирован');
    
    // Загружаем настройки
    await loadSettings();
    
    // Создаем UI элементы
    createUI();
    
    // Начинаем мониторинг страницы
    startMonitoring();
    
    // Устанавливаем интервал обновления если включен
    if (autoRefreshEnabled) {
      startAutoRefresh();
    }
  }

  // Загрузка настроек из storage
  async function loadSettings() {
    const result = await chrome.storage.sync.get([
      'autoBuy',
      'autoSell',
      'autoRefresh',
      'refreshInterval'
    ]);
    
    autoBuyEnabled = result.autoBuy || false;
    autoSellEnabled = result.autoSell || false;
    autoRefreshEnabled = result.autoRefresh || false;
    refreshInterval = result.refreshInterval || 10;
  }

  // Создание UI элементов на странице
  function createUI() {
    // Проверяем, не созданы ли уже элементы
    if (document.getElementById('funpay-helper-badge')) {
      return;
    }

    const badge = document.createElement('div');
    badge.id = 'funpay-helper-badge';
    badge.innerHTML = `
      <div class="funpay-helper-status">
        <span class="funpay-helper-icon">🤖</span>
        <span class="funpay-helper-text">Trading Helper активен</span>
      </div>
    `;
    document.body.appendChild(badge);

    // Показываем уведомление при загрузке
    showNotification('Расширение Funpay Trading Helper активировано', 'success');
  }

  // Мониторинг страницы на наличие торговых элементов
  function startMonitoring() {
    // Ищем элементы для покупки/продажи
    observePage();
    
    // Проверяем текущую страницу
    checkForTradingElements();
  }

  // Проверка наличия торговых элементов на странице
  function checkForTradingElements() {
    // Пример селекторов для Funpay (нужно адаптировать под реальную структуру сайта)
    const buyButtons = document.querySelectorAll('[class*="buy"], [class*="purchase"], button:contains("Купить")');
    const sellButtons = document.querySelectorAll('[class*="sell"], button:contains("Продать")');
    
    if (autoBuyEnabled && buyButtons.length > 0) {
      console.log('Найдены кнопки покупки:', buyButtons.length);
      // Здесь можно добавить логику автопокупки
    }
    
    if (autoSellEnabled && sellButtons.length > 0) {
      console.log('Найдены кнопки продажи:', sellButtons.length);
      // Здесь можно добавить логику автопродажи
    }
  }

  // Наблюдение за изменениями DOM
  function observePage() {
    const observer = new MutationObserver((mutations) => {
      checkForTradingElements();
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  // Автообновление страницы
  function startAutoRefresh() {
    if (refreshTimer) {
      clearInterval(refreshTimer);
    }
    
    refreshTimer = setInterval(() => {
      if (autoRefreshEnabled) {
        console.log('Автообновление страницы...');
        // Можно обновить только определенные элементы вместо полной перезагрузки
        location.reload();
      }
    }, refreshInterval * 1000);
  }

  // Показ уведомления
  function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `funpay-helper-notification funpay-helper-notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
      notification.classList.add('show');
    }, 10);

    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }

  // Обновление статистики сделок
  async function updateDealStats() {
    const result = await chrome.storage.local.get(['dealsToday', 'totalDeals']);
    const today = new Date().toDateString();
    const lastDealDate = result.lastDealDate;
    
    let dealsToday = result.dealsToday || 0;
    let totalDeals = result.totalDeals || 0;
    
    // Сбрасываем счетчик дня если это новый день
    if (lastDealDate !== today) {
      dealsToday = 0;
    }
    
    dealsToday++;
    totalDeals++;
    
    await chrome.storage.local.set({
      dealsToday: dealsToday,
      totalDeals: totalDeals,
      lastDealDate: today
    });
  }

  // Обработка сообщений от popup или background
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'toggleAutoBuy') {
      autoBuyEnabled = request.enabled;
      showNotification(
        autoBuyEnabled ? 'Автопокупка включена' : 'Автопокупка выключена',
        autoBuyEnabled ? 'success' : 'info'
      );
      sendResponse({ success: true });
    }
    
    if (request.action === 'toggleAutoSell') {
      autoSellEnabled = request.enabled;
      showNotification(
        autoSellEnabled ? 'Автопродажа включена' : 'Автопродажа выключена',
        autoSellEnabled ? 'success' : 'info'
      );
      sendResponse({ success: true });
    }
    
    if (request.action === 'updateSettings') {
      autoRefreshEnabled = request.settings.autoRefresh || false;
      refreshInterval = request.settings.refreshInterval || 10;
      
      if (autoRefreshEnabled) {
        startAutoRefresh();
      } else {
        if (refreshTimer) {
          clearInterval(refreshTimer);
          refreshTimer = null;
        }
      }
      
      sendResponse({ success: true });
    }
    
    return true;
  });

  // Инициализация при загрузке
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
