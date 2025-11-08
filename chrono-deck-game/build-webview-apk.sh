#!/bin/bash
set -e

echo "🎮 Создание WebView APK для ХроноКолода"
echo "========================================="

# Создаем простой wrapper APK используя готовые инструменты
BUILD_DIR="apk-webview"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

echo "📝 Создание HTML wrapper для WebView..."

# Создаем простое Android приложение
cat > $BUILD_DIR/create-apk.html << 'HTMLEOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ХроноКолода - Установщик APK</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        h1 { text-align: center; }
        .method {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
        }
        .method h2 { color: #ffd700; }
        a {
            color: #87ceeb;
            text-decoration: none;
        }
        a:hover { text-decoration: underline; }
        code {
            background: rgba(0,0,0,0.5);
            padding: 5px 10px;
            border-radius: 5px;
            display: block;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⏳ ХроноКолода: Создание APK</h1>
        
        <div class="method">
            <h2>🌐 Способ 1: Играть в браузере (Работает сейчас!)</h2>
            <p>Откройте файл <strong>build/index.html</strong> в браузере Chrome или Firefox.</p>
            <p>Игра полностью функциональна в браузере!</p>
        </div>

        <div class="method">
            <h2>📱 Способ 2: Онлайн конвертеры (Рекомендуется)</h2>
            <p>Используйте один из бесплатных онлайн-сервисов:</p>
            
            <h3>AppsGeyser (самый простой):</h3>
            <ol>
                <li>Перейдите на <a href="https://appsgeyser.com" target="_blank">https://appsgeyser.com</a></li>
                <li>Выберите "Website" → "Enter URL"</li>
                <li>Загрузите ZIP: <code>ChronoDeck-WebGame-v1.0.0.zip</code></li>
                <li>Или укажите путь к локальному файлу index.html</li>
                <li>Настройте название и иконку</li>
                <li>Скачайте готовый APK!</li>
            </ol>

            <h3>WebIntoApp:</h3>
            <ol>
                <li>Перейдите на <a href="https://app.webintoapp.com" target="_blank">https://app.webintoapp.com</a></li>
                <li>Загрузите ZIP файл игры</li>
                <li>Получите APK</li>
            </ol>

            <h3>Gonative.io:</h3>
            <ol>
                <li>Перейдите на <a href="https://gonative.io" target="_blank">https://gonative.io</a></li>
                <li>Бесплатная версия для тестирования</li>
                <li>Загрузите локальные файлы</li>
            </ol>
        </div>

        <div class="method">
            <h2>🔧 Способ 3: Android Studio (Для разработчиков)</h2>
            <ol>
                <li>Установите <a href="https://developer.android.com/studio" target="_blank">Android Studio</a></li>
                <li>Откройте проект из папки <code>android/</code></li>
                <li>Build → Build Bundle(s) / APK(s) → Build APK(s)</li>
                <li>APK будет в <code>android/app/build/outputs/apk/</code></li>
            </ol>
        </div>

        <div class="method">
            <h2>📦 Способ 4: Cordova CLI</h2>
            <p>Если установлен Node.js и Cordova:</p>
            <code>
npm install -g cordova<br>
cordova create chronodeckapp com.chronodeck.game ChronoDeck<br>
cp -r www/* chronodeckapp/www/<br>
cd chronodeckapp<br>
cordova platform add android<br>
cordova build android
            </code>
        </div>

        <div class="method">
            <h2>💡 Альтернатива: PWA (Progressive Web App)</h2>
            <p>На Android можно установить игру как PWA:</p>
            <ol>
                <li>Откройте <code>build/index.html</code> в Chrome</li>
                <li>Меню → "Добавить на главный экран"</li>
                <li>Игра будет работать как приложение!</li>
            </ol>
        </div>

        <hr>
        <p style="text-align: center; margin-top: 30px;">
            <strong>Веб-версия полностью функциональна!</strong><br>
            Откройте build/index.html и играйте прямо сейчас!
        </p>
    </div>
</body>
</html>
HTMLEOF

cp $BUILD_DIR/create-apk.html ../APK_CREATION_GUIDE.html

echo ""
echo "✅ Создан гайд по созданию APK"
echo "📄 Файл: APK_CREATION_GUIDE.html"
echo ""
echo "🌐 РЕКОМЕНДАЦИЯ: Используйте онлайн-конвертер"
echo "   → AppsGeyser: https://appsgeyser.com (бесплатно)"
echo "   → Загрузите ChronoDeck-WebGame-v1.0.0.zip"
echo "   → Получите готовый APK за 2 минуты!"
echo ""
