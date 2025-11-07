# Fake Mod Menu - Демонстрационное приложение

⚠️ **ВНИМАНИЕ**: Это демонстрационное приложение, созданное исключительно в образовательных целях. Все функции "читов" **НЕ РАБОТАЮТ** и представлены только в виде UI элементов.

## Описание

Это Android приложение демонстрирует визуальный интерфейс мод меню с оверлеем (наложением поверх других приложений). Приложение включает:

### Функциональность:
- ✅ Главный экран с кнопкой запуска
- ✅ Мод меню работающее поверх других приложений
- ✅ Перетаскиваемое окно меню
- ✅ Несколько вкладок с различными функциями

### Вкладки:
1. **Visuals** - Визуальные настройки (ESP Box, ESP Name, ESP Health, Distance, Lines, Skeleton, Crosshair, FOV Circle, Night Mode, No Flash)
2. **AimBot** - Автонаведение (Enable AimBot, Auto Shoot, Silent Aim, Aim at Head/Body, Target Lock, настройки FOV и Smooth)
3. **Misc** - Разное (Speed Hack, No Recoil, No Spread, Fast Reload, Infinite Ammo, Rapid Fire, Jump Hack, Fly Mode, Teleport, Anti Ban)
4. **Player** - Игрок (God Mode, Infinite Health/Armor, Auto Heal, Super Damage, One Shot Kill, No Fall/Fire Damage, Stealth Mode)
5. **Settings** - Настройки (Show FPS/Ping, Panic Button, Save Config, Auto Update, Menu Opacity)

## Требования

- Android SDK (минимальная версия: Android 5.0 / API 21)
- JDK 8 или выше
- Gradle 7.4+

## Установка и сборка

### 1. Клонирование проекта

```bash
cd FakeModMenu
```

### 2. Создание keystore для подписи APK

Запустите скрипт для создания keystore:

```bash
chmod +x create_keystore.sh
./create_keystore.sh
```

Или создайте вручную с помощью keytool:

```bash
keytool -genkeypair -v -keystore keystore.jks -alias modmenu -keyalg RSA -keysize 2048 -validity 10000
```

При создании вам будет предложено ввести:
- Пароль для keystore
- Пароль для ключа
- Информацию об организации (можно оставить пустым, нажимая Enter)

### 3. Настройка подписи

Создайте файл `keystore.properties` в корне проекта:

```properties
storePassword=ваш_пароль_хранилища
keyPassword=ваш_пароль_ключа
keyAlias=modmenu
storeFile=keystore.jks
```

**ВАЖНО**: Не добавляйте этот файл в git! Он содержит приватные данные.

### 4. Сборка APK

#### Debug версия (без подписи):
```bash
./gradlew assembleDebug
```
APK будет находиться в: `app/build/outputs/apk/debug/app-debug.apk`

#### Release версия (подписанная):
```bash
./gradlew assembleRelease
```
APK будет находиться в: `app/build/outputs/apk/release/app-release.apk`

### 5. Установка на устройство

```bash
# Для debug версии
adb install app/build/outputs/apk/debug/app-debug.apk

# Для release версии
adb install app/build/outputs/apk/release/app-release.apk
```

## Использование

1. Установите APK на Android устройство
2. Запустите приложение "Mod Menu"
3. При первом запуске разрешите приложению отображаться поверх других окон
4. Нажмите кнопку "Запустить"
5. Мод меню появится на экране
6. Перетаскивайте меню за заголовок
7. Переключайтесь между вкладками
8. Используйте кнопку "×" чтобы скрыть/показать меню

## Структура проекта

```
FakeModMenu/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/example/fakemodmenu/
│   │       │   ├── MainActivity.java          # Главная активность
│   │       │   └── OverlayService.java        # Сервис оверлея
│   │       ├── res/
│   │       │   ├── layout/
│   │       │   │   ├── activity_main.xml      # UI главного экрана
│   │       │   │   └── overlay_menu.xml       # UI мод меню
│   │       │   └── values/
│   │       │       ├── strings.xml
│   │       │       ├── colors.xml
│   │       │       └── themes.xml
│   │       └── AndroidManifest.xml
│   ├── build.gradle
│   └── proguard-rules.pro
├── build.gradle
├── settings.gradle
├── gradle.properties
├── create_keystore.sh                          # Скрипт создания keystore
└── README.md
```

## Разрешения

Приложение запрашивает следующие разрешения:
- `SYSTEM_ALERT_WINDOW` - для отображения оверлея поверх других приложений
- `FOREGROUND_SERVICE` - для работы сервиса оверлея

## Технические детали

- **Язык**: Java
- **Минимальная версия Android**: 5.0 (API 21)
- **Целевая версия Android**: 13 (API 33)
- **Библиотеки**:
  - AndroidX AppCompat 1.6.1
  - Material Components 1.9.0
  - ConstraintLayout 2.1.4

## Отладка

Для просмотра логов:
```bash
adb logcat | grep "FakeModMenu"
```

Для удаления приложения:
```bash
adb uninstall com.example.fakemodmenu
```

## Важные замечания

- ⚠️ Это **демонстрационное** приложение
- ⚠️ Все функции "читов" **НЕ РАБОТАЮТ**
- ⚠️ Приложение создано **исключительно в образовательных целях**
- ⚠️ Не используйте подобные приложения в реальных играх - это нарушает правила и может привести к бану

## Поддерживаемые устройства

- Android 5.0 и выше
- Все размеры экранов
- Все разрешения

## Лицензия

Создано в образовательных целях. Используйте на свой риск.

## Changelog

### Version 1.0
- Первый релиз
- Основной UI
- 5 вкладок с настройками
- Поддержка оверлея
- Перетаскиваемое окно

---

**Создано**: 2025
**Автор**: Demo App
**Цель**: Образовательная демонстрация
