// Модуль аналитики
class AnalyticsManager {
  constructor() {
    this.data = {
      sales: [],
      buyers: [],
      revenue: 0,
      totalSales: 0,
      startDate: new Date().toISOString()
    };
  }

  async init() {
    await this.loadData();
    this.startTracking();
  }

  async loadData() {
    return new Promise((resolve) => {
      chrome.storage.local.get(['analyticsData'], (result) => {
        if (result.analyticsData) {
          this.data = { ...this.data, ...result.analyticsData };
        }
        resolve();
      });
    });
  }

  async saveData() {
    return new Promise((resolve) => {
      chrome.storage.local.set({ analyticsData: this.data }, resolve);
    });
  }

  startTracking() {
    // Отслеживание продаж
    this.trackSales();
    
    // Отслеживание покупателей
    this.trackBuyers();
    
    // Отслеживание прибыли
    this.trackRevenue();
  }

  trackSales() {
    // Наблюдение за новыми продажами
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (this.isSaleElement(node)) {
            this.processSale(node);
          }
        });
      });
    });

    const salesContainer = document.querySelector('.sales-container, .orders-list');
    if (salesContainer) {
      observer.observe(salesContainer, { childList: true, subtree: true });
    }
  }

  isSaleElement(element) {
    return element.nodeType === 1 && 
           (element.classList.contains('order') || 
            element.classList.contains('sale-item') ||
            element.querySelector('.order'));
  }

  processSale(element) {
    try {
      const saleData = this.extractSaleData(element);
      if (saleData) {
        this.data.sales.push({
          ...saleData,
          timestamp: new Date().toISOString()
        });
        this.data.totalSales++;
        this.saveData();
      }
    } catch (error) {
      console.error('Ошибка обработки продажи:', error);
    }
  }

  extractSaleData(element) {
    const priceElement = element.querySelector('.price, [data-price]');
    const buyerElement = element.querySelector('.buyer, .username');
    const gameElement = element.querySelector('.game-name, .lot-title');
    
    if (!priceElement) return null;

    const priceText = priceElement.textContent.trim();
    const price = this.parsePrice(priceText);
    
    return {
      price: price,
      buyer: buyerElement ? buyerElement.textContent.trim() : 'Неизвестно',
      game: gameElement ? gameElement.textContent.trim() : 'Неизвестно',
      id: this.generateSaleId()
    };
  }

  parsePrice(priceText) {
    // Парсинг цены (удаляем валюту, пробелы и т.д.)
    const match = priceText.match(/[\d.,]+/);
    if (match) {
      return parseFloat(match[0].replace(/\s/g, '').replace(',', '.'));
    }
    return 0;
  }

  trackBuyers() {
    // Сбор статистики по покупателям
    const buyersMap = new Map();
    
    this.data.sales.forEach(sale => {
      const buyer = sale.buyer;
      if (!buyersMap.has(buyer)) {
        buyersMap.set(buyer, {
          name: buyer,
          totalPurchases: 0,
          totalSpent: 0
        });
      }
      
      const buyerData = buyersMap.get(buyer);
      buyerData.totalPurchases++;
      buyerData.totalSpent += sale.price;
    });
    
    this.data.buyers = Array.from(buyersMap.values());
  }

  trackRevenue() {
    this.data.revenue = this.data.sales.reduce((sum, sale) => sum + sale.price, 0);
  }

  generateSaleId() {
    return `sale-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  getStats() {
    return {
      totalSales: this.data.totalSales,
      totalRevenue: this.data.revenue,
      averageOrderValue: this.data.totalSales > 0 ? this.data.revenue / this.data.totalSales : 0,
      uniqueBuyers: this.data.buyers.length,
      topBuyers: this.data.buyers.sort((a, b) => b.totalSpent - a.totalSpent).slice(0, 10)
    };
  }

  exportData(format = 'json') {
    if (format === 'json') {
      return JSON.stringify(this.data, null, 2);
    } else if (format === 'csv') {
      return this.convertToCSV();
    }
  }

  convertToCSV() {
    const headers = ['Дата', 'Покупатель', 'Игра', 'Цена'];
    const rows = this.data.sales.map(sale => [
      sale.timestamp,
      sale.buyer,
      sale.game,
      sale.price
    ]);
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }
}

// Экспорт для использования в других модулях
if (typeof window !== 'undefined') {
  window.AnalyticsManager = AnalyticsManager;
}
