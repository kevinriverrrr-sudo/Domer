/**
 * FunPay Ultimate Pro - Background Service Worker
 * Фоновый процесс расширения
 */

// Установка расширения
chrome.runtime.onInstalled.addListener(async (details) => {
  console.log('FunPay Ultimate Pro установлено:', details.reason);

  if (details.reason === 'install') {
    // Первая установка
    await initializeExtension();
    // Открытие страницы приветствия
    chrome.tabs.create({ url: 'ui/options/welcome.html' });
  } else if (details.reason === 'update') {
    // Обновление
    console.log('Расширение обновлено до версии', chrome.runtime.getManifest().version);
  }
});

// Инициализация настроек по умолчанию
async function initializeExtension() {
  const defaultSettings = {
    version: chrome.runtime.getManifest().version,
    installedAt: Date.now(),
    
    // Автоответчик
    autoResponder: {
      enabled: false,
      delay: { min: 2000, max: 5000 },
      templates: getDefaultTemplates(),
      workingHours: { enabled: false, start: '09:00', end: '21:00' }
    },

    // Автозакупка
    autoPurchase: {
      enabled: false,
      maxPrice: 1000,
      filters: [],
      notifications: true
    },

    // Поднятие лотов
    lotBooster: {
      enabled: false,
      interval: 3600000,
      randomDelay: true,
      lots: []
    },

    // Аналитика конкурентов
    competitorTracker: {
      enabled: true,
      trackPrices: true,
      trackLots: true,
      competitors: []
    },

    // Автожалобы
    autoComplaints: {
      enabled: false,
      autoFill: true,
      reasons: []
    },

    // Уведомления
    notifications: {
      enabled: true,
      sound: true,
      desktop: true,
      orders: true,
      messages: true,
      priceChanges: true
    },

    // Безопасность
    security: {
      scamDetection: true,
      autoBlock: false
    },

    // Интерфейс
    ui: {
      theme: 'auto',
      language: 'ru',
      compactMode: false,
      animations: true
    }
  };

  await chrome.storage.local.set({ settings: defaultSettings });
  console.log('Настройки по умолчанию установлены');
}

function getDefaultTemplates() {
  return [
    {
      id: 'welcome',
      name: 'Приветствие',
      keyword: 'привет',
      text: 'Здравствуйте! Чем могу помочь?',
      trigger: 'contains',
      enabled: true
    },
    {
      id: 'available',
      name: 'Наличие',
      keyword: 'есть',
      text: 'Да, товар в наличии. Готов к продаже.',
      trigger: 'contains',
      enabled: true
    },
    {
      id: 'delivery',
      name: 'Доставка',
      keyword: 'доставка',
      text: 'Доставка осуществляется сразу после оплаты.',
      trigger: 'contains',
      enabled: true
    }
  ];
}

// Обработка сообщений
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Background получил сообщение:', message);

  switch (message.action) {
    case 'openDashboard':
      chrome.tabs.create({ url: 'ui/dashboard/dashboard.html' });
      break;

    case 'openSettings':
      chrome.runtime.openOptionsPage();
      break;

    case 'openAnalytics':
      chrome.tabs.create({ url: 'ui/dashboard/analytics.html' });
      break;

    case 'sync':
      handleSync(message.data);
      break;

    case 'notification':
      showNotification(message.title, message.message, message.type);
      break;

    case 'getStats':
      getStats().then(sendResponse);
      return true;

    case 'exportData':
      exportAllData().then(sendResponse);
      return true;
  }
});

// Синхронизация данных
async function handleSync(data) {
  await chrome.storage.local.set({
    lastSync: Date.now(),
    lastUrl: data.url,
    lastPageType: data.pageType
  });
}

// Показ уведомлений
function showNotification(title, message, type = 'info') {
  const icons = {
    info: 'icons/icon48.png',
    success: 'icons/icon48.png',
    warning: 'icons/icon48.png',
    error: 'icons/icon48.png'
  };

  chrome.notifications.create({
    type: 'basic',
    iconUrl: icons[type],
    title,
    message,
    priority: type === 'critical' ? 2 : 1
  });
}

// Получение статистики
async function getStats() {
  const data = await chrome.storage.local.get(['stats', 'salesData', 'history']);
  
  return {
    stats: data.stats || {},
    salesCount: data.salesData?.length || 0,
    historyCount: data.history?.length || 0,
    timestamp: Date.now()
  };
}

