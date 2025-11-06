/**
 * FunPay Ultimate Pro - Менеджер Цен
 * Автоматическое управление ценами на товары
 */

class PriceManager {
  constructor() {
    this.priceRules = [];
    this.monitoredLots = new Map();
    this.competitorPrices = new Map();
    this.init();
  }

  async init() {
    const rules = await FunPayStorage.get('priceRules', []);
    this.priceRules = rules;
    
    // Запуск мониторинга
    this.startMonitoring();
  }

  /**
   * Добавление правила цены
   */
  async addRule(rule) {
    const newRule = {
      id: FunPayUtils.generateId(),
      name: rule.name,
      lotId: rule.lotId,
      strategy: rule.strategy, // 'fixed', 'percent', 'competitor', 'dynamic'
      value: rule.value,
      min: rule.min,
      max: rule.max,
      enabled: true,
      created: Date.now()
    };

    this.priceRules.push(newRule);
    await this.saveRules();
    return newRule;
  }

  /**
   * Стратегия: Фиксированная цена
   */
  async applyFixedPrice(lotId, price) {
    await this.updateLotPrice(lotId, price);
    FunPayUtils.log(`Установлена фиксированная цена ${price} для лота ${lotId}`);
  }

  /**
   * Стратегия: Процент от базовой цены
   */
  async applyPercentPrice(lotId, basePrice, percent) {
    const newPrice = basePrice * (1 + percent / 100);
    const finalPrice = Math.max(0, newPrice);
    await this.updateLotPrice(lotId, finalPrice);
    FunPayUtils.log(`Цена изменена на ${percent}%: ${finalPrice}`);
  }

  /**
   * Стратегия: Цена на основе конкурентов
   */
  async applyCompetitorPrice(lotId, strategy = 'lowest') {
    const competitorPrices = await this.getCompetitorPrices(lotId);
    
    if (competitorPrices.length === 0) {
      FunPayUtils.log('Нет данных о ценах конкурентов');
      return;
    }

    let targetPrice;
    switch (strategy) {
      case 'lowest':
        targetPrice = Math.min(...competitorPrices) - 1;
        break;
      case 'average':
        targetPrice = competitorPrices.reduce((a, b) => a + b) / competitorPrices.length;
        break;
      case 'highest':
        targetPrice = Math.max(...competitorPrices);
        break;
      case 'below_average':
        const avg = competitorPrices.reduce((a, b) => a + b) / competitorPrices.length;
        targetPrice = avg * 0.95; // На 5% ниже среднего
        break;
    }

    await this.updateLotPrice(lotId, targetPrice);
    FunPayUtils.log(`Цена установлена по стратегии ${strategy}: ${targetPrice}`);
  }

  /**
   * Динамическое ценообразование
   */
  async applyDynamicPricing(lotId, factors) {
    const stats = await this.getLotStats(lotId);
    let priceMultiplier = 1;

    // Фактор спроса
    if (stats.views > 100) priceMultiplier += 0.1;
    if (stats.views > 500) priceMultiplier += 0.15;

    // Фактор продаж
    if (stats.sales > 10) priceMultiplier += 0.05;
    if (stats.sales > 50) priceMultiplier += 0.1;

    // Время суток
    const hour = new Date().getHours();
    if (hour >= 18 && hour <= 23) priceMultiplier += 0.05; // Пиковое время

    // День недели
    const day = new Date().getDay();
    if (day === 0 || day === 6) priceMultiplier += 0.05; // Выходные

    // Конкуренция
    const competitors = await this.getActiveCompetitors(lotId);
    if (competitors < 5) priceMultiplier += 0.1; // Мало конкурентов

    const basePrice = stats.basePrice || 100;
    const newPrice = basePrice * priceMultiplier;

    await this.updateLotPrice(lotId, newPrice);
    FunPayUtils.log(`Динамическая цена: ${newPrice} (множитель: ${priceMultiplier})`);
  }

  /**
   * Массовое изменение цен
   */
  async bulkPriceChange(lotIds, operation, value) {
    const results = [];
    
    for (let lotId of lotIds) {
      try {
        const currentPrice = await this.getCurrentPrice(lotId);
        let newPrice;

        switch (operation) {
          case 'increase':
            newPrice = currentPrice + value;
            break;
          case 'decrease':
            newPrice = currentPrice - value;
            break;
          case 'multiply':
            newPrice = currentPrice * value;
            break;
          case 'set':
            newPrice = value;
            break;
          case 'increase_percent':
            newPrice = currentPrice * (1 + value / 100);
            break;
          case 'decrease_percent':
            newPrice = currentPrice * (1 - value / 100);
            break;
        }

        newPrice = Math.max(0, newPrice); // Не допускаем отрицательные цены
        await this.updateLotPrice(lotId, newPrice);
        
        results.push({
          lotId,
          oldPrice: currentPrice,
          newPrice,
          success: true
        });

        await FunPayUtils.randomDelay(500, 1500); // Задержка между обновлениями
      } catch (error) {
        results.push({
          lotId,
          success: false,
          error: error.message
        });
      }
    }

    await FunPayStorage.history.add('bulk_price_change', { results });
    return results;
  }

