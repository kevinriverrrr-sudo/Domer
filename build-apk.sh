#!/bin/bash
# Скрипт для сборки APK файла

echo "🚀 Начинаем сборку APK..."

# Проверка наличия Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не установлен. Установите Node.js с https://nodejs.org/"
    exit 1
fi

# Проверка наличия npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm не установлен"
    exit 1
fi

# Установка зависимостей
echo "📦 Установка зависимостей..."
npm install

# Инициализация Capacitor (если еще не инициализирован)
if [ ! -d "android" ]; then
    echo "🔧 Инициализация Capacitor..."
    npx cap add android
fi

# Синхронизация файлов
echo "🔄 Синхронизация файлов..."
npx cap sync android

# Переход в директорию Android
cd android

# Проверка наличия Gradle
if [ ! -f "gradlew" ]; then
    echo "❌ Gradle wrapper не найден. Инициализируйте Android проект заново."
    exit 1
fi

# Сборка APK
echo "🔨 Сборка APK..."
./gradlew assembleRelease

# Проверка результата
if [ -f "app/build/outputs/apk/release/app-release.apk" ]; then
    echo "✅ APK успешно собран!"
    echo "📱 Файл находится в: android/app/build/outputs/apk/release/app-release.apk"
    
    # Копирование в корневую директорию
    cp app/build/outputs/apk/release/app-release.apk ../lua-script-generator.apk
    echo "📦 APK скопирован в корневую директорию: lua-script-generator.apk"
else
    echo "❌ Ошибка при сборке APK"
    exit 1
fi

cd ..

echo "🎉 Готово!"
