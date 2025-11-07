#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XGPT - Telegram бот для программирования
AI-помощник с интеграцией Gemini AI для создания кода и приложений
Включает лимиты, профиль, реферальную систему, создание архивов с кодом
"""

import logging
import json
import os
import re
import zipfile
import tempfile
import time
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
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
DAILY_LIMIT = 50  # Лимит запросов в день
REFERRAL_BONUS = 10  # Бонус за приглашение
BOSS_USER_IDS = []  # ID пользователей с правами босса (можно добавить через переменную окружения)

# Настройка Gemini AI для кодинга
genai.configure(api_key=GEMINI_API_KEY)
# Используем экспериментальную модель для лучшего кодинга
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Системный промпт для XGPT
XGPT_SYSTEM_PROMPT = """Ты XGPT - крутой AI-ассистент для программирования и создания приложений! 

Твой стиль общения:
- Используй эмодзи для выразительности 🚀💻✨
- Будь дружелюбным, но профессиональным
- Всегда упоминай "XGPT" в начале или конце ответов
- Когда пишешь код, делай его чистым, комментированным и готовым к использованию
- Если пользователь просит создать приложение/код, структурируй ответ так, чтобы можно было легко создать файлы

Формат для кода:
- Используй markdown с блоками кода
- Указывай язык программирования
- Добавляй комментарии
- Предлагай структуру проекта если нужно