// Экспорт всех данных
async function exportAllData() {
  const allData = await chrome.storage.local.get(null);
  
  return {
    version: chrome.runtime.getManifest().version,
    exportDate: new Date().toISOString(),
    data: allData
  };
}

// Периодические задачи
chrome.alarms.create('hourlyTasks', { periodInMinutes: 60 });
chrome.alarms.create('dailyTasks', { periodInMinutes: 1440 });

chrome.alarms.onAlarm.addListener((alarm) => {
  console.log('Alarm triggered:', alarm.name);

  switch (alarm.name) {
    case 'hourlyTasks':
      performHourlyTasks();
      break;
    case 'dailyTasks':
      performDailyTasks();
      break;
  }
});

async function performHourlyTasks() {
  console.log('Выполнение часовых задач...');
  
  // Очистка старых данных кэша
  const cache = await chrome.storage.local.get('cache');
  if (cache.cache) {
    const now = Date.now();
    const cleaned = {};
    Object.entries(cache.cache).forEach(([key, value]) => {
      if (now - value.timestamp < 3600000) { // Храним 1 час
        cleaned[key] = value;
      }
    });
    await chrome.storage.local.set({ cache: cleaned });
  }

  // Обновление статистики
  await updateStatistics();
}

async function performDailyTasks() {
  console.log('Выполнение ежедневных задач...');
  
  // Архивация старых данных
  await archiveOldData();
  
  // Создание резервной копии
  await createBackup();
  
  // Отправка отчета
  await generateDailyReport();
}

async function updateStatistics() {
  const stats = await chrome.storage.local.get('stats');
  // Обновление статистики
}

async function archiveOldData() {
  // Архивация данных старше 30 дней
  const history = await chrome.storage.local.get('history');
  if (history.history) {
    const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
    const recent = history.history.filter(h => h.timestamp > thirtyDaysAgo);
    await chrome.storage.local.set({ history: recent });
  }
}

async function createBackup() {
  const allData = await chrome.storage.local.get(null);
  const backup = {
    timestamp: Date.now(),
    data: allData
  };
  
  await chrome.storage.local.set({ lastBackup: backup });
  console.log('Резервная копия создана');
}

async function generateDailyReport() {
  const stats = await getStats();
  console.log('Ежедневный отчет:', stats);
  
  // Отправка уведомления с отчетом
  showNotification(
    'Ежедневный отчет FunPay Pro',
    `Продаж: ${stats.salesCount}, Событий: ${stats.historyCount}`,
    'info'
  );
}

// Обработка контекстного меню
chrome.contextMenus.create({
  id: 'funpay-pro-menu',
  title: 'FunPay Pro',
  contexts: ['all']
});

chrome.contextMenus.create({
  id: 'copy-to-clipboard',
  parentId: 'funpay-pro-menu',
  title: 'Копировать выделенное',
  contexts: ['selection']
});

chrome.contextMenus.create({
  id: 'add-to-monitor',
  parentId: 'funpay-pro-menu',
  title: 'Добавить в мониторинг',
  contexts: ['link']
});

chrome.contextMenus.create({
  id: 'quick-complaint',
  parentId: 'funpay-pro-menu',
  title: 'Быстрая жалоба',
  contexts: ['link', 'page']
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  console.log('Context menu clicked:', info.menuItemId);

  switch (info.menuItemId) {
    case 'copy-to-clipboard':
      chrome.tabs.sendMessage(tab.id, {
        action: 'copyText',
        text: info.selectionText
      });
      break;

    case 'add-to-monitor':
      chrome.tabs.sendMessage(tab.id, {
        action: 'addToMonitor',
        url: info.linkUrl
      });
      break;

    case 'quick-complaint':
      chrome.tabs.sendMessage(tab.id, {
        action: 'quickComplaint',
        url: info.pageUrl || info.linkUrl
      });
      break;
  }
});

// Обработка команд клавиатуры
chrome.commands.onCommand.addListener((command) => {
  console.log('Command received:', command);

  switch (command) {
    case 'toggle-auto-responder':
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, {
          action: 'toggleModule',
          module: 'autoResponder'
        });
      });
      break;

    case 'open-dashboard':
      chrome.tabs.create({ url: 'ui/dashboard/dashboard.html' });
      break;

    case 'quick-response':
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, {
          action: 'openQuickResponse'
        });
      });
      break;
  }
});

console.log('FunPay Ultimate Pro Background Service Worker загружен');
