/**
 * FunPay Ultimate Pro - Менеджер Уведомлений
 * Система уведомлений
 */

class NotificationManager {
  constructor() {
    this.enabled = true;
    this.soundEnabled = true;
    this.desktopEnabled = true;
    this.queue = [];
    this.init();
  }

  async init() {
    const settings = await FunPayStorage.settings.get('notifications');
    if (settings) {
      this.enabled = settings.enabled;
      this.soundEnabled = settings.sound;
      this.desktopEnabled = settings.desktop;
    }

    // Запрос разрешения на уведомления
    if (this.desktopEnabled && 'Notification' in window) {
      Notification.requestPermission();
    }
  }

  async notify(title, message, type = 'info', options = {}) {
    if (!this.enabled) return;

    const notification = {
      id: FunPayUtils.generateId(),
      title,
      message,
      type,
      timestamp: Date.now(),
      read: false,
      ...options
    };

    this.queue.push(notification);
    await this.saveQueue();

    // Показ уведомления
    if (this.desktopEnabled) {
      this.showDesktopNotification(notification);
    }

    if (this.soundEnabled) {
      this.playSound(type);
    }

    // In-page уведомление
    this.showInPageNotification(notification);

    // Статистика
    await FunPayStorage.stats.increment('notifications');

    return notification;
  }

  showDesktopNotification(notification) {
    if ('Notification' in window && Notification.permission === 'granted') {
      const n = new Notification(notification.title, {
        body: notification.message,
        icon: chrome.runtime.getURL('icons/icon48.png'),
        badge: chrome.runtime.getURL('icons/icon16.png'),
        tag: notification.id,
        requireInteraction: notification.type === 'critical'
      });

      n.onclick = () => {
        window.focus();
        this.markAsRead(notification.id);
        n.close();
      };

      setTimeout(() => n.close(), 10000);
    }
  }

  showInPageNotification(notification) {
    const container = this.getOrCreateContainer();
    
    const notificationEl = document.createElement('div');
    notificationEl.className = `funpay-notification funpay-notification-${notification.type}`;
    notificationEl.setAttribute('data-notification-id', notification.id);
    notificationEl.style.cssText = `
      background: ${this.getTypeColor(notification.type)};
      color: white;
      padding: 15px 20px;
      margin-bottom: 10px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      animation: slideIn 0.3s ease-out;
      display: flex;
      justify-content: space-between;
      align-items: center;
      min-width: 300px;
      max-width: 400px;
    `;

    const content = document.createElement('div');
    content.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 5px;">${notification.title}</div>
      <div style="font-size: 13px; opacity: 0.9;">${notification.message}</div>
    `;

    const closeBtn = document.createElement('button');
    closeBtn.textContent = '×';
    closeBtn.style.cssText = `
      background: none;
      border: none;
      color: white;
      font-size: 24px;
      cursor: pointer;
      padding: 0 5px;
      opacity: 0.7;
    `;
    closeBtn.onclick = () => {
      notificationEl.remove();
      this.markAsRead(notification.id);
    };

    notificationEl.appendChild(content);
    notificationEl.appendChild(closeBtn);
    container.appendChild(notificationEl);

    // Автоудаление через 5 секунд
    setTimeout(() => {
      notificationEl.style.animation = 'slideOut 0.3s ease-in';
      setTimeout(() => {
        notificationEl.remove();
        this.markAsRead(notification.id);
      }, 300);
    }, 5000);
  }

  getOrCreateContainer() {
    let container = document.getElementById('funpay-notifications-container');
    
    if (!container) {
      container = document.createElement('div');
      container.id = 'funpay-notifications-container';
      container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        display: flex;
        flex-direction: column;
      `;
      document.body.appendChild(container);

      // Добавление CSS анимаций
      const style = document.createElement('style');
      style.textContent = `
        @keyframes slideIn {
          from {
            transform: translateX(400px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        @keyframes slideOut {
          from {
            transform: translateX(0);
            opacity: 1;
          }
          to {
            transform: translateX(400px);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }

    return container;
  }

  getTypeColor(type) {
    const colors = {
      info: '#3498db',
      success: '#2ecc71',
      warning: '#f39c12',
      error: '#e74c3c',
      critical: '#c0392b'
    };
    return colors[type] || colors.info;
  }

  playSound(type) {
    try {
      const sounds = {
        info: 'notification.mp3',
        success: 'success.mp3',
        warning: 'warning.mp3',
        error: 'error.mp3',
        critical: 'critical.mp3'
      };

      const soundFile = sounds[type] || sounds.info;
      const audio = new Audio(chrome.runtime.getURL(`assets/sounds/${soundFile}`));
      audio.volume = 0.5;
      audio.play().catch(() => {});
    } catch (error) {
      // Звук необязателен
    }
  }

  async markAsRead(notificationId) {
    const notification = this.queue.find(n => n.id === notificationId);
    if (notification) {
      notification.read = true;
      await this.saveQueue();
    }
  }

  async markAllAsRead() {
    this.queue.forEach(n => n.read = true);
    await this.saveQueue();
  }

  getUnreadCount() {
    return this.queue.filter(n => !n.read).length;
  }

  getNotifications(filter = 'all', limit = 50) {
    let filtered = this.queue;

    if (filter === 'unread') {
      filtered = filtered.filter(n => !n.read);
    } else if (filter !== 'all') {
      filtered = filtered.filter(n => n.type === filter);
    }

    return filtered.slice(-limit).reverse();
  }

  async clearNotifications() {
    this.queue = [];
    await this.saveQueue();
  }

  async saveQueue() {
    // Ограничение размера очереди
    if (this.queue.length > 1000) {
      this.queue = this.queue.slice(-1000);
    }
    await FunPayStorage.set('notificationQueue', this.queue);
  }

  // Предустановленные типы уведомлений
  async notifyNewOrder(orderData) {
    return await this.notify(
      'Новый заказ!',
      `От ${orderData.buyer} на сумму ${orderData.amount}`,
      'success',
      { category: 'order', data: orderData }
    );
  }

  async notifyNewMessage(messageData) {
    return await this.notify(
      'Новое сообщение',
      `${messageData.sender}: ${messageData.preview}`,
      'info',
      { category: 'message', data: messageData }
    );
  }

  async notifyPriceChange(itemData) {
    return await this.notify(
      'Изменение цены',
      `${itemData.title}: новая цена ${itemData.newPrice}`,
      'warning',
      { category: 'price', data: itemData }
    );
  }

  async notifySecurityThreat(threatData) {
    return await this.notify(
      'Обнаружена угроза!',
      threatData.description,
      'critical',
      { category: 'security', data: threatData }
    );
  }
}

// Инициализация
let notificationManager;
if (typeof window !== 'undefined') {
  notificationManager = new NotificationManager();
}