Помни: ты XGPT - лучший помощник для разработчиков! 🎯"""

# Файл для хранения данных
DATA_FILE = "users_data.json"


def load_data():
    """Загрузка данных пользователей из файла"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_data(data):
    """Сохранение данных пользователей в файл"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user_data(user_id):
    """Получение данных пользователя"""
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {
            "requests_today": 0,
            "last_reset_date": datetime.now().strftime("%Y-%m-%d"),
            "total_requests": 0,
            "referral_code": f"REF{user_id}",
            "referred_by": None,
            "referrals_count": 0,
            "bonus_requests": 0,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "history": []
        }
        save_data(data)
    return data[str(user_id)]


def update_user_data(user_id, updates):
    """Обновление данных пользователя"""
    data = load_data()
    if str(user_id) not in data:
        get_user_data(user_id)
        data = load_data()
    
    data[str(user_id)].update(updates)
    save_data(data)


def reset_daily_limits():
    """Сброс дневных лимитов для всех пользователей"""
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    
    for user_id, user_data in data.items():
        if user_data.get("last_reset_date") != today:
            user_data["requests_today"] = 0
            user_data["last_reset_date"] = today
            data[user_id] = user_data
    
    save_data(data)


def can_make_request(user_id):
    """Проверка возможности сделать запрос"""
    user_data = get_user_data(user_id)
    reset_daily_limits()
    
    # Обновляем данные после сброса
    user_data = get_user_data(user_id)
    
    available_requests = DAILY_LIMIT + user_data.get("bonus_requests", 0)
    return user_data["requests_today"] < available_requests


def get_available_requests(user_id):
    """Получение количества доступных запросов"""
    user_data = get_user_data(user_id)
    reset_daily_limits()
    user_data = get_user_data(user_id)
    
    available_requests = DAILY_LIMIT + user_data.get("bonus_requests", 0)
    return max(0, available_requests - user_data["requests_today"])


def use_request(user_id):
    """Использование запроса"""
    user_data = get_user_data(user_id)
    user_data["requests_today"] += 1
    user_data["total_requests"] += 1
    update_user_data(user_id, user_data)


def add_to_history(user_id, message, response):
    """Добавление запроса в историю"""
    user_data = get_user_data(user_id)
    history = user_data.get("history", [])
    
    # Ограничиваем историю последними 50 запросами
    if len(history) >= 50:
        history.pop(0)
    
    history.append({
        "message": message[:100],  # Ограничиваем длину
        "response": response[:200] if response else "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    user_data["history"] = history
    update_user_data(user_id, user_data)


def get_main_keyboard():
    """Главное меню с кнопками"""
    keyboard = [
        [InlineKeyboardButton("📊 Профиль", callback_data="profile"),
         InlineKeyboardButton("📈 Статистика", callback_data="stats")],
        [InlineKeyboardButton("🎁 Реферальная система", callback_data="referral"),
         InlineKeyboardButton("📜 История запросов", callback_data="history")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help"),
         InlineKeyboardButton("⚙️ Настройки", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    
    # Проверяем реферальный код
    if context.args:
        ref_code = context.args[0]
        if ref_code.startswith("REF"):
            referred_user_id = ref_code.replace("REF", "")
            user_data = get_user_data(user_id)
            
            # Если пользователь еще не был приглашен
            if not user_data.get("referred_by"):
                user_data["referred_by"] = referred_user_id
                update_user_data(user_id, user_data)
                
                # Начисляем бонус пригласившему
                referrer_data = get_user_data(int(referred_user_id))
                referrer_data["referrals_count"] += 1
                referrer_data["bonus_requests"] += REFERRAL_BONUS
                update_user_data(int(referred_user_id), referrer_data)
    
    user_data = get_user_data(user_id)
    reset_daily_limits()
    
    welcome_text = (
        f"🚀 Привет, {username}!\n\n"
        f"✨ Я XGPT - твой AI-помощник для программирования!\n"
        f"💻 Создаю код, приложения и помогаю с разработкой\n\n"
        f"📊 У тебя доступно запросов: {get_available_requests(user_id)}\n\n"
        f"💡 Просто опиши что нужно создать, и я помогу!\n"
        f"📦 Если нужен код - я создам архив с проектом!\n"
        f"📱 Используй кнопки ниже для управления."
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = (
        "📚 Помощь по использованию XGPT:\n\n"
        "✨ XGPT - твой AI-помощник для программирования!\n\n"
        "🔹 Просто опиши что нужно создать - приложение, скрипт, сайт\n"
        "🔹 Я создам код и отправлю архив с проектом\n"
        "🔹 У тебя есть лимит 50 запросов в день\n"
        "🔹 За каждого приглашенного друга получаешь +10 запросов\n"
        "🔹 Используй кнопки меню для навигации\n\n"
        "📊 Команды:\n"
        "/start - Главное меню\n"
        "/help - Эта справка\n"
        "/profile - Профиль пользователя\n"
        "/referral - Реферальная ссылка\n"
        "/stats - Статистика\n"
        "/history - История запросов\n"
        "/boss - Добавить запросы\n\n"
        "💡 Примеры запросов:\n"
        "• 'Создай калькулятор на Python'\n"
        "• 'Сделай веб-сайт с формой'\n"
        "• 'Напиши Telegram бота'\n\n"
        "🎯 XGPT всегда готов помочь!"
    )
    
    await update.message.reply_text(help_text, reply_markup=get_main_keyboard())


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда профиля"""
    await show_profile(update, context)


