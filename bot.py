#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = "7560458678:AAHbtiK7z0QiII5Iz3fzo17cReOaDS-2tBU"
API_KEY = "c253831ad835f851d5ebd505d7fa6ddf"
API_BASE_URL = "https://www.1secmail.com/api/v1/"

user_emails = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Привет! Я бот для генерации временных Gmail почт.\n\n"
        "Доступные команды:\n"
        "/generate - Сгенерировать новую временную почту\n"
        "/check - Проверить почту на новые письма\n"
        "/myemail - Показать вашу текущую почту\n"
        "/help - Показать справку"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Справка по использованию бота:\n\n"
        "1. /generate - Создает новую временную почту Gmail\n"
        "2. /check - Проверяет вашу почту на наличие новых писем\n"
        "3. /myemail - Показывает адрес вашей текущей почты\n"
        "4. /help - Показывает эту справку\n\n"
        "После генерации почты вы можете использовать её для регистрации. "
        "Используйте /check для получения кодов подтверждения."
    )
    await update.message.reply_text(help_text)

async def generate_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}?action=genRandomMailbox&count=1") as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        email = data[0]
                        user_emails[user_id] = email
                        message = (
                            f"Временная почта успешно создана!\n\n"
                            f"Ваш email: `{email}`\n\n"
                            f"Используйте эту почту для регистрации. "
                            f"После получения письма используйте /check для просмотра кодов."
                        )
                        await update.message.reply_text(message, parse_mode='Markdown')
                    else:
                        await update.message.reply_text("Ошибка при генерации почты. Попробуйте позже.")
                else:
                    import random
                    import string
                    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                    email = f"{username}@1secmail.com"
                    user_emails[user_id] = email
                    message = (
                        f"Временная почта успешно создана!\n\n"
                        f"Ваш email: `{email}`\n\n"
                        f"Используйте эту почту для регистрации. "
                        f"После получения письма используйте /check для просмотра кодов."
                    )
                    await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка при генерации почты: {e}")
        await update.message.reply_text("Произошла ошибка при генерации почты. Попробуйте позже.")

async def check_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_emails:
        await update.message.reply_text(
            "У вас нет активной почты. Используйте /generate для создания новой."
        )
        return
    email = user_emails[user_id]
    try:
        login, domain = email.split('@')
        async with aiohttp.ClientSession() as session:
            url = f"{API_BASE_URL}?action=getMessages&login={login}&domain={domain}"
            async with session.get(url) as response:
                if response.status == 200:
                    messages = await response.json()
                    if not messages:
                        await update.message.reply_text("Писем пока нет. Проверьте позже.")
                        return
                    messages_text = f"Найдено писем: {len(messages)}\n\n"
                    for msg in messages[:5]:
                        msg_id = msg['id']
                        sender = msg['from']
                        subject = msg['subject']
                        date = msg['date']
                        read_url = f"{API_BASE_URL}?action=readMessage&login={login}&domain={domain}&id={msg_id}"
                        async with session.get(read_url) as read_response:
                            if read_response.status == 200:
                                message_data = await read_response.json()
                                body = message_data.get('textBody', message_data.get('htmlBody', ''))
                                import re
                                codes = re.findall(r'\b\d{4,8}\b', body)
                                messages_text += f"От: {sender}\n"
                                messages_text += f"Тема: {subject}\n"
                                messages_text += f"Дата: {date}\n"
                                if codes:
                                    messages_text += f"Найденные коды: {', '.join(codes[:5])}\n"
                                messages_text += f"Текст:\n{body[:200]}...\n\n"
                    await update.message.reply_text(messages_text)
                else:
                    await update.message.reply_text("Ошибка при проверке почты. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Ошибка при проверке почты: {e}")
        await update.message.reply_text("Произошла ошибка при проверке почты.")

async def my_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_emails:
        await update.message.reply_text(
            "У вас нет активной почты. Используйте /generate для создания новой."
        )
    else:
        email = user_emails[user_id]
        await update.message.reply_text(
            f"Ваша текущая почта: `{email}`",
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("generate", generate_email))
    application.add_handler(CommandHandler("check", check_email))
    application.add_handler(CommandHandler("myemail", my_email))
    application.add_error_handler(error_handler)
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
