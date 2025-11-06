// Background Service Worker
importScripts('utils/auth.js');

const authManager = new AuthManager();

// Проверка аутентификации при запуске
chrome.runtime.onInstalled.addListener(async () => {
  await authManager.loadAuthState();
});

// Обработка сообщений от content script и popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'checkAuth') {
    authManager.loadAuthState().then(() => {
      sendResponse({ authenticated: authManager.isAuthenticated() });
    });
    return true;
  }
  
  if (request.action === 'authenticate') {
    authManager.authenticate(request.key).then((success) => {
      sendResponse({ success });
    });
    return true;
  }
  
  if (request.action === 'logout') {
    authManager.logout().then(() => {
      sendResponse({ success: true });
    });
    return true;
  }
  
  if (request.action === 'autoRaiseLots') {
    handleAutoRaiseLots(request.config);
    sendResponse({ success: true });
  }
  
  if (request.action === 'scheduleAutoRaise') {
    scheduleAutoRaise(request.config);
    sendResponse({ success: true });
  }
  
  if (request.action === 'openPopup') {
    chrome.action.openPopup();
    sendResponse({ success: true });
  }
  
  if (request.action === 'notification') {
    showNotification(request.title, request.message);
    sendResponse({ success: true });
  }
  
  if (request.action === 'addAccount') {
    // Делегируем в content script или обрабатываем здесь
    chrome.storage.local.get(['multiAccounts'], (result) => {
      const accounts = result.multiAccounts || [];
      const account = {
        id: `acc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: request.accountData.name,
        authKey: request.accountData.authKey,
        settings: {},
        createdAt: new Date().toISOString()
      };
      accounts.push(account);
      chrome.storage.local.set({ multiAccounts: accounts }, () => {
        sendResponse({ success: true });
      });
    });
    return true;
  }
  
  if (request.action === 'switchAccount') {
    chrome.storage.local.get(['multiAccounts'], (result) => {
      const accounts = result.multiAccounts || [];
      const account = accounts.find(acc => acc.id === request.accountId);
      if (account) {
        chrome.storage.local.set({ 
          currentAccountId: account.id,
          settings: account.settings || {}
        }, () => {
          sendResponse({ success: true });
        });
      } else {
        sendResponse({ success: false });
      }
    });
    return true;
  }
  
  if (request.action === 'getAccounts') {
    chrome.storage.local.get(['multiAccounts'], (result) => {
      sendResponse({ accounts: result.multiAccounts || [] });
    });
    return true;
  }
  
  return true;
});

// Автоподнятие лотов
function handleAutoRaiseLots(config) {
  chrome.tabs.query({ url: 'https://funpay.com/*' }, (tabs) => {
    tabs.forEach(tab => {
      chrome.tabs.sendMessage(tab.id, {
        action: 'raiseLots',
        config: config
      });
    });
  });
}

// Планирование автоподнятия
function scheduleAutoRaise(config) {
  const interval = config.interval || 3600000; // По умолчанию 1 час
  
  chrome.alarms.create('autoRaiseLots', {
    delayInMinutes: interval / 60000,
    periodInMinutes: interval / 60000
  });
  
  chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'autoRaiseLots') {
      handleAutoRaiseLots(config);
    }
  });
}

// Уведомления
chrome.notifications.onClicked.addListener((notificationId) => {
  chrome.tabs.create({ url: 'https://funpay.com/' });
});

function showNotification(title, message) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icons/icon48.png',
    title: title,
    message: message
  });
}

// Экспорт функции уведомлений
self.showNotification = showNotification;
