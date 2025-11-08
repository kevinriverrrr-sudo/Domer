#!/bin/bash

# Скрипт для запуска Telegram бота

echo "🚀 Запуск Card Checker Bot..."
echo ""
echo "📝 Убедитесь что вы настроили config.py с вашими credentials:"
echo "   - BOT_TOKEN (уже настроен)"
echo "   - PAYPAL_CLIENT_ID"
echo "   - PAYPAL_SECRET"
echo ""

cd /workspace

# Запуск бота
python3 bot.py
