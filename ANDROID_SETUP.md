# Android Build Configuration

Этот файл содержит инструкции для автоматической инициализации Android проекта.

## Автоматическая инициализация

Запустите следующие команды для создания Android проекта:

```bash
# Установка зависимостей
npm install

# Добавление Android платформы
npx cap add android

# Синхронизация файлов
npx cap sync android
```

После этого структура Android проекта будет создана автоматически в папке `android/`.

## Структура Android проекта

После инициализации будет создана следующая структура:

```
android/
├── app/
│   ├── build.gradle
│   ├── src/
│   │   └── main/
│   │       ├── AndroidManifest.xml
│   │       ├── java/
│   │       └── res/
│   └── build/
│       └── outputs/
│           └── apk/
│               └── release/
│                   └── app-release.apk  (готовый APK)
├── build.gradle
├── gradle.properties
├── settings.gradle
└── gradlew (Linux/macOS) или gradlew.bat (Windows)
```

## Сборка APK

После инициализации используйте скрипты сборки:
- Linux/macOS: `./build-apk.sh`
- Windows: `build-apk.bat`

Или вручную:
```bash
cd android
./gradlew assembleRelease
```

Готовый APK будет в: `android/app/build/outputs/apk/release/app-release.apk`
