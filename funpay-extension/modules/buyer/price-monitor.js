/**
 * FunPay Ultimate Pro - Мониторинг Цен
 * Отслеживание изменений цен на товары
 */

class PriceMonitor {
  constructor() {
    this.enabled = false;
    this.monitoredItems = new Map();
    this.priceHistory = new Map();
    this.alerts = [];
    this.init();
  }

  async init() {
    const settings = await FunPayStorage.settings.get('priceMonitor');
    if (settings) {
      this.enabled = settings.enabled;
      this.alerts = settings.alerts || [];
    }

    // Загрузка истории цен
    const history = await FunPayStorage.get('priceHistory', {});
    this.priceHistory = new Map(Object.entries(history));

    if (this.enabled) {
      this.start();
    }
  }

  start() {
    this.enabled = true;
    this.startMonitoring();
    FunPayUtils.log('Мониторинг цен запущен');
  }

  stop() {
    this.enabled = false;
    if (this.monitorInterval) {
      clearInterval(this.monitorInterval);
    }
    FunPayUtils.log('Мониторинг цен остановлен');
  }

  startMonitoring() {
    // Проверка каждые 5 минут
    this.monitorInterval = setInterval(() => {
      this.checkPrices();
    }, 5 * 60 * 1000);

    // Первая проверка
    this.checkPrices();
  }

  async checkPrices() {
    if (!this.enabled) return;

    FunPayUtils.log('Проверка цен...');

    for (let [itemId, item] of this.monitoredItems) {
      try {
        const currentPrice = await this.fetchCurrentPrice(itemId);
        
        if (currentPrice !== null) {
          await this.updatePrice(itemId, currentPrice);
          await this.checkAlerts(itemId, currentPrice);
        }
      } catch (error) {
        FunPayUtils.log(`Ошибка проверки цены для ${itemId}:`, error, 'error');
      }
    }
  }

  async fetchCurrentPrice(itemId) {
    // Поиск элемента на странице
    const itemElement = document.querySelector(`[data-id="${itemId}"], [data-offer-id="${itemId}"]`);
    
    if (itemElement) {
      const priceElement = itemElement.querySelector('.price, .tc-price');
      if (priceElement) {
        return FunPayUtils.parsePrice(priceElement.textContent);
      }
    }

    // Если на странице нет, берем из кэша
    const cached = this.priceHistory.get(itemId);
    return cached?.prices[cached.prices.length - 1]?.price || null;
  }

  async updatePrice(itemId, newPrice) {
    let history = this.priceHistory.get(itemId) || {
      itemId,
      prices: []
    };

    const lastPrice = history.prices[history.prices.length - 1];
    
    // Добавляем только если цена изменилась
    if (!lastPrice || lastPrice.price !== newPrice) {
      history.prices.push({
        price: newPrice,
        timestamp: Date.now()
      });

      // Ограничение истории
      if (history.prices.length > 100) {
        history.prices = history.prices.slice(-100);
      }

      this.priceHistory.set(itemId, history);
      await this.savePriceHistory();

      // Логирование изменения
      if (lastPrice) {
        const change = newPrice - lastPrice.price;
        const changePercent = (change / lastPrice.price) * 100;
        
        FunPayUtils.log(`Цена изменилась: ${itemId}`, {
          old: lastPrice.price,
          new: newPrice,
          change,
          changePercent: changePercent.toFixed(2) + '%'
        });
      }
    }
  }

  async checkAlerts(itemId, currentPrice) {
    const item = this.monitoredItems.get(itemId);
    if (!item) return;

    for (let alert of this.alerts) {
      if (!alert.enabled || alert.itemId !== itemId) continue;

      let triggered = false;
      let message = '';

      switch (alert.type) {
        case 'below':
          if (currentPrice < alert.targetPrice) {
            triggered = true;
            message = `Цена упала ниже ${FunPayUtils.formatPrice(alert.targetPrice)}!`;
          }
          break;

        case 'above':
          if (currentPrice > alert.targetPrice) {
            triggered = true;
            message = `Цена поднялась выше ${FunPayUtils.formatPrice(alert.targetPrice)}!`;
          }
          break;

        case 'change':
          const history = this.priceHistory.get(itemId);
          if (history && history.prices.length >= 2) {
            const prevPrice = history.prices[history.prices.length - 2].price;
            const change = Math.abs(currentPrice - prevPrice);
            const changePercent = (change / prevPrice) * 100;
            
            if (changePercent >= alert.changePercent) {
              triggered = true;
              message = `Цена изменилась на ${changePercent.toFixed(2)}%!`;
            }
          }
          break;
      }

      if (triggered) {
        await this.triggerAlert(alert, item, currentPrice, message);
      }
    }
  }

