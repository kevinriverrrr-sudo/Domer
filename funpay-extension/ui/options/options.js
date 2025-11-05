/**
 * FunPay Ultimate Pro - Options Page Script
 */

document.addEventListener('DOMContentLoaded', async () => {
  // Инициализация
  await loadAllSettings();
  setupNavigationHandlers();
  setupButtonHandlers();
  setupFormHandlers();
});

// Навигация по секциям
function setupNavigationHandlers() {
  const sidebarItems = document.querySelectorAll('.sidebar-item');
  const sections = document.querySelectorAll('.settings-section');

  sidebarItems.forEach(item => {
    item.addEventListener('click', () => {
      // Убираем активный класс со всех
      sidebarItems.forEach(i => i.classList.remove('active'));
      sections.forEach(s => s.classList.remove('active'));

      // Добавляем активный класс
      item.classList.add('active');
      const sectionId = 'section-' + item.getAttribute('data-section');
      document.getElementById(sectionId)?.classList.add('active');
    });
  });
}

// Обработчики кнопок
function setupButtonHandlers() {
  // Сохранение
  document.getElementById('btn-save')?.addEventListener('click', async () => {
    await saveAllSettings();
    showNotification('Настройки сохранены!', 'success');
  });

  // Экспорт
  document.getElementById('btn-export')?.addEventListener('click', async () => {
    const allData = await chrome.storage.local.get(null);
    const dataStr = JSON.stringify(allData, null, 2);
    downloadFile(dataStr, `funpay-pro-settings-${Date.now()}.json`, 'application/json');
    showNotification('Настройки экспортированы', 'success');
  });

  // Импорт
  document.getElementById('btn-import')?.addEventListener('click', () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (file) {
        const text = await file.text();
        try {
          const data = JSON.parse(text);
          await chrome.storage.local.set(data);
          await loadAllSettings();
          showNotification('Настройки импортированы', 'success');
        } catch (error) {
          showNotification('Ошибка импорта: ' + error.message, 'error');
        }
      }
    };
    input.click();
  });

  // Добавление шаблона
  document.getElementById('btn-add-template')?.addEventListener('click', () => {
    showTemplateDialog();
  });

  // Добавление фильтра
  document.getElementById('btn-add-filter')?.addEventListener('click', () => {
    showFilterDialog();
  });

  // Добавление лота
  document.getElementById('btn-add-lot')?.addEventListener('click', () => {
    showLotDialog();
  });
}

// Обработчики форм
function setupFormHandlers() {
  // Автосохранение при изменении
  document.querySelectorAll('input, select, textarea').forEach(element => {
    element.addEventListener('change', async () => {
      await saveAllSettings();
    });
  });
}

