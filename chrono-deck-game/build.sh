#!/bin/bash
echo "🎮 Сборка ХроноКолода APK..."
echo "================================"

# Проверка наличия необходимых инструментов
if ! command -v java &> /dev/null; then
    echo "❌ Java не установлена. Установите JDK 8 или выше."
    exit 1
fi

# Создание wrapper для gradle если его нет
if [ ! -f "android/gradlew" ]; then
    echo "📦 Создание Gradle Wrapper..."
    cd android
    gradle wrapper --gradle-version 8.0
    chmod +x gradlew
    cd ..
fi

echo "🔨 Компиляция APK..."
cd android

# Сборка debug версии
./gradlew assembleDebug

if [ $? -eq 0 ]; then
    echo "✅ APK успешно создан!"
    echo "📍 Расположение: android/app/build/outputs/apk/debug/app-debug.apk"
    
    # Копируем APK в корень проекта
    cp app/build/outputs/apk/debug/app-debug.apk ../ChronoDeck-v1.0.0-debug.apk
    echo "📦 APK скопирован в: ChronoDeck-v1.0.0-debug.apk"
else
    echo "❌ Ошибка при сборке APK"
    exit 1
fi

cd ..
echo "================================"
echo "🎉 Готово!"