async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда реферальной системы"""
    await show_referral(update, context)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда статистики"""
    await show_stats(update, context)


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда истории"""
    await show_history(update, context)


async def boss_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Секретная команда /boss - добавляет запросы сколько указано"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "🔐 Секретная команда /boss\n\n"
            "Использование: /boss <количество>\n"
            "Пример: /boss 100\n\n"
            "Добавляет указанное количество запросов к вашему балансу.\n"
            "💡 Введи сколько запросов хочешь получить!"
        )
        return
    
    try:
        amount = int(context.args[0])
        if amount <= 0:
            await update.message.reply_text("❌ Количество должно быть положительным числом.")
            return
        
        if amount > 10000:
            await update.message.reply_text("❌ Максимальное количество за раз: 10000")
            return
        
        user_data = get_user_data(user_id)
        user_data["bonus_requests"] = user_data.get("bonus_requests", 0) + amount
        update_user_data(user_id, user_data)
        
        await update.message.reply_text(
            f"✅ Добавлено {amount} запросов!\n"
            f"📊 Теперь у тебя доступно: {get_available_requests(user_id)} запросов\n\n"
            f"🎉 Наслаждайся использованием XGPT!"
        )
    except ValueError:
        await update.message.reply_text("❌ Неверный формат. Используй: /boss <число>")


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ профиля пользователя"""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    reset_daily_limits()
    user_data = get_user_data(user_id)
    
    username = update.effective_user.username or update.effective_user.first_name
    available = get_available_requests(user_id)
    
    profile_text = (
        f"👤 Профиль пользователя: {username}\n\n"
        f"📊 Статистика:\n"
        f"• Запросов сегодня: {user_data['requests_today']}/{DAILY_LIMIT + user_data.get('bonus_requests', 0)}\n"
        f"• Доступно запросов: {available}\n"
        f"• Всего запросов: {user_data['total_requests']}\n"
        f"• Бонусных запросов: {user_data.get('bonus_requests', 0)}\n\n"
        f"🎁 Реферальная система:\n"
        f"• Приглашено друзей: {user_data['referrals_count']}\n"
        f"• Реферальный код: `{user_data['referral_code']}`\n"
        f"• Приглашен: {'Да' if user_data.get('referred_by') else 'Нет'}\n\n"
        f"📅 Дата регистрации: {user_data.get('created_at', 'Неизвестно')}"
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(profile_text, reply_markup=get_main_keyboard(), parse_mode='Markdown')
    else:
        await update.message.reply_text(profile_text, reply_markup=get_main_keyboard(), parse_mode='Markdown')


async def show_referral(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ реферальной системы"""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    bot_username = context.bot.username
    referral_link = f"https://t.me/{bot_username}?start={user_data['referral_code']}"
    
    referral_text = (
        f"🎁 Реферальная система\n\n"
        f"📊 Твоя статистика:\n"
        f"• Приглашено друзей: {user_data['referrals_count']}\n"
        f"• Получено бонусов: {user_data['referrals_count'] * REFERRAL_BONUS} запросов\n\n"
        f"🔗 Твоя реферальная ссылка:\n"
        f"`{referral_link}`\n\n"
        f"💡 За каждого приглашенного друга ты получаешь +{REFERRAL_BONUS} запросов!\n"
        f"📱 Поделись ссылкой с друзьями!"
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Копировать ссылку", url=referral_link)],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")]
    ]
    
    if update.callback_query:
        await update.callback_query.edit_message_text(referral_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.message.reply_text(referral_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')


async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ статистики"""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    reset_daily_limits()
    user_data = get_user_data(user_id)
    
    available = get_available_requests(user_id)
    used_today = user_data['requests_today']
    total = user_data['total_requests']
    
    stats_text = (
        f"📈 Статистика использования\n\n"
        f"📊 Сегодня:\n"
        f"• Использовано: {used_today}\n"
        f"• Доступно: {available}\n"
        f"• Лимит: {DAILY_LIMIT + user_data.get('bonus_requests', 0)}\n\n"
        f"📈 Всего:\n"
        f"• Всего запросов: {total}\n"
        f"• Бонусных запросов: {user_data.get('bonus_requests', 0)}\n\n"
        f"🎁 Рефералы:\n"
        f"• Приглашено: {user_data['referrals_count']}\n"
        f"• Заработано бонусов: {user_data['referrals_count'] * REFERRAL_BONUS}"
    )
    
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")]]
    
    if update.callback_query:
        await update.callback_query.edit_message_text(stats_text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(stats_text, reply_markup=InlineKeyboardMarkup(keyboard))


async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ истории запросов"""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    history = user_data.get("history", [])
    
    if not history:
        history_text = "📜 История запросов пуста.\n\nНачни общаться с ботом, и здесь появятся твои запросы!"
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")]]
    else:
        history_text = f"📜 Последние запросы (всего: {len(history)}):\n\n"
        for i, item in enumerate(history[-10:], 1):  # Показываем последние 10
            history_text += f"{i}. {item['message']}\n"
            history_text += f"   ⏰ {item['timestamp']}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🗑️ Очистить историю", callback_data="clear_history")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")]
        ]
    
    if update.callback_query:
        await update.callback_query.edit_message_text(history_text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(history_text, reply_markup=InlineKeyboardMarkup(keyboard))


async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ настроек"""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    settings_text = (
        "⚙️ Настройки\n\n"
        "📊 Параметры системы:\n"
        f"🔹 Лимит запросов в день: {DAILY_LIMIT}\n"
        f"🔹 Бонус за приглашение: +{REFERRAL_BONUS} запросов\n"
        f"🔹 История запросов: последние 50\n"
        f"🔹 Твои бонусные запросы: {user_data.get('bonus_requests', 0)}\n\n"
        "💡 Используй реферальную систему для получения дополнительных запросов!\n"
        "🔐 Используй команду /boss для добавления запросов!\n\n"
        "✨ XGPT - твой лучший помощник!"
    )
    
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")]]
    
    if update.callback_query:
        await update.callback_query.edit_message_text(settings_text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(settings_text, reply_markup=InlineKeyboardMarkup(keyboard))


async def clear_history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Очистка истории запросов"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    user_data = get_user_data(user_id)
    user_data["history"] = []
    update_user_data(user_id, user_data)
    
    await query.answer("✅ История очищена!")
    await show_history(update, context)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "profile":
        await show_profile(update, context)
    elif query.data == "referral":
        await show_referral(update, context)
    elif query.data == "stats":
        await show_stats(update, context)
    elif query.data == "history":
        await show_history(update, context)
    elif query.data == "help":
        await help_command(update, context)
    elif query.data == "settings":
        await show_settings(update, context)
    elif query.data == "clear_history":
        await clear_history_callback(update, context)
    elif query.data == "back_to_menu":
        user_id = update.effective_user.id
        user_data = get_user_data(user_id)
        reset_daily_limits()
        available = get_available_requests(user_id)
        
        menu_text = (
            f"📱 Главное меню XGPT\n\n"
            f"📊 Доступно запросов: {available}\n\n"
            f"✨ Выбери действие:"
        )
        await query.edit_message_text(menu_text, reply_markup=get_main_keyboard())


def extract_code_blocks(text):
    """Извлечение блоков кода из текста"""
    code_blocks = []
    # Ищем блоки кода в markdown формате (с поддержкой разных вариантов)
    patterns = [
        r'```(\w+)?\n(.*?)```',  # Стандартный формат
        r'```(\w+)\s*\n(.*?)```',  # С пробелами
        r'```\s*(\w+)?\s*\n(.*?)```',  # С пробелами вокруг языка
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            if len(match) == 2:
                lang, code = match
            else:
                lang = match[0] if match else None
                code = match[1] if len(match) > 1 else match[0]
            
            code = code.strip() if isinstance(code, str) else str(code).strip()
            if code and len(code) > 10:  # Минимальная длина кода
                code_blocks.append({
                    'language': (lang or 'txt').strip(),
                    'code': code
                })
    
    # Удаляем дубликаты
    seen = set()
    unique_blocks = []
    for block in code_blocks:
        code_hash = hash(block['code'])
        if code_hash not in seen:
            seen.add(code_hash)
            unique_blocks.append(block)
    
    return unique_blocks


def create_project_archive(code_blocks, project_name="project"):
    """Создание ZIP архива с проектом"""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"{project_name}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, block in enumerate(code_blocks):
            lang = block['language']
            code = block['code']
            
            # Определяем расширение файла
            extensions = {
                'python': '.py',
                'py': '.py',
                'javascript': '.js',
                'js': '.js',
                'typescript': '.ts',
                'ts': '.ts',
                'html': '.html',
                'css': '.css',
                'java': '.java',
                'cpp': '.cpp',
                'c': '.c',
                'go': '.go',
                'rust': '.rs',
                'php': '.php',
                'ruby': '.rb',
                'swift': '.swift',
                'kotlin': '.kt',
                'sql': '.sql',
                'json': '.json',
                'xml': '.xml',
                'yaml': '.yml',
                'yml': '.yml',
                'sh': '.sh',
                'bash': '.sh',
                'txt': '.txt'
            }
            
            ext = extensions.get(lang.lower(), '.txt')
            filename = f"file_{i+1}{ext}" if len(code_blocks) > 1 else f"main{ext}"
            
            # Добавляем README если несколько файлов
            if len(code_blocks) > 1 and i == 0:
                readme = f"# {project_name}\n\nПроект создан с помощью XGPT\n\n"
                zipf.writestr("README.md", readme)
            
            zipf.writestr(filename, code)
    
    return zip_path


async def generate_with_retry(prompt, max_retries=3):
    """Генерация ответа с повторными попытками при ошибках"""
    for attempt in range(max_retries):
        try:
            # Небольшая задержка перед запросом для снижения нагрузки
            if attempt > 0:
                await asyncio.sleep(1)
            
            response = model.generate_content(prompt)
            return response
        except Exception as e:
            error_str = str(e).lower()
            
            # Ошибка 429 - слишком много запросов
            if "429" in error_str or "resource exhausted" in error_str or "quota" in error_str:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3  # Увеличиваем задержку: 3, 6, 9 секунд
                    logger.warning(f"Rate limit hit (429), waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise Exception("Превышен лимит запросов к API. Пожалуйста, подожди немного и попробуй снова через 1-2 минуты.")
            
            # Другие ошибки - пробуем еще раз с задержкой
            elif attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                logger.warning(f"Error occurred, retrying in {wait_time} seconds: {e}")
                await asyncio.sleep(wait_time)
                continue
            else:
                raise
    
    raise Exception("Не удалось получить ответ после нескольких попыток")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Проверяем лимит
    if not can_make_request(user_id):
        available = get_available_requests(user_id)
        await update.message.reply_text(
            f"❌ Достигнут дневной лимит запросов!\n\n"
            f"📊 Доступно запросов: {available}\n"
            f"💡 Пригласи друзей, чтобы получить дополнительные запросы!\n"
            f"📱 Используй /referral для получения реферальной ссылки.\n\n"
            f"✨ XGPT всегда готов помочь!",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Отправляем сообщение о том, что бот думает
    thinking_message = await update.message.reply_text("🚀 XGPT думает...")
    
    request_used = False
    try:
        # Формируем промпт с системным контекстом
        full_prompt = f"{XGPT_SYSTEM_PROMPT}\n\nЗапрос пользователя: {user_message}\n\nОтветь в стиле XGPT:"
        
        # Получаем ответ от Gemini AI с повторными попытками
        response = await generate_with_retry(full_prompt)
        
        # Получаем текст ответа
        response_text = response.text if hasattr(response, 'text') else str(response)
        
        # Добавляем подпись XGPT если её нет
        if "XGPT" not in response_text:
            response_text = f"✨ {response_text}\n\n— XGPT"
        
        # Используем запрос только если успешно получили ответ
        use_request(user_id)
        request_used = True
        
        # Добавляем в историю
        add_to_history(user_id, user_message, response_text)
        
        # Проверяем, есть ли код в ответе
        code_blocks = extract_code_blocks(response_text)
        
        # Отправляем текстовый ответ
        if len(response_text) > 4096:
            chunks = [response_text[i:i+4096] for i in range(0, len(response_text), 4096)]
            await thinking_message.edit_text(chunks[0], parse_mode='Markdown')
            for chunk in chunks[1:]:
                await update.message.reply_text(chunk, parse_mode='Markdown')
        else:
            await thinking_message.edit_text(response_text, parse_mode='Markdown')
        
        # Если есть код, создаем архив
        if code_blocks:
            try:
                # Определяем название проекта из запроса
                project_name = "xgpt_project"
                if any(word in user_message.lower() for word in ['приложение', 'app', 'application']):
                    project_name = "app"
                elif any(word in user_message.lower() for word in ['сайт', 'site', 'website', 'web']):
                    project_name = "website"
                elif any(word in user_message.lower() for word in ['бот', 'bot']):
                    project_name = "bot"
                
                zip_path = create_project_archive(code_blocks, project_name)
                
                # Отправляем архив
                with open(zip_path, 'rb') as zip_file:
                    await update.message.reply_document(
                        document=zip_file,
                        filename=f"{project_name}.zip",
                        caption="📦 Архив с проектом от XGPT! Распакуй и используй 🚀"
                    )
                
                # Удаляем временный файл
                os.remove(zip_path)
                os.rmdir(os.path.dirname(zip_path))
                
            except Exception as e:
                logger.error(f"Ошибка при создании архива: {e}")
                await update.message.reply_text(
                    "⚠️ Код создан, но не удалось создать архив. "
                    "Скопируй код из сообщения выше.\n\n✨ XGPT"
                )
        
        # Показываем оставшиеся запросы
        available = get_available_requests(user_id)
        if available <= 5:
            await update.message.reply_text(
                f"⚠️ Осталось запросов: {available}\n"
                f"💡 Пригласи друзей для получения дополнительных запросов!\n\n"
                f"✨ XGPT",
                reply_markup=get_main_keyboard()
            )
        
    except Exception as e:
        logger.error(f"Ошибка при обращении к Gemini AI: {e}")
        error_message = str(e)
        
        # Специальная обработка ошибки 429
        if "429" in error_message or "resource exhausted" in error_message.lower() or "quota" in error_message.lower() or "лимит" in error_message.lower():
            # При ошибке 429 не списываем запрос
            if not request_used:
                error_text = (
                    f"⏳ Упс! Превышен лимит запросов к API.\n\n"
                    f"💡 XGPT обрабатывает много запросов прямо сейчас.\n"
                    f"⏰ Подожди 1-2 минуты и попробуй снова.\n\n"
                    f"✅ Твой запрос не был использован - можешь попробовать еще раз!\n\n"
                    f"✨ XGPT всегда готов помочь, просто нужно немного подождать!"
                )
            else:
                error_text = (
                    f"⏳ Упс! Превышен лимит запросов к API.\n\n"
                    f"💡 XGPT обрабатывает много запросов прямо сейчас.\n"
                    f"⏰ Подожди 1-2 минуты и попробуй снова.\n\n"
                    f"✨ XGPT всегда готов помочь, просто нужно немного подождать!"
                )
        else:
            # При других ошибках также не списываем запрос, если он не был использован
            if not request_used:
                error_text = (
                    f"❌ Упс! Произошла ошибка, но XGPT не сдается!\n\n"
                    f"Ошибка: {error_message[:200]}\n\n"
                    f"💡 Попробуй:\n"
                    f"• Переформулировать запрос\n"
                    f"• Подождать немного и попробовать снова\n"
                    f"• Использовать команду /help\n\n"
                    f"✅ Твой запрос не был использован - можешь попробовать еще раз!\n\n"
                    f"✨ XGPT всегда готов помочь!"
                )
            else:
                error_text = (
                    f"❌ Упс! Произошла ошибка, но XGPT не сдается!\n\n"
                    f"Ошибка: {error_message[:200]}\n\n"
                    f"💡 Попробуй:\n"
                    f"• Переформулировать запрос\n"
                    f"• Подождать немного и попробовать снова\n"
                    f"• Использовать команду /help\n\n"
                    f"✨ XGPT всегда готов помочь!"
                )
        
        await thinking_message.edit_text(error_text)


def main() -> None:
    """Основная функция запуска бота"""
    # Инициализируем данные
    reset_daily_limits()
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("referral", referral_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("boss", boss_command))
    
    # Регистрируем обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Регистрируем обработчик текстовых сообщений (должен быть последним)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logger.info("🚀 Запуск XGPT - AI-помощник для программирования...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
