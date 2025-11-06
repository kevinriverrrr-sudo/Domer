/**
 * FunPay Ultimate Pro - Детектор Мошенников
 * Система обнаружения и защиты от мошенников
 */

class ScamDetector {
  constructor() {
    this.enabled = true;
    this.scamPatterns = [];
    this.suspiciousUsers = new Map();
    this.blacklist = [];
    this.whitelist = [];
    this.init();
  }

  async init() {
    const settings = await FunPayStorage.settings.get('scamDetector');
    if (settings) {
      this.enabled = settings.enabled;
    }

    this.blacklist = await FunPayStorage.get('securityBlacklist', []);
    this.whitelist = await FunPayStorage.get('securityWhitelist', []);
    this.scamPatterns = this.getDefaultScamPatterns();

    if (this.enabled) {
      this.start();
    }
  }

  start() {
    this.enabled = true;
    this.monitorPage();
    FunPayUtils.log('Детектор мошенников запущен');
  }

  stop() {
    this.enabled = false;
    if (this.observer) {
      this.observer.disconnect();
    }
    FunPayUtils.log('Детектор мошенников остановлен');
  }

  monitorPage() {
    // Наблюдение за элементами страницы
    this.observer = new MutationObserver(() => {
      this.scanForThreats();
    });

    this.observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    // Первичное сканирование
    this.scanForThreats();
  }

  scanForThreats() {
    if (!this.enabled) return;

    // Проверка сообщений
    this.scanMessages();

    // Проверка пользователей
    this.scanUsers();

    // Проверка объявлений
    this.scanListings();
  }

  scanMessages() {
    const messages = document.querySelectorAll('.message, .chat-message');
    
    messages.forEach(messageEl => {
      if (messageEl.hasAttribute('data-scam-checked')) return;
      messageEl.setAttribute('data-scam-checked', 'true');

      const text = messageEl.textContent.toLowerCase();
      const threats = this.detectThreatsInText(text);

      if (threats.length > 0) {
        this.handleThreat(messageEl, 'message', threats);
      }
    });
  }

  scanUsers() {
    const userElements = document.querySelectorAll('[data-user-id], .user-card, .seller-info');
    
    userElements.forEach(userEl => {
      const userId = userEl.getAttribute('data-user-id');
      if (!userId || userEl.hasAttribute('data-security-checked')) return;
      userEl.setAttribute('data-security-checked', 'true');

      // Проверка в черном списке
      if (this.isBlacklisted(userId)) {
        this.markAsBlacklisted(userEl, userId);
        return;
      }

      // Анализ подозрительности
      const suspicionLevel = this.analyzeUser(userEl, userId);
      if (suspicionLevel > 60) {
        this.markAsSuspicious(userEl, userId, suspicionLevel);
      }
    });
  }

  scanListings() {
    const listings = document.querySelectorAll('.tc-item, .offer-list-item');
    
    listings.forEach(listingEl => {
      if (listingEl.hasAttribute('data-listing-checked')) return;
      listingEl.setAttribute('data-listing-checked', 'true');

      const threats = this.analyzeListing(listingEl);
      if (threats.length > 0) {
        this.handleThreat(listingEl, 'listing', threats);
      }
    });
  }

  detectThreatsInText(text) {
    const threats = [];

    this.scamPatterns.forEach(pattern => {
      if (pattern.regex.test(text)) {
        threats.push({
          type: pattern.type,
          severity: pattern.severity,
          description: pattern.description
        });
      }
    });

    return threats;
  }

