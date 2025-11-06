// Модуль автоподнятия лотов
class AutoRaiseManager {
  constructor() {
    this.isEnabled = false;
    this.interval = 3600000; // 1 час по умолчанию
    this.intervalId = null;
    this.lastRaiseTime = null;
  }

  async init() {
    await this.loadSettings();
    if (this.isEnabled) {
      this.start();
    }
  }

  async loadSettings() {
    return new Promise((resolve) => {
      chrome.storage.local.get(['settings'], (result) => {
        if (result.settings && result.settings.autoRaise) {
          this.isEnabled = result.settings.autoRaise.enabled || false;
          this.interval = result.settings.autoRaise.interval || 3600000;
        }
        resolve();
      });
    });
  }

  start() {
    if (this.intervalId) {
      this.stop();
    }
    
    // Поднятие сразу при запуске
    this.raiseLots();
    
    // Планирование регулярных поднятий
    this.intervalId = setInterval(() => {
      this.raiseLots();
    }, this.interval);
  }

  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  raiseLots() {
    try {
      // Поиск всех кнопок поднятия лотов
      const raiseButtons = this.findRaiseButtons();
      
      if (raiseButtons.length === 0) {
        console.log('Кнопки поднятия не найдены');
        return;
      }

      let raisedCount = 0;
      raiseButtons.forEach((button, index) => {
        setTimeout(() => {
          if (this.canRaise(button)) {
            button.click();
            raisedCount++;
            console.log(`Лот ${index + 1} поднят`);
          }
        }, index * 500); // Задержка между кликами
      });

      this.lastRaiseTime = new Date();
      
      chrome.runtime.sendMessage({
        action: 'notification',
        title: 'Автоподнятие лотов',
        message: `Поднято лотов: ${raisedCount}`
      });

    } catch (error) {
      console.error('Ошибка при поднятии лотов:', error);
    }
  }

  findRaiseButtons() {
    // Различные селекторы для кнопок поднятия
    const selectors = [
      '[data-action="raise"]',
      '.btn-raise',
      '.lot-up-btn',
      '[class*="raise"]',
      'button:contains("Поднять")',
      'a:contains("Поднять")'
    ];

    let buttons = [];
    
    selectors.forEach(selector => {
      try {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
          if (this.isRaiseButton(el)) {
            buttons.push(el);
          }
        });
      } catch (e) {
        // Селектор не поддерживается
      }
    });

    // Альтернативный поиск по тексту
    if (buttons.length === 0) {
      const allButtons = document.querySelectorAll('button, a');
      allButtons.forEach(btn => {
        const text = btn.textContent.toLowerCase();
        if (text.includes('поднять') || text.includes('raise') || text.includes('up')) {
          if (this.isRaiseButton(btn)) {
            buttons.push(btn);
          }
        }
      });
    }

    return Array.from(new Set(buttons)); // Удаляем дубликаты
  }

  isRaiseButton(element) {
    if (!element || element.disabled) return false;
    
    const text = element.textContent.toLowerCase();
    const classes = element.className.toLowerCase();
    
    return (text.includes('поднять') || 
            text.includes('raise') || 
            classes.includes('raise') ||
            classes.includes('up')) &&
           !classes.includes('disabled');
  }

  canRaise(button) {
    if (!button) return false;
    if (button.disabled) return false;
    if (button.style.display === 'none') return false;
    
    // Проверка наличия родительского элемента
    const parent = button.closest('.lot-card, .offer-card');
    if (!parent) return true;
    
    // Проверка, не находится ли лот в блокировке
    return !parent.classList.contains('disabled') && 
           !parent.classList.contains('blocked');
  }

  updateSettings(settings) {
    this.isEnabled = settings.enabled || false;
    this.interval = settings.interval || 3600000;
    
    if (this.isEnabled) {
      this.start();
    } else {
      this.stop();
    }
  }
}

// Экспорт
if (typeof window !== 'undefined') {
  window.AutoRaiseManager = AutoRaiseManager;
}