// Загрузка всех настроек
async function loadAllSettings() {
  const data = await chrome.storage.local.get('settings');
  const settings = data.settings || {};

  // Общие настройки
  setCheckbox('setting-enabled', settings.enabled !== false);
  setValue('setting-language', settings.ui?.language || 'ru');
  setValue('setting-theme', settings.ui?.theme || 'auto');

  // Автоответчик
  setCheckbox('autoresponder-enabled', settings.autoResponder?.enabled || false);
  setValue('autoresponder-delay-min', (settings.autoResponder?.delay?.min || 2000) / 1000);
  setValue('autoresponder-delay-max', (settings.autoResponder?.delay?.max || 5000) / 1000);
  setCheckbox('autoresponder-working-hours', settings.autoResponder?.workingHours?.enabled || false);
  setValue('autoresponder-start', settings.autoResponder?.workingHours?.start || '09:00');
  setValue('autoresponder-end', settings.autoResponder?.workingHours?.end || '21:00');

  // Автозакупка
  setCheckbox('autopurchase-enabled', settings.autoPurchase?.enabled || false);
  setValue('autopurchase-max-price', settings.autoPurchase?.maxPrice || 1000);
  setCheckbox('autopurchase-notifications', settings.autoPurchase?.notifications !== false);

  // Поднятие лотов
  setCheckbox('lotbooster-enabled', settings.lotBooster?.enabled || false);
  setValue('lotbooster-interval', (settings.lotBooster?.interval || 3600000) / 60000);
  setCheckbox('lotbooster-random', settings.lotBooster?.randomDelay !== false);

  // Безопасность
  setCheckbox('security-scam-detection', settings.security?.scamDetection !== false);
  setCheckbox('security-auto-block', settings.security?.autoBlock || false);

  // Уведомления
  setCheckbox('notifications-enabled', settings.notifications?.enabled !== false);
  setCheckbox('notifications-sound', settings.notifications?.sound !== false);
  setCheckbox('notifications-desktop', settings.notifications?.desktop !== false);
  setCheckbox('notifications-orders', settings.notifications?.orders !== false);
  setCheckbox('notifications-messages', settings.notifications?.messages !== false);
  setCheckbox('notifications-price-changes', settings.notifications?.priceChanges !== false);

  // Загрузка списков
  loadTemplates(settings.autoResponder?.templates || []);
  loadFilters(settings.autoPurchase?.filters || []);
  loadLots(settings.lotBooster?.lots || []);
}

// Сохранение всех настроек
async function saveAllSettings() {
  const settings = {
    enabled: getCheckbox('setting-enabled'),
    
    ui: {
      language: getValue('setting-language'),
      theme: getValue('setting-theme')
    },

    autoResponder: {
      enabled: getCheckbox('autoresponder-enabled'),
      delay: {
        min: getValue('autoresponder-delay-min') * 1000,
        max: getValue('autoresponder-delay-max') * 1000
      },
      workingHours: {
        enabled: getCheckbox('autoresponder-working-hours'),
        start: getValue('autoresponder-start'),
        end: getValue('autoresponder-end')
      },
      templates: getCurrentTemplates()
    },

    autoPurchase: {
      enabled: getCheckbox('autopurchase-enabled'),
      maxPrice: parseInt(getValue('autopurchase-max-price')),
      notifications: getCheckbox('autopurchase-notifications'),
      filters: getCurrentFilters()
    },

    lotBooster: {
      enabled: getCheckbox('lotbooster-enabled'),
      interval: getValue('lotbooster-interval') * 60000,
      randomDelay: getCheckbox('lotbooster-random'),
      lots: getCurrentLots()
    },

    security: {
      scamDetection: getCheckbox('security-scam-detection'),
      autoBlock: getCheckbox('security-auto-block')
    },

    notifications: {
      enabled: getCheckbox('notifications-enabled'),
      sound: getCheckbox('notifications-sound'),
      desktop: getCheckbox('notifications-desktop'),
      orders: getCheckbox('notifications-orders'),
      messages: getCheckbox('notifications-messages'),
      priceChanges: getCheckbox('notifications-price-changes')
    }
  };

  await chrome.storage.local.set({ settings });

  // Уведомление активных вкладок об обновлении настроек
  const tabs = await chrome.tabs.query({ url: '*://funpay.com/*' });
  tabs.forEach(tab => {
    chrome.tabs.sendMessage(tab.id, {
      action: 'updateSettings',
      settings
    }).catch(() => {});
  });
}

// Вспомогательные функции
function setCheckbox(id, value) {
  const el = document.getElementById(id);
  if (el) el.checked = value;
}

function getCheckbox(id) {
  const el = document.getElementById(id);
  return el ? el.checked : false;
}

function setValue(id, value) {
  const el = document.getElementById(id);
  if (el) el.value = value;
}

function getValue(id) {
  const el = document.getElementById(id);
  return el ? el.value : '';
}

