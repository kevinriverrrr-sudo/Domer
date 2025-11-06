/**
 * FunPay Ultimate Pro - Аналитика Продаж
 * Подробная статистика и аналитика продаж
 */

class SalesAnalytics {
  constructor() {
    this.salesData = [];
    this.enabled = true;
    this.init();
  }

  async init() {
    this.salesData = await FunPayStorage.get('salesData', []);
    if (this.enabled) {
      this.startTracking();
    }
  }

  startTracking() {
    // Отслеживание новых продаж
    this.observeSales();
    FunPayUtils.log('Аналитика продаж запущена');
  }

  observeSales() {
    // Наблюдение за страницей заказов
    const ordersContainer = document.querySelector('.orders-list, [class*="orders"]');
    
    if (ordersContainer) {
      this.observer = new MutationObserver(() => {
        this.detectNewSales();
      });

      this.observer.observe(ordersContainer, {
        childList: true,
        subtree: true
      });
    }

    // Периодическая проверка
    setInterval(() => this.detectNewSales(), 60000); // Каждую минуту
  }

  async detectNewSales() {
    const completedOrders = document.querySelectorAll('.order-completed, [data-status="completed"]');
    
    for (let orderEl of completedOrders) {
      const orderId = orderEl.getAttribute('data-order-id') || orderEl.id;
      
      // Проверяем, не записана ли уже эта продажа
      if (!this.salesData.find(s => s.orderId === orderId)) {
        const saleData = this.extractSaleData(orderEl);
        await this.recordSale(saleData);
      }
    }
  }

  extractSaleData(orderElement) {
    return {
      orderId: orderElement.getAttribute('data-order-id') || FunPayUtils.generateId(),
      product: this.extractText(orderElement, '.product-name, .lot-title'),
      amount: FunPayUtils.parsePrice(this.extractText(orderElement, '.amount, .price')),
      buyer: this.extractText(orderElement, '.buyer-name, .username'),
      category: this.extractText(orderElement, '.category'),
      timestamp: Date.now(),
      date: new Date().toISOString()
    };
  }

  extractText(element, selector) {
    const el = element.querySelector(selector);
    return el ? el.textContent.trim() : '';
  }

  async recordSale(saleData) {
    this.salesData.push(saleData);
    
    // Ограничение размера данных
    if (this.salesData.length > 10000) {
      this.salesData = this.salesData.slice(-10000);
    }

    await this.saveSalesData();
    await FunPayStorage.stats.increment('totalSales');
    
    FunPayUtils.log('Новая продажа записана:', saleData);
  }

  // Получение статистики за период
  getStatistics(period = 'day', category = null) {
    const periods = {
      hour: 3600000,
      day: 86400000,
      week: 604800000,
      month: 2592000000,
      year: 31536000000
    };

    const periodMs = periods[period] || periods.day;
    const since = Date.now() - periodMs;

    let filtered = this.salesData.filter(sale => sale.timestamp >= since);
    
    if (category) {
      filtered = filtered.filter(sale => sale.category === category);
    }

    const stats = {
      period,
      totalSales: filtered.length,
      totalRevenue: 0,
      averageOrderValue: 0,
      products: {},
      buyers: {},
      categories: {},
      timeline: this.generateTimeline(filtered, period),
      topProducts: [],
      topBuyers: [],
      hourlyDistribution: this.getHourlyDistribution(filtered),
      dailyDistribution: this.getDailyDistribution(filtered)
    };

    // Расчет метрик
    filtered.forEach(sale => {
      stats.totalRevenue += sale.amount;

      // По продуктам
      if (sale.product) {
        if (!stats.products[sale.product]) {
          stats.products[sale.product] = { count: 0, revenue: 0 };
        }
        stats.products[sale.product].count++;
        stats.products[sale.product].revenue += sale.amount;
      }

      // По покупателям
      if (sale.buyer) {
        if (!stats.buyers[sale.buyer]) {
          stats.buyers[sale.buyer] = { count: 0, revenue: 0 };
        }
        stats.buyers[sale.buyer].count++;
        stats.buyers[sale.buyer].revenue += sale.amount;
      }

      // По категориям
      if (sale.category) {
        if (!stats.categories[sale.category]) {
          stats.categories[sale.category] = { count: 0, revenue: 0 };
        }
        stats.categories[sale.category].count++;
        stats.categories[sale.category].revenue += sale.amount;
      }
    });

    stats.averageOrderValue = stats.totalSales > 0 ? stats.totalRevenue / stats.totalSales : 0;

    // Топ продукты
    stats.topProducts = Object.entries(stats.products)
      .map(([name, data]) => ({ name, ...data }))
      .sort((a, b) => b.revenue - a.revenue)
      .slice(0, 10);

    // Топ покупатели
    stats.topBuyers = Object.entries(stats.buyers)
      .map(([name, data]) => ({ name, ...data }))
      .sort((a, b) => b.revenue - a.revenue)
      .slice(0, 10);

    return stats;
  }

  generateTimeline(sales, period) {
    const timeline = {};
    const intervals = {
      hour: 3600000,
      day: 86400000,
      week: 86400000, // По дням внутри недели
      month: 86400000,
      year: 2592000000 // По месяцам внутри года
    };

    const interval = intervals[period] || intervals.day;

    sales.forEach(sale => {
      const timeKey = Math.floor(sale.timestamp / interval) * interval;
      const date = new Date(timeKey);
      const label = this.formatTimelineLabel(date, period);

      if (!timeline[label]) {
        timeline[label] = { sales: 0, revenue: 0 };
      }

      timeline[label].sales++;
      timeline[label].revenue += sale.amount;
    });

    return timeline;
  }

