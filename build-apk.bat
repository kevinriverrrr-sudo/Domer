@echo off
REM Скрипт для сборки APK файла (Windows)

echo 🚀 Начинаем сборку APK...

REM Проверка наличия Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js не установлен. Установите Node.js с https://nodejs.org/
    exit /b 1
)

REM Установка зависимостей
echo 📦 Установка зависимостей...
call npm install

REM Инициализация Capacitor (если еще не инициализирован)
if not exist "android" (
    echo 🔧 Инициализация Capacitor...
    call npx cap add android
)

REM Синхронизация файлов
echo 🔄 Синхронизация файлов...
call npx cap sync android

REM Переход в директорию Android
cd android

REM Сборка APK
echo 🔨 Сборка APK...
call gradlew.bat assembleRelease

REM Проверка результата
if exist "app\build\outputs\apk\release\app-release.apk" (
    echo ✅ APK успешно собран!
    echo 📱 Файл находится в: android\app\build\outputs\apk\release\app-release.apk
    
    REM Копирование в корневую директорию
    copy "app\build\outputs\apk\release\app-release.apk" "..\lua-script-generator.apk"
    echo 📦 APK скопирован в корневую директорию: lua-script-generator.apk
) else (
    echo ❌ Ошибка при сборке APK
    exit /b 1
)

cd ..

echo 🎉 Готово!
