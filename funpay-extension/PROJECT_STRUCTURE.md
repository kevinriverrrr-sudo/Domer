# 📁 Структура проекта FunPay Ultimate Pro

```
funpay-extension/
│
├── 📄 manifest.json                    # Манифест расширения (Manifest V3)
├── 📄 README.md                        # Основная документация
├── 📄 INSTALL.md                       # Инструкция по установке
├── 📄 FEATURES.md                      # Полный список функций (228+)
├── 📄 CHANGELOG.md                     # История изменений
├── 📄 LICENSE                          # MIT лицензия
├── 📄 .gitignore                       # Git ignore файл
│
├── 📂 icons/                           # Иконки расширения
│   ├── icon16.png
│   ├── icon32.png
│   ├── icon48.png
│   └── icon128.png
│
├── 📂 lib/                             # Библиотеки и утилиты
│   ├── utils.js                        # Вспомогательные функции
│   └── storage.js                      # Менеджер хранилища
│
├── 📂 modules/                         # Основные модули
│   │
│   ├── 📂 seller/                      # Модули для продавцов
│   │   ├── auto-responder.js           # Автоответчик (15 функций)
│   │   ├── price-manager.js            # Управление ценами (18 функций)
│   │   ├── lot-booster.js              # Поднятие лотов (12 функций)
│   │   └── order-automation.js         # Автоматизация заказов (12 функций)
│   │
│   ├── 📂 buyer/                       # Модули для покупателей
│   │   ├── auto-purchase.js            # Автозакупка (15 функций)
│   │   └── price-monitor.js            # Мониторинг цен (12 функций)
│   │
│   ├── 📂 analytics/                   # Аналитика
│   │   ├── competitor-tracker.js       # Трекер конкурентов (16 функций)
│   │   └── sales-stats.js              # Статистика продаж (20 функций)
│   │
│   ├── 📂 automation/                  # Автоматизация
│   │   └── auto-complaints.js          # Автожалобы (10 функций)
│   │
│   ├── 📂 security/                    # Безопасность
│   │   └── scam-detector.js            # Детектор мошенников (15 функций)
│   │
│   ├── 📂 notifications/               # Уведомления
│   │   └── notification-manager.js     # Менеджер уведомлений (15 функций)
│   │
│   └── 📂 common/                      # Общие модули
│       └── dom-observer.js             # Наблюдатель DOM
│
├── 📂 content/                         # Content Scripts
│   ├── main.js                         # Главный content script
│   └── page-injector.js                # Инжектор улучшений страницы
│
├── 📂 background/                      # Background Scripts
│   └── service-worker.js               # Service Worker (фоновый процесс)
│
├── 📂 ui/                              # Пользовательский интерфейс
│   │
│   ├── 📂 popup/                       # Popup окно
│   │   ├── popup.html                  # HTML popup
│   │   ├── popup.js                    # JavaScript popup
│   │   └── popup.css                   # (встроенные стили)
│   │
│   ├── 📂 options/                     # Страница настроек
│   │   ├── options.html                # HTML настроек
│   │   ├── options.js                  # JavaScript настроек
│   │   └── options.css                 # CSS настроек
│   │
│   ├── 📂 dashboard/                   # Дашборд
│   │   └── dashboard.html              # Дашборд с аналитикой
│   │
│   └── 📂 components/                  # UI компоненты
│       └── (будущие компоненты)
│
└── 📂 assets/                          # Ресурсы
    └── 📂 styles/                      # Стили
        ├── inject.css                  # Инжектируемые стили
        └── themes.css                  # Темы оформления

```

---

## 🎯 Основные файлы

### Manifest
- `manifest.json` - Конфигурация расширения, разрешения, content scripts

### Библиотеки
- `lib/utils.js` - 50+ утилитарных функций
- `lib/storage.js` - Система хранения данных, кэш, статистика

### Core модули
- **Продавцы**: 4 модуля, 57+ функций
- **Покупатели**: 2 модуля, 27+ функций  
- **Аналитика**: 2 модуля, 36+ функций
- **Автоматизация**: 1 модуль, 10+ функций
- **Безопасность**: 1 модуль, 15+ функций
- **Уведомления**: 1 модуль, 15+ функций

### Content Scripts
- `content/main.js` - Главный скрипт, инициализация всех модулей
- `content/page-injector.js` - Улучшения интерфейса FunPay

### Background
- `background/service-worker.js` - Фоновые задачи, синхронизация, алармы

### UI
- **Popup**: Быстрый доступ к основным функциям
- **Options**: Детальные настройки всех модулей
- **Dashboard**: Полная аналитика и статистика

---

## 📊 Статистика проекта

- **Всего файлов**: 30+
- **Строк кода**: ~8000+
- **Функций**: 228+
- **Модулей**: 12
- **Тем оформления**: 8
- **Поддерживаемые браузеры**: Chrome, Edge, Firefox

---

## 🔄 Порядок загрузки

1. **Service Worker** (`background/service-worker.js`) - запускается первым
2. **Библиотеки** (`lib/*`) - загружаются на страницу
3. **Модули** (`modules/*`) - инициализируются автоматически
4. **Main Script** (`content/main.js`) - координирует все модули
5. **Page Injector** (`content/page-injector.js`) - улучшает интерфейс

---

## 🎨 Файлы стилей

- `inject.css` - Базовые стили для всех внедряемых элементов
- `themes.css` - 8 тем: светлая, темная, OLED, синяя, зеленая, красная, фиолетовая, авто

---

## 💾 Хранилище данных

Все данные хранятся в `chrome.storage.local`:

- `settings` - Настройки всех модулей
- `stats` - Общая статистика
- `salesData` - Данные о продажах
- `history` - История операций
- `templates` - Шаблоны автоответчика
- `cache` - Кэшированные данные
- `priceHistory` - История цен
- `competitorTrackingData` - Данные конкурентов
- `securityBlacklist` - Черный список
- `notificationQueue` - Очередь уведомлений

---

## 🚀 Точки входа

1. **Popup**: `ui/popup/popup.html` - открывается при клике на иконку
2. **Options**: `ui/options/options.html` - страница настроек
3. **Dashboard**: `ui/dashboard/dashboard.html` - дашборд аналитики
4. **Content Scripts**: автоматически на всех страницах FunPay
5. **Service Worker**: работает постоянно в фоне

---

**Проект создан с ❤️ для сообщества FunPay**
