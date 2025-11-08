#!/bin/bash

# Скрипт для автоматической сборки и подписи APK
# Использование: ./build-apk.sh

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        📱 Сборка и подпись APK для FunPay Mobile            ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Проверка наличия Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Ошибка: Node.js не установлен!"
    echo "Установите Node.js с https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js установлен: $(node --version)"
echo ""

# Проверка наличия npm
if ! command -v npm &> /dev/null; then
    echo "❌ Ошибка: npm не установлен!"
    exit 1
fi

echo "✅ npm установлен: $(npm --version)"
echo ""

# Проверка наличия eas-cli
if ! command -v eas &> /dev/null; then
    echo "⚠️  EAS CLI не установлен. Устанавливаю..."
    npm install -g eas-cli
    echo "✅ EAS CLI установлен!"
else
    echo "✅ EAS CLI установлен: $(eas --version)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 ВЫБЕРИТЕ МЕТОД СБОРКИ:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1) EAS Build - Продакшен (рекомендуется)"
echo "   ✅ Автоматическая подпись"
echo "   ✅ Оптимизированный APK"
echo "   ⏱️  Время: 10-20 минут"
echo ""
echo "2) EAS Build - Preview (быстрее)"
echo "   ✅ Автоматическая подпись"
echo "   ⚡ Быстрая сборка"
echo "   ⏱️  Время: 8-15 минут"
echo ""
echo "3) Локальная сборка"
echo "   ⚠️  Требуется Android Studio"
echo "   ⚠️  Нужно настроить вручную"
echo "   ⏱️  Время: 5-10 минут"
echo ""
read -p "Введите номер (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Запуск сборки продакшен APK..."
        echo ""
        echo "Expo автоматически:"
        echo "  ✅ Создаст keystore"
        echo "  ✅ Соберет APK"
        echo "  ✅ Подпишет APK"
        echo ""
        
        # Проверка авторизации
        if ! eas whoami &> /dev/null; then
            echo "⚠️  Необходима авторизация в Expo"
            echo "Войдите в аккаунт или создайте новый"
            echo ""
            eas login
        fi
        
        echo ""
        echo "🔨 Начинаю сборку..."
        eas build -p android --profile production
        
        echo ""
        echo "✅ Сборка запущена!"
        echo "📥 Скачайте готовый APK по ссылке выше"
        ;;
    
    2)
        echo ""
        echo "🚀 Запуск сборки preview APK..."
        echo ""
        
        # Проверка авторизации
        if ! eas whoami &> /dev/null; then
            echo "⚠️  Необходима авторизация в Expo"
            eas login
        fi
        
        echo ""
        echo "🔨 Начинаю сборку..."
        eas build -p android --profile preview
        
        echo ""
        echo "✅ Сборка запущена!"
        echo "📥 Скачайте готовый APK по ссылке выше"
        ;;
    
    3)
        echo ""
        echo "🔧 Локальная сборка APK..."
        echo ""
        
        # Проверка Android SDK
        if [ -z "$ANDROID_HOME" ]; then
            echo "❌ Ошибка: ANDROID_HOME не настроен!"
            echo ""
            echo "Установите Android Studio и настройте переменные:"
            echo "  export ANDROID_HOME=\$HOME/Android/Sdk"
            echo "  export PATH=\$PATH:\$ANDROID_HOME/platform-tools"
            echo ""
            exit 1
        fi
        
        echo "✅ ANDROID_HOME: $ANDROID_HOME"
        echo ""
        echo "📦 Установка зависимостей..."
        npm install
        
        echo ""
        echo "🔨 Создание нативных папок..."
        npx expo prebuild
        
        echo ""
        echo "🏗️  Сборка APK..."
        cd android
        ./gradlew assembleRelease
        
        echo ""
        echo "✅ APK собран!"
        echo "📁 Файл: android/app/build/outputs/apk/release/app-release.apk"
        echo ""
        echo "⚠️  ВНИМАНИЕ: APK не подписан!"
        echo "Для подписи используйте keytool и jarsigner"
        echo "Или используйте EAS Build для автоматической подписи"
        ;;
    
    *)
        echo "❌ Неверный выбор!"
        exit 1
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Готово!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
