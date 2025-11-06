import asyncio
import logging
import aiohttp
from datetime import datetime
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

# API для временных почт (1secmail.com)
API_BASE_URL = "https://www.1secmail.com/api/v1/"

# Хранилище почт пользователей {user_id: {email: str, login: str, domain: str}}
user_emails = {}

async def generate_email(user_id: int) -> dict:
    """Генерирует новую временную почту"""
    async with aiohttp.ClientSession() as session:
        try:
            # Получаем случайный домен
            async with session.get(f"{API_BASE_URL}?action=genRandomMailbox&count=1") as resp:
                domains = await resp.json()
                if domains and len(domains) > 0:
                    email = domains[0]
                    login, domain = email.split('@')
                    
                    user_emails[user_id] = {
                        'email': email,
                        'login': login,
                        'domain': domain
                    }
                    return user_emails[user_id]
        except Exception as e:
            logger.error(f"Ошибка генерации почты: {e}")
            return None

async def get_messages(user_id: int) -> list:
    """Получает письма для почты пользователя"""
    if user_id not in user_emails:
        return []
    
    email_data = user_emails[user_id]
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{API_BASE_URL}?action=getMessages&login={email_data['login']}&domain={email_data['domain']}"
            async with session.get(url) as resp:
                messages = await resp.json()
                return messages if messages else []
        except Exception as e:
            logger.error(f"Ошибка получения писем: {e}")
            return []

async def read_message(user_id: int, message_id: int) -> dict:
    """Читает конкретное письмо"""
    if user_id not in user_emails:
        return None
    
    email_data = user_emails[user_id]
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{API_BASE_URL}?action=readMessage&login={email_data['login']}&domain={email_data['domain']}&id={message_id}"
            async with session.get(url) as resp:
                message = await resp.json()
                return message
        except Exception as e:
            logger.error(f"Ошибка чтения письма: {e}")
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
                date_str = datetime.fromtimestamp(int(msg['date'].split('.')[0])).strftime('%d.%m.%Y %H:%M')
                button_text = f"📧 {msg['from']} - {date_str}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"read_{msg['id']}")])
            
            keyboard.append([InlineKeyboardButton("🔄 Обновить", callback_data="check_messages")])
            keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    elif query.data.startswith("read_"):
        message_id = int(query.data.split("_")[1])
        message = await read_message(user_id, message_id)
        
        if message:
            date_str = datetime.fromtimestamp(int(message['date'].split('.')[0])).strftime('%d.%m.%Y %H:%M:%S')
            text = (
                f"📧 <b>Письмо #{message_id}</b>\n\n"
                f"<b>От:</b> {message['from']}\n"
                f"<b>Тема:</b> {message['subject']}\n"
                f"<b>Дата:</b> {date_str}\n\n"
                f"<b>Содержимое:</b>\n"
                f"<pre>{message.get('textBody', message.get('htmlBody', 'Нет содержимого'))[:2000]}</pre>"
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
