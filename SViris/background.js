// Background service worker for SViris extension

let monitoringSettings = {
  scripts: true,
  network: true,
  cookies: true,
  downloads: true
};

let behaviorStats = {
  scripts: 0,
  requests: 0,
  warnings: 0
};

// Initialize settings
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({ 
    monitoring: monitoringSettings,
    behaviorStats: behaviorStats,
    activityLog: []
  });
  console.log('SViris extension installed');
});

// Load settings on startup
chrome.storage.local.get(['monitoring', 'behaviorStats'], (result) => {
  if (result.monitoring) monitoringSettings = result.monitoring;
  if (result.behaviorStats) behaviorStats = result.behaviorStats;
});

// Listen for messages from popup and content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'updateMonitoring':
      monitoringSettings = request.settings;
      break;
      
    case 'logActivity':
      logActivity(request.data);
      break;
      
    case 'incrementStat':
      incrementStat(request.stat);
      break;
      
    case 'checkUrl':
      checkUrlSafety(request.url).then(result => sendResponse(result));
      return true; // Keep channel open for async response
      
    case 'reportSuspicious':
      handleSuspiciousActivity(request.data);
      break;
  }
});

// Monitor web requests
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    if (!monitoringSettings.network) return;
    
    incrementStat('requests');
    
    // Check for suspicious patterns
    const url = details.url.toLowerCase();
    const suspiciousPatterns = [
      'malware',
      'phishing',
      'trojan',
      'keylogger',
      '.exe',
      '.scr',
      '.vbs',
      '.bat'
    ];
    
    const isSuspicious = suspiciousPatterns.some(pattern => url.includes(pattern));
    
    if (isSuspicious && details.type !== 'main_frame') {
      incrementStat('warnings');
      logActivity({
        type: 'warning',
        message: `Подозрительный запрос: ${truncateUrl(details.url)}`,
        timestamp: Date.now()
      });
      
      // Show notification
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon48.png',
        title: 'SViris: Предупреждение',
        message: 'Обнаружен подозрительный сетевой запрос',
        priority: 2
      });
    }
  },
  { urls: ["<all_urls>"] }
);

// Monitor downloads
chrome.downloads.onCreated.addListener((downloadItem) => {
  if (!monitoringSettings.downloads) return;
  
  const filename = downloadItem.filename.toLowerCase();
  const dangerousExtensions = ['.exe', '.bat', '.cmd', '.scr', '.vbs', '.js', '.jar', '.app'];
  
  const isDangerous = dangerousExtensions.some(ext => filename.endsWith(ext));
  
  if (isDangerous) {
    incrementStat('warnings');
    logActivity({
      type: 'danger',
      message: `Загрузка потенциально опасного файла: ${downloadItem.filename}`,
      timestamp: Date.now()
    });
    
    // Show warning notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'SViris: Внимание!',
      message: `Загружается потенциально опасный файл: ${downloadItem.filename}`,
      priority: 2
    });
  }
});

// Monitor tab updates for phishing detection
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    checkPageSafety(tab.url, tabId);
  }
});

// Context menu for quick URL checking
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'checkLinkSafety',
    title: 'Проверить ссылку с SViris',
    contexts: ['link']
  });
  
  chrome.contextMenus.create({
    id: 'checkPageSafety',
    title: 'Проверить страницу с SViris',
    contexts: ['page']
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'checkLinkSafety') {
    chrome.action.openPopup();
    // Send URL to popup
    setTimeout(() => {
      chrome.runtime.sendMessage({ 
        action: 'scanUrl', 
        url: info.linkUrl 
      });
    }, 500);
  } else if (info.menuItemId === 'checkPageSafety') {
    chrome.action.openPopup();
    setTimeout(() => {
      chrome.runtime.sendMessage({ 
        action: 'scanUrl', 
        url: tab.url 
      });
    }, 500);
  }
});

// Helper functions
function incrementStat(stat) {
  behaviorStats[stat] = (behaviorStats[stat] || 0) + 1;
  chrome.storage.local.set({ behaviorStats });
  
  // Broadcast to popup if open
  chrome.runtime.sendMessage({ 
    action: 'statsUpdated', 
    stats: behaviorStats 
  }).catch(() => {}); // Ignore errors if popup is closed
}

function logActivity(data) {
  chrome.storage.local.get(['activityLog'], (result) => {
    const log = result.activityLog || [];
    log.push(data);
    
    // Keep only last 100 entries
    const updatedLog = log.slice(-100);
    chrome.storage.local.set({ activityLog: updatedLog });
  });
}

function handleSuspiciousActivity(data) {
  incrementStat('warnings');
  logActivity({
    type: 'warning',
    message: data.message,
    timestamp: Date.now()
  });
}

async function checkPageSafety(url, tabId) {
  // Check for known phishing patterns
  const phishingPatterns = [
    /paypal.*verify/i,
    /amazon.*account.*suspend/i,
    /banking.*secure.*login/i,
    /verify.*account/i,
    /suspended.*account/i,
    /unusual.*activity/i
  ];
  
  const urlLower = url.toLowerCase();
  const isPhishingPattern = phishingPatterns.some(pattern => pattern.test(urlLower));
  
  if (isPhishingPattern) {
    incrementStat('warnings');
    logActivity({
      type: 'danger',
      message: `Обнаружен подозрительный шаблон в URL: ${truncateUrl(url)}`,
      timestamp: Date.now()
    });
    
    // Update badge
    chrome.action.setBadgeText({ text: '!', tabId });
    chrome.action.setBadgeBackgroundColor({ color: '#e74c3c', tabId });
    
    // Show notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'SViris: Возможный фишинг!',
      message: 'Эта страница может быть опасной. Будьте осторожны!',
      priority: 2
    });
  }
}

async function checkUrlSafety(url) {
  // Simple reputation check based on patterns
  const dangerousPatterns = [
    /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/,  // IP address
    /bit\.ly|tinyurl|shorturl/i,           // URL shorteners
    /\.tk$|\.ml$|\.ga$/i,                  // Free domains
    /password|login|verify|account/i       // Suspicious keywords
  ];
  
  const score = dangerousPatterns.filter(pattern => pattern.test(url)).length;
  
  return {
    safe: score === 0,
    score: score,
    risk: score === 0 ? 'low' : score === 1 ? 'medium' : 'high'
  };
}

function truncateUrl(url, maxLength = 50) {
  if (url.length <= maxLength) return url;
  return url.substring(0, maxLength) + '...';
}

// Reset stats daily
chrome.alarms.create('resetDailyStats', { periodInMinutes: 1440 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'resetDailyStats') {
    behaviorStats = { scripts: 0, requests: 0, warnings: 0 };
    chrome.storage.local.set({ behaviorStats });
  }
});

console.log('SViris background service worker initialized');
