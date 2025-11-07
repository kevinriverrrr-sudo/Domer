#!/bin/bash
# Скрипт для сборки APK через Docker (не требует установки Android SDK)

echo "🐳 Сборка APK через Docker..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker с https://www.docker.com/"
    exit 1
fi

# Создание dist директории если её нет
if [ ! -d "dist" ]; then
    echo "📦 Копирование файлов в dist..."
    mkdir -p dist
    cp index.html style.css script.js manifest.json dist/
fi

# Сборка Docker образа
echo "🔨 Сборка Docker образа..."
docker build -t lua-generator-builder .

# Запуск сборки APK
echo "🚀 Запуск сборки APK..."
docker run --rm -v "$(pwd):/output" lua-generator-builder sh -c "
    cd android && ./gradlew assembleRelease && \
    cp app/build/outputs/apk/release/app-release.apk /output/lua-script-generator.apk
"

if [ -f "lua-script-generator.apk" ]; then
    echo "✅ APK успешно собран: lua-script-generator.apk"
else
    echo "❌ Ошибка при сборке APK"
    exit 1
fi
