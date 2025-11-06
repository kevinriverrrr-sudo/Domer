#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import asyncio
import aiohttp
import urllib.parse
import html
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = "7560458678:AAHbtiK7z0QiII5Iz3fzo17cReOaDS-2tBU"
RAPIDAPI_KEY = "0fa02ae94fmsh38e4f0db6422798p18660ejsn43145aca047e"
API_KEY = "c253831ad835f851d5ebd505d7fa6ddf"  # Оригинальный API ключ
API_HOST = "flash-temp-mail.p.rapidapi.com"
API_BASE_URL = f"https://{API_HOST}"

user_emails = {}
user_mailbox_ids = {}  # Храним ID почтового ящика для каждого пользователя

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
    max_retries = 3
    retry_delay = 2  # секунды
    
    for attempt in range(max_retries):
        try:
            headers = {
                'x-rapidapi-key': RAPIDAPI_KEY,
                'x-rapidapi-host': API_HOST,
                'Content-Type': 'application/json'
            }
            payload = {"not_required": "not_required"}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{API_BASE_URL}/mailbox/create?free_domains=false",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"API Response: {data}")
                        
                        # Парсим ответ API
                        email = None
                        mailbox_id = None
                        
                        if 'email' in data:
                            email = data['email']
                            mailbox_id = data.get('id') or data.get('mailbox_id') or data.get('mailboxId')
                        elif 'address' in data:
                            email = data['address']
                            mailbox_id = data.get('id') or data.get('mailbox_id') or data.get('mailboxId')
                        elif isinstance(data, str):
                            # Если ответ - просто строка с email
                            email = data
                        elif isinstance(data, dict) and len(data) == 1:
                            # Пробуем взять первое значение
                            email = list(data.values())[0]
                        
                        if email:
                            user_emails[user_id] = email
                            if mailbox_id:
                                user_mailbox_ids[user_id] = mailbox_id
                            
                            message = (
                                f"Временная почта успешно создана!\n\n"
                                f"Ваш email: `{email}`\n\n"
                                f"Используйте эту почту для регистрации. "
                                f"После получения письма используйте /check для просмотра кодов."
                            )
                            await update.message.reply_text(message, parse_mode='Markdown')
                            return
                        else:
                            logger.error(f"Неожиданный формат ответа API: {data}")
                            await update.message.reply_text("Ошибка при генерации почты. Попробуйте позже.")
                            return
                    
                    elif response.status == 403:
                        error_text = await response.text()
                        logger.error(f"Ошибка API 403: {error_text}")
                        # Пробуем альтернативный сервис как fallback
                        if attempt == 0:
                            logger.info("Пробуем альтернативный сервис временных почт...")
                            # Используем 1secmail как fallback
                            try:
                                async with session.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1") as fallback_response:
                                    if fallback_response.status == 200:
                                        fallback_data = await fallback_response.json()
                                        if fallback_data and len(fallback_data) > 0:
                                            email = fallback_data[0]
                                            user_emails[user_id] = email
                                            message = (
                                                f"Временная почта успешно создана (через альтернативный сервис)!\n\n"
                                                f"Ваш email: `{email}`\n\n"
                                                f"Используйте эту почту для регистрации. "
                                                f"После получения письма используйте /check для просмотра кодов."
                                            )
                                            await update.message.reply_text(message, parse_mode='Markdown')
                                            return
                            except Exception as fallback_error:
                                logger.error(f"Ошибка fallback сервиса: {fallback_error}")
                        
                        await update.message.reply_text(
                            "Ошибка доступа к API. Проверьте подписку на RapidAPI или попробуйте позже."
                        )
                        return
                    
                    elif response.status == 429:
                        if attempt < max_retries - 1:
                            wait_time = retry_delay * (attempt + 1)
                            logger.warning(f"Rate limit (429), ожидание {wait_time} секунд перед повтором...")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            error_text = await response.text()
                            logger.error(f"Ошибка API 429 после {max_retries} попыток: {error_text}")
                            await update.message.reply_text(
                                "Превышен лимит запросов. Подождите немного и попробуйте снова."
                            )
                            return
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка API: {response.status} - {error_text}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay)
                            continue
                        else:
                            await update.message.reply_text(
                                f"Ошибка при генерации почты (код {response.status}). Попробуйте позже."
                            )
                            return
                            
        except asyncio.TimeoutError:
            logger.error(f"Таймаут при генерации почты (попытка {attempt + 1})")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                continue
            else:
                await update.message.reply_text("Таймаут при подключении к API. Попробуйте позже.")
                return
                
        except Exception as e:
            logger.error(f"Ошибка при генерации почты: {e}", exc_info=True)
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                continue
            else:
                await update.message.reply_text("Произошла ошибка при генерации почты. Попробуйте позже.")
                return

