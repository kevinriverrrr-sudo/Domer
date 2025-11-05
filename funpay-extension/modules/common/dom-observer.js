/**
 * FunPay Ultimate Pro - DOM Observer
 * Наблюдение за изменениями DOM
 */

class DOMObserver {
  constructor() {
    this.observers = new Map();
    this.callbacks = new Map();
    this.init();
  }

  init() {
    FunPayUtils.log('DOM Observer инициализирован');
  }

  /**
   * Наблюдение за элементом
   */
  observe(selector, callback, options = {}) {
    const observerId = FunPayUtils.generateId();
    
    const config = {
      childList: options.childList !== false,
      subtree: options.subtree !== false,
      attributes: options.attributes || false,
      characterData: options.characterData || false,
      attributeOldValue: options.attributeOldValue || false,
      characterDataOldValue: options.characterDataOldValue || false
    };

    const element = typeof selector === 'string' 
      ? document.querySelector(selector) 
      : selector;

    if (!element) {
      setTimeout(() => this.observe(selector, callback, options), 1000);
      return observerId;
    }

    const observer = new MutationObserver((mutations) => {
      callback(mutations, observer);
    });

    observer.observe(element, config);
    
    this.observers.set(observerId, observer);
    this.callbacks.set(observerId, { selector, callback, options });

    return observerId;
  }

  /**
   * Остановка наблюдения
   */
  disconnect(observerId) {
    const observer = this.observers.get(observerId);
    if (observer) {
      observer.disconnect();
      this.observers.delete(observerId);
      this.callbacks.delete(observerId);
      return true;
    }
    return false;
  }

  /**
   * Остановка всех наблюдений
   */
  disconnectAll() {
    this.observers.forEach(observer => observer.disconnect());
    this.observers.clear();
    this.callbacks.clear();
  }

  /**
   * Ожидание появления элемента
   */
  waitForElement(selector, timeout = 10000) {
    return new Promise((resolve, reject) => {
      const element = document.querySelector(selector);
      if (element) {
        resolve(element);
        return;
      }

      const observer = new MutationObserver(() => {
        const element = document.querySelector(selector);
        if (element) {
          observer.disconnect();
          clearTimeout(timer);
          resolve(element);
        }
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true
      });

      const timer = setTimeout(() => {
        observer.disconnect();
        reject(new Error(`Element ${selector} not found within ${timeout}ms`));
      }, timeout);
    });
  }

  /**
   * Наблюдение за добавлением элементов
   */
  onElementAdded(selector, callback) {
    return this.observe(document.body, (mutations) => {
      mutations.forEach(mutation => {
        mutation.addedNodes.forEach(node => {
          if (node.nodeType === 1) {
            if (node.matches(selector)) {
              callback(node);
            }
            node.querySelectorAll(selector).forEach(callback);
          }
        });
      });
    });
  }

  /**
   * Наблюдение за удалением элементов
   */
  onElementRemoved(selector, callback) {
    return this.observe(document.body, (mutations) => {
      mutations.forEach(mutation => {
        mutation.removedNodes.forEach(node => {
          if (node.nodeType === 1) {
            if (node.matches(selector)) {
              callback(node);
            }
          }
        });
      });
    });
  }

  /**
   * Наблюдение за изменением атрибутов
   */
  onAttributeChange(selector, attributeName, callback) {
    return this.observe(document.body, (mutations) => {
      mutations.forEach(mutation => {
        if (mutation.type === 'attributes' && 
            mutation.attributeName === attributeName) {
          const element = mutation.target;
          if (element.matches(selector)) {
            callback(element, mutation.oldValue);
          }
        }
      });
    }, { attributes: true, attributeOldValue: true });
  }

  /**
   * Наблюдение за изменением текста
   */
  onTextChange(selector, callback) {
    return this.observe(document.body, (mutations) => {
      mutations.forEach(mutation => {
        if (mutation.type === 'characterData') {
          const element = mutation.target.parentElement;
          if (element && element.matches(selector)) {
            callback(element, mutation.oldValue);
          }
        }
      });
    }, { characterData: true, characterDataOldValue: true, subtree: true });
  }
}

// Singleton
const domObserver = new DOMObserver();
