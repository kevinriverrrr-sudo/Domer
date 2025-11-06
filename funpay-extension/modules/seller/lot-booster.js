/**
 * FunPay Ultimate Pro - Поднятие Лотов
 * Автоматическое поднятие объявлений
 */

class LotBooster {
  constructor() {
    this.enabled = false;
    this.interval = 3600000; // 1 час по умолчанию
    this.lots = [];
    this.lastBoost = new Map();
    this.timer = null;
    this.init();
  }

  async init() {
    const settings = await FunPayStorage.settings.get('lotBooster');
    if (settings) {
      this.enabled = settings.enabled;
      this.interval = settings.interval;
      this.lots = settings.lots || [];
    }

    if (this.enabled) {
      this.start();
    }
  }

  start() {
    this.enabled = true;
    this.scheduleBoost();
    FunPayUtils.log('Автоподнятие лотов запущено');
  }

  stop() {
    this.enabled = false;
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    FunPayUtils.log('Автоподнятие лотов остановлено');
  }

  scheduleBoost() {
    if (!this.enabled) return;

    const delay = this.calculateNextBoostDelay();
    
    this.timer = setTimeout(async () => {
      await this.boostAllLots();
      this.scheduleBoost(); // Планируем следующий цикл
    }, delay);

    FunPayUtils.log(`Следующее поднятие через ${Math.round(delay / 60000)} минут`);
  }

  calculateNextBoostDelay() {
    // Добавляем случайную задержку для имитации человеческого поведения
    const randomDelay = Math.random() * 600000; // До 10 минут
    return this.interval + randomDelay;
  }

  async boostAllLots() {
    if (!this.enabled) return;

    FunPayUtils.log('Начато поднятие лотов...');
    let boosted = 0;
    let failed = 0;

    for (let lot of this.lots) {
      if (!lot.enabled) continue;

      // Проверка минимального интервала между поднятиями
      const lastBoost = this.lastBoost.get(lot.id);
      if (lastBoost && Date.now() - lastBoost < lot.minInterval) {
        FunPayUtils.log(`Лот ${lot.id} пропущен (слишком рано)`);
        continue;
      }

      try {
        const success = await this.boostLot(lot.id);
        
        if (success) {
          boosted++;
          this.lastBoost.set(lot.id, Date.now());
          
          // Сохранение в историю
          await FunPayStorage.history.add('lot_boost', {
            lotId: lot.id,
            name: lot.name,
            timestamp: Date.now()
          });

          // Случайная задержка между поднятиями
          await FunPayUtils.randomDelay(5000, 15000);
        } else {
          failed++;
        }
      } catch (error) {
        FunPayUtils.log(`Ошибка поднятия лота ${lot.id}:`, error, 'error');
        failed++;
      }
    }

    // Статистика
    await FunPayStorage.stats.increment('totalBoosts');
    await FunPayStorage.stats.set('lastBoostTime', Date.now());

    // Уведомление
    FunPayUtils.notify(
      'Поднятие завершено',
      `Поднято: ${boosted}, Ошибок: ${failed}`,
      'success'
    );

    FunPayUtils.log(`Поднятие завершено. Успешно: ${boosted}, Ошибок: ${failed}`);
  }

  async boostLot(lotId) {
    try {
      // Поиск кнопки поднятия на странице
      const boostButton = this.findBoostButton(lotId);
      
      if (!boostButton) {
        FunPayUtils.log(`Кнопка поднятия не найдена для лота ${lotId}`);
        return false;
      }

      // Проверка доступности поднятия
      if (boostButton.disabled || boostButton.classList.contains('disabled')) {
        FunPayUtils.log(`Поднятие недоступно для лота ${lotId}`);
        return false;
      }

      // Клик по кнопке
      boostButton.click();
      
      // Ожидание подтверждения
      await FunPayUtils.sleep(1000);
      
      // Проверка модального окна подтверждения
      const confirmButton = document.querySelector('.modal-confirm, .btn-confirm, button[type="submit"]');
      if (confirmButton) {
        confirmButton.click();
        await FunPayUtils.sleep(500);
      }

      FunPayUtils.log(`Лот ${lotId} успешно поднят`);
      return true;

    } catch (error) {
      FunPayUtils.log(`Ошибка поднятия лота ${lotId}:`, error, 'error');
      return false;
    }
  }

