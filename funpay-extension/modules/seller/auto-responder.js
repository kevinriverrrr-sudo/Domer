/**
 * FunPay Ultimate Pro - Автоответчик
 * Автоматические ответы на сообщения покупателей
 */

class AutoResponder {
  constructor() {
    this.enabled = false;
    this.templates = [];
    this.delay = { min: 2000, max: 5000 };
    this.processedMessages = new Set();
    this.init();
  }

  async init() {
    const settings = await FunPayStorage.settings.get('autoResponder');
    if (settings) {
      this.enabled = settings.enabled;
      this.templates = settings.templates || [];
      this.delay = settings.delay || this.delay;
    }
    
    if (this.enabled) {
      this.start();
    }
  }

  start() {
    this.enabled = true;
    this.observeMessages();
    FunPayUtils.log('Автоответчик запущен');
  }

  stop() {
    this.enabled = false;
    if (this.observer) {
      this.observer.disconnect();
    }
    FunPayUtils.log('Автоответчик остановлен');
  }

  observeMessages() {
    const chatContainer = document.querySelector('.chat-container, .messages-list, [class*="chat"]');
    
    if (!chatContainer) {
      setTimeout(() => this.observeMessages(), 1000);
      return;
    }

    this.observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) {
            this.processNewMessage(node);
          }
        });
      });
    });

    this.observer.observe(chatContainer, {
      childList: true,
      subtree: true
    });
  }

  async processNewMessage(messageNode) {
    if (!this.enabled) return;

    // Проверяем, что это входящее сообщение
    if (!this.isIncomingMessage(messageNode)) return;

    const messageId = this.getMessageId(messageNode);
    if (this.processedMessages.has(messageId)) return;

    this.processedMessages.add(messageId);

    const messageText = this.getMessageText(messageNode);
    const response = this.findResponse(messageText);

    if (response) {
      await this.sendResponse(response, messageText);
      
      // Сохранение в историю
      await FunPayStorage.history.add('auto_response', {
        incoming: messageText,
        response: response.text,
        template: response.name
      });

      // Статистика
      await FunPayStorage.stats.increment('autoResponses');
    }
  }

  isIncomingMessage(node) {
    // Проверка классов и атрибутов сообщения
    return node.classList && (
      node.classList.contains('message-incoming') ||
      node.classList.contains('incoming') ||
      node.querySelector('.message-incoming') ||
      !node.classList.contains('message-outgoing')
    );
  }

  getMessageId(node) {
    return node.getAttribute('data-message-id') || 
           node.id || 
           FunPayUtils.generateId();
  }

  getMessageText(node) {
    const textElement = node.querySelector('.message-text, .msg-text, [class*="text"]');
    return textElement ? textElement.textContent.trim() : '';
  }

  findResponse(messageText) {
    const lowerText = messageText.toLowerCase();

    // Поиск по ключевым словам
    for (let template of this.templates) {
      if (!template.enabled) continue;

      // Точное совпадение
      if (template.trigger === 'exact' && lowerText === template.keyword.toLowerCase()) {
        return template;
      }

      // Содержит ключевое слово
      if (template.trigger === 'contains' && lowerText.includes(template.keyword.toLowerCase())) {
        return template;
      }

      // Начинается с
      if (template.trigger === 'starts' && lowerText.startsWith(template.keyword.toLowerCase())) {
        return template;
      }

      // Регулярное выражение
      if (template.trigger === 'regex') {
        try {
          const regex = new RegExp(template.keyword, 'i');
          if (regex.test(messageText)) {
            return template;
          }
        } catch (e) {
          console.error('Invalid regex:', template.keyword);
        }
      }
    }

    // Дефолтный ответ
    const defaultTemplate = this.templates.find(t => t.isDefault);
    return defaultTemplate || null;
  }

  async sendResponse(template, incomingMessage) {
    // Проверка рабочего времени
    if (template.workingHours?.enabled) {
      if (!this.isWorkingTime(template.workingHours)) {
        FunPayUtils.log('Вне рабочего времени, ответ не отправлен');
        return;
      }
    }

    // Задержка для имитации печати
    const delayTime = Math.random() * (this.delay.max - this.delay.min) + this.delay.min;
    await FunPayUtils.sleep(delayTime);

    // Обработка переменных в тексте
    let responseText = this.processVariables(template.text, incomingMessage);

    // Отправка сообщения
    this.sendMessage(responseText);

    FunPayUtils.log('Автоответ отправлен:', { template: template.name, response: responseText });
  }

  processVariables(text, incomingMessage) {
    const variables = {
      '{user}': this.getUserName(),
      '{time}': new Date().toLocaleTimeString('ru-RU'),
      '{date}': new Date().toLocaleDateString('ru-RU'),
      '{message}': incomingMessage,
      '{seller}': this.getSellerName(),
      '{random}': Math.floor(Math.random() * 100)
    };

    let processed = text;
    for (let [variable, value] of Object.entries(variables)) {
      processed = processed.replace(new RegExp(variable, 'g'), value);
    }

    return processed;
  }

  getUserName() {
    const userElement = document.querySelector('.chat-username, .user-name, [class*="username"]');
    return userElement ? userElement.textContent.trim() : 'Пользователь';
  }

  getSellerName() {
    const sellerElement = document.querySelector('.seller-name, .profile-name');
    return sellerElement ? sellerElement.textContent.trim() : '';
  }

  sendMessage(text) {
    // Находим поле ввода
    const input = document.querySelector('textarea[name="message"], .message-input, input[type="text"][class*="message"]');
    const sendButton = document.querySelector('button[type="submit"], .send-button, button[class*="send"]');

    if (input && sendButton) {
      // Устанавливаем текст
      input.value = text;
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));

      // Имитация печати
      setTimeout(() => {
        sendButton.click();
      }, 500);
    }
  }

  isWorkingTime(workingHours) {
    const now = new Date();
    const currentTime = now.getHours() * 60 + now.getMinutes();
    
    const [startHour, startMin] = workingHours.start.split(':').map(Number);
    const [endHour, endMin] = workingHours.end.split(':').map(Number);
    
    const startTime = startHour * 60 + startMin;
    const endTime = endHour * 60 + endMin;

    return currentTime >= startTime && currentTime <= endTime;
  }

  async addTemplate(template) {
    const newTemplate = {
      id: FunPayUtils.generateId(),
      name: template.name,
      keyword: template.keyword,
      text: template.text,
      trigger: template.trigger || 'contains',
      enabled: true,
      isDefault: template.isDefault || false,
      workingHours: template.workingHours || null,
      created: Date.now()
    };

    this.templates.push(newTemplate);
    await this.saveSettings();
    return newTemplate;
  }

  async updateTemplate(id, updates) {
    const index = this.templates.findIndex(t => t.id === id);
    if (index !== -1) {
      this.templates[index] = { ...this.templates[index], ...updates };
      await this.saveSettings();
      return this.templates[index];
    }
    return null;
  }

  async deleteTemplate(id) {
    this.templates = this.templates.filter(t => t.id !== id);
    await this.saveSettings();
  }

  async saveSettings() {
    await FunPayStorage.settings.set('autoResponder', {
      enabled: this.enabled,
      templates: this.templates,
      delay: this.delay
    });
  }

  // Предустановленные шаблоны
  static getDefaultTemplates() {
    return [
      {
        name: 'Приветствие',
        keyword: 'привет',
        text: 'Здравствуйте! Чем могу помочь?',
        trigger: 'contains'
      },
      {
        name: 'Вопрос о наличии',
        keyword: 'есть',
        text: 'Да, товар в наличии. Готов к продаже.',
        trigger: 'contains'
      },
      {
        name: 'Вопрос о цене',
        keyword: 'цена',
        text: 'Цена указана в объявлении. Скидки обсуждаются индивидуально.',
        trigger: 'contains'
      },
      {
        name: 'Вопрос о доставке',
        keyword: 'доставка',
        text: 'Доставка осуществляется сразу после оплаты.',
        trigger: 'contains'
      },
      {
        name: 'Благодарность',
        keyword: 'спасибо',
        text: 'Пожалуйста! Обращайтесь!',
        trigger: 'contains'
      }
    ];
  }
}

// Инициализация
let autoResponder;
if (FunPayUtils.isFunPayPage()) {
  autoResponder = new AutoResponder();
}
