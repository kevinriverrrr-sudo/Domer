/**
 * FunPay Ultimate Pro - Трекер Конкурентов
 * Мониторинг и аналитика конкурентов
 */

class CompetitorTracker {
  constructor() {
    this.competitors = [];
    this.trackingData = new Map();
    this.enabled = false;
    this.init();
  }

  async init() {
    const settings = await FunPayStorage.settings.get('competitorTracker');
    if (settings) {
      this.competitors = settings.competitors || [];
      this.enabled = settings.enabled || false;
    }

    // Загрузка данных трекинга
    const data = await FunPayStorage.get('competitorTrackingData', {});
    this.trackingData = new Map(Object.entries(data));

    if (this.enabled) {
      this.start();
    }
  }

  start() {
    this.enabled = true;
    this.startTracking();
    FunPayUtils.log('Трекинг конкурентов запущен');
  }

  stop() {
    this.enabled = false;
    if (this.trackingInterval) {
      clearInterval(this.trackingInterval);
    }
    FunPayUtils.log('Трекинг конкурентов остановлен');
  }

  startTracking() {
    // Отслеживание каждые 10 минут
    this.trackingInterval = setInterval(() => {
      this.trackAllCompetitors();
    }, 10 * 60 * 1000);

    // Первый трекинг
    this.trackAllCompetitors();
  }

  async trackAllCompetitors() {
    if (!this.enabled) return;

    FunPayUtils.log('Обновление данных о конкурентах...');

    for (let competitor of this.competitors) {
      if (!competitor.enabled) continue;

      try {
        const data = await this.trackCompetitor(competitor);
        await this.saveCompetitorData(competitor.id, data);
      } catch (error) {
        FunPayUtils.log(`Ошибка трекинга ${competitor.name}:`, error, 'error');
      }

      // Задержка между запросами
      await FunPayUtils.randomDelay(2000, 5000);
    }

    await FunPayStorage.stats.increment('competitorChecks');
  }

  async trackCompetitor(competitor) {
    const data = {
      id: competitor.id,
      name: competitor.name,
      timestamp: Date.now(),
      lots: [],
      prices: [],
      stats: {}
    };

    // Парсинг данных со страницы конкурента
    const competitorLots = this.findCompetitorLots(competitor.userId);
    
    for (let lot of competitorLots) {
      const lotData = {
        id: lot.id,
        title: lot.title,
        price: lot.price,
        inStock: lot.inStock,
        category: lot.category,
        timestamp: Date.now()
      };

      data.lots.push(lotData);
      data.prices.push(lot.price);
    }

    // Статистика
    data.stats = {
      totalLots: data.lots.length,
      averagePrice: data.prices.length > 0 
        ? data.prices.reduce((a, b) => a + b) / data.prices.length 
        : 0,
      minPrice: data.prices.length > 0 ? Math.min(...data.prices) : 0,
      maxPrice: data.prices.length > 0 ? Math.max(...data.prices) : 0,
      inStockCount: data.lots.filter(l => l.inStock).length
    };

    return data;
  }

  findCompetitorLots(userId) {
    const lots = [];
    const lotElements = document.querySelectorAll(`.tc-item[data-user-id="${userId}"], .offer-list-item`);

    lotElements.forEach(el => {
      // Проверяем, принадлежит ли лот конкуренту
      const sellerLink = el.querySelector('a[href*="/users/"]');
      if (sellerLink && sellerLink.href.includes(userId)) {
        const lot = {
          id: el.getAttribute('data-id') || el.getAttribute('data-offer-id'),
          title: this.extractText(el, '.tc-title, .offer-title'),
          price: FunPayUtils.parsePrice(this.extractText(el, '.tc-price, .price')),
          inStock: !el.classList.contains('out-of-stock'),
          category: this.extractText(el, '.tc-category, .category'),
          element: el
        };

        if (lot.id) {
          lots.push(lot);
        }
      }
    });

    return lots;
  }

  extractText(element, selector) {
    const el = element.querySelector(selector);
    return el ? el.textContent.trim() : '';
  }

