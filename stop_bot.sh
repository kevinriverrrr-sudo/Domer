#!/bin/bash

# Остановка бота

echo "⏹️  Остановка Card Checker Bot..."

if pgrep -f "python3 bot.py" > /dev/null; then
    pkill -f "python3 bot.py"
    sleep 1
    
    if pgrep -f "python3 bot.py" > /dev/null; then
        echo "⚠️  Бот не остановился. Принудительная остановка..."
        pkill -9 -f "python3 bot.py"
    fi
    
    echo "✅ Бот остановлен!"
else
    echo "ℹ️  Бот не запущен"
fi
