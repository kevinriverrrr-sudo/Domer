/**
 * FunPay Ultimate Pro - Автожалобы
 * Автоматическая подача жалоб на нарушителей
 */

class AutoComplaints {
  constructor() {
    this.enabled = false;
    this.autoFill = true;
    this.reasons = [];
    this.blacklist = [];
    this.complaintsHistory = [];
    this.init();
  }

  async init() {
    const settings = await FunPayStorage.settings.get('autoComplaints');
    if (settings) {
      this.enabled = settings.enabled;
      this.autoFill = settings.autoFill;
      this.reasons = settings.reasons || [];
    }

    this.blacklist = await FunPayStorage.get('complaintsBlacklist', []);
    this.complaintsHistory = await FunPayStorage.get('complaintsHistory', []);

    if (this.enabled) {
      this.start();
    }
  }

  start() {
    this.enabled = true;
    this.observePage();
    FunPayUtils.log('Система автожалоб запущена');
  }

  stop() {
    this.enabled = false;
    if (this.observer) {
      this.observer.disconnect();
    }
    FunPayUtils.log('Система автожалоб остановлена');
  }

  observePage() {
    // Наблюдение за появлением элементов для жалоб
    this.observer = new MutationObserver(() => {
      this.checkForComplaintOpportunities();
    });

    this.observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    // Первая проверка
    this.checkForComplaintOpportunities();
  }

  checkForComplaintOpportunities() {
    if (!this.enabled) return;

    // Проверка кнопок жалоб на странице
    const complaintButtons = document.querySelectorAll('[class*="report"], [class*="complaint"], a[href*="complaint"]');
    
    complaintButtons.forEach(button => {
      if (!button.hasAttribute('data-auto-complaint-processed')) {
        button.setAttribute('data-auto-complaint-processed', 'true');
        
        // Проверяем, в черном ли списке пользователь
        const userId = this.extractUserId(button);
        if (userId && this.isInBlacklist(userId)) {
          this.handleComplaintButton(button, userId);
        }
      }
    });
  }

  extractUserId(element) {
    // Извлечение ID пользователя из различных атрибутов
    return element.getAttribute('data-user-id') ||
           element.closest('[data-user-id]')?.getAttribute('data-user-id') ||
           this.extractUserIdFromUrl(element.href);
  }

  extractUserIdFromUrl(url) {
    if (!url) return null;
    const match = url.match(/users?[\/=](\d+)/);
    return match ? match[1] : null;
  }

  isInBlacklist(userId) {
    return this.blacklist.some(entry => 
      entry.userId === userId && entry.autoComplaint
    );
  }

  async handleComplaintButton(button, userId) {
    try {
      FunPayUtils.log(`Обработка жалобы на пользователя ${userId}`);

      // Клик по кнопке жалобы
      button.click();

      // Ожидание появления формы
      await FunPayUtils.sleep(1000);

      if (this.autoFill) {
        await this.fillComplaintForm(userId);
      }

    } catch (error) {
      FunPayUtils.log('Ошибка при подаче жалобы:', error, 'error');
    }
  }

  async fillComplaintForm(userId) {
    // Поиск формы жалобы
    const form = document.querySelector('form[class*="complaint"], form[class*="report"]');
    if (!form) {
      FunPayUtils.log('Форма жалобы не найдена');
      return;
    }

    const blacklistEntry = this.blacklist.find(entry => entry.userId === userId);
    if (!blacklistEntry) return;

    // Выбор причины жалобы
    const reasonSelect = form.querySelector('select[name*="reason"], select[name*="type"]');
    if (reasonSelect && blacklistEntry.complaintReason) {
      reasonSelect.value = blacklistEntry.complaintReason;
      reasonSelect.dispatchEvent(new Event('change', { bubbles: true }));
    }

    // Заполнение текстового поля
    const descriptionField = form.querySelector('textarea[name*="description"], textarea[name*="comment"]');
    if (descriptionField && blacklistEntry.complaintText) {
      descriptionField.value = blacklistEntry.complaintText;
      descriptionField.dispatchEvent(new Event('input', { bubbles: true }));
    }

    // Загрузка доказательств (если есть)
    if (blacklistEntry.evidence && blacklistEntry.evidence.length > 0) {
      await this.uploadEvidence(form, blacklistEntry.evidence);
    }

    // Автоматическая отправка (если включено)
    if (blacklistEntry.autoSubmit) {
      await FunPayUtils.sleep(2000);
      const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
      if (submitButton) {
        submitButton.click();
        
        // Сохранение в историю
        await this.saveComplaintToHistory(userId, blacklistEntry);
        
        FunPayUtils.notify(
          'Жалоба отправлена',
          `Автоматическая жалоба на пользователя ${userId}`,
          'success'
        );
      }
    }
  }

  async uploadEvidence(form, evidence) {
    const fileInput = form.querySelector('input[type="file"]');
    if (!fileInput) return;

    try {
      // Здесь должна быть логика загрузки файлов
      FunPayUtils.log('Загрузка доказательств:', evidence);
    } catch (error) {
      FunPayUtils.log('Ошибка загрузки доказательств:', error, 'error');
    }
  }

  async addToBlacklist(entry) {
    const newEntry = {
      id: FunPayUtils.generateId(),
      userId: entry.userId,
      username: entry.username || '',
      reason: entry.reason || '',
      complaintReason: entry.complaintReason || '',
      complaintText: entry.complaintText || '',
      autoComplaint: entry.autoComplaint !== false,
      autoSubmit: entry.autoSubmit || false,
      evidence: entry.evidence || [],
      added: Date.now()
    };

    this.blacklist.push(newEntry);
    await this.saveBlacklist();
    
    FunPayUtils.log('Пользователь добавлен в черный список:', newEntry);
    return newEntry;
  }