  async saveCompetitorData(competitorId, data) {
    let history = this.trackingData.get(competitorId) || {
      competitorId,
      snapshots: []
    };

    history.snapshots.push(data);

    // Ограничение истории (последние 100 снимков)
    if (history.snapshots.length > 100) {
      history.snapshots = history.snapshots.slice(-100);
    }

    this.trackingData.set(competitorId, history);
    await this.saveTrackingData();

    // Анализ изменений
    await this.analyzeChanges(competitorId, history);
  }

  async analyzeChanges(competitorId, history) {
    if (history.snapshots.length < 2) return;

    const current = history.snapshots[history.snapshots.length - 1];
    const previous = history.snapshots[history.snapshots.length - 2];

    const changes = {
      newLots: [],
      removedLots: [],
      priceChanges: [],
      stockChanges: []
    };

    // Новые лоты
    const previousLotIds = new Set(previous.lots.map(l => l.id));
    const currentLotIds = new Set(current.lots.map(l => l.id));

    current.lots.forEach(lot => {
      if (!previousLotIds.has(lot.id)) {
        changes.newLots.push(lot);
      }
    });

    // Удаленные лоты
    previous.lots.forEach(lot => {
      if (!currentLotIds.has(lot.id)) {
        changes.removedLots.push(lot);
      }
    });

    // Изменения цен
    current.lots.forEach(lot => {
      const oldLot = previous.lots.find(l => l.id === lot.id);
      if (oldLot && oldLot.price !== lot.price) {
        changes.priceChanges.push({
          lot: lot.title,
          oldPrice: oldLot.price,
          newPrice: lot.price,
          change: lot.price - oldLot.price,
          changePercent: ((lot.price - oldLot.price) / oldLot.price) * 100
        });
      }
    });

    // Уведомления о значимых изменениях
    if (changes.newLots.length > 0) {
      FunPayUtils.notify(
        'Конкурент добавил лоты',
        `${current.name}: ${changes.newLots.length} новых лотов`,
        'info'
      );
    }

    if (changes.priceChanges.length > 0) {
      const significantChanges = changes.priceChanges.filter(c => Math.abs(c.changePercent) > 10);
      if (significantChanges.length > 0) {
        FunPayUtils.notify(
          'Конкурент изменил цены',
          `${current.name}: ${significantChanges.length} значительных изменений`,
          'warning'
        );
      }
    }

    // Сохранение в истории
    await FunPayStorage.history.add('competitor_changes', {
      competitor: current.name,
      changes
    });
  }

  async addCompetitor(competitor) {
    const newCompetitor = {
      id: FunPayUtils.generateId(),
      name: competitor.name,
      userId: competitor.userId,
      url: competitor.url || '',
      category: competitor.category || '',
      enabled: true,
      added: Date.now()
    };

    this.competitors.push(newCompetitor);
    await this.saveSettings();
    return newCompetitor;
  }

  async removeCompetitor(competitorId) {
    this.competitors = this.competitors.filter(c => c.id !== competitorId);
    this.trackingData.delete(competitorId);
    await this.saveSettings();
    await this.saveTrackingData();
  }

  async toggleCompetitor(competitorId) {
    const competitor = this.competitors.find(c => c.id === competitorId);
    if (competitor) {
      competitor.enabled = !competitor.enabled;
      await this.saveSettings();
      return competitor.enabled;
    }
    return false;
  }

  getCompetitorStatistics(competitorId, period = 'week') {
    const history = this.trackingData.get(competitorId);
    if (!history || history.snapshots.length === 0) {
      return null;
    }

    const periods = {
      day: 86400000,
      week: 604800000,
      month: 2592000000
    };

    const periodMs = periods[period] || periods.week;
    const since = Date.now() - periodMs;
    const snapshots = history.snapshots.filter(s => s.timestamp >= since);

    if (snapshots.length === 0) return null;

    const stats = {
      competitor: snapshots[0].name,
      period,
      snapshots: snapshots.length,
      averageLots: 0,
      averagePrice: 0,
      priceRange: { min: Infinity, max: 0 },
      lotTurnover: 0,
      activity: this.calculateActivity(snapshots)
    };

    // Расчет средних значений
    let totalLots = 0;
    let totalPrices = 0;
    let priceCount = 0;

    snapshots.forEach(snapshot => {
      totalLots += snapshot.stats.totalLots;
      
      snapshot.prices.forEach(price => {
        totalPrices += price;
        priceCount++;
        if (price < stats.priceRange.min) stats.priceRange.min = price;
        if (price > stats.priceRange.max) stats.priceRange.max = price;
      });
    });

    stats.averageLots = totalLots / snapshots.length;
    stats.averagePrice = priceCount > 0 ? totalPrices / priceCount : 0;

    // Оборот лотов (сколько лотов добавлено/удалено)
    const allLotIds = new Set();
    snapshots.forEach(s => s.lots.forEach(l => allLotIds.add(l.id)));
    stats.lotTurnover = allLotIds.size;

    return stats;
  }

