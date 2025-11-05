#!/bin/bash
# Полная автоматическая компиляция APK

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   Компиляция SAMP Arizona RP Admin Tools в APK             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Установка зависимостей
echo "[1/5] Установка системных зависимостей..."
sudo apt-get update -qq
sudo apt-get install -y -qq git unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev 2>&1 | grep -v "^$"

echo "[2/5] Установка Python зависимостей..."
pip3 install --user --quiet buildozer kivy cython pyperclip
export PATH="$HOME/.local/bin:$PATH"

echo "[3/5] Инициализация Buildozer..."
if [ ! -f "buildozer.spec" ]; then
    buildozer init
fi

echo "[4/5] Компиляция APK..."
echo "    ⚠️  Это займет 30-60 минут при первом запуске!"
echo "    Buildozer скачает Android SDK и NDK автоматически"
echo ""

buildozer android debug

if [ -f "bin/*.apk" ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    ✅ УСПЕШНО!                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📱 APK файл создан:"
    ls -lh bin/*.apk
    echo ""
    echo "🎉 Установите APK на Android устройство!"
else
    echo ""
    echo "❌ APK файл не создан"
    echo "Проверьте логи в папке .buildozer/"
fi
