import asyncio
import logging
import aiohttp
import random
import string
from datetime import datetime
from dateutil import parser as date_parser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = "7560458678:AAHbtiK7z0QiII5Iz3fzo17cReOaDS-2tBU"

# API для временных почт (Mail.tm)
API_BASE_URL = "https://api.mail.tm"
DOMAINS_URL = f"{API_BASE_URL}/domains"
MESSAGES_URL = f"{API_BASE_URL}/messages"

# Альтернативный API (Guerrilla Mail)
GUERRILLA_API = "https://www.guerrillamail.com/ajax.php"

# Хранилище почт пользователей {user_id: {email: str, login: str, domain: str, token: str}}
user_emails = {}

async def generate_email(user_id: int) -> dict:
    """Генерирует новую временную почту"""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            # Получаем список доступных доменов
            async with session.get(DOMAINS_URL) as resp:
                if resp.status != 200:
                    logger.error(f"Ошибка получения доменов: статус {resp.status}")
                    # Fallback на 1secmail если mail.tm не работает
                    return await generate_email_tempmail(user_id)
                
                domains_data = await resp.json()
                if not domains_data or 'hydra:member' not in domains_data:
                    logger.error("Неверный формат ответа от API доменов")
                    return await generate_email_tempmail(user_id)
                
                domains = domains_data['hydra:member']
                if not domains:
                    logger.error("Список доменов пуст")
                    return await generate_email_tempmail(user_id)
                
                # Выбираем первый доступный домен
                domain = domains[0]['domain']
                
                # Генерируем случайный логин
                login = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
                email = f"{login}@{domain}"
                
                # Генерируем пароль
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                
                # Создаем аккаунт
                account_data = {
                    "address": email,
                    "password": password
                }
                
                async with session.post(f"{API_BASE_URL}/accounts", json=account_data) as resp2:
                    if resp2.status in [200, 201]:
                        # Получаем токен через логин
                        login_data = {
                            "address": email,
                            "password": password
                        }
                        token = ''
                        async with session.post(f"{API_BASE_URL}/token", json=login_data) as resp3:
                            if resp3.status in [200, 201]:
                                token_info = await resp3.json()
                                token = token_info.get('token', '')
                                logger.info(f"Токен получен для {email}")
                            else:
                                error_text = await resp3.text()
                                logger.error(f"Ошибка получения токена: статус {resp3.status}, ответ: {error_text}")
                        
                        user_emails[user_id] = {
                            'email': email,
                            'login': login,
                            'domain': domain,
                            'token': token,
                            'password': password,
                            'api': 'mailtm'
                        }
                        logger.info(f"Создана почта для пользователя {user_id}: {email}, токен: {'есть' if token else 'нет'}")
                        return user_emails[user_id]
                    else:
                        error_text = await resp2.text()
                        logger.error(f"Ошибка создания аккаунта: статус {resp2.status}, ответ: {error_text}")
                        return await generate_email_tempmail(user_id)
                        
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети при генерации почты: {e}")
            return await generate_email_tempmail(user_id)
        except Exception as e:
            logger.error(f"Ошибка генерации почты: {e}", exc_info=True)
            return await generate_email_tempmail(user_id)

