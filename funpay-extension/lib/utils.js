/**
 * FunPay Ultimate Pro - Утилиты
 * Библиотека вспомогательных функций
 */

const FunPayUtils = {
  /**
   * Генерация уникального ID
   */
  generateId() {
    return `fp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  },

  /**
   * Форматирование даты
   */
  formatDate(date, format = 'full') {
    const d = new Date(date);
    const formats = {
      full: d.toLocaleString('ru-RU'),
      date: d.toLocaleDateString('ru-RU'),
      time: d.toLocaleTimeString('ru-RU'),
      iso: d.toISOString(),
      relative: this.getRelativeTime(d)
    };
    return formats[format] || formats.full;
  },

  /**
   * Относительное время
   */
  getRelativeTime(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    const intervals = {
      год: 31536000,
      месяц: 2592000,
      неделя: 604800,
      день: 86400,
      час: 3600,
      минута: 60,
      секунда: 1
    };

    for (let [name, value] of Object.entries(intervals)) {
      const interval = Math.floor(seconds / value);
      if (interval >= 1) {
        return `${interval} ${name}${interval > 1 ? (name === 'час' ? 'а' : name === 'месяц' ? 'а' : 'ы') : ''} назад`;
      }
    }
    return 'только что';
  },

  /**
   * Форматирование цены
   */
  formatPrice(price, currency = '₽') {
    return `${parseFloat(price).toFixed(2)} ${currency}`;
  },

  /**
   * Парсинг цены из строки
   */
  parsePrice(priceString) {
    const match = priceString.match(/[\d,.]+/);
    return match ? parseFloat(match[0].replace(',', '.')) : 0;
  },

  /**
   * Задержка
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  },

  /**
   * Случайная задержка
   */
  randomDelay(min = 1000, max = 3000) {
    return this.sleep(Math.random() * (max - min) + min);
  },

  /**
   * Debounce функция
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  /**
   * Throttle функция
   */
  throttle(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },

  /**
   * Копирование в буфер обмена
   */
  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (err) {
      console.error('Ошибка копирования:', err);
      return false;
    }
  },

  /**
   * Скачивание файла
   */
  downloadFile(content, filename, type = 'text/plain') {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  },

  /**
   * Экспорт в JSON
   */
  exportToJSON(data, filename) {
    const json = JSON.stringify(data, null, 2);
    this.downloadFile(json, filename, 'application/json');
  },

  /**
   * Экспорт в CSV
   */
  exportToCSV(data, filename) {
    const headers = Object.keys(data[0] || {});
    const csv = [
      headers.join(','),
      ...data.map(row => headers.map(h => JSON.stringify(row[h] || '')).join(','))
    ].join('\n');
    this.downloadFile(csv, filename, 'text/csv');
  },

  /**
   * Хэширование строки
   */
  async hashString(str) {
    const encoder = new TextEncoder();
    const data = encoder.encode(str);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  },

  /**
   * Проверка email
   */
  isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  },

  /**
   * Проверка URL
   */
  isValidUrl(url) {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  },

  /**
   * Получение параметров из URL
   */
  getUrlParams(url = window.location.href) {
    return Object.fromEntries(new URL(url).searchParams);
  },

  /**
   * Создание уведомления
   */
  notify(title, message, type = 'info') {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body: message,
        icon: chrome.runtime.getURL('icons/icon48.png'),
        badge: chrome.runtime.getURL('icons/icon16.png')
      });
    }
  },

  /**
   * Логирование с меткой времени
   */
  log(message, data = null, level = 'info') {
    const timestamp = new Date().toISOString();
    const prefix = `[FunPay Pro ${timestamp}]`;
    
    if (data) {
      console[level](prefix, message, data);
    } else {
      console[level](prefix, message);
    }
  },

  /**
   * Безопасный парсинг JSON
   */
  safeJSONParse(str, fallback = null) {
    try {
      return JSON.parse(str);
    } catch {
      return fallback;
    }
  },

  /**
   * Проверка на мобильное устройство
   */
  isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  },

  /**
   * Получение информации о браузере
   */
  getBrowserInfo() {
    const ua = navigator.userAgent;
    let browser = 'Unknown';
    
    if (ua.includes('Chrome')) browser = 'Chrome';
    else if (ua.includes('Firefox')) browser = 'Firefox';
    else if (ua.includes('Safari')) browser = 'Safari';
    else if (ua.includes('Edge')) browser = 'Edge';
    else if (ua.includes('Opera')) browser = 'Opera';
    
    return { browser, userAgent: ua };
  },

  /**
   * Санитизация HTML
   */
  sanitizeHTML(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
  },

  /**
   * Извлечение текста из HTML
   */
  stripHTML(html) {
    const div = document.createElement('div');
    div.innerHTML = html;
    return div.textContent || div.innerText || '';
  },

  /**
   * Подсветка текста
   */
  highlightText(text, search) {
    if (!search) return text;
    const regex = new RegExp(`(${search})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  },

  /**
   * Truncate текста
   */
  truncate(text, length, suffix = '...') {
    return text.length > length ? text.substring(0, length) + suffix : text;
  },

  /**
   * Капитализация первой буквы
   */
  capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  },

  /**
   * Генерация случайной строки
   */
  randomString(length = 10) {
    return Math.random().toString(36).substring(2, length + 2);
  },

  /**
   * Проверка FunPay страницы
   */
  isFunPayPage() {
    return window.location.hostname.includes('funpay');
  },

  /**
   * Получение типа текущей страницы FunPay
   */
  getPageType() {
    const path = window.location.pathname;
    if (path.includes('/orders/')) return 'orders';
    if (path.includes('/lots/')) return 'lots';
    if (path.includes('/users/')) return 'profile';
    if (path.includes('/chat/')) return 'chat';
    if (path === '/') return 'home';
    return 'other';
  }
};

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FunPayUtils;
}
