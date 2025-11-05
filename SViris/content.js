// Content script for SViris - monitors page behavior

(function() {
  'use strict';

  let monitoringEnabled = true;
  let scriptCount = 0;
  let suspiciousActivities = [];

  // Initialize
  chrome.storage.local.get(['monitoring'], (result) => {
    const settings = result.monitoring || {};
    monitoringEnabled = settings.scripts !== false;
    
    if (monitoringEnabled) {
      initializeMonitoring();
    }
  });

  function initializeMonitoring() {
    // Monitor script execution
    monitorScriptExecution();
    
    // Monitor DOM manipulation
    monitorDOMChanges();
    
    // Monitor form submissions
    monitorFormSubmissions();
    
    // Monitor console activity
    monitorConsoleActivity();
    
    // Check for suspicious iframes
    checkSuspiciousIframes();
    
    // Monitor clipboard access
    monitorClipboardAccess();
  }

  // Monitor script execution
  function monitorScriptExecution() {
    const originalCreateElement = document.createElement;
    
    document.createElement = function(tagName) {
      const element = originalCreateElement.call(document, tagName);
      
      if (tagName.toLowerCase() === 'script') {
        scriptCount++;
        chrome.runtime.sendMessage({ 
          action: 'incrementStat', 
          stat: 'scripts' 
        });
        
        // Check for suspicious script sources
        const observer = new MutationObserver((mutations) => {
          mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'src') {
              const src = element.src;
              if (src && isSuspiciousUrl(src)) {
                reportSuspicious('Обнаружен подозрительный скрипт: ' + src);
              }
            }
          });
        });
        
        observer.observe(element, { attributes: true });
      }
      
      return element;
    };
  }

  // Monitor DOM changes for suspicious activity
  function monitorDOMChanges() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) { // Element node
            // Check for hidden iframes
            if (node.tagName === 'IFRAME' && isHidden(node)) {
              reportSuspicious('Обнаружен скрытый iframe');
            }
            
            // Check for suspicious forms
            if (node.tagName === 'FORM') {
              const action = node.getAttribute('action');
              if (action && isSuspiciousUrl(action)) {
                reportSuspicious('Обнаружена подозрительная форма: ' + action);
              }
            }
          }
        });
      });
    });

    observer.observe(document.body || document.documentElement, {
      childList: true,
      subtree: true
    });
  }

  // Monitor form submissions
  function monitorFormSubmissions() {
    document.addEventListener('submit', (event) => {
      const form = event.target;
      const action = form.action;
      
      // Check if form is submitting to a different domain
      if (action && !isSameDomain(action, window.location.href)) {
        const hasPasswordField = form.querySelector('input[type="password"]');
        
        if (hasPasswordField) {
          reportSuspicious('Форма с паролем отправляется на внешний домен: ' + action);
        }
      }
    }, true);
  }

  // Monitor console activity
  function monitorConsoleActivity() {
    const originalError = console.error;
    const originalWarn = console.warn;
    
    console.error = function(...args) {
      // Check for security-related errors
      const message = args.join(' ');
      if (message.includes('SecurityError') || message.includes('CORS')) {
        reportSuspicious('Обнаружена ошибка безопасности: ' + message.substring(0, 100));
      }
      originalError.apply(console, args);
    };
    
    console.warn = function(...args) {
      const message = args.join(' ');
      if (message.includes('Mixed Content') || message.includes('Insecure')) {
        reportSuspicious('Предупреждение безопасности: ' + message.substring(0, 100));
      }
      originalWarn.apply(console, args);
    };
  }

  // Check for suspicious iframes
  function checkSuspiciousIframes() {
    setTimeout(() => {
      const iframes = document.querySelectorAll('iframe');
      iframes.forEach((iframe) => {
        const src = iframe.src;
        
        if (isHidden(iframe)) {
          reportSuspicious('Найден скрытый iframe');
        }
        
        if (src && isSuspiciousUrl(src)) {
          reportSuspicious('Обнаружен iframe с подозрительным источником: ' + src);
        }
      });
    }, 2000);
  }

  // Monitor clipboard access
  function monitorClipboardAccess() {
    document.addEventListener('copy', () => {
      chrome.runtime.sendMessage({ 
        action: 'logActivity', 
        data: {
          type: 'info',
          message: 'Страница получила доступ к буферу обмена',
          timestamp: Date.now()
        }
      });
    });

    document.addEventListener('paste', () => {
      chrome.runtime.sendMessage({ 
        action: 'logActivity', 
        data: {
          type: 'info',
          message: 'Страница прочитала данные из буфера обмена',
          timestamp: Date.now()
        }
      });
    });
  }

  // Helper functions
  function isSuspiciousUrl(url) {
    try {
      const urlObj = new URL(url, window.location.href);
      const suspiciousPatterns = [
        /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/,  // IP address
        /\.tk$|\.ml$|\.ga$|\.cf$/i,            // Free domains
        /malware|phish|hack|crack/i,            // Suspicious keywords
        /bit\.ly|tinyurl|shorturl/i             // URL shorteners
      ];
      
      return suspiciousPatterns.some(pattern => pattern.test(urlObj.href));
    } catch (e) {
      return false;
    }
  }

  function isSameDomain(url1, url2) {
    try {
      const domain1 = new URL(url1).hostname;
      const domain2 = new URL(url2).hostname;
      return domain1 === domain2;
    } catch (e) {
      return false;
    }
  }

  function isHidden(element) {
    const style = window.getComputedStyle(element);
    return style.display === 'none' || 
           style.visibility === 'hidden' || 
           style.opacity === '0' ||
           element.offsetWidth === 0 ||
           element.offsetHeight === 0;
  }

  function reportSuspicious(message) {
    suspiciousActivities.push(message);
    
    chrome.runtime.sendMessage({
      action: 'reportSuspicious',
      data: {
        message: message,
        url: window.location.href,
        timestamp: Date.now()
      }
    });
  }

  // Check for anti-debugging techniques
  function detectAntiDebugging() {
    const start = performance.now();
    debugger; // This will slow down execution if debugger is open
    const end = performance.now();
    
    if (end - start > 100) {
      reportSuspicious('Обнаружена попытка определения отладчика');
    }
  }

  // Periodically check for suspicious activity
  setInterval(() => {
    checkSuspiciousIframes();
  }, 30000); // Every 30 seconds

  // Detect SSL/TLS issues
  if (window.location.protocol === 'http:' && !window.location.hostname.includes('localhost')) {
    const hasSensitiveFields = document.querySelector('input[type="password"], input[type="email"]');
    
    if (hasSensitiveFields) {
      reportSuspicious('Небезопасное соединение (HTTP) с полями для ввода конфиденциальных данных');
    }
  }

  // Detect clickjacking attempts
  if (window.top !== window.self) {
    reportSuspicious('Страница загружена во фрейме - возможна попытка clickjacking');
  }

  // Listen for messages from background script
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getSuspiciousActivities') {
      sendResponse({ activities: suspiciousActivities });
    }
  });

  console.log('SViris content script loaded on:', window.location.href);
})();
