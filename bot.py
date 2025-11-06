# -*- coding: utf-8 -*-
import logging
import json
import os
import hashlib
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode

# Настройки
BOT_TOKEN = "8588890122:AAF870IhnaQRmo_pn8OIVj_xH6skyNwVZy0"
ADMIN_ID = 7694543415

# Файлы для хранения данных
CODES_FILE = "shared_codes.json"
BLOCKED_USERS_FILE = "blocked_users.json"
BOT_STATUS_FILE = "bot_status.json"
LANGUAGES_FILE = "user_languages.json"
BOT_COPIES_FILE = "bot_copies.json"
ORIGINAL_BOT_INFO_FILE = "original_bot_info.json"
ISSUED_CODES_FILE = "issued_codes.json"

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Локализация
TEXTS = {
    'ru': {
        'welcome': '👋 Добро пожаловать!\n\nВыберите действие:',
        'admin_panel_available': '\n\n🔐 Доступна админ панель: /admin',
        'get_code': '🔑 Получить код',
        'share_code': '📤 Поделиться кодом',
        'blocked': '❌ Вы заблокированы и не можете использовать бота.',
        'bot_disabled': '⏸ Бот временно выключен.',
        'maintenance': '🔧 Бот находится на техническом обслуживании. Пожалуйста, попробуйте позже.',
        'code_message': 'Уважаемый @{username} ({first_name}), хотим сообщить вам, что если вдруг вы получите код, вы должны выслать в ответ.',
        'yes': '✅ Да',
        'no': '❌ Нет',
        'code_issued': '✅ Код успешно выдан!\n\n🔑 Ваш код: <code>{code}</code>\n\nИспользуйте его на сайте cto.new',
        'code_refused': '❌ Вы отказались от получения кода.',
        'share_code_prompt': '📤 Поделитесь кодом:\n\nОтправьте код, которым хотите поделиться с другими пользователями.',
        'code_added': '✅ Код успешно добавлен! Другие пользователи смогут его использовать.',
        'use_buttons': 'Используйте кнопки для навигации.',
        'admin_panel': '🔐 Админ панель',
        'no_admin_access': '❌ У вас нет доступа к админ панели.',
        'codes_empty': '📋 Список кодов пуст.',
        'shared_codes': '📋 Поделенные коды:\n\n',
        'code_item': '{idx}. Код: <code>{code}</code>\n   Пользователь: @{username} ({first_name})\n   ID: {user_id}\n   Время: {timestamp}\n\n',
        'block_user_prompt': '🚫 Отправьте ID пользователя для блокировки:\n\nИспользуйте /cancel для отмены.',
        'no_blocked_users': '✅ Заблокированных пользователей нет.',
        'blocked_users_list': '🚫 Заблокированные пользователи:\n\n',
        'unblock_user_prompt': '\nОтправьте ID пользователя для разблокировки:\n\nИспользуйте /cancel для отмены.',
        'maintenance_enabled': '🔧 Режим технического обслуживания включен.',
        'maintenance_disabled': '🔧 Режим технического обслуживания выключен.',
        'bot_disabled_msg': '⏸ Бот выключен.',
        'bot_enabled_msg': '▶️ Бот включен.',
        'user_blocked': '✅ Пользователь {id} заблокирован.',
        'user_already_blocked': '⚠️ Пользователь {id} уже заблокирован.',
        'user_unblocked': '✅ Пользователь {id} разблокирован.',
        'user_not_blocked': '⚠️ Пользователь {id} не был заблокирован.',
        'invalid_id': '❌ Неверный формат ID. Отправьте числовой ID.',
        'unblock_error': '❌ Ошибка при разблокировке.',
        'action_cancelled': '❌ Действие отменено.',
        'cancelled': '❌ Отменено.',
        'language_changed': '🌐 Язык изменен на русский.',
        'select_language': '🌐 Выберите язык / Select language:',
        'current_language': 'Текущий язык: Русский',
        'no_codes_available': '❌ К сожалению, сейчас нет доступных кодов. Поделитесь кодом, чтобы другие пользователи могли его получить!',
        'create_bot_copy': '🤖 Создать копию бота',
        'create_bot_copy_prompt': '🤖 Отправьте токен нового бота от BotFather:\n\nИспользуйте /cancel для отмены.',
        'bot_copy_created': '✅ Копия бота успешно создана!\n\nТокен: <code>{token}</code>\n\nТеперь запустите этот бот с этим токеном.',
        'invalid_token': '❌ Неверный формат токена. Токен должен быть в формате: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz',
        'copy_bot_info': '📋 Это копия бота\n\nОригинальный бот: @{original_username}\nСоздатель: @{creator_username}',
        'code_valid': '✅ Код действителен',
        'code_invalid': '❌ Код не действителен',
        'code_validated': '✅ Спасибо! Код останется в базе данных.',
        'code_removed': '✅ Код удален из базы данных.'
    },
    'en': {
        'welcome': '👋 Welcome!\n\nChoose an action:',
        'admin_panel_available': '\n\n🔐 Admin panel available: /admin',
        'get_code': '🔑 Get code',
        'share_code': '📤 Share code',
        'blocked': '❌ You are blocked and cannot use the bot.',
        'bot_disabled': '⏸ Bot is temporarily disabled.',
        'maintenance': '🔧 Bot is under maintenance. Please try again later.',
        'code_message': 'Dear @{username} ({first_name}), we want to inform you that if you receive a code, you must send a reply.',
        'yes': '✅ Yes',
        'no': '❌ No',
        'code_issued': '✅ Code successfully issued!\n\n🔑 Your code: <code>{code}</code>\n\nUse it on cto.new website',
        'code_refused': '❌ You refused to receive the code.',
        'share_code_prompt': '📤 Share code:\n\nSend the code you want to share with other users.',
        'code_added': '✅ Code successfully added! Other users will be able to use it.',
        'use_buttons': 'Use buttons for navigation.',
        'admin_panel': '🔐 Admin panel',
        'no_admin_access': '❌ You do not have access to the admin panel.',
        'codes_empty': '📋 Code list is empty.',
        'shared_codes': '📋 Shared codes:\n\n',
        'code_item': '{idx}. Code: <code>{code}</code>\n   User: @{username} ({first_name})\n   ID: {user_id}\n   Time: {timestamp}\n\n',
        'block_user_prompt': '🚫 Send user ID to block:\n\nUse /cancel to cancel.',
        'no_blocked_users': '✅ No blocked users.',
        'blocked_users_list': '🚫 Blocked users:\n\n',
        'unblock_user_prompt': '\nSend user ID to unblock:\n\nUse /cancel to cancel.',
        'maintenance_enabled': '🔧 Maintenance mode enabled.',
        'maintenance_disabled': '🔧 Maintenance mode disabled.',
        'bot_disabled_msg': '⏸ Bot disabled.',
        'bot_enabled_msg': '▶️ Bot enabled.',
        'user_blocked': '✅ User {id} blocked.',
        'user_already_blocked': '⚠️ User {id} is already blocked.',
        'user_unblocked': '✅ User {id} unblocked.',
        'user_not_blocked': '⚠️ User {id} was not blocked.',
        'invalid_id': '❌ Invalid ID format. Send a numeric ID.',
        'unblock_error': '❌ Error unblocking.',
        'action_cancelled': '❌ Action cancelled.',
        'cancelled': '❌ Cancelled.',
        'language_changed': '🌐 Language changed to English.',
        'select_language': '🌐 Выберите язык / Select language:',
        'current_language': 'Current language: English',
        'no_codes_available': '❌ Unfortunately, there are no codes available right now. Share a code so other users can get it!',
        'create_bot_copy': '🤖 Create bot copy',
        'create_bot_copy_prompt': '🤖 Send the new bot token from BotFather:\n\nUse /cancel to cancel.',
        'bot_copy_created': '✅ Bot copy successfully created!\n\nToken: <code>{token}</code>\n\nNow run this bot with this token.',
        'invalid_token': '❌ Invalid token format. Token should be in format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz',
        'copy_bot_info': '📋 This is a bot copy\n\nOriginal bot: @{original_username}\nCreator: @{creator_username}',
        'code_valid': '✅ Code valid',
        'code_invalid': '❌ Code invalid',
        'code_validated': '✅ Thank you! Code will remain in database.',
        'code_removed': '✅ Code removed from database.'
    }
}

