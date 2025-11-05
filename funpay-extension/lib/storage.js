/**
 * FunPay Ultimate Pro - Менеджер Хранилища
 * Управление данными расширения
 */

const FunPayStorage = {
  /**
   * Получение данных из storage
   */
  async get(key, defaultValue = null) {
    try {
      const result = await chrome.storage.local.get(key);
      return result[key] !== undefined ? result[key] : defaultValue;
    } catch (error) {
      console.error('Storage get error:', error);
      return defaultValue;
    }
  },

  /**
   * Сохранение данных в storage
   */
  async set(key, value) {
    try {
      await chrome.storage.local.set({ [key]: value });
      return true;
    } catch (error) {
      console.error('Storage set error:', error);
      return false;
    }
  },

  /**
   * Удаление данных из storage
   */
  async remove(key) {
    try {
      await chrome.storage.local.remove(key);
      return true;
    } catch (error) {
      console.error('Storage remove error:', error);
      return false;
    }
  },

  /**
   * Очистка всего storage
   */
  async clear() {
    try {
      await chrome.storage.local.clear();
      return true;
    } catch (error) {
      console.error('Storage clear error:', error);
      return false;
    }
  },

  /**
   * Получение всех данных
   */
  async getAll() {
    try {
      return await chrome.storage.local.get(null);
    } catch (error) {
      console.error('Storage getAll error:', error);
      return {};
    }
  },

  /**
   * Настройки расширения
   */
  settings: {
    async get(key, defaultValue) {
      const settings = await FunPayStorage.get('settings', {});
      return settings[key] !== undefined ? settings[key] : defaultValue;
    },

    async set(key, value) {
      const settings = await FunPayStorage.get('settings', {});
      settings[key] = value;
      return await FunPayStorage.set('settings', settings);
    },

    async getAll() {
      return await FunPayStorage.get('settings', {});
    },

    async setAll(settings) {
      return await FunPayStorage.set('settings', settings);
    },

    // Настройки по умолчанию
    defaults: {
      // Автоответчик
      autoResponder: {
        enabled: false,
        delay: { min: 2000, max: 5000 },
        templates: [],
        workingHours: { enabled: false, start: '09:00', end: '21:00' },
        keywords: []
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
        interval: 3600000, // 1 час
        randomDelay: true
      },

      // Аналитика конкурентов
      competitorAnalytics: {
        enabled: true,
        trackPrices: true,
        trackLots: true,
        competitors: []
      },

      // Автожалобы
      autoComplaints: {
        enabled: false,
        reasons: [],
        autoFill: true
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
        blacklist: [],
        whitelist: [],
        autoBlock: false
      },

      // Интерфейс
      ui: {
        theme: 'auto',
        language: 'ru',
        compactMode: false,
        animations: true
      },

      // Аналитика
      analytics: {
        trackSales: true,
        trackViews: true,
        exportFormat: 'json'
      },

      // Автоматизация
      automation: {
        autoAcceptOrders: false,
        autoCompleteOrders: false,
        autoReply: true
      }
    }
  },

  /**
   * Статистика
   */
  stats: {
    async increment(key) {
      const stats = await FunPayStorage.get('stats', {});
      stats[key] = (stats[key] || 0) + 1;
      stats[`${key}_lastUpdate`] = Date.now();
      await FunPayStorage.set('stats', stats);
      return stats[key];
    },

    async set(key, value) {
      const stats = await FunPayStorage.get('stats', {});
      stats[key] = value;
      stats[`${key}_lastUpdate`] = Date.now();
      await FunPayStorage.set('stats', stats);
    },

    async get(key, defaultValue = 0) {
      const stats = await FunPayStorage.get('stats', {});
      return stats[key] !== undefined ? stats[key] : defaultValue;
    },

    async getAll() {
      return await FunPayStorage.get('stats', {});
    },

    async reset() {
      await FunPayStorage.set('stats', {});
    }
  },

  /**
   * Кэш
   */
  cache: {
    async get(key, maxAge = 3600000) { // 1 час по умолчанию
      const cache = await FunPayStorage.get('cache', {});
      const item = cache[key];
      
      if (!item) return null;
      
      const age = Date.now() - item.timestamp;
      if (age > maxAge) {
        delete cache[key];
        await FunPayStorage.set('cache', cache);
        return null;
      }
      
      return item.data;
    },

    async set(key, data) {
      const cache = await FunPayStorage.get('cache', {});
      cache[key] = {
        data,
        timestamp: Date.now()
      };
      await FunPayStorage.set('cache', cache);
    },

    async clear() {
      await FunPayStorage.set('cache', {});
    }
  },

  /**
   * История
   */
  history: {
    async add(type, data) {
      const history = await FunPayStorage.get('history', []);
      history.unshift({
        id: FunPayUtils.generateId(),
        type,
        data,
        timestamp: Date.now()
      });
      
      // Ограничение размера истории
      if (history.length > 1000) {
        history.splice(1000);
      }
      
      await FunPayStorage.set('history', history);
    },

    async get(limit = 100, type = null) {
      const history = await FunPayStorage.get('history', []);
      let filtered = type ? history.filter(h => h.type === type) : history;
      return filtered.slice(0, limit);
    },

    async clear() {
      await FunPayStorage.set('history', []);
    }
  },

  /**
   * Шаблоны
   */
  templates: {
    async add(template) {
      const templates = await FunPayStorage.get('templates', []);
      template.id = template.id || FunPayUtils.generateId();
      template.created = Date.now();
      templates.push(template);
      await FunPayStorage.set('templates', templates);
      return template;
    },

    async update(id, updates) {
      const templates = await FunPayStorage.get('templates', []);
      const index = templates.findIndex(t => t.id === id);
      if (index !== -1) {
        templates[index] = { ...templates[index], ...updates };
        await FunPayStorage.set('templates', templates);
        return templates[index];
      }
      return null;
    },

    async delete(id) {
      const templates = await FunPayStorage.get('templates', []);
      const filtered = templates.filter(t => t.id !== id);
      await FunPayStorage.set('templates', filtered);
    },

    async getAll() {
      return await FunPayStorage.get('templates', []);
    },

    async get(id) {
      const templates = await FunPayStorage.get('templates', []);
      return templates.find(t => t.id === id);
    }
  },

  /**
   * Экспорт данных
   */
  async export() {
    const data = await this.getAll();
    return {
      version: chrome.runtime.getManifest().version,
      exportDate: new Date().toISOString(),
      data
    };
  },

  /**
   * Импорт данных
   */
  async import(exportData) {
    try {
      if (exportData.data) {
        for (let [key, value] of Object.entries(exportData.data)) {
          await this.set(key, value);
        }
        return true;
      }
      return false;
    } catch (error) {
      console.error('Import error:', error);
      return false;
    }
  }
};

// Экспорт
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FunPayStorage;
}