  async triggerAlert(alert, item, price, message) {
    FunPayUtils.notify(
      'Уведомление о цене',
      `${item.title}: ${message}\nТекущая цена: ${FunPayUtils.formatPrice(price)}`,
      'info'
    );

    // Сохранение в истории
    await FunPayStorage.history.add('price_alert', {
      alert: alert.name,
      item: item.title,
      price,
      message
    });

    await FunPayStorage.stats.increment('priceAlerts');

    // Отключаем алерт если он одноразовый
    if (alert.once) {
      alert.enabled = false;
      await this.saveSettings();
    }
  }

  async addMonitoredItem(item) {
    const itemId = item.id || FunPayUtils.generateId();
    
    const monitoredItem = {
      id: itemId,
      title: item.title,
      url: item.url || window.location.href,
      seller: item.seller || '',
      category: item.category || '',
      added: Date.now()
    };

    this.monitoredItems.set(itemId, monitoredItem);
    
    // Сохранение начальной цены
    if (item.currentPrice) {
      await this.updatePrice(itemId, item.currentPrice);
    }

    await this.saveSettings();
    return monitoredItem;
  }

  async removeMonitoredItem(itemId) {
    this.monitoredItems.delete(itemId);
    this.priceHistory.delete(itemId);
    
    // Удаляем связанные алерты
    this.alerts = this.alerts.filter(a => a.itemId !== itemId);
    
    await this.saveSettings();
    await this.savePriceHistory();
  }

  async addAlert(alert) {
    const newAlert = {
      id: FunPayUtils.generateId(),
      name: alert.name,
      itemId: alert.itemId,
      type: alert.type, // 'below', 'above', 'change'
      targetPrice: alert.targetPrice || null,
      changePercent: alert.changePercent || null,
      enabled: true,
      once: alert.once || false,
      created: Date.now()
    };

    this.alerts.push(newAlert);
    await this.saveSettings();
    return newAlert;
  }

  async removeAlert(alertId) {
    this.alerts = this.alerts.filter(a => a.id !== alertId);
    await this.saveSettings();
  }

  getPriceStatistics(itemId) {
    const history = this.priceHistory.get(itemId);
    if (!history || history.prices.length === 0) {
      return null;
    }

    const prices = history.prices.map(p => p.price);
    const current = prices[prices.length - 1];
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const avg = prices.reduce((a, b) => a + b) / prices.length;

    return {
      current,
      min,
      max,
      average: avg,
      samples: prices.length,
      trend: this.calculateTrend(prices),
      history: history.prices
    };
  }

  calculateTrend(prices) {
    if (prices.length < 2) return 'stable';

    const recent = prices.slice(-10); // Последние 10 замеров
    const oldAvg = recent.slice(0, 5).reduce((a, b) => a + b) / 5;
    const newAvg = recent.slice(-5).reduce((a, b) => a + b) / 5;

    const change = ((newAvg - oldAvg) / oldAvg) * 100;

    if (change > 5) return 'rising';
    if (change < -5) return 'falling';
    return 'stable';
  }

  async getPriceGraph(itemId, period = 'week') {
    const history = this.priceHistory.get(itemId);
    if (!history) return null;

    const periods = {
      day: 86400000,
      week: 604800000,
      month: 2592000000
    };

    const periodMs = periods[period] || periods.week;
    const since = Date.now() - periodMs;

    const filtered = history.prices.filter(p => p.timestamp >= since);

    return {
      labels: filtered.map(p => new Date(p.timestamp).toLocaleString('ru-RU')),
      data: filtered.map(p => p.price)
    };
  }

  async savePriceHistory() {
    const historyObject = Object.fromEntries(this.priceHistory);
    await FunPayStorage.set('priceHistory', historyObject);
  }

  async saveSettings() {
    const monitoredItemsArray = Array.from(this.monitoredItems.values());
    
    await FunPayStorage.settings.set('priceMonitor', {
      enabled: this.enabled,
      monitoredItems: monitoredItemsArray,
      alerts: this.alerts
    });
  }
}

// Инициализация
let priceMonitor;
if (FunPayUtils.isFunPayPage()) {
  priceMonitor = new PriceMonitor();
}
