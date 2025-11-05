// Проверка активности расширения на текущей странице
document.addEventListener('DOMContentLoaded', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
  if (!tab.url || !tab.url.includes('funpay.com')) {
    document.getElementById('status').innerHTML = `
      <span class="status-dot" style="background: #f56565;"></span>
      <span>Откройте Funpay.com</span>
    `;
    document.body.style.opacity = '0.6';
    return;
  }

  // Загрузка настроек
  loadSettings();
  loadStats();

  // Обработчики событий
  document.getElementById('btn-auto-buy').addEventListener('click', toggleAutoBuy);
  document.getElementById('btn-auto-sell').addEventListener('click', toggleAutoSell);
  document.getElementById('notifications').addEventListener('change', saveSettings);
  document.getElementById('auto-refresh').addEventListener('change', saveSettings);
  document.getElementById('refresh-interval').addEventListener('change', saveSettings);
  document.getElementById('btn-reset').addEventListener('click', resetSettings);
});

async function loadSettings() {
  const result = await chrome.storage.sync.get([
    'notifications',
    'autoRefresh',
    'refreshInterval',
    'autoBuy',
    'autoSell'
  ]);

  document.getElementById('notifications').checked = result.notifications || false;
  document.getElementById('auto-refresh').checked = result.autoRefresh || false;
  document.getElementById('refresh-interval').value = result.refreshInterval || 10;
  
  updateButtonStates(result.autoBuy, result.autoSell);
}

function updateButtonStates(autoBuy, autoSell) {
  const buyBtn = document.getElementById('btn-auto-buy');
  const sellBtn = document.getElementById('btn-auto-sell');
  
  if (autoBuy) {
    buyBtn.classList.add('active');
    buyBtn.textContent = 'Автопокупка: ВКЛ';
  } else {
    buyBtn.classList.remove('active');
    buyBtn.textContent = 'Автопокупка';
  }
  
  if (autoSell) {
    sellBtn.classList.add('active');
    sellBtn.textContent = 'Автопродажа: ВКЛ';
  } else {
    sellBtn.classList.remove('active');
    sellBtn.textContent = 'Автопродажа';
  }
}

async function toggleAutoBuy() {
  const result = await chrome.storage.sync.get(['autoBuy']);
  const newValue = !result.autoBuy;
  
  await chrome.storage.sync.set({ autoBuy: newValue });
  
  // Отправляем сообщение в content script
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  chrome.tabs.sendMessage(tab.id, {
      action: 'toggleAutoBuy',
      enabled: newValue
  });
  
  updateButtonStates(newValue, result.autoSell);
}

async function toggleAutoSell() {
  const result = await chrome.storage.sync.get(['autoSell']);
  const newValue = !result.autoSell;
  
  await chrome.storage.sync.set({ autoSell: newValue });
  
  // Отправляем сообщение в content script
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  chrome.tabs.sendMessage(tab.id, {
      action: 'toggleAutoSell',
      enabled: newValue
  });
  
  updateButtonStates(result.autoBuy, newValue);
}

async function saveSettings() {
  const settings = {
    notifications: document.getElementById('notifications').checked,
    autoRefresh: document.getElementById('auto-refresh').checked,
    refreshInterval: parseInt(document.getElementById('refresh-interval').value) || 10
  };
  
  await chrome.storage.sync.set(settings);
  
  // Отправляем сообщение в content script для обновления настроек
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  chrome.tabs.sendMessage(tab.id, {
      action: 'updateSettings',
      settings: settings
  });
}

async function loadStats() {
  const result = await chrome.storage.local.get(['dealsToday', 'totalDeals']);
  
  document.getElementById('deals-today').textContent = result.dealsToday || 0;
  document.getElementById('total-deals').textContent = result.totalDeals || 0;
}

async function resetSettings() {
  if (confirm('Вы уверены, что хотите сбросить все настройки?')) {
    await chrome.storage.sync.clear();
    await chrome.storage.local.set({ dealsToday: 0, totalDeals: 0 });
    loadSettings();
    loadStats();
  }
}