  calculateActivity(snapshots) {
    if (snapshots.length < 2) return 'low';

    let changes = 0;
    for (let i = 1; i < snapshots.length; i++) {
      const prev = snapshots[i - 1];
      const curr = snapshots[i];

      // Подсчет изменений
      if (prev.stats.totalLots !== curr.stats.totalLots) changes++;
      if (Math.abs(prev.stats.averagePrice - curr.stats.averagePrice) > 10) changes++;
    }

    const changeRate = changes / snapshots.length;
    if (changeRate > 0.5) return 'high';
    if (changeRate > 0.2) return 'medium';
    return 'low';
  }

  async compareWithOwnPrices() {
    const comparison = {
      competitors: [],
      myAveragePrice: await this.getMyAveragePrice(),
      recommendations: []
    };

    for (let competitor of this.competitors) {
      if (!competitor.enabled) continue;

      const stats = this.getCompetitorStatistics(competitor.id, 'day');
      if (stats) {
        comparison.competitors.push({
          name: competitor.name,
          averagePrice: stats.averagePrice,
          difference: stats.averagePrice - comparison.myAveragePrice,
          differencePercent: ((stats.averagePrice - comparison.myAveragePrice) / comparison.myAveragePrice) * 100
        });
      }
    }

    // Сортировка по цене
    comparison.competitors.sort((a, b) => a.averagePrice - b.averagePrice);

    // Рекомендации
    if (comparison.competitors.length > 0) {
      const cheapest = comparison.competitors[0];
      const mostExpensive = comparison.competitors[comparison.competitors.length - 1];

      if (comparison.myAveragePrice > cheapest.averagePrice) {
        comparison.recommendations.push({
          type: 'price_too_high',
          message: `Ваши цены выше минимальных на ${Math.abs(cheapest.differencePercent).toFixed(2)}%`,
          action: 'Рассмотрите снижение цен для конкурентоспособности'
        });
      }

      if (comparison.myAveragePrice < mostExpensive.averagePrice * 0.7) {
        comparison.recommendations.push({
          type: 'price_too_low',
          message: 'Ваши цены значительно ниже рынка',
          action: 'Возможно, стоит повысить цены'
        });
      }
    }

    return comparison;
  }

  async getMyAveragePrice() {
    // Получение средней цены своих товаров
    const myLots = document.querySelectorAll('.my-lot, .tc-item.own');
    const prices = [];

    myLots.forEach(lot => {
      const priceEl = lot.querySelector('.price, .tc-price');
      if (priceEl) {
        prices.push(FunPayUtils.parsePrice(priceEl.textContent));
      }
    });

    return prices.length > 0 ? prices.reduce((a, b) => a + b) / prices.length : 0;
  }

  async exportCompetitorData(competitorId) {
    const history = this.trackingData.get(competitorId);
    const competitor = this.competitors.find(c => c.id === competitorId);

    if (!history || !competitor) return null;

    return {
      competitor,
      history: history.snapshots,
      statistics: this.getCompetitorStatistics(competitorId, 'month'),
      exportDate: new Date().toISOString()
    };
  }

  async saveTrackingData() {
    const dataObject = Object.fromEntries(this.trackingData);
    await FunPayStorage.set('competitorTrackingData', dataObject);
  }

  async saveSettings() {
    await FunPayStorage.settings.set('competitorTracker', {
      enabled: this.enabled,
      competitors: this.competitors
    });
  }
}

// Инициализация
let competitorTracker;
if (FunPayUtils.isFunPayPage()) {
  competitorTracker = new CompetitorTracker();
}
