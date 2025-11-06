// Background service worker для расширения Funpay Trading Helper

// Обработка установки расширения
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('Funpay Trading Helper установлен');
    
    // Устанавливаем значения по умолчанию
    chrome.storage.sync.set({
      notifications: true,
      autoRefresh: false,
      refreshInterval: 10,
      autoBuy: false,
      autoSell: false
    });
    
    chrome.storage.local.set({
      dealsToday: 0,
      totalDeals: 0
    });
  }
});

// Обработка обновления расширения
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'update') {
    console.log('Funpay Trading Helper обновлен');
  }
});

// Обработка нажатия на иконку расширения
chrome.action.onClicked.addListener((tab) => {
  // Проверяем, что мы на странице Funpay
  if (tab.url && tab.url.includes('funpay.com')) {
    // Popup откроется автоматически благодаря action.default_popup в manifest
    console.log('Расширение активировано на Funpay');
  } else {
    // Можно открыть страницу Funpay или показать уведомление
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'Funpay Trading Helper',
      message: 'Откройте сайт Funpay.com для использования расширения'
    });
  }
});

// Обработка сообщений от content script или popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'dealCompleted') {
    // Обновляем статистику при завершении сделки
    chrome.storage.local.get(['dealsToday', 'totalDeals'], (result) => {
      const today = new Date().toDateString();
      const lastDealDate = result.lastDealDate;
      
      let dealsToday = result.dealsToday || 0;
      let totalDeals = result.totalDeals || 0;
      
      if (lastDealDate !== today) {
        dealsToday = 0;
      }
      
      dealsToday++;
      totalDeals++;
      
      chrome.storage.local.set({
        dealsToday: dealsToday,
        totalDeals: totalDeals,
        lastDealDate: today
      });
    });
    
    sendResponse({ success: true });
  }
  
  return true;
});

// Проверка доступности сайта Funpay
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && tab.url.includes('funpay.com')) {
    console.log('Страница Funpay загружена');
  }
});