  formatTimelineLabel(date, period) {
    switch (period) {
      case 'hour':
        return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
      case 'day':
        return date.toLocaleTimeString('ru-RU', { hour: '2-digit' });
      case 'week':
      case 'month':
        return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
      case 'year':
        return date.toLocaleDateString('ru-RU', { month: 'short' });
      default:
        return date.toLocaleString('ru-RU');
    }
  }

  getHourlyDistribution(sales) {
    const distribution = new Array(24).fill(0).map((_, i) => ({
      hour: i,
      sales: 0,
      revenue: 0
    }));

    sales.forEach(sale => {
      const hour = new Date(sale.timestamp).getHours();
      distribution[hour].sales++;
      distribution[hour].revenue += sale.amount;
    });

    return distribution;
  }

  getDailyDistribution(sales) {
    const days = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
    const distribution = days.map((day, i) => ({
      day,
      dayIndex: i,
      sales: 0,
      revenue: 0
    }));

    sales.forEach(sale => {
      const day = new Date(sale.timestamp).getDay();
      distribution[day].sales++;
      distribution[day].revenue += sale.amount;
    });

    return distribution;
  }

  // Прогнозирование
  forecastRevenue(days = 7) {
    const stats = this.getStatistics('month');
    
    if (stats.totalSales === 0) {
      return { forecast: 0, confidence: 0 };
    }

    const daysOfData = this.salesData.length > 0 
      ? (Date.now() - this.salesData[0].timestamp) / 86400000 
      : 1;

    const dailyAverage = stats.totalRevenue / daysOfData;
    const forecast = dailyAverage * days;

    // Расчет доверительного интервала (упрощенный)
    const confidence = Math.min(daysOfData / 30 * 100, 95); // Максимум 95%

    return {
      forecast,
      dailyAverage,
      confidence,
      period: days
    };
  }

  // Конверсионная воронка
  getConversionFunnel() {
    // Здесь должна быть логика сбора данных о воронке
    // Для примера используем заглушки
    return {
      views: 1000,
      clicks: 300,
      orders: 100,
      completed: 80,
      conversionRate: {
        viewToClick: 30,
        clickToOrder: 33.33,
        orderToComplete: 80,
        overall: 8
      }
    };
  }

  // Анализ трендов
  analyzeTrends() {
    const currentWeek = this.getStatistics('week');
    const previousWeek = this.getStatistics('week'); // Здесь нужна логика для предыдущей недели
    
    const trends = {
      salesGrowth: 0,
      revenueGrowth: 0,
      avgOrderGrowth: 0,
      trend: 'stable'
    };

    if (previousWeek.totalSales > 0) {
      trends.salesGrowth = ((currentWeek.totalSales - previousWeek.totalSales) / previousWeek.totalSales) * 100;
      trends.revenueGrowth = ((currentWeek.totalRevenue - previousWeek.totalRevenue) / previousWeek.totalRevenue) * 100;
      trends.avgOrderGrowth = ((currentWeek.averageOrderValue - previousWeek.averageOrderValue) / previousWeek.averageOrderValue) * 100;
      
      if (trends.revenueGrowth > 10) trends.trend = 'growing';
      else if (trends.revenueGrowth < -10) trends.trend = 'declining';
    }

    return trends;
  }

  // Сегментация покупателей
  segmentCustomers() {
    const buyers = {};

    this.salesData.forEach(sale => {
      if (!buyers[sale.buyer]) {
        buyers[sale.buyer] = {
          name: sale.buyer,
          purchases: 0,
          totalSpent: 0,
          firstPurchase: sale.timestamp,
          lastPurchase: sale.timestamp
        };
      }

      const buyer = buyers[sale.buyer];
      buyer.purchases++;
      buyer.totalSpent += sale.amount;
      if (sale.timestamp > buyer.lastPurchase) buyer.lastPurchase = sale.timestamp;
    });

    const segments = {
      vip: [],        // 10+ покупок
      regular: [],    // 5-9 покупок
      occasional: [], // 2-4 покупки
      oneTime: []     // 1 покупка
    };

    Object.values(buyers).forEach(buyer => {
      if (buyer.purchases >= 10) segments.vip.push(buyer);
      else if (buyer.purchases >= 5) segments.regular.push(buyer);
      else if (buyer.purchases >= 2) segments.occasional.push(buyer);
      else segments.oneTime.push(buyer);
    });

    return segments;
  }

  // Экспорт данных
  async exportSalesData(format = 'json', period = 'month') {
    const stats = this.getStatistics(period);
    
    if (format === 'csv') {
      return this.exportToCSV(stats);
    } else {
      return {
        statistics: stats,
        rawData: this.salesData,
        exportDate: new Date().toISOString()
      };
    }
  }

  exportToCSV(stats) {
    const headers = ['Дата', 'Продукт', 'Покупатель', 'Сумма', 'Категория'];
    const rows = this.salesData.map(sale => [
      new Date(sale.timestamp).toLocaleString('ru-RU'),
      sale.product,
      sale.buyer,
      sale.amount,
      sale.category
    ]);

    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }

  async saveSalesData() {
    await FunPayStorage.set('salesData', this.salesData);
  }
}

// Инициализация
let salesAnalytics;
if (FunPayUtils.isFunPayPage()) {
  salesAnalytics = new SalesAnalytics();
}
