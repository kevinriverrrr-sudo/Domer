#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram бот с интеграцией Gemini AI
"""

import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_BOT_TOKEN = "7560458678:AAHbtiK7z0QiII5Iz3fzo17cReOaDS-2tBU"
GEMINI_API_KEY = "AIzaSyC-u6Of5R3wYfXXie6kwh5yAcyDq1HCNAc"

# Настройка Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    await update.message.reply_text(
        "Привет! Я бот с интеграцией Gemini AI.\n"
        "Просто отправь мне сообщение, и я отвечу с помощью нейросети Gemini!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n\n"
        "Просто отправь мне любое сообщение, и я отвечу с помощью Gemini AI!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    user_message = update.message.text
    
    # Отправляем сообщение о том, что бот думает
    thinking_message = await update.message.reply_text("🤔 Думаю...")
    
    try:
        # Получаем ответ от Gemini AI
        response = model.generate_content(user_message)
        
        # Получаем текст ответа
        response_text = response.text if hasattr(response, 'text') else str(response)
        
        # Отправляем ответ пользователю (разбиваем на части, если слишком длинный)
        if len(response_text) > 4096:
            # Telegram ограничивает длину сообщения до 4096 символов
            chunks = [response_text[i:i+4096] for i in range(0, len(response_text), 4096)]
            await thinking_message.edit_text(chunks[0])
            for chunk in chunks[1:]:
                await update.message.reply_text(chunk)
        else:
            await thinking_message.edit_text(response_text)
        
    except Exception as e:
        logger.error(f"Ошибка при обращении к Gemini AI: {e}")
        await thinking_message.edit_text(
            f"Извините, произошла ошибка при обработке вашего запроса.\n"
            f"Ошибка: {str(e)}"
        )


def main() -> None:
    """Основная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logger.info("Запуск Telegram бота...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