  async removeFromBlacklist(id) {
    this.blacklist = this.blacklist.filter(entry => entry.id !== id);
    await this.saveBlacklist();
  }

  async updateBlacklistEntry(id, updates) {
    const index = this.blacklist.findIndex(entry => entry.id === id);
    if (index !== -1) {
      this.blacklist[index] = { ...this.blacklist[index], ...updates };
      await this.saveBlacklist();
      return this.blacklist[index];
    }
    return null;
  }

  async saveComplaintToHistory(userId, entry) {
    this.complaintsHistory.push({
      id: FunPayUtils.generateId(),
      userId,
      username: entry.username,
      reason: entry.complaintReason,
      text: entry.complaintText,
      timestamp: Date.now(),
      status: 'submitted'
    });

    // Ограничение истории
    if (this.complaintsHistory.length > 500) {
      this.complaintsHistory = this.complaintsHistory.slice(-500);
    }

    await FunPayStorage.set('complaintsHistory', this.complaintsHistory);
    await FunPayStorage.stats.increment('totalComplaints');
  }

  getComplaintStatistics(period = 'month') {
    const periods = {
      day: 86400000,
      week: 604800000,
      month: 2592000000
    };

    const periodMs = periods[period] || periods.month;
    const since = Date.now() - periodMs;

    const recent = this.complaintsHistory.filter(c => c.timestamp >= since);

    const stats = {
      total: recent.length,
      byReason: {},
      byUser: {},
      period
    };

    recent.forEach(complaint => {
      // По причинам
      const reason = complaint.reason || 'Не указана';
      stats.byReason[reason] = (stats.byReason[reason] || 0) + 1;

      // По пользователям
      const user = complaint.username || complaint.userId;
      stats.byUser[user] = (stats.byUser[user] || 0) + 1;
    });

    return stats;
  }

  async detectScammer(userId, evidence) {
    // Автоматическое определение мошенника по признакам
    const scamIndicators = {
      newAccount: false,
      lowRating: false,
      negativeReviews: false,
      suspiciousActivity: false,
      reportedBefore: false
    };

    // Проверка возраста аккаунта
    const accountAge = await this.getAccountAge(userId);
    if (accountAge < 7) { // Меньше недели
      scamIndicators.newAccount = true;
    }

    // Проверка рейтинга
    const rating = await this.getUserRating(userId);
    if (rating < 3.0) {
      scamIndicators.lowRating = true;
    }

    // Проверка отзывов
    const reviews = await this.getUserReviews(userId);
    const negativeCount = reviews.filter(r => r.rating < 3).length;
    if (negativeCount > reviews.length * 0.3) { // Более 30% негативных
      scamIndicators.negativeReviews = true;
    }

    // Проверка предыдущих жалоб
    const previousComplaints = this.complaintsHistory.filter(c => c.userId === userId);
    if (previousComplaints.length > 0) {
      scamIndicators.reportedBefore = true;
    }

    // Подсчет индикаторов
    const indicatorCount = Object.values(scamIndicators).filter(v => v).length;
    const scamProbability = (indicatorCount / Object.keys(scamIndicators).length) * 100;

    return {
      userId,
      indicators: scamIndicators,
      probability: scamProbability,
      recommendation: scamProbability > 60 ? 'report' : scamProbability > 30 ? 'caution' : 'safe'
    };
  }

  async getAccountAge(userId) {
    // Получение возраста аккаунта в днях
    // Здесь должна быть логика парсинга страницы пользователя
    return 30; // Заглушка
  }

  async getUserRating(userId) {
    // Получение рейтинга пользователя
    const userPage = document.querySelector(`[data-user-id="${userId}"]`);
    if (userPage) {
      const ratingEl = userPage.querySelector('.rating, [class*="rating"]');
      if (ratingEl) {
        const match = ratingEl.textContent.match(/(\d+\.?\d*)/);
        return match ? parseFloat(match[1]) : 5.0;
      }
    }
    return 5.0;
  }

  async getUserReviews(userId) {
    // Получение отзывов пользователя
    // Здесь должна быть логика парсинга отзывов
    return []; // Заглушка
  }

  async exportBlacklist() {
    return {
      blacklist: this.blacklist,
      history: this.complaintsHistory,
      exportDate: new Date().toISOString()
    };
  }

  async importBlacklist(data) {
    if (data.blacklist) {
      this.blacklist = data.blacklist;
      await this.saveBlacklist();
      return true;
    }
    return false;
  }

  async saveBlacklist() {
    await FunPayStorage.set('complaintsBlacklist', this.blacklist);
  }

  async saveSettings() {
    await FunPayStorage.settings.set('autoComplaints', {
      enabled: this.enabled,
      autoFill: this.autoFill,
      reasons: this.reasons
    });
  }

  // Предустановленные причины жалоб
  static getComplaintReasons() {
    return [
      { value: 'scam', label: 'Мошенничество' },
      { value: 'fake', label: 'Фейковые товары' },
      { value: 'spam', label: 'Спам' },
      { value: 'inappropriate', label: 'Неподобающее поведение' },
      { value: 'fake_reviews', label: 'Накрутка отзывов' },
      { value: 'price_manipulation', label: 'Манипуляция ценами' },
      { value: 'account_theft', label: 'Кража аккаунтов' },
      { value: 'other', label: 'Другое' }
    ];
  }
}

// Инициализация
let autoComplaints;
if (FunPayUtils.isFunPayPage()) {
  autoComplaints = new AutoComplaints();
}