  analyzeUser(userElement, userId) {
    let suspicionScore = 0;
    const indicators = [];

    // 1. Новый аккаунт
    const registrationDate = this.getRegistrationDate(userElement);
    if (registrationDate && Date.now() - registrationDate < 7 * 86400000) {
      suspicionScore += 30;
      indicators.push('Новый аккаунт (< 7 дней)');
    }

    // 2. Низкий рейтинг
    const rating = this.getUserRating(userElement);
    if (rating < 3.0) {
      suspicionScore += 25;
      indicators.push(`Низкий рейтинг: ${rating}`);
    }

    // 3. Мало сделок
    const dealsCount = this.getDealsCount(userElement);
    if (dealsCount < 5) {
      suspicionScore += 20;
      indicators.push(`Мало сделок: ${dealsCount}`);
    }

    // 4. Негативные отзывы
    const negativeReviews = this.getNegativeReviewsCount(userElement);
    if (negativeReviews > 3) {
      suspicionScore += 35;
      indicators.push(`Негативные отзывы: ${negativeReviews}`);
    }

    // 5. Подозрительное имя
    const username = this.getUsername(userElement);
    if (this.isSuspiciousUsername(username)) {
      suspicionScore += 15;
      indicators.push('Подозрительное имя');
    }

    // 6. Отсутствие аватара
    if (!this.hasAvatar(userElement)) {
      suspicionScore += 10;
      indicators.push('Нет аватара');
    }

    if (suspicionScore > 0) {
      this.suspiciousUsers.set(userId, {
        score: suspicionScore,
        indicators,
        timestamp: Date.now()
      });
    }

    return suspicionScore;
  }

  analyzeListing(listingElement) {
    const threats = [];
    const title = this.extractText(listingElement, '.tc-title, .title');
    const description = this.extractText(listingElement, '.tc-desc, .description');
    const price = FunPayUtils.parsePrice(this.extractText(listingElement, '.tc-price, .price'));

    // Проверка текста на подозрительные паттерны
    const text = (title + ' ' + description).toLowerCase();
    const textThreats = this.detectThreatsInText(text);
    threats.push(...textThreats);

    // Слишком низкая цена
    if (price > 0 && price < 10) {
      threats.push({
        type: 'suspicious_price',
        severity: 'medium',
        description: 'Подозрительно низкая цена'
      });
    }

    return threats;
  }

  handleThreat(element, type, threats) {
    const severity = Math.max(...threats.map(t => this.getSeverityLevel(t.severity)));
    
    // Визуальное предупреждение
    this.addWarningBadge(element, severity);

    // Уведомление для критических угроз
    if (severity >= 3) {
      FunPayUtils.notify(
        'Обнаружена угроза!',
        threats.map(t => t.description).join(', '),
        'warning'
      );
    }

    // Логирование
    FunPayStorage.history.add('security_threat', {
      type,
      threats,
      severity,
      timestamp: Date.now()
    });
  }

  addWarningBadge(element, severity) {
    const colors = ['yellow', 'orange', 'red', 'darkred'];
    const labels = ['Внимание', 'Осторожно', 'Опасно', 'Мошенник'];
    
    const badge = document.createElement('div');
    badge.className = 'funpay-security-badge';
    badge.style.cssText = `
      position: absolute;
      top: 5px;
      right: 5px;
      background: ${colors[severity - 1] || 'yellow'};
      color: white;
      padding: 3px 8px;
      border-radius: 3px;
      font-size: 11px;
      font-weight: bold;
      z-index: 1000;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    `;
    badge.textContent = labels[severity - 1] || 'Внимание';
    
    element.style.position = 'relative';
    element.appendChild(badge);
  }

