/**
 * FunPay Ultimate Pro - Автоматизация Заказов
 * Автоматическая обработка заказов
 */

class OrderAutomation {
  constructor() {
    this.enabled = false;
    this.autoAccept = false;
    this.autoComplete = false;
    this.autoDelivery = false;
    this.templates = [];
    this.init();
  }

  async init() {
    const settings = await FunPayStorage.settings.get('orderAutomation');
    if (settings) {
      Object.assign(this, settings);
    }
    
    if (this.enabled) {
      this.start();
    }
  }

  start() {
    this.enabled = true;
    this.observeOrders();
    FunPayUtils.log('Автоматизация заказов запущена');
  }

  stop() {
    this.enabled = false;
    if (this.observer) {
      this.observer.disconnect();
    }
    FunPayUtils.log('Автоматизация заказов остановлена');
  }

  observeOrders() {
    const orderContainer = document.querySelector('.orders-list, [class*="order"]');
    
    if (!orderContainer) {
      setTimeout(() => this.observeOrders(), 2000);
      return;
    }

    this.observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1 && this.isOrderNode(node)) {
            this.processNewOrder(node);
          }
        });
      });
    });

    this.observer.observe(orderContainer, {
      childList: true,
      subtree: true
    });

    // Обработка существующих заказов
    const existingOrders = orderContainer.querySelectorAll('.order-item, [class*="order"]');
    existingOrders.forEach(order => this.processNewOrder(order));
  }

  isOrderNode(node) {
    return node.classList && (
      node.classList.contains('order-item') ||
      node.classList.contains('order') ||
      node.hasAttribute('data-order-id')
    );
  }

  async processNewOrder(orderNode) {
    if (!this.enabled) return;

    const orderId = this.getOrderId(orderNode);
    const orderData = this.extractOrderData(orderNode);

    FunPayUtils.log('Новый заказ обнаружен:', orderData);

    // Уведомление о новом заказе
    FunPayUtils.notify(
      'Новый заказ!',
      `Заказ #${orderId} на сумму ${orderData.amount}`,
      'info'
    );

    // Звуковое уведомление
    this.playNotificationSound();

    // Автопринятие заказа
    if (this.autoAccept) {
      await FunPayUtils.randomDelay(2000, 5000);
      await this.acceptOrder(orderNode, orderId);
    }

    // Автоматическая доставка
    if (this.autoDelivery && orderData.deliveryInfo) {
      await FunPayUtils.randomDelay(3000, 7000);
      await this.deliverOrder(orderNode, orderId, orderData);
    }

    // Автозавершение
    if (this.autoComplete) {
      await FunPayUtils.randomDelay(5000, 10000);
      await this.completeOrder(orderNode, orderId);
    }

    // Сохранение в истории
    await FunPayStorage.history.add('order', orderData);
    await FunPayStorage.stats.increment('totalOrders');
  }

  getOrderId(node) {
    return node.getAttribute('data-order-id') || 
           node.querySelector('[data-order-id]')?.getAttribute('data-order-id') ||
           FunPayUtils.generateId();
  }

  extractOrderData(node) {
    const data = {
      id: this.getOrderId(node),
      buyer: this.extractText(node, '.buyer-name, .username'),
      amount: this.extractText(node, '.amount, .price'),
      product: this.extractText(node, '.product-name, .lot-title'),
      status: this.extractText(node, '.status, .order-status'),
      timestamp: Date.now(),
      deliveryInfo: this.extractDeliveryInfo(node)
    };

    return data;
  }

  extractText(node, selector) {
    const element = node.querySelector(selector);
    return element ? element.textContent.trim() : '';
  }

  extractDeliveryInfo(node) {
    // Извлечение информации для доставки (логин, пароль, и т.д.)
    const infoElement = node.querySelector('.delivery-info, .order-details');
    if (!infoElement) return null;

    return {
      text: infoElement.textContent.trim(),
      parsed: this.parseDeliveryInfo(infoElement.textContent)
    };
  }

  parseDeliveryInfo(text) {
    // Парсинг информации о доставке
    const info = {};
    
    // Логин
    const loginMatch = text.match(/логин[:\s]+([^\s,]+)/i);
    if (loginMatch) info.login = loginMatch[1];

    // Пароль
    const passwordMatch = text.match(/пароль[:\s]+([^\s,]+)/i);
    if (passwordMatch) info.password = passwordMatch[1];

    // Email
    const emailMatch = text.match(/([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/);
    if (emailMatch) info.email = emailMatch[1];

    return info;
  }

  async acceptOrder(orderNode, orderId) {
    try {
      const acceptButton = orderNode.querySelector('.btn-accept, button[class*="accept"]');
      
      if (acceptButton && !acceptButton.disabled) {
        acceptButton.click();
        FunPayUtils.log(`Заказ ${orderId} принят автоматически`);
        
        await FunPayStorage.stats.increment('autoAcceptedOrders');
        return true;
      }
    } catch (error) {
      FunPayUtils.log(`Ошибка принятия заказа ${orderId}:`, error, 'error');
    }
    return false;
  }

  async deliverOrder(orderNode, orderId, orderData) {
    try {
      // Поиск шаблона доставки
      const template = this.findDeliveryTemplate(orderData);
      
      if (!template) {
        FunPayUtils.log(`Шаблон доставки не найден для заказа ${orderId}`);
        return false;
      }

      // Заполнение полей доставки
      const deliveryText = this.processDeliveryTemplate(template, orderData);
      
      const deliveryField = orderNode.querySelector('textarea[name="delivery"], .delivery-input');
      if (deliveryField) {
        deliveryField.value = deliveryText;
        deliveryField.dispatchEvent(new Event('input', { bubbles: true }));
      }

      // Клик по кнопке доставки
      const deliverButton = orderNode.querySelector('.btn-deliver, button[class*="deliver"]');
      if (deliverButton) {
        await FunPayUtils.sleep(500);
        deliverButton.click();
        
        FunPayUtils.log(`Заказ ${orderId} доставлен автоматически`);
        await FunPayStorage.stats.increment('autoDeliveredOrders');
        return true;
      }
    } catch (error) {
      FunPayUtils.log(`Ошибка доставки заказа ${orderId}:`, error, 'error');
    }
    return false;
  }

  async completeOrder(orderNode, orderId) {
    try {
      const completeButton = orderNode.querySelector('.btn-complete, button[class*="complete"]');
      
      if (completeButton && !completeButton.disabled) {
        completeButton.click();
        
        FunPayUtils.log(`Заказ ${orderId} завершен автоматически`);
        await FunPayStorage.stats.increment('autoCompletedOrders');
        return true;
      }
    } catch (error) {
      FunPayUtils.log(`Ошибка завершения заказа ${orderId}:`, error, 'error');
    }
    return false;
  }

  findDeliveryTemplate(orderData) {
    // Поиск подходящего шаблона по названию товара
    return this.templates.find(t => 
      t.enabled && 
      (!t.productFilter || orderData.product.includes(t.productFilter))
    );
  }

  processDeliveryTemplate(template, orderData) {
    let text = template.text;

    // Замена переменных
    const variables = {
      '{buyer}': orderData.buyer,
      '{product}': orderData.product,
      '{order_id}': orderData.id,
      '{date}': new Date().toLocaleDateString('ru-RU'),
      '{time}': new Date().toLocaleTimeString('ru-RU')
    };

    for (let [variable, value] of Object.entries(variables)) {
      text = text.replace(new RegExp(variable, 'g'), value);
    }

    return text;
  }

  playNotificationSound() {
    try {
      const audio = new Audio(chrome.runtime.getURL('assets/sounds/notification.mp3'));
      audio.volume = 0.5;
      audio.play().catch(e => FunPayUtils.log('Sound error:', e));
    } catch (error) {
      // Звук не критичен
    }
  }

  async addDeliveryTemplate(template) {
    const newTemplate = {
      id: FunPayUtils.generateId(),
      name: template.name,
      text: template.text,
      productFilter: template.productFilter || null,
      enabled: true,
      created: Date.now()
    };

    this.templates.push(newTemplate);
    await this.saveSettings();
    return newTemplate;
  }

  async getOrderStatistics(period = 'day') {
    const history = await FunPayStorage.history.get(1000, 'order');
    const now = Date.now();
    const periods = {
      hour: 3600000,
      day: 86400000,
      week: 604800000,
      month: 2592000000
    };

    const periodMs = periods[period] || periods.day;
    const filtered = history.filter(h => now - h.timestamp < periodMs);

    const stats = {
      total: filtered.length,
      totalAmount: 0,
      averageAmount: 0,
      products: {},
      buyers: {}
    };

    filtered.forEach(order => {
      const amount = FunPayUtils.parsePrice(order.data.amount);
      stats.totalAmount += amount;

      // По товарам
      const product = order.data.product;
      stats.products[product] = (stats.products[product] || 0) + 1;

      // По покупателям
      const buyer = order.data.buyer;
      stats.buyers[buyer] = (stats.buyers[buyer] || 0) + 1;
    });

    stats.averageAmount = stats.total > 0 ? stats.totalAmount / stats.total : 0;

    return stats;
  }

  async saveSettings() {
    await FunPayStorage.settings.set('orderAutomation', {
      enabled: this.enabled,
      autoAccept: this.autoAccept,
      autoComplete: this.autoComplete,
      autoDelivery: this.autoDelivery,
      templates: this.templates
    });
  }
}

// Инициализация
let orderAutomation;
if (FunPayUtils.isFunPayPage()) {
  orderAutomation = new OrderAutomation();
}