async def check_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_emails:
        await update.message.reply_text(
            "У вас нет активной почты. Используйте /generate для создания новой."
        )
        return
    
    email = user_emails[user_id]
    mailbox_id = user_mailbox_ids.get(user_id)
    
    # Проверяем, какой сервис используется (по домену)
    is_1secmail = '@1secmail.com' in email or '@1secmail.org' in email or '@1secmail.net' in email
    
    try:
        if is_1secmail:
            # Используем 1secmail API
            login, domain = email.split('@')
            async with aiohttp.ClientSession() as session:
                url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
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
                            
                            read_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg_id}"
                            async with session.get(read_url, timeout=aiohttp.ClientTimeout(total=10)) as read_response:
                                if read_response.status == 200:
                                    message_data = await read_response.json()
                                    body = message_data.get('textBody', message_data.get('htmlBody', ''))
                                    codes = re.findall(r'\b\d{4,8}\b', body)
                                    
                                    messages_text += f"От: {sender}\n"
                                    messages_text += f"Тема: {subject}\n"
                                    messages_text += f"Дата: {date}\n"
                                    if codes:
                                        messages_text += f"Найденные коды: {', '.join(codes[:5])}\n"
                                    if isinstance(body, str):
                                        body_clean = html.unescape(body)
                                        body_clean = re.sub(r'<[^>]+>', '', body_clean)
                                        messages_text += f"Текст:\n{body_clean[:300]}...\n\n"
                                    else:
                                        messages_text += f"Текст:\n{str(body)[:300]}...\n\n"
                        
                        await update.message.reply_text(messages_text)
                    else:
                        await update.message.reply_text("Ошибка при проверке почты. Попробуйте позже.")
            return
        
        # Используем RapidAPI flash-temp-mail
        headers = {
            'x-rapidapi-key': RAPIDAPI_KEY,
            'x-rapidapi-host': API_HOST,
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            # Пробуем разные варианты endpoints для получения писем
            # Вариант 1: используем mailbox_id если есть
            if mailbox_id:
                url = f"{API_BASE_URL}/mailbox/{mailbox_id}/messages"
            else:
                # Вариант 2: используем email
                encoded_email = urllib.parse.quote(email)
                url = f"{API_BASE_URL}/mailbox/{encoded_email}/messages"
            
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Messages response: {data}")
                    
                    # Обрабатываем разные форматы ответа
                    messages = []
                    if isinstance(data, list):
                        messages = data
                    elif isinstance(data, dict):
                        messages = data.get('messages', data.get('items', []))
                    
                    if not messages:
                        await update.message.reply_text("Писем пока нет. Проверьте позже.")
                        return
                    
                    messages_text = f"Найдено писем: {len(messages)}\n\n"
                    
                    for msg in messages[:5]:  # Показываем последние 5 писем
                        msg_id = msg.get('id') or msg.get('messageId') or msg.get('message_id')
                        sender = msg.get('from') or msg.get('sender') or msg.get('fromAddress', 'Неизвестно')
                        subject = msg.get('subject') or msg.get('title', 'Без темы')
                        date = msg.get('date') or msg.get('receivedAt') or msg.get('timestamp', 'Неизвестно')
                        
                        # Получаем содержимое письма
                        if mailbox_id:
                            read_url = f"{API_BASE_URL}/mailbox/{mailbox_id}/messages/{msg_id}"
                        else:
                            encoded_email = urllib.parse.quote(email)
                            read_url = f"{API_BASE_URL}/mailbox/{encoded_email}/messages/{msg_id}"
                        
                        async with session.get(read_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as read_response:
                            if read_response.status == 200:
                                message_data = await read_response.json()
                                body = message_data.get('textBody') or message_data.get('text') or message_data.get('body') or message_data.get('htmlBody', '')
                                
                                codes = re.findall(r'\b\d{4,8}\b', body)
                                
                                messages_text += f"От: {sender}\n"
                                messages_text += f"Тема: {subject}\n"
                                messages_text += f"Дата: {date}\n"
                                
                                if codes:
                                    messages_text += f"Найденные коды: {', '.join(codes[:5])}\n"
                                
                                # Очищаем HTML теги если есть
                                if isinstance(body, str):
                                    body_clean = html.unescape(body)
                                    body_clean = re.sub(r'<[^>]+>', '', body_clean)
                                    messages_text += f"Текст:\n{body_clean[:300]}...\n\n"
                                else:
                                    messages_text += f"Текст:\n{str(body)[:300]}...\n\n"
                            else:
                                # Если не удалось прочитать письмо, показываем только заголовок
                                messages_text += f"От: {sender}\n"
                                messages_text += f"Тема: {subject}\n"
                                messages_text += f"Дата: {date}\n\n"
                    
                    await update.message.reply_text(messages_text)
                elif response.status == 403:
                    await update.message.reply_text("Ошибка доступа к API при проверке почты. Попробуйте позже.")
                elif response.status == 429:
                    await update.message.reply_text("Превышен лимит запросов. Подождите немного и попробуйте снова.")
                elif response.status == 404:
                    await update.message.reply_text("Почтовый ящик не найден. Используйте /generate для создания новой почты.")
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка при проверке почты: {response.status} - {error_text}")
                    await update.message.reply_text(f"Ошибка при проверке почты (код {response.status}). Попробуйте позже.")
                    
    except asyncio.TimeoutError:
        await update.message.reply_text("Таймаут при подключении к API. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Ошибка при проверке почты: {e}", exc_info=True)
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