# Загрузка данных
def load_json(file_path, default={}):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Получение языка пользователя
def get_user_language(user_id):
    languages = load_json(LANGUAGES_FILE, {})
    return languages.get(str(user_id), 'ru')

# Сохранение языка пользователя
def set_user_language(user_id, lang):
    languages = load_json(LANGUAGES_FILE, {})
    languages[str(user_id)] = lang
    save_json(LANGUAGES_FILE, languages)

# Получение текста по ключу
def t(user_id, key, **kwargs):
    lang = get_user_language(user_id)
    text = TEXTS[lang].get(key, TEXTS['ru'].get(key, key))
    return text.format(**kwargs) if kwargs else text

def is_blocked(user_id):
    blocked_users_list = load_json(BLOCKED_USERS_FILE, [])
    return str(user_id) in blocked_users_list

def is_admin(user_id):
    return user_id == ADMIN_ID

def is_bot_enabled():
    bot_status_data = load_json(BOT_STATUS_FILE, {"maintenance": False, "enabled": True})
    return bot_status_data.get("enabled", True)

def is_maintenance_mode():
    bot_status_data = load_json(BOT_STATUS_FILE, {"maintenance": False, "enabled": True})
    return bot_status_data.get("maintenance", False)

# Главное меню
def get_main_keyboard(user_id):
    lang = get_user_language(user_id)
    keyboard = [
        [KeyboardButton(t(user_id, 'get_code'))],
        [KeyboardButton(t(user_id, 'share_code'))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Админ панель
def get_admin_keyboard(user_id):
    keyboard = [
        [InlineKeyboardButton("📋 Посмотреть коды" if get_user_language(user_id) == 'ru' else "📋 View codes", callback_data="admin_view_codes")],
        [InlineKeyboardButton("🚫 Заблокировать пользователя" if get_user_language(user_id) == 'ru' else "🚫 Block user", callback_data="admin_block_user")],
        [InlineKeyboardButton("✅ Разблокировать пользователя" if get_user_language(user_id) == 'ru' else "✅ Unblock user", callback_data="admin_unblock_user")],
        [InlineKeyboardButton("🔧 Техническое обслуживание" if get_user_language(user_id) == 'ru' else "🔧 Maintenance", callback_data="admin_maintenance")],
        [InlineKeyboardButton("⏸ Выключить бота" if get_user_language(user_id) == 'ru' else "⏸ Disable bot", callback_data="admin_disable_bot")],
        [InlineKeyboardButton("▶️ Включить бота" if get_user_language(user_id) == 'ru' else "▶️ Enable bot", callback_data="admin_enable_bot")],
        [InlineKeyboardButton("🤖 Создать копию бота" if get_user_language(user_id) == 'ru' else "🤖 Create bot copy", callback_data="admin_create_copy")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура выбора языка
def get_language_keyboard():
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Проверка, является ли бот копией
def is_bot_copy():
    original_info = load_json(ORIGINAL_BOT_INFO_FILE, {})
    return bool(original_info.get('original_username'))

# Получение информации об оригинальном боте
def get_original_bot_info():
    return load_json(ORIGINAL_BOT_INFO_FILE, {})

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_blocked(user_id):
        await update.message.reply_text(t(user_id, 'blocked'))
        return
    
    if not is_bot_enabled():
        await update.message.reply_text(t(user_id, 'bot_disabled'))
        return
    
    if is_maintenance_mode():
        await update.message.reply_text(t(user_id, 'maintenance'))
        return
    
    welcome_text = t(user_id, 'welcome')
    
    # Если это копия бота, показываем информацию об оригинале
    if is_bot_copy():
        original_info = get_original_bot_info()
        copy_info = t(user_id, 'copy_bot_info',
            original_username=original_info.get('original_username', 'N/A'),
            creator_username=original_info.get('creator_username', 'N/A')
        )
        welcome_text = copy_info + "\n\n" + welcome_text
    
    if is_admin(user_id):
        welcome_text += t(user_id, 'admin_panel_available')
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard(user_id)
    )

# Обработчик команды /language или /lang
async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    await update.message.reply_text(
        t(user_id, 'select_language'),
        reply_markup=get_language_keyboard()
    )

# Обработчик команды /admin
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(t(user_id, 'no_admin_access'))
        return
    
    await update.message.reply_text(
        t(user_id, 'admin_panel'),
        reply_markup=get_admin_keyboard(user_id)
    )

# Обработчик кнопки "Получить код"
async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    first_name = update.effective_user.first_name or ("Пользователь" if get_user_language(user_id) == 'ru' else "User")
    
    if is_blocked(user_id):
        await update.message.reply_text(t(user_id, 'blocked'))
        return
    
    if not is_bot_enabled():
        await update.message.reply_text(t(user_id, 'bot_disabled'))
        return
    
    if is_maintenance_mode():
        await update.message.reply_text(t(user_id, 'maintenance'))
        return
    
    message_text = t(user_id, 'code_message', username=username, first_name=first_name)
    
    keyboard = [
        [InlineKeyboardButton(t(user_id, 'yes'), callback_data=f"code_confirm_yes_{user_id}")],
        [InlineKeyboardButton(t(user_id, 'no'), callback_data=f"code_confirm_no_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

# Обработчик подтверждения получения кода
async def code_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data.split("_")
    action = data[2]  # yes или no
    
    if action == "yes":
        # Берем код из списка поделенных кодов
        codes_list = load_json(CODES_FILE, [])
        
        if not codes_list:
            await query.edit_message_text(t(user_id, 'no_codes_available'))
            return
        
        # Берем первый доступный код
        code_data = codes_list[0]
        code = code_data['code']
        
        # Создаем хеш кода для идентификации
        code_hash = hashlib.md5(f"{code}_{user_id}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        # Временно удаляем код из списка (вернем обратно если действителен)
        codes_list.pop(0)
        save_json(CODES_FILE, codes_list)
        
        # Сохраняем информацию о выданном коде для проверки валидности
        issued_codes = load_json(ISSUED_CODES_FILE, {})
        issued_codes[code_hash] = code_data
        save_json(ISSUED_CODES_FILE, issued_codes)
        
        # Показываем код с кнопками валидности
        keyboard = [
            [InlineKeyboardButton(t(user_id, 'code_valid'), callback_data=f"code_valid_{code_hash}")],
            [InlineKeyboardButton(t(user_id, 'code_invalid'), callback_data=f"code_invalid_{code_hash}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            t(user_id, 'code_issued', code=code) + "\n\n" + t(user_id, 'code_valid') + " / " + t(user_id, 'code_invalid') + "?",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text(t(user_id, 'code_refused'))

# Обработчик кнопки "Поделиться кодом"
async def share_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_blocked(user_id):
        await update.message.reply_text(t(user_id, 'blocked'))
        return
    
    if not is_bot_enabled():
        await update.message.reply_text(t(user_id, 'bot_disabled'))
        return
    
    if is_maintenance_mode():
        await update.message.reply_text(t(user_id, 'maintenance'))
        return
    
    await update.message.reply_text(t(user_id, 'share_code_prompt'))
    context.user_data['waiting_for_code'] = True

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # Проверка админских действий (приоритет)
    if is_admin(user_id):
        admin_action = context.user_data.get('admin_action')
        if admin_action == 'create_copy':
            # Проверка формата токена (должен быть в формате 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)
            if ':' in text and len(text.split(':')) == 2:
                token_parts = text.split(':')
                if token_parts[0].isdigit() and len(token_parts[1]) > 10:
                    # Получаем информацию о текущем боте через application
                    try:
                        application = context.application
                        bot_info = await application.bot.get_me()
                        original_username = bot_info.username
                    except Exception as e:
                        logger.error(f"Ошибка получения информации о боте: {e}")
                        original_username = "N/A"
                    
                    # Сохраняем информацию о копии
                    copies = load_json(BOT_COPIES_FILE, [])
                    copy_info = {
                        'token': text,
                        'creator_id': user_id,
                        'creator_username': update.effective_user.username or update.effective_user.first_name,
                        'original_username': original_username,
                        'created_at': datetime.now().isoformat()
                    }
                    copies.append(copy_info)
                    save_json(BOT_COPIES_FILE, copies)
                    
                    # Создаем файл с информацией для копии бота
                    original_bot_info = {
                        'original_username': original_username,
                        'creator_username': copy_info['creator_username'],
                        'created_at': copy_info['created_at']
                    }
                    # Сохраняем в файл для копии (будет использоваться при запуске копии)
                    copy_info_file = f"copy_info_{text.replace(':', '_')}.json"
                    save_json(copy_info_file, original_bot_info)
                    
                    await update.message.reply_text(
                        t(user_id, 'bot_copy_created', token=text) + f"\n\n📝 Для запуска копии используйте:\npython3 create_copy.py {text}",
                        parse_mode=ParseMode.HTML,
                        reply_markup=get_admin_keyboard(user_id)
                    )
                else:
                    await update.message.reply_text(
                        t(user_id, 'invalid_token'),
                        reply_markup=get_admin_keyboard(user_id)
                    )
            else:
                await update.message.reply_text(
                    t(user_id, 'invalid_token'),
                    reply_markup=get_admin_keyboard(user_id)
                )
            context.user_data['admin_action'] = None
            return
        elif admin_action == 'block':
            try:
                target_id = int(text)
                blocked_users_list = load_json(BLOCKED_USERS_FILE, [])
                if str(target_id) not in blocked_users_list:
                    blocked_users_list.append(str(target_id))
                    save_json(BLOCKED_USERS_FILE, blocked_users_list)
                    await update.message.reply_text(
                        t(user_id, 'user_blocked', id=target_id),
                        reply_markup=get_admin_keyboard(user_id)
                    )
                else:
                    await update.message.reply_text(
                        t(user_id, 'user_already_blocked', id=target_id),
                        reply_markup=get_admin_keyboard(user_id)
                    )
            except ValueError:
                await update.message.reply_text(
                    t(user_id, 'invalid_id'),
                    reply_markup=get_admin_keyboard(user_id)
                )
            context.user_data['admin_action'] = None
            return
        elif admin_action == 'unblock':
            try:
                target_id = str(text)
                blocked_users_list = load_json(BLOCKED_USERS_FILE, [])
                if target_id in blocked_users_list:
                    blocked_users_list.remove(target_id)
                    save_json(BLOCKED_USERS_FILE, blocked_users_list)
                    await update.message.reply_text(
                        t(user_id, 'user_unblocked', id=target_id),
                        reply_markup=get_admin_keyboard(user_id)
                    )
                else:
                    await update.message.reply_text(
                        t(user_id, 'user_not_blocked', id=target_id),
                        reply_markup=get_admin_keyboard(user_id)
                    )
            except:
                await update.message.reply_text(
                    t(user_id, 'unblock_error'),
                    reply_markup=get_admin_keyboard(user_id)
                )
            context.user_data['admin_action'] = None
            return
    
    if is_blocked(user_id):
        return
    
    if not is_bot_enabled() or is_maintenance_mode():
        return
    
    # Если пользователь делится кодом
    if context.user_data.get('waiting_for_code'):
        username = update.effective_user.username or update.effective_user.first_name
        first_name = update.effective_user.first_name or ("Пользователь" if get_user_language(user_id) == 'ru' else "User")
        
        code_data = {
            "code": text,
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "timestamp": datetime.now().isoformat()
        }
        
        codes_list = load_json(CODES_FILE, [])
        codes_list.append(code_data)
        save_json(CODES_FILE, codes_list)
        
        context.user_data['waiting_for_code'] = False
        
        await update.message.reply_text(
            t(user_id, 'code_added'),
            reply_markup=get_main_keyboard(user_id)
        )
        return
    
    # Обработка обычных сообщений
    if text == t(user_id, 'get_code') or text == "🔑 Получить код" or text == "🔑 Get code":
        await get_code(update, context)
    elif text == t(user_id, 'share_code') or text == "📤 Поделиться кодом" or text == "📤 Share code":
        await share_code(update, context)
    else:
        await update.message.reply_text(
            t(user_id, 'use_buttons'),
            reply_markup=get_main_keyboard(user_id)
        )

# Обработчики админ панели
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.edit_message_text(t(user_id, 'no_admin_access'))
        return
    
    data = query.data
    
    if data == "admin_view_codes":
        codes_list = load_json(CODES_FILE, [])
        if not codes_list:
            await query.edit_message_text(
                t(user_id, 'codes_empty'),
                reply_markup=get_admin_keyboard(user_id)
            )
        else:
            codes_text = t(user_id, 'shared_codes')
            for idx, code_data in enumerate(codes_list[-20:], 1):
                codes_text += t(user_id, 'code_item',
                    idx=idx,
                    code=code_data['code'],
                    username=code_data.get('username', 'N/A'),
                    first_name=code_data.get('first_name', 'N/A'),
                    user_id=code_data['user_id'],
                    timestamp=code_data.get('timestamp', 'N/A')
                )
            
            await query.edit_message_text(
                codes_text,
                parse_mode=ParseMode.HTML,
                reply_markup=get_admin_keyboard(user_id)
            )
    
    elif data == "admin_block_user":
        await query.edit_message_text(
            t(user_id, 'block_user_prompt'),
            reply_markup=None
        )
        context.user_data['admin_action'] = 'block'
    
    elif data == "admin_unblock_user":
        blocked_users_list = load_json(BLOCKED_USERS_FILE, [])
        if not blocked_users_list:
            await query.edit_message_text(
                t(user_id, 'no_blocked_users'),
                reply_markup=get_admin_keyboard(user_id)
            )
        else:
            blocked_text = t(user_id, 'blocked_users_list')
            for uid in blocked_users_list:
                blocked_text += f"ID: {uid}\n"
            
            await query.edit_message_text(
                blocked_text + t(user_id, 'unblock_user_prompt'),
                reply_markup=None
            )
            context.user_data['admin_action'] = 'unblock'
    
    elif data == "admin_maintenance":
        bot_status_data = load_json(BOT_STATUS_FILE, {"maintenance": False, "enabled": True})
        bot_status_data["maintenance"] = not bot_status_data["maintenance"]
        save_json(BOT_STATUS_FILE, bot_status_data)
        status_text = t(user_id, 'maintenance_enabled' if bot_status_data["maintenance"] else 'maintenance_disabled')
        await query.edit_message_text(
            status_text,
            reply_markup=get_admin_keyboard(user_id)
        )
    
    elif data == "admin_disable_bot":
        bot_status_data = load_json(BOT_STATUS_FILE, {"maintenance": False, "enabled": True})
        bot_status_data["enabled"] = False
        save_json(BOT_STATUS_FILE, bot_status_data)
        await query.edit_message_text(
            t(user_id, 'bot_disabled_msg'),
            reply_markup=get_admin_keyboard(user_id)
        )
    
    elif data == "admin_enable_bot":
        bot_status_data = load_json(BOT_STATUS_FILE, {"maintenance": False, "enabled": True})
        bot_status_data["enabled"] = True
        bot_status_data["maintenance"] = False
        save_json(BOT_STATUS_FILE, bot_status_data)
        await query.edit_message_text(
            t(user_id, 'bot_enabled_msg'),
            reply_markup=get_admin_keyboard(user_id)
        )
    
    elif data == "admin_create_copy":
        await query.edit_message_text(
            t(user_id, 'create_bot_copy_prompt'),
            reply_markup=None
        )
        context.user_data['admin_action'] = 'create_copy'

# Обработчик подтверждения валидности кода
async def code_validity_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data.split("_")
    validity = data[1]  # valid или invalid
    code_hash = data[2]  # хеш кода
    
    # Получаем информацию о выданном коде из файла
    issued_codes = load_json(ISSUED_CODES_FILE, {})
    code_data = issued_codes.get(code_hash)
    
    if not code_data:
        await query.edit_message_text("❌ Информация о коде не найдена.")
        return
    
    code = code_data['code']
    
    if validity == "valid":
        # Код действителен - возвращаем его в конец списка
        codes_list = load_json(CODES_FILE, [])
        codes_list.append(code_data)
        save_json(CODES_FILE, codes_list)
        
        await query.edit_message_text(
            t(user_id, 'code_validated'),
            parse_mode=ParseMode.HTML
        )
    elif validity == "invalid":
        # Код не действителен - удаляем из базы (уже удален, просто подтверждаем)
        await query.edit_message_text(
            t(user_id, 'code_removed'),
            parse_mode=ParseMode.HTML
        )
    
    # Удаляем информацию о выданном коде из временного хранилища
    issued_codes.pop(code_hash, None)
    save_json(ISSUED_CODES_FILE, issued_codes)

# Обработчик выбора языка
async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = query.data.split("_")[1]  # ru или en
    
    set_user_language(user_id, lang)
    
    await query.edit_message_text(t(user_id, 'language_changed'))

# Команда отмены
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_admin(user_id) and context.user_data.get('admin_action'):
        context.user_data['admin_action'] = None
        await update.message.reply_text(
            t(user_id, 'action_cancelled'),
            reply_markup=get_admin_keyboard(user_id)
        )
    elif context.user_data.get('waiting_for_code'):
        context.user_data['waiting_for_code'] = False
        await update.message.reply_text(
            t(user_id, 'cancelled'),
            reply_markup=get_main_keyboard(user_id)
        )

def main():
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("lang", language_command))
    application.add_handler(CallbackQueryHandler(code_confirm, pattern="^code_confirm_"))
    application.add_handler(CallbackQueryHandler(code_validity_callback, pattern="^code_(valid|invalid)_"))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    
    # Обработчик сообщений должен быть последним
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск бота
    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
