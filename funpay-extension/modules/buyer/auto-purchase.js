/**
 * FunPay Ultimate Pro - Автозакупка
 * Автоматическая покупка товаров
 */

class AutoPurchase {
  constructor() {
    this.enabled = false;
    this.filters = [];
    this.maxPrice = 1000;
    this.watchedProducts = new Map();
    this.purchaseQueue = [];
    this.init();
  }

  async init() {
    const settings = await FunPayStorage.settings.get('autoPurchase');
    if (settings) {
      this.enabled = settings.enabled;
      this.filters = settings.filters || [];
      this.maxPrice = settings.maxPrice || 1000;
    }

    if (this.enabled) {
      this.start();
    }
  }

  start() {
    this.enabled = true;
    this.startMonitoring();
    FunPayUtils.log('Автозакупка запущена');
  }

  stop() {
    this.enabled = false;
    if (this.monitorInterval) {
      clearInterval(this.monitorInterval);
    }
    FunPayUtils.log('Автозакупка остановлена');
  }

  startMonitoring() {
    // Мониторинг каждые 30 секунд
    this.monitorInterval = setInterval(() => {
      this.checkProducts();
    }, 30000);

    // Первая проверка сразу
    this.checkProducts();
  }

  async checkProducts() {
    if (!this.enabled) return;

    const products = this.findProductsOnPage();
    
    for (let product of products) {
      if (this.matchesFilters(product)) {
        await this.considerPurchase(product);
      }
    }
  }

  findProductsOnPage() {
    const products = [];
    const productElements = document.querySelectorAll('.tc-item, .offer-list-item, [class*="product"]');

    productElements.forEach(el => {
      const product = {
        id: el.getAttribute('data-id') || el.getAttribute('data-offer-id'),
        title: this.extractText(el, '.tc-title, .offer-title, .title'),
        price: FunPayUtils.parsePrice(this.extractText(el, '.tc-price, .price')),
        seller: this.extractText(el, '.tc-seller, .seller-name'),
        rating: this.extractRating(el),
        element: el
      };

      if (product.id && product.price > 0) {
        products.push(product);
      }
    });

    return products;
  }

  extractText(element, selector) {
    const el = element.querySelector(selector);
    return el ? el.textContent.trim() : '';
  }

  extractRating(element) {
    const ratingEl = element.querySelector('.rating, .stars, [class*="rating"]');
    if (!ratingEl) return 0;
    
    const ratingText = ratingEl.textContent;
    const match = ratingText.match(/(\d+\.?\d*)/);
    return match ? parseFloat(match[1]) : 0;
  }

  matchesFilters(product) {
    for (let filter of this.filters) {
      if (!filter.enabled) continue;

      // Проверка цены
      if (filter.maxPrice && product.price > filter.maxPrice) continue;
      if (filter.minPrice && product.price < filter.minPrice) continue;

      // Проверка названия
      if (filter.titleContains) {
        const title = product.title.toLowerCase();
        const search = filter.titleContains.toLowerCase();
        if (!title.includes(search)) continue;
      }

      // Проверка продавца
      if (filter.seller && product.seller !== filter.seller) continue;

      // Проверка рейтинга
      if (filter.minRating && product.rating < filter.minRating) continue;

      // Все фильтры пройдены
      return true;
    }

    // Проверка максимальной цены по умолчанию
    return product.price <= this.maxPrice;
  }

  async considerPurchase(product) {
    // Проверяем, не покупали ли уже
    if (this.watchedProducts.has(product.id)) {
      const watched = this.watchedProducts.get(product.id);
      if (watched.purchased) return;
    }

    // Добавляем в очередь
    this.purchaseQueue.push(product);
    this.watchedProducts.set(product.id, {
      product,
      added: Date.now(),
      purchased: false
    });

    FunPayUtils.log('Товар добавлен в очередь покупки:', product);

    // Попытка покупки
    await this.attemptPurchase(product);
  }

  async attemptPurchase(product) {
    try {
      FunPayUtils.log('Попытка покупки:', product);

      // Уведомление
      FunPayUtils.notify(
        'Автозакупка',
        `Попытка купить: ${product.title} за ${FunPayUtils.formatPrice(product.price)}`,
        'info'
      );

      // Клик по товару
      const buyButton = product.element.querySelector('.btn-buy, button[class*="buy"], a[href*="buy"]');
      
      if (!buyButton) {
        FunPayUtils.log('Кнопка покупки не найдена');
        return false;
      }

      // Открываем страницу товара
      buyButton.click();
      
      // Ждем загрузки
      await FunPayUtils.sleep(2000);

      // Подтверждение покупки
      const confirmButton = document.querySelector('.btn-confirm-purchase, button[class*="confirm"]');
      if (confirmButton) {
        confirmButton.click();
        
        // Отмечаем как купленный
        const watched = this.watchedProducts.get(product.id);
        if (watched) {
          watched.purchased = true;
        }

        // Сохранение в истории
        await FunPayStorage.history.add('auto_purchase', product);
        await FunPayStorage.stats.increment('autoPurchases');

        FunPayUtils.notify(
          'Покупка завершена!',
          `Куплено: ${product.title}`,
          'success'
        );

        FunPayUtils.log('Покупка успешна:', product);
        return true;
      }

    } catch (error) {
      FunPayUtils.log('Ошибка автозакупки:', error, 'error');
    }

    return false;
  }

  async addFilter(filter) {
    const newFilter = {
      id: FunPayUtils.generateId(),
      name: filter.name,
      titleContains: filter.titleContains || null,
      minPrice: filter.minPrice || null,
      maxPrice: filter.maxPrice || null,
      seller: filter.seller || null,
      minRating: filter.minRating || null,
      enabled: true,
      created: Date.now()
    };

    this.filters.push(newFilter);
    await this.saveSettings();
    return newFilter;
  }

  async removeFilter(id) {
    this.filters = this.filters.filter(f => f.id !== id);
    await this.saveSettings();
  }

  async toggleFilter(id) {
    const filter = this.filters.find(f => f.id === id);
    if (filter) {
      filter.enabled = !filter.enabled;
      await this.saveSettings();
      return filter.enabled;
    }
    return false;
  }

  async getPurchaseHistory(limit = 100) {
    return await FunPayStorage.history.get(limit, 'auto_purchase');
  }

  async getPurchaseStats() {
    const history = await this.getPurchaseHistory(1000);
    
    const stats = {
      total: history.length,
      totalSpent: 0,
      averagePrice: 0,
      sellers: {},
      products: {}
    };

    history.forEach(purchase => {
      const product = purchase.data;
      stats.totalSpent += product.price;

      // По продавцам
      stats.sellers[product.seller] = (stats.sellers[product.seller] || 0) + 1;

      // По товарам
      const title = product.title;
      stats.products[title] = (stats.products[title] || 0) + 1;
    });

    stats.averagePrice = stats.total > 0 ? stats.totalSpent / stats.total : 0;

    return stats;
  }

  async saveSettings() {
    await FunPayStorage.settings.set('autoPurchase', {
      enabled: this.enabled,
      filters: this.filters,
      maxPrice: this.maxPrice
    });
  }
}

// Инициализация
let autoPurchase;
if (FunPayUtils.isFunPayPage()) {
  autoPurchase = new AutoPurchase();
}
