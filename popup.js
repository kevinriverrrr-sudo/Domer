// Popup Script
document.addEventListener('DOMContentLoaded', () => {
  // Проверка аутентификации
  chrome.runtime.sendMessage({ action: 'checkAuth' }, (response) => {
    if (response && response.authenticated) {
      loadSettings();
    } else {
      showStatus('Требуется аутентификация', 'error');
    }
  });
  
  // Аутентификация
  document.getElementById('authBtn').addEventListener('click', () => {
    const key = document.getElementById('authKey').value;
    chrome.runtime.sendMessage({ action: 'authenticate', key }, (response) => {
      if (response && response.success) {
        showStatus('Успешно подключено!', 'success');
        loadSettings();
      } else {
        showStatus('Неверный ключ доступа!', 'error');
      }
    });
  });
  
  // Сохранение настроек
  document.getElementById('saveBtn').addEventListener('click', () => {
    saveSettings();
  });
  
  // Обновление статистики
  document.getElementById('refreshStatsBtn').addEventListener('click', () => {
    refreshStats();
  });
  
  // Экспорт данных
  document.getElementById('exportBtn').addEventListener('click', () => {
    exportData();
  });
  
  // Мультиаккаунт
  document.getElementById('addAccountBtn').addEventListener('click', () => {
    const name = prompt('Введите имя аккаунта:');
    const key = prompt('Введите ключ доступа:');
    if (name && key) {
      addAccount(name, key);
    }
  });
  
  document.getElementById('switchAccountBtn').addEventListener('click', () => {
    const accountId = document.getElementById('accountSelect').value;
    if (accountId) {
      switchAccount(accountId);
    }
  });
  
  function loadSettings() {
    chrome.storage.local.get(['settings'], (result) => {
      const settings = result.settings || {};
      
      if (settings.theme) {
        document.getElementById('theme').value = settings.theme;
      }
      
      if (settings.primaryColor) {
        document.getElementById('primaryColor').value = settings.primaryColor;
      }
      
      if (settings.animations !== undefined) {
        document.getElementById('animations').checked = settings.animations;
      }
      
      if (settings.autoRaise) {
        document.getElementById('autoRaiseEnabled').checked = settings.autoRaise.enabled || false;
        document.getElementById('autoRaiseInterval').value = settings.autoRaise.interval / 60000 || 60;
      }
      
      if (settings.autoMessages) {
        document.getElementById('autoMessagesEnabled').checked = settings.autoMessages.enabled || false;
        document.getElementById('messageTemplate').value = settings.autoMessages.template || '';
      }
      
      if (settings.analytics !== undefined) {
        document.getElementById('analyticsEnabled').checked = settings.analytics;
      }
    });
  }
  
  function saveSettings() {
    const settings = {
      theme: document.getElementById('theme').value,
      primaryColor: document.getElementById('primaryColor').value,
      animations: document.getElementById('animations').checked,
      autoRaise: {
        enabled: document.getElementById('autoRaiseEnabled').checked,
        interval: parseInt(document.getElementById('autoRaiseInterval').value) * 60000
      },
      autoMessages: {
        enabled: document.getElementById('autoMessagesEnabled').checked,
        template: document.getElementById('messageTemplate').value
      },
      analytics: document.getElementById('analyticsEnabled').checked
    };
    
    chrome.storage.local.set({ settings }, () => {
      showStatus('Настройки сохранены!', 'success');
      
      // Уведомление content script об обновлении настроек
      chrome.tabs.query({ url: 'https://funpay.com/*' }, (tabs) => {
        tabs.forEach(tab => {
          chrome.tabs.sendMessage(tab.id, {
            action: 'settingsUpdated',
            settings: settings
          });
        });
      });
    });
    
    // Настройка автоподнятия
    if (settings.autoRaise.enabled) {
      chrome.runtime.sendMessage({
        action: 'scheduleAutoRaise',
        config: settings.autoRaise
      });
    }
  }
  
  function exportData() {
    chrome.storage.local.get(['analytics'], (result) => {
      const data = result.analytics || {};
      const json = JSON.stringify(data, null, 2);
      const blob = new Blob([json], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `funpay-analytics-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      showStatus('Данные экспортированы!', 'success');
    });
  }
  
  function showStatus(message, type) {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = `status ${type} show`;
    setTimeout(() => {
      status.classList.remove('show');
    }, 3000);
  }
  
  function refreshStats() {
    chrome.tabs.query({ url: 'https://funpay.com/*' }, (tabs) => {
      if (tabs.length > 0) {
        chrome.tabs.sendMessage(tabs[0].id, { action: 'getAnalytics' }, (response) => {
          if (response && response.success && response.stats) {
            displayStats(response.stats);
          } else {
            // Получаем данные из storage
            chrome.storage.local.get(['analyticsData'], (result) => {
              if (result.analyticsData) {
                const stats = {
                  totalSales: result.analyticsData.totalSales || 0,
                  totalRevenue: result.analyticsData.revenue || 0,
                  uniqueBuyers: result.analyticsData.buyers ? result.analyticsData.buyers.length : 0,
                  averageOrderValue: result.analyticsData.totalSales > 0 ? 
                    result.analyticsData.revenue / result.analyticsData.totalSales : 0
                };
                displayStats(stats);
              }
            });
          }
        });
      }
    });
  }
  
  function displayStats(stats) {
    document.getElementById('totalSales').textContent = stats.totalSales || 0;
    document.getElementById('totalRevenue').textContent = (stats.totalRevenue || 0).toFixed(2);
    document.getElementById('uniqueBuyers').textContent = stats.uniqueBuyers || 0;
    document.getElementById('avgOrder').textContent = (stats.averageOrderValue || 0).toFixed(2);
    document.getElementById('statsDisplay').style.display = 'block';
  }
  
  function addAccount(name, key) {
    chrome.runtime.sendMessage({ 
      action: 'addAccount', 
      accountData: { name, authKey: key } 
    }, (response) => {
      if (response && response.success) {
        showStatus('Аккаунт добавлен!', 'success');
        loadAccounts();
      } else {
        showStatus('Ошибка добавления аккаунта', 'error');
      }
    });
  }
  
  function switchAccount(accountId) {
    chrome.runtime.sendMessage({ 
      action: 'switchAccount', 
      accountId 
    }, (response) => {
      if (response && response.success) {
        showStatus('Аккаунт переключен!', 'success');
        loadSettings();
      } else {
        showStatus('Ошибка переключения аккаунта', 'error');
      }
    });
  }
  
  function loadAccounts() {
    chrome.runtime.sendMessage({ action: 'getAccounts' }, (response) => {
      if (response && response.accounts) {
        const select = document.getElementById('accountSelect');
        select.innerHTML = '<option value="">Выберите аккаунт</option>';
        response.accounts.forEach(acc => {
          const option = document.createElement('option');
          option.value = acc.id;
          option.textContent = acc.name;
          select.appendChild(option);
        });
      }
    });
  }
  
  // Загрузка статистики при открытии
  refreshStats();
  loadAccounts();
});
