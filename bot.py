import json
import os
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import aiofiles

# Токен бота
BOT_TOKEN = "7560458678:AAHbtiK7z0QiII5Iz3fzo17cReOaDS-2tBU"
ADMIN_PASSWORD = "admin"

# Файл для хранения данных
DATA_FILE = "data.json"

# Инициализация данных
async def load_data():
    if os.path.exists(DATA_FILE):
        async with aiofiles.open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
    return {
        "users": {},
        "admin_users": [],
        "trends": {"diamond": 1.0, "gold": 1.0, "crystal": 1.0},
        "top_clickers": [],
        "top_miners": [],
        "top_richest": []
    }

async def save_data(data):
    async with aiofiles.open(DATA_FILE, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=2))

def get_user(user_id, data):
    if str(user_id) not in data["users"]:
        data["users"][str(user_id)] = {
            "diamond": 0,
            "gold": 0,
            "crystal": 0,
            "click_power": 1,
            "mines": [],
            "total_clicks": 0,
            "total_mined": 0,
            "username": "",
            "level": 1,
            "experience": 0
        }
    return data["users"][str(user_id)]

# Клавиатуры
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("💎 Профиль", callback_data="profile")],
        [InlineKeyboardButton("👆 Кликер", callback_data="clicker")],
        [InlineKeyboardButton("⛏️ Майнинг", callback_data="mining")],
        [InlineKeyboardButton("🏭 Фермы", callback_data="farms")],
        [InlineKeyboardButton("💸 Переводы", callback_data="transfers")],
        [InlineKeyboardButton("📊 Тренды", callback_data="trends")],
        [InlineKeyboardButton("🏆 Топы", callback_data="tops")],
        [InlineKeyboardButton("💰 Закупка валюты", callback_data="buy_currency")],
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("👥 Управление пользователями", callback_data="admin_users")],
        [InlineKeyboardButton("📊 Статистика бота", callback_data="admin_stats")],
        [InlineKeyboardButton("💎 Управление валютами", callback_data="admin_currency")],
        [InlineKeyboardButton("📈 Управление трендами", callback_data="admin_trends")],
        [InlineKeyboardButton("🔄 Сброс данных", callback_data="admin_reset")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def mining_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("⛏️ Купить шахту (100💎)", callback_data="buy_mine")],
        [InlineKeyboardButton("⬆️ Улучшить шахту (50💎)", callback_data="upgrade_mine")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def farms_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🏭 Купить ферму (500💎)", callback_data="buy_farm")],
        [InlineKeyboardButton("⬆️ Улучшить ферму (200💎)", callback_data="upgrade_farm")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def tops_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("👆 Топ кликеров", callback_data="top_clickers")],
        [InlineKeyboardButton("⛏️ Топ майнеров", callback_data="top_miners")],
        [InlineKeyboardButton("💰 Топ богачей", callback_data="top_richest")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def buy_currency_keyboard():
    keyboard = [
        [InlineKeyboardButton("💎 Купить Алмазы (100💰 за 1💎)", callback_data="buy_diamond")],
        [InlineKeyboardButton("🪙 Купить Золото (10💰 за 1🪙)", callback_data="buy_gold")],
        [InlineKeyboardButton("💠 Купить Кристаллы (50💰 за 1💠)", callback_data="buy_crystal")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = await load_data()
    user_id = update.effective_user.id
    user = get_user(user_id, data)
    user["username"] = update.effective_user.username or f"User_{user_id}"
    await save_data(data)
    
    text = f"""
👋 Добро пожаловать в Алмазный Кликер!

💎 Алмазы: {user['diamond']}
🪙 Золото: {user['gold']}
💠 Кристаллы: {user['crystal']}

Выберите действие:
"""
    await update.message.reply_text(text, reply_markup=main_menu_keyboard())

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = await load_data()
    user_id = update.effective_user.id
    
    # Проверяем, является ли пользователь админом
    if str(user_id) in data.get("admin_users", []):
        await update.message.reply_text("🔐 Админ панель:", reply_markup=admin_menu_keyboard())
    else:
        await update.message.reply_text("🔐 Введите пароль для доступа к админ панели:")

async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 3:
        await update.message.reply_text("❌ Формат: /transfer @username amount currency\nПример: /transfer @user 100 diamond")
        return
    
    data = await load_data()
    user_id = update.effective_user.id
    user = get_user(user_id, data)
    
    try:
        target_username = context.args[0].replace("@", "")
        amount = float(context.args[1])
        currency = context.args[2].lower()
        
        # Найти пользователя по username
        target_user_id = None
        for uid, u in data['users'].items():
            if u.get('username', '').lower() == target_username.lower():
                target_user_id = uid
                break
        
        if not target_user_id:
            await update.message.reply_text("❌ Пользователь не найден!")
            return
        
        target_user = get_user(int(target_user_id), data)
        
        if currency == "diamond":
            if user['diamond'] >= amount:
                user['diamond'] -= amount
                target_user['diamond'] += amount
                await update.message.reply_text(f"✅ Переведено {amount}💎 пользователю @{target_username}")
            else:
                await update.message.reply_text("❌ Недостаточно алмазов!")
        elif currency == "gold":
            if user['gold'] >= amount:
                user['gold'] -= amount
                target_user['gold'] += amount
                await update.message.reply_text(f"✅ Переведено {amount}🪙 пользователю @{target_username}")
            else:
                await update.message.reply_text("❌ Недостаточно золота!")
        elif currency == "crystal":
            if user['crystal'] >= amount:
                user['crystal'] -= amount
                target_user['crystal'] += amount
                await update.message.reply_text(f"✅ Переведено {amount}💠 пользователю @{target_username}")
            else:
                await update.message.reply_text("❌ Недостаточно кристаллов!")
        else:
            await update.message.reply_text("❌ Неверная валюта! Используйте: diamond, gold, crystal")
        
        await save_data(data)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def add_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = await load_data()
    user_id = update.effective_user.id
    
    if str(user_id) not in data.get("admin_users", []):
        await update.message.reply_text("❌ У вас нет доступа к этой команде!")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("❌ Формат: /add_currency @username amount [currency]\nПример: /add_currency @user 1000 diamond\nПо умолчанию: diamond")
        return
    
    try:
        target_username = context.args[0].replace("@", "")
        amount = float(context.args[1])
        # Валюта опциональна, по умолчанию diamond
        currency = context.args[2].lower() if len(context.args) >= 3 else "diamond"
        
        target_user_id = None
        for uid, u in data['users'].items():
            if u.get('username', '').lower() == target_username.lower():
                target_user_id = uid
                break
        
        if not target_user_id:
            await update.message.reply_text("❌ Пользователь не найден!")
            return
        
        target_user = get_user(int(target_user_id), data)
        
        if currency == "diamond" or currency == "💎":
            target_user['diamond'] += amount
            await update.message.reply_text(f"✅ Добавлено {amount}💎 пользователю @{target_username}")
        elif currency == "gold" or currency == "🪙":
            target_user['gold'] += amount
            await update.message.reply_text(f"✅ Добавлено {amount}🪙 пользователю @{target_username}")
        elif currency == "crystal" or currency == "💠":
            target_user['crystal'] += amount
            await update.message.reply_text(f"✅ Добавлено {amount}💠 пользователю @{target_username}")
        else:
            await update.message.reply_text("❌ Неверная валюта! Используйте: diamond, gold, crystal")
            return
        
        await save_data(data)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def del_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = await load_data()
    user_id = update.effective_user.id
    
    if str(user_id) not in data.get("admin_users", []):
        await update.message.reply_text("❌ У вас нет доступа к этой команде!")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("❌ Формат: /del_currency @username amount [currency]\nПример: /del_currency @user 1000 diamond\nПо умолчанию: diamond")
        return
    
    try:
        target_username = context.args[0].replace("@", "")
        amount = float(context.args[1])
        # Валюта опциональна, по умолчанию diamond
        currency = context.args[2].lower() if len(context.args) >= 3 else "diamond"
        
        target_user_id = None
        for uid, u in data['users'].items():
            if u.get('username', '').lower() == target_username.lower():
                target_user_id = uid
                break
        
        if not target_user_id:
            await update.message.reply_text("❌ Пользователь не найден!")
            return
        
        target_user = get_user(int(target_user_id), data)
        
        if currency == "diamond" or currency == "💎":
            if target_user['diamond'] >= amount:
                target_user['diamond'] -= amount
                await update.message.reply_text(f"✅ Удалено {amount}💎 у пользователя @{target_username}")
            else:
                await update.message.reply_text("❌ У пользователя недостаточно алмазов!")
        elif currency == "gold" or currency == "🪙":
            if target_user['gold'] >= amount:
                target_user['gold'] -= amount
                await update.message.reply_text(f"✅ Удалено {amount}🪙 у пользователя @{target_username}")
            else:
                await update.message.reply_text("❌ У пользователя недостаточно золота!")
        elif currency == "crystal" or currency == "💠":
            if target_user['crystal'] >= amount:
                target_user['crystal'] -= amount
                await update.message.reply_text(f"✅ Удалено {amount}💠 у пользователя @{target_username}")
            else:
                await update.message.reply_text("❌ У пользователя недостаточно кристаллов!")
        else:
            await update.message.reply_text("❌ Неверная валюта! Используйте: diamond, gold, crystal")
            return
        
        await save_data(data)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def set_trend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = await load_data()
    user_id = update.effective_user.id
    
    if str(user_id) not in data.get("admin_users", []):
        await update.message.reply_text("❌ У вас нет доступа к этой команде!")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("❌ Формат: /set_trend currency value")
        return
    
    try:
        currency = context.args[0].lower()
        value = float(context.args[1])
        
        if currency not in data['trends']:
            await update.message.reply_text("❌ Неверная валюта! Используйте: diamond, gold, crystal")
            return
        
        data['trends'][currency] = value
        await save_data(data)
        await update.message.reply_text(f"✅ Тренд {currency} установлен: {value}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def reset_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = await load_data()
    user_id = update.effective_user.id
    
    if str(user_id) not in data.get("admin_users", []):
        await update.message.reply_text("❌ У вас нет доступа к этой команде!")
        return
    
    data['users'] = {}
    await save_data(data)
    await update.message.reply_text("✅ Все данные сброшены!")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = await load_data()
    user_id = query.from_user.id
    
    if query.data == "main_menu":
        await query.edit_message_text("🏠 Главное меню:", reply_markup=main_menu_keyboard())
        return
    
    if query.data == "profile":
        user = get_user(user_id, data)
        total_wealth = user['diamond'] + user['gold'] * 0.1 + user['crystal'] * 0.5
        text = f"""
👤 Профиль

💎 Алмазы: {user['diamond']}
🪙 Золото: {user['gold']}
💠 Кристаллы: {user['crystal']}
👆 Сила клика: {user['click_power']}
⛏️ Шахт: {len(user['mines'])}
📊 Уровень: {user['level']}
⭐ Опыт: {user['experience']}/{user['level'] * 100}
💰 Общее богатство: {total_wealth:.2f}
👆 Всего кликов: {user['total_clicks']}
⛏️ Всего добыто: {user['total_mined']}
"""
        await query.edit_message_text(text, reply_markup=main_menu_keyboard())
        await save_data(data)
        return
    
    if query.data == "clicker":
        user = get_user(user_id, data)
        user['diamond'] += user['click_power']
        user['total_clicks'] += 1
        user['experience'] += 1
        
        # Проверка уровня
        exp_needed = user['level'] * 100
        if user['experience'] >= exp_needed:
            user['level'] += 1
            user['experience'] = 0
            user['click_power'] += 1
            await query.answer("🎉 Уровень повышен! Сила клика увеличена!", show_alert=True)
        
        await save_data(data)
        await query.edit_message_text(
            f"👆 Клик! +{user['click_power']}💎\n\n💎 Алмазы: {user['diamond']}",
            reply_markup=main_menu_keyboard()
        )
        return
    
    if query.data == "mining":
        user = get_user(user_id, data)
        text = f"""
⛏️ Майнинг

💎 Алмазы: {user['diamond']}
⛏️ Шахт: {len(user['mines'])}
💰 Доход с шахт: {len(user['mines']) * 10}💎/час
"""
        await query.edit_message_text(text, reply_markup=mining_menu_keyboard())
        await save_data(data)
        return
    
    if query.data == "buy_mine":
        user = get_user(user_id, data)
        if user['diamond'] >= 100:
            user['diamond'] -= 100
            user['mines'].append({"level": 1, "income": 10})
            await query.answer("✅ Шахта куплена!", show_alert=True)
            await query.edit_message_text(
                f"⛏️ Майнинг\n\n💎 Алмазы: {user['diamond']}\n⛏️ Шахт: {len(user['mines'])}",
                reply_markup=mining_menu_keyboard()
            )
        else:
            await query.answer("❌ Недостаточно алмазов!", show_alert=True)
        await save_data(data)
        return
    
    if query.data == "upgrade_mine":
        user = get_user(user_id, data)
        if len(user['mines']) > 0 and user['diamond'] >= 50:
            user['diamond'] -= 50
            user['mines'][0]['level'] += 1
            user['mines'][0]['income'] += 5
            await query.answer("✅ Шахта улучшена!", show_alert=True)
            await query.edit_message_text(
                f"⛏️ Майнинг\n\n💎 Алмазы: {user['diamond']}\n⛏️ Шахт: {len(user['mines'])}",
                reply_markup=mining_menu_keyboard()
            )
        else:
            await query.answer("❌ Нет шахт или недостаточно алмазов!", show_alert=True)
        await save_data(data)
        return
    
    if query.data == "farms":
        user = get_user(user_id, data)
        farms_count = len([m for m in user['mines'] if m.get('type') == 'farm'])
        text = f"""
🏭 Фермы

💎 Алмазы: {user['diamond']}
🏭 Ферм: {farms_count}
💰 Доход с ферм: {farms_count * 50}💎/час
"""
        await query.edit_message_text(text, reply_markup=farms_menu_keyboard())
        await save_data(data)
        return
    
    if query.data == "buy_farm":
        user = get_user(user_id, data)
        if user['diamond'] >= 500:
            user['diamond'] -= 500
            if 'mines' not in user:
                user['mines'] = []
            user['mines'].append({"level": 1, "income": 50, "type": "farm"})
            await query.answer("✅ Ферма куплена!", show_alert=True)
            farms_count = len([m for m in user['mines'] if m.get('type') == 'farm'])
            await query.edit_message_text(
                f"🏭 Фермы\n\n💎 Алмазы: {user['diamond']}\n🏭 Ферм: {farms_count}",
                reply_markup=farms_menu_keyboard()
            )
        else:
            await query.answer("❌ Недостаточно алмазов!", show_alert=True)
        await save_data(data)
        return
    
    if query.data == "upgrade_farm":
        user = get_user(user_id, data)
        farms = [m for m in user['mines'] if m.get('type') == 'farm']
        if len(farms) > 0 and user['diamond'] >= 200:
            user['diamond'] -= 200
            farms[0]['level'] += 1
            farms[0]['income'] += 25
            await query.answer("✅ Ферма улучшена!", show_alert=True)
            farms_count = len([m for m in user['mines'] if m.get('type') == 'farm'])
            await query.edit_message_text(
                f"🏭 Фермы\n\n💎 Алмазы: {user['diamond']}\n🏭 Ферм: {farms_count}",
                reply_markup=farms_menu_keyboard()
            )
        else:
            await query.answer("❌ Нет ферм или недостаточно алмазов!", show_alert=True)
        await save_data(data)
        return
    
    if query.data == "transfers":
        user = get_user(user_id, data)
        await query.edit_message_text(
            f"""
💸 Переводы

💎 Алмазы: {user['diamond']}
🪙 Золото: {user['gold']}
💠 Кристаллы: {user['crystal']}

Для перевода отправьте команду:
/transfer @username amount currency

Пример: /transfer @user 100 diamond
Валюты: diamond, gold, crystal
""",
            reply_markup=main_menu_keyboard()
        )
        await save_data(data)
        return
    
    if query.data == "trends":
        trends = data['trends']
        text = f"""
📊 Тренды валют

💎 Алмазы: {trends['diamond']:.2f}x
🪙 Золото: {trends['gold']:.2f}x
💠 Кристаллы: {trends['crystal']:.2f}x

Тренды меняются каждый час!
"""
        await query.edit_message_text(text, reply_markup=main_menu_keyboard())
        return
    
    if query.data == "tops":
        await query.edit_message_text("🏆 Выберите топ:", reply_markup=tops_menu_keyboard())
        return
    
    if query.data == "top_clickers":
        data = await load_data()
        users_list = [(uid, u['total_clicks']) for uid, u in data['users'].items()]
        users_list.sort(key=lambda x: x[1], reverse=True)
        top = users_list[:10]
        text = "👆 Топ кликеров:\n\n"
        for i, (uid, clicks) in enumerate(top, 1):
            username = data['users'][uid].get('username', f'User_{uid}')
            text += f"{i}. {username}: {clicks} кликов\n"
        await query.edit_message_text(text, reply_markup=tops_menu_keyboard())
        return
    
    if query.data == "top_miners":
        data = await load_data()
        users_list = [(uid, u['total_mined']) for uid, u in data['users'].items()]
        users_list.sort(key=lambda x: x[1], reverse=True)
        top = users_list[:10]
        text = "⛏️ Топ майнеров:\n\n"
        for i, (uid, mined) in enumerate(top, 1):
            username = data['users'][uid].get('username', f'User_{uid}')
            text += f"{i}. {username}: {mined} добыто\n"
        await query.edit_message_text(text, reply_markup=tops_menu_keyboard())
        return
    
    if query.data == "top_richest":
        data = await load_data()
        users_list = []
        for uid, u in data['users'].items():
            wealth = u['diamond'] + u['gold'] * 0.1 + u['crystal'] * 0.5
            users_list.append((uid, wealth))
        users_list.sort(key=lambda x: x[1], reverse=True)
        top = users_list[:10]
        text = "💰 Топ богачей:\n\n"
        for i, (uid, wealth) in enumerate(top, 1):
            username = data['users'][uid].get('username', f'User_{uid}')
            text += f"{i}. {username}: {wealth:.2f}💎\n"
        await query.edit_message_text(text, reply_markup=tops_menu_keyboard())
        return
    
    if query.data == "buy_currency":
        user = get_user(user_id, data)
        text = f"""
💰 Закупка валюты

💎 Алмазы: {user['diamond']}
🪙 Золото: {user['gold']}
💠 Кристаллы: {user['crystal']}

Выберите валюту для покупки:
"""
        await query.edit_message_text(text, reply_markup=buy_currency_keyboard())
        await save_data(data)
        return
    
    if query.data == "buy_diamond":
        user = get_user(user_id, data)
        cost = 100
        if user['gold'] >= cost:
            user['gold'] -= cost
            user['diamond'] += 1
            await query.answer("✅ Алмаз куплен!", show_alert=True)
            await query.edit_message_text(
                f"💰 Закупка валюты\n\n💎 Алмазы: {user['diamond']}\n🪙 Золото: {user['gold']}",
                reply_markup=buy_currency_keyboard()
            )
        else:
            await query.answer("❌ Недостаточно золота!", show_alert=True)
        await save_data(data)
        return
    
    if query.data == "buy_gold":
        user = get_user(user_id, data)
        cost = 10
        if user['crystal'] >= cost:
            user['crystal'] -= cost
            user['gold'] += 1
            await query.answer("✅ Золото куплено!", show_alert=True)
            await query.edit_message_text(
                f"💰 Закупка валюты\n\n🪙 Золото: {user['gold']}\n💠 Кристаллы: {user['crystal']}",
                reply_markup=buy_currency_keyboard()
            )
        else:
            await query.answer("❌ Недостаточно кристаллов!", show_alert=True)
        await save_data(data)
        return
    
    if query.data == "buy_crystal":
        user = get_user(user_id, data)
        cost = 50
        if user['diamond'] >= cost:
            user['diamond'] -= cost
            user['crystal'] += 1
            await query.answer("✅ Кристалл куплен!", show_alert=True)
            await query.edit_message_text(
                f"💰 Закупка валюты\n\n💎 Алмазы: {user['diamond']}\n💠 Кристаллы: {user['crystal']}",
                reply_markup=buy_currency_keyboard()
            )
        else:
            await query.answer("❌ Недостаточно алмазов!", show_alert=True)
        await save_data(data)
        return
    
    # Админ панель
    if query.data.startswith("admin_"):
        if str(user_id) not in data.get("admin_users", []):
            await query.answer("❌ У вас нет доступа к админ панели!", show_alert=True)
            return
        
        if query.data == "admin_users":
            total_users = len(data['users'])
            text = f"👥 Управление пользователями\n\nВсего пользователей: {total_users}"
            await query.edit_message_text(text, reply_markup=admin_menu_keyboard())
            return
        
        if query.data == "admin_stats":
            total_users = len(data['users'])
            total_clicks = sum(u['total_clicks'] for u in data['users'].values())
            total_mined = sum(u['total_mined'] for u in data['users'].values())
            text = f"""
📊 Статистика бота

👥 Пользователей: {total_users}
👆 Всего кликов: {total_clicks}
⛏️ Всего добыто: {total_mined}
"""
            await query.edit_message_text(text, reply_markup=admin_menu_keyboard())
            return
        
        if query.data == "admin_currency":
            await query.edit_message_text(
                "💎 Управление валютами\n\nИспользуйте команды:\n/add_currency @username amount currency\n/del_currency @username amount currency",
                reply_markup=admin_menu_keyboard()
            )
            return
        
        if query.data == "admin_trends":
            trends = data['trends']
            await query.edit_message_text(
                f"📈 Управление трендами\n\nТекущие тренды:\n💎 Алмазы: {trends['diamond']:.2f}x\n🪙 Золото: {trends['gold']:.2f}x\n💠 Кристаллы: {trends['crystal']:.2f}x\n\nИспользуйте: /set_trend currency value",
                reply_markup=admin_menu_keyboard()
            )
            return
        
        if query.data == "admin_reset":
            await query.edit_message_text(
                "🔄 Сброс данных\n\n⚠️ ВНИМАНИЕ! Это действие удалит все данные.\nИспользуйте: /reset_all (требует подтверждения)",
                reply_markup=admin_menu_keyboard()
            )
            return

# Обработка текстовых сообщений (для админ пароля)
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = await load_data()
    user_id = update.effective_user.id
    text = update.message.text
    
    # Проверка пароля админа
    if text == ADMIN_PASSWORD:
        if str(user_id) not in data.get("admin_users", []):
            data.setdefault("admin_users", []).append(str(user_id))
            await save_data(data)
            await update.message.reply_text("✅ Вы получили доступ к админ панели!", reply_markup=admin_menu_keyboard())
        else:
            await update.message.reply_text("🔐 Админ панель:", reply_markup=admin_menu_keyboard())
        return

# Автоматический доход от майнинга
async def mining_income(context: ContextTypes.DEFAULT_TYPE):
    data = await load_data()
    for user_id, user in data['users'].items():
        total_income = 0
        for mine in user.get('mines', []):
            total_income += mine.get('income', 0)
        if total_income > 0:
            user['diamond'] += total_income
            user['total_mined'] += total_income
    await save_data(data)

# Обновление трендов
async def update_trends(context: ContextTypes.DEFAULT_TYPE):
    import random
    data = await load_data()
    data['trends']['diamond'] = round(random.uniform(0.8, 1.2), 2)
    data['trends']['gold'] = round(random.uniform(0.8, 1.2), 2)
    data['trends']['crystal'] = round(random.uniform(0.8, 1.2), 2)
    await save_data(data)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("transfer", transfer))
    app.add_handler(CommandHandler("add_currency", add_currency))
    app.add_handler(CommandHandler("del_currency", del_currency))
    app.add_handler(CommandHandler("set_trend", set_trend))
    app.add_handler(CommandHandler("reset_all", reset_all))
    
    # Обработчики кнопок и сообщений
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Планировщик задач (если доступен)
    try:
        job_queue = app.job_queue
        if job_queue:
            job_queue.run_repeating(mining_income, interval=3600, first=3600)  # Каждый час
            job_queue.run_repeating(update_trends, interval=3600, first=3600)  # Каждый час
    except:
        print("JobQueue не доступен, автоматические задачи отключены")
    
    print("Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