async def generate_email_tempmail(user_id: int) -> dict:
    """Генерация через temp-mail.org API"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            # Получаем список доменов
            async with session.get('https://www.1secmail.com/api/v1/?action=getDomainList') as resp:
                if resp.status == 200:
                    domains = await resp.json()
                    if domains:
                        login = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                        domain = random.choice(domains)
                        email = f"{login}@{domain}"
                        
                        user_emails[user_id] = {
                            'email': email,
                            'login': login,
                            'domain': domain,
                            'token': '',
                            'password': '',
                            'api': '1secmail'
                        }
                        logger.info(f"Создана почта через 1secmail для пользователя {user_id}: {email}")
                        return user_emails[user_id]
        except Exception as e:
            logger.error(f"Ошибка генерации через temp-mail: {e}")
        
        # Используем известные домены
        domains_list = ['1secmail.com', '1secmail.org', '1secmail.net', 'wwjmp.com', 'esiix.com', 'bttmp.com', 'kidderminster.com']
        login = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        domain = random.choice(domains_list)
        email = f"{login}@{domain}"
        
        user_emails[user_id] = {
            'email': email,
            'login': login,
            'domain': domain,
            'token': '',
            'password': '',
            'api': '1secmail'
        }
        logger.info(f"Создана почта через 1secmail (fallback) для пользователя {user_id}: {email}")
        return user_emails[user_id]

async def get_messages(user_id: int) -> list:
    """Получает письма для почты пользователя"""
    if user_id not in user_emails:
        return []
    
    email_data = user_emails[user_id]
    
    # Если есть токен, используем Mail.tm API
    if email_data.get('token'):
        headers = {
            'Authorization': f'Bearer {email_data["token"]}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as session:
            try:
                async with session.get(MESSAGES_URL) as resp:
                    if resp.status == 401:
                        # Токен истек, обновляем
                        logger.info(f"Токен истек для {email_data['email']}, обновляем...")
                        login_data = {
                            "address": email_data['email'],
                            "password": email_data['password']
                        }
                        async with aiohttp.ClientSession() as session2:
                            async with session2.post(f"{API_BASE_URL}/token", json=login_data) as resp2:
                                if resp2.status in [200, 201]:
                                    token_info = await resp2.json()
                                    new_token = token_info.get('token', '')
                                    if new_token:
                                        email_data['token'] = new_token
                                        # Пробуем снова получить письма
                                        headers['Authorization'] = f'Bearer {new_token}'
                                        async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as session3:
                                            async with session3.get(MESSAGES_URL) as resp3:
                                                if resp3.status == 200:
                                                    data = await resp3.json()
                                                    logger.info(f"Получено писем через Mail.tm: {len(data.get('hydra:member', [])) if isinstance(data, dict) else len(data) if isinstance(data, list) else 0}")
                                                    if 'hydra:member' in data:
                                                        return data['hydra:member']
                                                    return data if isinstance(data, list) else []
                    
                    if resp.status == 200:
                        data = await resp.json()
                        logger.info(f"Получено писем через Mail.tm: {len(data.get('hydra:member', [])) if isinstance(data, dict) else len(data) if isinstance(data, list) else 0}")
                        if 'hydra:member' in data:
                            return data['hydra:member']
                        return data if isinstance(data, list) else []
                    else:
                        error_text = await resp.text()
                        logger.error(f"Ошибка получения писем через Mail.tm: статус {resp.status}, ответ: {error_text[:200]}")
            except asyncio.TimeoutError:
                logger.error("Таймаут при получении писем через Mail.tm")
            except Exception as e:
                logger.error(f"Ошибка получения писем через Mail.tm: {e}", exc_info=True)
    
    # Fallback на 1secmail
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.1secmail.com/',
        'Origin': 'https://www.1secmail.com'
    }
    
    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as session:
        try:
            # Пробуем разные варианты URL
            urls = [
                f"https://www.1secmail.com/api/v1/?action=getMessages&login={email_data['login']}&domain={email_data['domain']}",
                f"https://www.1secmail.com/api/v1/?action=getMessages&login={email_data['login']}&domain={email_data['domain']}&_={int(asyncio.get_event_loop().time())}"
            ]
            
            for url in urls:
                try:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            messages = await resp.json()
                            logger.info(f"Получено писем через 1secmail: {len(messages) if messages else 0}")
                            return messages if messages else []
                        elif resp.status == 403:
                            logger.warning(f"403 ошибка от 1secmail, пробуем другой способ...")
                            continue
                except Exception as e:
                    logger.warning(f"Ошибка при запросе к {url}: {e}")
                    continue
            
            logger.error(f"Не удалось получить письма через 1secmail")
            return []
        except asyncio.TimeoutError:
            logger.error("Таймаут при получении писем через 1secmail")
            return []
        except Exception as e:
            logger.error(f"Ошибка получения писем: {e}", exc_info=True)
            return []

async def read_message(user_id: int, message_id: int) -> dict:
    """Читает конкретное письмо"""
    if user_id not in user_emails:
        return None
    
    email_data = user_emails[user_id]
    
    # Если есть токен, используем Mail.tm API
    if email_data.get('token'):
        headers = {
            'Authorization': f'Bearer {email_data["token"]}',
            'Accept': 'application/json'
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.get(f"{MESSAGES_URL}/{message_id}") as resp:
                    if resp.status == 200:
                        message = await resp.json()
                        # Преобразуем формат Mail.tm в нужный формат
                        from_addr_obj = message.get('from', {})
                        if isinstance(from_addr_obj, dict):
                            from_addr = from_addr_obj.get('address', 'Неизвестно')
                        else:
                            from_addr = str(from_addr_obj)
                        
                        created_at = message.get('createdAt', '')
                        if isinstance(created_at, dict):
                            timestamp = created_at.get('timestamp', 0)
                        elif isinstance(created_at, str):
                            # Парсим ISO формат даты
                            try:
                                dt = date_parser.parse(created_at)
                                timestamp = int(dt.timestamp())
                            except:
                                timestamp = 0
                        else:
                            timestamp = int(created_at) if created_at else 0
                        
                        # Получаем текст письма
                        text_body = message.get('text', '')
                        if not text_body:
                            # Пробуем получить через отдельный запрос
                            try:
                                async with session.get(f"{MESSAGES_URL}/{message_id}/download") as resp2:
                                    if resp2.status == 200:
                                        text_body = await resp2.text()
                            except:
                                pass
                        
                        return {
                            'from': from_addr,
                            'subject': message.get('subject', ''),
                            'textBody': text_body or message.get('text', ''),
                            'htmlBody': message.get('html', []),
                            'date': str(timestamp),
                            'createdAt': created_at
                        }
                    else:
                        error_text = await resp.text()
                        logger.error(f"Ошибка чтения письма через Mail.tm: статус {resp.status}, ответ: {error_text}")
            except Exception as e:
                logger.error(f"Ошибка чтения письма через Mail.tm: {e}", exc_info=True)
    
    # Fallback на 1secmail
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={email_data['login']}&domain={email_data['domain']}&id={message_id}"
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.error(f"Ошибка чтения письма: статус {resp.status}")
                    return None
                message = await resp.json()
                return message
        except Exception as e:
            logger.error(f"Ошибка чтения письма: {e}", exc_info=True)
            return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        "📧 Я бот для создания временных почтовых ящиков.\n\n"
        "✨ Возможности:\n"
        "• Генерация временных email адресов\n"
        "• Получение писем в реальном времени\n"
        "• Просмотр содержимого писем\n\n"
        "🚀 Начните с создания новой почты!"
    )
    
    keyboard = [
        [InlineKeyboardButton("📧 Создать новую почту", callback_data="create_email")],
        [InlineKeyboardButton("📬 Проверить письма", callback_data="check_messages")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "create_email":
        email_data = await generate_email(user_id)
        if email_data:
            text = (
                "✅ Новая временная почта создана!\n\n"
                f"📧 <b>Ваш email:</b>\n"
                f"<code>{email_data['email']}</code>\n\n"
                "💡 Скопируйте этот адрес и используйте для регистраций.\n"
                "📬 Нажмите 'Проверить письма' чтобы увидеть входящие сообщения."
            )
        else:
            text = "❌ Ошибка при создании почты. Попробуйте позже."
        
        keyboard = [
            [InlineKeyboardButton("📬 Проверить письма", callback_data="check_messages")],
            [InlineKeyboardButton("🔄 Создать другую почту", callback_data="create_email")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    elif query.data == "check_messages":
        if user_id not in user_emails:
            text = (
                "⚠️ У вас нет активной почты.\n\n"
                "Сначала создайте новую почту."
            )
            keyboard = [
                [InlineKeyboardButton("📧 Создать новую почту", callback_data="create_email")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)
            return
        
        messages = await get_messages(user_id)
        email_data = user_emails[user_id]
        
        if not messages:
            text = (
                f"📭 Писем пока нет\n\n"
                f"📧 Ваша почта: <code>{email_data['email']}</code>\n\n"
                "Письма появятся здесь автоматически, когда кто-то отправит сообщение на ваш адрес."
            )
            keyboard = [
                [InlineKeyboardButton("🔄 Обновить", callback_data="check_messages")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            text = f"📬 У вас {len(messages)} письмо(а)\n\n📧 Почта: <code>{email_data['email']}</code>\n\n"
            keyboard = []
            
            for msg in messages[:10]:  # Показываем максимум 10 писем
                # Обработка разных форматов ответа
                if isinstance(msg, dict):
                    if 'from' in msg or 'createdAt' in msg:
                        # Формат Mail.tm
                        from_addr_obj = msg.get('from', {})
                        if isinstance(from_addr_obj, dict):
                            from_addr = from_addr_obj.get('address', 'Неизвестно')
                        else:
                            from_addr = str(from_addr_obj)
                        
                        date_val = msg.get('createdAt', '')
                        if isinstance(date_val, dict):
                            timestamp = date_val.get('timestamp', 0)
                        elif isinstance(date_val, str):
                            try:
                                dt = date_parser.parse(date_val)
                                timestamp = int(dt.timestamp())
                            except:
                                timestamp = 0
                        else:
                            timestamp = int(date_val) if date_val else 0
                        
                        date_str = datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M') if timestamp > 0 else 'Неизвестно'
                        msg_id = msg.get('id', '')
                    else:
                        # Формат 1secmail
                        from_addr = msg.get('from', 'Неизвестно')
                        date_val = msg.get('date', '0')
                        date_str = datetime.fromtimestamp(int(date_val.split('.')[0])).strftime('%d.%m.%Y %H:%M')
                        msg_id = msg.get('id', '')
                    
                    button_text = f"📧 {from_addr[:30]} - {date_str}"
                    keyboard.append([InlineKeyboardButton(button_text, callback_data=f"read_{msg_id}")])
            
            keyboard.append([InlineKeyboardButton("🔄 Обновить", callback_data="check_messages")])
            keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    elif query.data.startswith("read_"):
        message_id = int(query.data.split("_")[1])
        message = await read_message(user_id, message_id)
        
        if message:
            # Обработка разных форматов
            if 'createdAt' in message:
                # Mail.tm формат
                date_val = message.get('createdAt', '')
                if isinstance(date_val, dict):
                    timestamp = date_val.get('timestamp', 0)
                elif isinstance(date_val, str):
                    try:
                        dt = date_parser.parse(date_val)
                        timestamp = int(dt.timestamp())
                    except:
                        timestamp = 0
                else:
                    timestamp = int(date_val) if date_val else 0
                
                date_str = datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M:%S') if timestamp > 0 else 'Неизвестно'
                from_addr_obj = message.get('from', {})
                if isinstance(from_addr_obj, dict):
                    from_addr = from_addr_obj.get('address', 'Неизвестно')
                else:
                    from_addr = str(from_addr_obj)
                subject = message.get('subject', 'Без темы')
                text_body = message.get('text', message.get('textBody', 'Нет содержимого'))
            else:
                # 1secmail формат
                date_val = message.get('date', '0')
                date_str = datetime.fromtimestamp(int(date_val.split('.')[0])).strftime('%d.%m.%Y %H:%M:%S')
                from_addr = message.get('from', 'Неизвестно')
                subject = message.get('subject', 'Без темы')
                text_body = message.get('textBody', message.get('htmlBody', 'Нет содержимого'))
            
            text = (
                f"📧 <b>Письмо #{message_id}</b>\n\n"
                f"<b>От:</b> {from_addr}\n"
                f"<b>Тема:</b> {subject}\n"
                f"<b>Дата:</b> {date_str}\n\n"
                f"<b>Содержимое:</b>\n"
                f"<pre>{str(text_body)[:2000]}</pre>"
            )
        else:
            text = "❌ Ошибка при чтении письма."
        
        keyboard = [
            [InlineKeyboardButton("⬅️ Назад к письмам", callback_data="check_messages")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    elif query.data == "help":
        text = (
            "ℹ️ <b>Помощь</b>\n\n"
            "📧 <b>Как использовать:</b>\n"
            "1. Нажмите 'Создать новую почту'\n"
            "2. Скопируйте полученный email адрес\n"
            "3. Используйте его для регистраций\n"
            "4. Проверяйте входящие письма\n\n"
            "💡 <b>Особенности:</b>\n"
            "• Почты работают до 1 часа\n"
            "• Письма автоматически удаляются\n"
            "• Можно создать несколько почт\n\n"
            "🔒 <b>Безопасность:</b>\n"
            "• Не используйте для важных данных\n"
            "• Почты временные и публичные"
        )
        keyboard = [
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    elif query.data == "main_menu":
        user = query.from_user
        welcome_text = (
            f"👋 Главное меню\n\n"
            "📧 Выберите действие:"
        )
        keyboard = [
            [InlineKeyboardButton("📧 Создать новую почту", callback_data="create_email")],
            [InlineKeyboardButton("📬 Проверить письма", callback_data="check_messages")],
            [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(welcome_text, reply_markup=reply_markup)

def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем бота
    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