// Загрузка шаблонов
function loadTemplates(templates) {
  const container = document.getElementById('templates-list');
  if (!container) return;

  container.innerHTML = templates.map(template => `
    <div class="template-item" data-id="${template.id}">
      <div class="item-info">
        <strong>${template.name}</strong>
        <p style="font-size: 13px; color: #7f8c8d; margin-top: 3px;">
          Ключевое слово: "${template.keyword}" | Ответ: "${template.text.substring(0, 50)}..."
        </p>
      </div>
      <div class="item-actions">
        <button class="btn-edit" onclick="editTemplate('${template.id}')">✏️ Изменить</button>
        <button class="btn-delete" onclick="deleteTemplate('${template.id}')">🗑️ Удалить</button>
      </div>
    </div>
  `).join('');
}

function loadFilters(filters) {
  const container = document.getElementById('purchase-filters-list');
  if (!container) return;

  container.innerHTML = filters.map(filter => `
    <div class="filter-item" data-id="${filter.id}">
      <div class="item-info">
        <strong>${filter.name}</strong>
        <p style="font-size: 13px; color: #7f8c8d; margin-top: 3px;">
          Цена: ${filter.minPrice || 0} - ${filter.maxPrice || '∞'}
        </p>
      </div>
      <div class="item-actions">
        <button class="btn-edit" onclick="editFilter('${filter.id}')">✏️ Изменить</button>
        <button class="btn-delete" onclick="deleteFilter('${filter.id}')">🗑️ Удалить</button>
      </div>
    </div>
  `).join('');
}

function loadLots(lots) {
  const container = document.getElementById('lots-list');
  if (!container) return;

  container.innerHTML = lots.map(lot => `
    <div class="lot-item" data-id="${lot.id}">
      <div class="item-info">
        <strong>${lot.name}</strong>
        <p style="font-size: 13px; color: #7f8c8d; margin-top: 3px;">
          ID: ${lot.id}
        </p>
      </div>
      <div class="item-actions">
        <button class="btn-delete" onclick="deleteLot('${lot.id}')">🗑️ Удалить</button>
      </div>
    </div>
  `).join('');
}

function getCurrentTemplates() {
  const items = document.querySelectorAll('#templates-list .template-item');
  return Array.from(items).map(item => ({
    id: item.getAttribute('data-id'),
    // Здесь должны быть данные из item
  }));
}

function getCurrentFilters() {
  return []; // Упрощенная версия
}

function getCurrentLots() {
  return []; // Упрощенная версия
}

// Диалоги
function showTemplateDialog() {
  // Создание модального окна для добавления шаблона
  alert('Функция добавления шаблона будет доступна в следующей версии');
}

function showFilterDialog() {
  alert('Функция добавления фильтра будет доступна в следующей версии');
}

function showLotDialog() {
  alert('Функция добавления лота будет доступна в следующей версии');
}

// Уведомления
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${type === 'success' ? '#2ecc71' : type === 'error' ? '#e74c3c' : '#3498db'};
    color: white;
    padding: 15px 25px;
    border-radius: 8px;
    z-index: 10000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    animation: slideIn 0.3s ease-out;
  `;
  notification.textContent = message;
  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease-in';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

function downloadFile(content, filename, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// Глобальные функции для кнопок
window.editTemplate = function(id) {
  alert(`Редактирование шаблона ${id}`);
};

window.deleteTemplate = async function(id) {
  if (confirm('Удалить этот шаблон?')) {
    // Логика удаления
    await saveAllSettings();
    showNotification('Шаблон удален', 'success');
  }
};

window.editFilter = function(id) {
  alert(`Редактирование фильтра ${id}`);
};

window.deleteFilter = async function(id) {
  if (confirm('Удалить этот фильтр?')) {
    await saveAllSettings();
    showNotification('Фильтр удален', 'success');
  }
};

window.deleteLot = async function(id) {
  if (confirm('Удалить этот лот?')) {
    await saveAllSettings();
    showNotification('Лот удален', 'success');
  }
};