  /**
   * Обновление цены лота
   */
  async updateLotPrice(lotId, newPrice) {
    // Применение минимальных и максимальных ограничений
    const rule = this.priceRules.find(r => r.lotId === lotId);
    if (rule) {
      if (rule.min && newPrice < rule.min) newPrice = rule.min;
      if (rule.max && newPrice > rule.max) newPrice = rule.max;
    }

    // Округление до 2 знаков
    newPrice = Math.round(newPrice * 100) / 100;

    // Отправка запроса на обновление цены
    try {
      // Здесь должен быть реальный API запрос к FunPay
      // Пример: await this.sendPriceUpdateRequest(lotId, newPrice);
      
      this.monitoredLots.set(lotId, {
        price: newPrice,
        updated: Date.now()
      });

      // Уведомление
      FunPayUtils.notify(
        'Цена обновлена',
        `Лот ${lotId}: новая цена ${FunPayUtils.formatPrice(newPrice)}`,
        'success'
      );

      // Статистика
      await FunPayStorage.stats.increment('priceUpdates');
      
      return true;
    } catch (error) {
      FunPayUtils.log('Ошибка обновления цены:', error, 'error');
      return false;
    }
  }

  /**
   * Получение текущей цены лота
   */
  async getCurrentPrice(lotId) {
    // Попытка получить из кэша
    const cached = this.monitoredLots.get(lotId);
    if (cached && Date.now() - cached.updated < 60000) {
      return cached.price;
    }

    // Получение с страницы
    const priceElement = document.querySelector(`[data-lot-id="${lotId}"] .price, .lot-price`);
    if (priceElement) {
      return FunPayUtils.parsePrice(priceElement.textContent);
    }

    return 0;
  }

  /**
   * Получение цен конкурентов
   */
  async getCompetitorPrices(lotId) {
    // Здесь должна быть логика парсинга цен конкурентов
    // Возвращаем данные из кэша или парсим страницу
    const cached = await FunPayStorage.cache.get(`competitor_prices_${lotId}`);
    if (cached) return cached;

    // Парсинг цен с страницы категории
    const prices = [];
    const priceElements = document.querySelectorAll('.tc-item .tc-price, .offer-list-item .price');
    
    priceElements.forEach(el => {
      const price = FunPayUtils.parsePrice(el.textContent);
      if (price > 0) prices.push(price);
    });

    // Кэширование на 5 минут
    await FunPayStorage.cache.set(`competitor_prices_${lotId}`, prices);
    
    return prices;
  }

  /**
   * Статистика лота
   */
  async getLotStats(lotId) {
    const stats = await FunPayStorage.get(`lot_stats_${lotId}`, {
      views: 0,
      sales: 0,
      basePrice: 0,
      lastUpdate: 0
    });
    return stats;
  }

  /**
   * Активные конкуренты
   */
  async getActiveCompetitors(lotId) {
    // Подсчет конкурентов в той же категории
    const competitorElements = document.querySelectorAll('.tc-item, .offer-list-item');
    return competitorElements.length;
  }

  /**
   * Мониторинг цен
   */
  startMonitoring() {
    // Проверка правил каждые 5 минут
    setInterval(async () => {
      for (let rule of this.priceRules) {
        if (!rule.enabled) continue;

        try {
          switch (rule.strategy) {
            case 'fixed':
              await this.applyFixedPrice(rule.lotId, rule.value);
              break;
            case 'percent':
              const basePrice = await this.getCurrentPrice(rule.lotId);
              await this.applyPercentPrice(rule.lotId, basePrice, rule.value);
              break;
            case 'competitor':
              await this.applyCompetitorPrice(rule.lotId, rule.value);
              break;
            case 'dynamic':
              await this.applyDynamicPricing(rule.lotId, rule.value);
              break;
          }
        } catch (error) {
          FunPayUtils.log(`Ошибка применения правила ${rule.name}:`, error, 'error');
        }
      }
    }, 5 * 60 * 1000); // 5 минут
  }

  /**
   * Анализ оптимальной цены
   */
  async analyzePriceOptimization(lotId) {
    const stats = await this.getLotStats(lotId);
    const competitorPrices = await this.getCompetitorPrices(lotId);
    
    const analysis = {
      currentPrice: stats.basePrice,
      competitorMin: Math.min(...competitorPrices),
      competitorMax: Math.max(...competitorPrices),
      competitorAvg: competitorPrices.reduce((a, b) => a + b) / competitorPrices.length,
      recommended: 0,
      reasoning: []
    };

    // Рекомендация на основе анализа
    if (stats.views < 10) {
      analysis.recommended = analysis.competitorMin * 0.95;
      analysis.reasoning.push('Мало просмотров - рекомендуется снизить цену');
    } else if (stats.sales > 20) {
      analysis.recommended = analysis.currentPrice * 1.1;
      analysis.reasoning.push('Высокие продажи - можно повысить цену');
    } else {
      analysis.recommended = analysis.competitorAvg;
      analysis.reasoning.push('Рекомендуется средняя рыночная цена');
    }

    return analysis;
  }

  /**
   * Экспорт правил
   */
  async exportRules() {
    return {
      rules: this.priceRules,
      exportDate: new Date().toISOString()
    };
  }

  /**
   * Импорт правил
   */
  async importRules(data) {
    if (data.rules) {
      this.priceRules = data.rules;
      await this.saveRules();
      return true;
    }
    return false;
  }

  async saveRules() {
    await FunPayStorage.set('priceRules', this.priceRules);
  }
}

// Инициализация
let priceManager;
if (FunPayUtils.isFunPayPage()) {
  priceManager = new PriceManager();
}