  findBoostButton(lotId) {
    // Поиск кнопки по различным селекторам
    const selectors = [
      `[data-lot-id="${lotId}"] .btn-boost`,
      `[data-lot-id="${lotId}"] button[class*="up"]`,
      `#lot-${lotId} .boost-button`,
      `.lot-item[data-id="${lotId}"] .btn-raise`
    ];

    for (let selector of selectors) {
      const button = document.querySelector(selector);
      if (button) return button;
    }

    return null;
  }

  async addLot(lot) {
    const newLot = {
      id: lot.id,
      name: lot.name,
      enabled: true,
      minInterval: lot.minInterval || 3600000, // 1 час минимум
      priority: lot.priority || 0,
      added: Date.now()
    };

    this.lots.push(newLot);
    await this.saveSettings();
    return newLot;
  }

  async removeLot(lotId) {
    this.lots = this.lots.filter(l => l.id !== lotId);
    this.lastBoost.delete(lotId);
    await this.saveSettings();
  }

  async updateLot(lotId, updates) {
    const index = this.lots.findIndex(l => l.id === lotId);
    if (index !== -1) {
      this.lots[index] = { ...this.lots[index], ...updates };
      await this.saveSettings();
      return this.lots[index];
    }
    return null;
  }

  async toggleLot(lotId) {
    const lot = this.lots.find(l => l.id === lotId);
    if (lot) {
      lot.enabled = !lot.enabled;
      await this.saveSettings();
      return lot.enabled;
    }
    return false;
  }

  /**
   * Массовое добавление лотов
   */
  async addLotsFromPage() {
    const lotElements = document.querySelectorAll('.tc-item, .lot-item, [data-lot-id]');
    const addedLots = [];

    for (let element of lotElements) {
      const lotId = element.getAttribute('data-lot-id') || element.getAttribute('data-id');
      const nameElement = element.querySelector('.tc-title, .lot-name, .title');
      const name = nameElement ? nameElement.textContent.trim() : `Лот ${lotId}`;

      if (lotId && !this.lots.find(l => l.id === lotId)) {
        const lot = await this.addLot({ id: lotId, name });
        addedLots.push(lot);
      }
    }

    FunPayUtils.log(`Добавлено лотов: ${addedLots.length}`);
    return addedLots;
  }

  /**
   * Получение статистики поднятий
   */
  async getBoostStats() {
    const stats = {
      totalBoosts: await FunPayStorage.stats.get('totalBoosts', 0),
      lastBoostTime: await FunPayStorage.stats.get('lastBoostTime', 0),
      lotsCount: this.lots.length,
      enabledLots: this.lots.filter(l => l.enabled).length,
      nextBoostTime: this.timer ? Date.now() + this.interval : null
    };

    return stats;
  }

  /**
   * Оптимальное время поднятия
   */
  getOptimalBoostTime() {
    // Пиковые часы: 18:00-23:00
    const now = new Date();
    const hour = now.getHours();
    
    if (hour >= 18 && hour <= 23) {
      return 'peak'; // Пиковое время
    } else if (hour >= 12 && hour <= 17) {
      return 'normal'; // Обычное время
    } else {
      return 'low'; // Низкая активность
    }
  }

  /**
   * Умное поднятие (в оптимальное время)
   */
  async scheduleSmartBoost() {
    const optimalTime = this.getOptimalBoostTime();
    
    let delay;
    switch (optimalTime) {
      case 'peak':
        delay = 30 * 60 * 1000; // Каждые 30 минут в пик
        break;
      case 'normal':
        delay = 60 * 60 * 1000; // Каждый час
        break;
      case 'low':
        delay = 120 * 60 * 1000; // Каждые 2 часа
        break;
    }

    this.interval = delay;
    this.scheduleBoost();
  }

  /**
   * Экспорт настроек
   */
  async exportSettings() {
    return {
      enabled: this.enabled,
      interval: this.interval,
      lots: this.lots,
      lastBoost: Array.from(this.lastBoost.entries())
    };
  }

  /**
   * Импорт настроек
   */
  async importSettings(data) {
    if (data.lots) {
      this.lots = data.lots;
      this.interval = data.interval || this.interval;
      
      if (data.lastBoost) {
        this.lastBoost = new Map(data.lastBoost);
      }
      
      await this.saveSettings();
      return true;
    }
    return false;
  }

  async saveSettings() {
    await FunPayStorage.settings.set('lotBooster', {
      enabled: this.enabled,
      interval: this.interval,
      lots: this.lots
    });
  }
}

// Инициализация
let lotBooster;
if (FunPayUtils.isFunPayPage()) {
  lotBooster = new LotBooster();
}
