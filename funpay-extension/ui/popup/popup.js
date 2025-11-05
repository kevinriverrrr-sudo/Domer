/**
 * FunPay Ultimate Pro - Popup Script
 */

document.addEventListener('DOMContentLoaded', async () => {
  // Загрузка статистики
  await loadStats();

  // Загрузка состояний модулей
  await loadModuleStates();

  // Обработчики переключателей
  setupToggleHandlers();

  // Обработчики кнопок
  setupButtonHandlers();

  // Обновление статистики каждые 5 секунд
  setInterval(loadStats, 5000);
});

async function loadStats() {
  try {
    const stats = await chrome.storage.local.get('stats');
    const data = stats.stats || {};

    document.getElementById('stat-orders').textContent = data.totalOrders || 0;
    document.getElementById('stat-sales').textContent = data.totalSales || 0;
    document.getElementById('stat-responses').textContent = data.autoResponses || 0;
    document.getElementById('stat-boosts').textContent = data.totalBoosts || 0;
  } catch (error) {
    console.error('Error loading stats:', error);
  }
}

async function loadModuleStates() {
  try {
    const settings = await chrome.storage.local.get('settings');
    const config = settings.settings || {};

    // Автоответчик
    const autoResponderToggle = document.getElementById('toggle-auto-responder');
    if (autoResponderToggle) {
      autoResponderToggle.checked = config.autoResponder?.enabled || false;
    }

    // Автозакупка
    const autoPurchaseToggle = document.getElementById('toggle-auto-purchase');
    if (autoPurchaseToggle) {
      autoPurchaseToggle.checked = config.autoPurchase?.enabled || false;
    }

    // Поднятие лотов
    const lotBoosterToggle = document.getElementById('toggle-lot-booster');
    if (lotBoosterToggle) {
      lotBoosterToggle.checked = config.lotBooster?.enabled || false;
    }

    // Трекер конкурентов
    const competitorToggle = document.getElementById('toggle-competitor');
    if (competitorToggle) {
      competitorToggle.checked = config.competitorTracker?.enabled || false;
    }

    // Безопасность
    const securityToggle = document.getElementById('toggle-security');
    if (securityToggle) {
      securityToggle.checked = config.security?.scamDetection !== false;
    }
  } catch (error) {
    console.error('Error loading module states:', error);
  }
}

function setupToggleHandlers() {
  // Автоответчик
  document.getElementById('toggle-auto-responder')?.addEventListener('change', async (e) => {
    await updateModuleSetting('autoResponder', 'enabled', e.target.checked);
    showNotification(e.target.checked ? 'Автоответчик включен' : 'Автоответчик выключен');
  });

  // Автозакупка
  document.getElementById('toggle-auto-purchase')?.addEventListener('change', async (e) => {
    await updateModuleSetting('autoPurchase', 'enabled', e.target.checked);
    showNotification(e.target.checked ? 'Автозакупка включена' : 'Автозакупка выключена');
  });

  // Поднятие лотов
  document.getElementById('toggle-lot-booster')?.addEventListener('change', async (e) => {
    await updateModuleSetting('lotBooster', 'enabled', e.target.checked);
    showNotification(e.target.checked ? 'Поднятие лотов включено' : 'Поднятие лотов выключено');
  });

  // Трекер конкурентов
  document.getElementById('toggle-competitor')?.addEventListener('change', async (e) => {
    await updateModuleSetting('competitorTracker', 'enabled', e.target.checked);
    showNotification(e.target.checked ? 'Трекер конкурентов включен' : 'Трекер конкурентов выключен');
  });

  // Безопасность
  document.getElementById('toggle-security')?.addEventListener('change', async (e) => {
    await updateModuleSetting('security', 'scamDetection', e.target.checked);
    showNotification(e.target.checked ? 'Защита включена' : 'Защита выключена');
  });
}

async function updateModuleSetting(module, key, value) {
  try {
    const settings = await chrome.storage.local.get('settings');
    const config = settings.settings || {};
    
    if (!config[module]) {
      config[module] = {};
    }
    
    config[module][key] = value;
    
    await chrome.storage.local.set({ settings: config });

    // Отправка сообщения активным вкладкам
    const tabs = await chrome.tabs.query({ url: '*://funpay.com/*' });
    tabs.forEach(tab => {
      chrome.tabs.sendMessage(tab.id, {
        action: 'updateSettings',
        settings: config
      });
    });
  } catch (error) {
    console.error('Error updating setting:', error);
  }
}

function setupButtonHandlers() {
  // Дашборд
  document.getElementById('btn-dashboard')?.addEventListener('click', () => {
    chrome.tabs.create({ url: 'ui/dashboard/dashboard.html' });
  });

  // Аналитика
  document.getElementById('btn-analytics')?.addEventListener('click', () => {
    chrome.tabs.create({ url: 'ui/dashboard/analytics.html' });
  });

  // Настройки
  document.getElementById('btn-settings')?.addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
  });

  // Экспорт
  document.getElementById('btn-export')?.addEventListener('click', async () => {
    const allData = await chrome.storage.local.get(null);
    const dataStr = JSON.stringify(allData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `funpay-pro-export-${Date.now()}.json`;
    a.click();
    
    URL.revokeObjectURL(url);
    showNotification('Данные экспортированы');
  });

  // Помощь
  document.getElementById('link-help')?.addEventListener('click', (e) => {
    e.preventDefault();
    chrome.tabs.create({ url: 'ui/options/help.html' });
  });

  // Документация
  document.getElementById('link-docs')?.addEventListener('click', (e) => {
    e.preventDefault();
    chrome.tabs.create({ url: 'ui/options/docs.html' });
  });
}

function showNotification(message) {
  // Создание временного уведомления
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    background: #2ecc71;
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
    z-index: 10000;
    animation: slideDown 0.3s ease-out;
  `;
  notification.textContent = message;
  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = 'slideUp 0.3s ease-in';
    setTimeout(() => notification.remove(), 300);
  }, 2000);
}