  markAsBlacklisted(element, userId) {
    element.style.cssText += `
      border: 2px solid red !important;
      background: rgba(255, 0, 0, 0.1) !important;
      opacity: 0.6;
    `;

    const overlay = document.createElement('div');
    overlay.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(255, 0, 0, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 999;
    `;
    overlay.innerHTML = '<strong style="color: red;">ЗАБЛОКИРОВАН</strong>';
    
    element.style.position = 'relative';
    element.appendChild(overlay);
  }

  markAsSuspicious(element, userId, score) {
    const badge = document.createElement('div');
    badge.className = 'funpay-suspicious-badge';
    badge.style.cssText = `
      position: absolute;
      top: 5px;
      left: 5px;
      background: orange;
      color: white;
      padding: 5px 10px;
      border-radius: 5px;
      font-size: 12px;
      font-weight: bold;
      z-index: 1000;
      cursor: help;
    `;
    badge.textContent = `⚠ Подозрительный (${score}%)`;
    badge.title = this.getSuspicionDetails(userId);
    
    element.style.position = 'relative';
    element.appendChild(badge);
  }

  getSuspicionDetails(userId) {
    const data = this.suspiciousUsers.get(userId);
    if (!data) return '';
    return 'Индикаторы:\n' + data.indicators.join('\n');
  }

  isBlacklisted(userId) {
    return this.blacklist.some(entry => entry.userId === userId);
  }

  async addToBlacklist(userId, username, reason) {
    const entry = {
      id: FunPayUtils.generateId(),
      userId,
      username,
      reason,
      added: Date.now()
    };

    this.blacklist.push(entry);
    await FunPayStorage.set('securityBlacklist', this.blacklist);
    
    FunPayUtils.log('Пользователь добавлен в черный список:', entry);
    return entry;
  }

  async addToWhitelist(userId, username) {
    const entry = {
      id: FunPayUtils.generateId(),
      userId,
      username,
      added: Date.now()
    };

    this.whitelist.push(entry);
    await FunPayStorage.set('securityWhitelist', this.whitelist);
    
    return entry;
  }

  // Вспомогательные методы
  getRegistrationDate(element) {
    const regDateEl = element.querySelector('[data-reg-date], .reg-date');
    if (regDateEl) {
      return new Date(regDateEl.textContent).getTime();
    }
    return null;
  }

  getUserRating(element) {
    const ratingEl = element.querySelector('.rating, [class*="rating"]');
    if (ratingEl) {
      const match = ratingEl.textContent.match(/(\d+\.?\d*)/);
      return match ? parseFloat(match[1]) : 5.0;
    }
    return 5.0;
  }

  getDealsCount(element) {
    const dealsEl = element.querySelector('.deals-count, [class*="deals"]');
    if (dealsEl) {
      const match = dealsEl.textContent.match(/(\d+)/);
      return match ? parseInt(match[1]) : 0;
    }
    return 0;
  }

  getNegativeReviewsCount(element) {
    // Здесь должна быть логика подсчета негативных отзывов
    return 0;
  }

  getUsername(element) {
    const usernameEl = element.querySelector('.username, .user-name, [class*="username"]');
    return usernameEl ? usernameEl.textContent.trim() : '';
  }

  hasAvatar(element) {
    const avatar = element.querySelector('.avatar, .user-avatar, img[class*="avatar"]');
    return avatar && avatar.src && !avatar.src.includes('default');
  }

  isSuspiciousUsername(username) {
    const suspiciousPatterns = [
      /admin/i,
      /moderator/i,
      /official/i,
      /support/i,
      /\d{8,}/,  // Много цифр подряд
      /[A-Z]{10,}/i,  // Много букв подряд
      /(.)\1{5,}/  // Повторяющиеся символы
    ];

    return suspiciousPatterns.some(pattern => pattern.test(username));
  }

  extractText(element, selector) {
    const el = element.querySelector(selector);
    return el ? el.textContent.trim() : '';
  }

  getSeverityLevel(severity) {
    const levels = { low: 1, medium: 2, high: 3, critical: 4 };
    return levels[severity] || 1;
  }

  getDefaultScamPatterns() {
    return [
      {
        type: 'phishing_link',
        regex: /(bit\.ly|goo\.gl|tinyurl|t\.me\/[^\/]+bot)/i,
        severity: 'high',
        description: 'Подозрительная ссылка'
      },
      {
        type: 'external_payment',
        regex: /(оплата|оплатить|payment).*(вне сайта|другой сайт|другую систему)/i,
        severity: 'critical',
        description: 'Попытка увести оплату с сайта'
      },
      {
        type: 'urgent_pressure',
        regex: /(срочно|быстро|только сейчас|ограниченное|последний).*(купи|покупай|оплати)/i,
        severity: 'medium',
        description: 'Давление на срочность'
      },
      {
        type: 'too_good',
        regex: /(бесплатно|даром|в подарок|халява).*(аккаунт|скины|донат)/i,
        severity: 'high',
        description: 'Слишком хорошее предложение'
      },
      {
        type: 'personal_data',
        regex: /(дайте|скинь|отправь).*(пароль|код|смс|sms)/i,
        severity: 'critical',
        description: 'Запрос личных данных'
      }
    ];
  }

  async getSecurityReport() {
    return {
      blacklistCount: this.blacklist.length,
      whitelistCount: this.whitelist.length,
      suspiciousUsers: this.suspiciousUsers.size,
      threatsDetected: await FunPayStorage.stats.get('threatsDetected', 0),
      lastScan: Date.now()
    };
  }
}

// Инициализация
let scamDetector;
if (FunPayUtils.isFunPayPage()) {
  scamDetector = new ScamDetector();
}
