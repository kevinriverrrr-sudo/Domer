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
        "top_richest": [],
        "bosses": [],
        "lottery_pool": {"diamond": 0, "gold": 0, "crystal": 0},
        "weekly_quests": {}
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
            "experience": 0,
            "daily_reward": {"last_date": None, "streak": 0},
            "achievements": [],
            "autoclicker_level": 0,
            "autoclicker_power": 0,
            "upgrades": {"multiplier": 1.0, "bonus_chance": 0},
            "referral_code": str(user_id)[-6:],
            "referred_by": None,
            "referrals": [],
            "lottery_tickets": 0,
            "boss_damage": 0,
            "shop_items": [],
            "weekly_quests_progress": {}
        }
    return data["users"][str(user_id)]

# Клавиатуры
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("💎 Профиль", callback_data="profile")],
        [InlineKeyboardButton("👆 Кликер", callback_data="clicker")],
        [InlineKeyboardButton("⛏️ Майнинг", callback_data="mining")],
        [InlineKeyboardButton("🏭 Фермы", callback_data="farms")],
        [InlineKeyboardButton("🎁 Ежедневная награда", callback_data="daily_reward")],
        [InlineKeyboardButton("🏅 Достижения", callback_data="achievements")],
        [InlineKeyboardButton("🎰 Лотерея", callback_data="lottery")],
        [InlineKeyboardButton("🎯 Задания", callback_data="quests")],
        [InlineKeyboardButton("👥 Рефералы", callback_data="referrals")],
        [InlineKeyboardButton("👾 Боссы", callback_data="bosses")],
        [InlineKeyboardButton("🛒 Магазин", callback_data="shop")],
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

def clicker_upgrades_keyboard():
    keyboard = [
        [InlineKeyboardButton("⚡ Улучшить силу клика (100💎)", callback_data="upgrade_click_power")],
        [InlineKeyboardButton("🤖 Купить автокликер (500💎)", callback_data="buy_autoclicker")],
        [InlineKeyboardButton("⬆️ Улучшить автокликер (200💎)", callback_data="upgrade_autoclicker")],
        [InlineKeyboardButton("✨ Множитель x2 (1000💎)", callback_data="buy_multiplier")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def lottery_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎫 Купить билет (50💎)", callback_data="buy_lottery_ticket")],
        [InlineKeyboardButton("🎰 Сыграть в лотерею", callback_data="play_lottery")],
        [InlineKeyboardButton("📊 Статистика лотереи", callback_data="lottery_stats")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def shop_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎨 Тема профиля (200💎)", callback_data="buy_profile_theme")],
        [InlineKeyboardButton("💫 Эффект кликера (300💎)", callback_data="buy_clicker_effect")],
        [InlineKeyboardButton("🌟 Премиум статус (1000💎)", callback_data="buy_premium")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def bosses_keyboard():
    keyboard = [
        [InlineKeyboardButton("👾 Атаковать босса", callback_data="attack_boss")],
        [InlineKeyboardButton("📊 Статус босса", callback_data="boss_status")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = await load_data()
    user_id = update.effective_user.id
    user = get_user(user_id, data)
    user["username"] = update.effective_user.username or f"User_{user_id}"
    
    # Обработка реферального кода
    if context.args and len(context.args) > 0:
        ref_code = context.args[0]
        # Найти пользователя с этим кодом
        for uid, u in data['users'].items():
            if u.get('referral_code') == ref_code and str(uid) != str(user_id):
                if not user.get('referred_by'):
                    user['referred_by'] = u.get('username', f'User_{uid}')
                    if 'referrals' not in u:
                        u['referrals'] = []
                    u['referrals'].append(str(user_id))
                    # Бонус новому пользователю
                    user['diamond'] += 100
                    user['gold'] += 500
                    # Бонус рефереру
                    u['diamond'] += 50
                    await update.message.reply_text(f"🎉 Вы ввели реферальный код! Получено 100💎 и 500🪙")
                break
    
    await save_data(data)
    
    text = f"""
👋 Добро пожаловать в Алмазный Кликер!

💎 Алмазы: {user['diamond']}
🪙 Золото: {user['gold']}
💠 Кристаллы: {user['crystal']}

Выберите действие:
"""
    await update.message.reply_text(text, reply_markup=main_menu_keyboard())

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("❌ Формат: /referral код\nПример: /referral 123456")
        return
    
    data = await load_data()
    user_id = update.effective_user.id
    user = get_user(user_id, data)
    ref_code = context.args[0]
    
    # Найти пользователя с этим кодом
    found = False
    for uid, u in data['users'].items():
        if u.get('referral_code') == ref_code and str(uid) != str(user_id):
            if not user.get('referred_by'):
                user['referred_by'] = u.get('username', f'User_{uid}')
                if 'referrals' not in u:
                    u['referrals'] = []
                u['referrals'].append(str(user_id))
                # Бонус новому пользователю
                user['diamond'] += 100
                user['gold'] += 500
                # Бонус рефереру
                u['diamond'] += 50
                await update.message.reply_text(f"✅ Реферальный код активирован! Получено 100💎 и 500🪙")
                found = True
            else:
                await update.message.reply_text("❌ Вы уже использовали реферальный код!")
                found = True
            break
    
    if not found:
        await update.message.reply_text("❌ Реферальный код не найден!")
    
    await save_data(data)

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
        achievements_count = len(user.get('achievements', []))
        referrals_count = len(user.get('referrals', []))
        autoclicker_level = user.get('autoclicker_level', 0)
        multiplier = user.get('upgrades', {}).get('multiplier', 1.0)
        premium = "🌟" if 'premium' in user.get('shop_items', []) else ""
        
        text = f"""
👤 Профиль {premium}

💎 Алмазы: {user['diamond']}
🪙 Золото: {user['gold']}
💠 Кристаллы: {user['crystal']}
👆 Сила клика: {user['click_power']}
✨ Множитель: x{multiplier}
🤖 Автокликер: Уровень {autoclicker_level} ({user.get('autoclicker_power', 0)}/мин)
⛏️ Шахт: {len(user['mines'])}
📊 Уровень: {user['level']}
⭐ Опыт: {user['experience']}/{user['level'] * 100}
💰 Общее богатство: {total_wealth:.2f}
👆 Всего кликов: {user['total_clicks']}
⛏️ Всего добыто: {user['total_mined']}
🏅 Достижений: {achievements_count}/8
👥 Рефералов: {referrals_count}
🔗 Реферальный код: {user.get('referral_code', 'N/A')}
"""
        await query.edit_message_text(text, reply_markup=main_menu_keyboard())
        await save_data(data)
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
            
            # Обновление прогресса заданий
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            if str(week_start) in data.get('weekly_quests', {}):
                if 'weekly_quests_progress' not in user:
                    user['weekly_quests_progress'] = {}
                user['weekly_quests_progress']['mines'] = len(user['mines'])
            
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
    
    # Ежедневная награда
    if query.data == "daily_reward":
        user = get_user(user_id, data)
        today = datetime.now().date()
        last_date = user['daily_reward'].get('last_date')
        
        if last_date:
            try:
                last_date = datetime.fromisoformat(last_date).date()
            except:
                last_date = None
        
        if last_date == today:
            await query.answer("❌ Вы уже получили награду сегодня!", show_alert=True)
            await query.edit_message_text(
                f"🎁 Ежедневная награда\n\nВы уже получили награду сегодня!\nСерия дней: {user['daily_reward']['streak']}",
                reply_markup=main_menu_keyboard()
            )
        else:
            streak = user['daily_reward'].get('streak', 0)
            if last_date and (today - last_date).days == 1:
                streak += 1
            elif last_date and (today - last_date).days > 1:
                streak = 1
            else:
                streak = 1
            
            reward_diamond = 50 + (streak * 10)
            reward_gold = 100 + (streak * 20)
            
            user['diamond'] += reward_diamond
            user['gold'] += reward_gold
            user['daily_reward']['last_date'] = str(today)
            user['daily_reward']['streak'] = streak
            
            await query.answer(f"✅ Награда получена! Серия: {streak} дней", show_alert=True)
            await query.edit_message_text(
                f"🎁 Ежедневная награда\n\n✅ Получено:\n💎 +{reward_diamond} алмазов\n🪙 +{reward_gold} золота\n\nСерия дней: {streak}",
                reply_markup=main_menu_keyboard()
            )
        await save_data(data)
        return
    
    # Достижения
    if query.data == "achievements":
        user = get_user(user_id, data)
        achievements_list = [
            {"id": "first_click", "name": "Первый клик", "desc": "Сделать первый клик", "reward": 10},
            {"id": "hundred_clicks", "name": "Сотня кликов", "desc": "Сделать 100 кликов", "reward": 50},
            {"id": "thousand_clicks", "name": "Тысяча кликов", "desc": "Сделать 1000 кликов", "reward": 200},
            {"id": "ten_thousand_clicks", "name": "Десять тысяч", "desc": "Сделать 10000 кликов", "reward": 1000},
            {"id": "first_mine", "name": "Первый рудник", "desc": "Купить первую шахту", "reward": 100},
            {"id": "level_10", "name": "Уровень 10", "desc": "Достичь 10 уровня", "reward": 500},
            {"id": "level_25", "name": "Уровень 25", "desc": "Достичь 25 уровня", "reward": 2000},
            {"id": "rich", "name": "Богач", "desc": "Иметь 10000 алмазов", "reward": 5000},
        ]
        
        text = "🏅 Достижения:\n\n"
        for ach in achievements_list:
            status = "✅" if ach['id'] in user.get('achievements', []) else "⭕"
            text += f"{status} {ach['name']}: {ach['desc']}\n"
        
        text += f"\n💎 Алмазы: {user['diamond']}"
        await query.edit_message_text(text, reply_markup=main_menu_keyboard())
        await save_data(data)
        return
    
    # Проверка достижений
    def check_achievements(user, data):
        new_achievements = []
        if user['total_clicks'] >= 1 and "first_click" not in user.get('achievements', []):
            new_achievements.append(("first_click", 10))
        if user['total_clicks'] >= 100 and "hundred_clicks" not in user.get('achievements', []):
            new_achievements.append(("hundred_clicks", 50))
        if user['total_clicks'] >= 1000 and "thousand_clicks" not in user.get('achievements', []):
            new_achievements.append(("thousand_clicks", 200))
        if user['total_clicks'] >= 10000 and "ten_thousand_clicks" not in user.get('achievements', []):
            new_achievements.append(("ten_thousand_clicks", 1000))
        if len(user.get('mines', [])) >= 1 and "first_mine" not in user.get('achievements', []):
            new_achievements.append(("first_mine", 100))
        if user['level'] >= 10 and "level_10" not in user.get('achievements', []):
            new_achievements.append(("level_10", 500))
        if user['level'] >= 25 and "level_25" not in user.get('achievements', []):
            new_achievements.append(("level_25", 2000))
        if user['diamond'] >= 10000 and "rich" not in user.get('achievements', []):
            new_achievements.append(("rich", 5000))
        
        for ach_id, reward in new_achievements:
            if 'achievements' not in user:
                user['achievements'] = []
            user['achievements'].append(ach_id)
            user['diamond'] += reward
        
        return new_achievements
    
    # Кликер - открывает меню улучшений или кликает
    if query.data == "clicker":
        user = get_user(user_id, data)
        multiplier = user.get('upgrades', {}).get('multiplier', 1.0)
        reward = int(user['click_power'] * multiplier)
        user['diamond'] += reward
        user['total_clicks'] += 1
        user['experience'] += 1
        
        # Обновление прогресса заданий
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        if str(week_start) in data.get('weekly_quests', {}):
            if 'weekly_quests_progress' not in user:
                user['weekly_quests_progress'] = {}
            user['weekly_quests_progress']['clicks'] = user['weekly_quests_progress'].get('clicks', 0) + 1
        
        # Проверка достижений
        new_achs = check_achievements(user, data)
        
        # Проверка уровня
        exp_needed = user['level'] * 100
        if user['experience'] >= exp_needed:
            user['level'] += 1
            user['experience'] = 0
            user['click_power'] += 1
            await query.answer("🎉 Уровень повышен! Сила клика увеличена!", show_alert=True)
        
        ach_text = ""
        if new_achs:
            ach_text = f"\n\n🏅 Новое достижение! +{sum(r for _, r in new_achs)}💎"
        
        keyboard = [
            [InlineKeyboardButton("👆 Кликнуть еще", callback_data="clicker")],
            [InlineKeyboardButton("⚡ Улучшения", callback_data="clicker_upgrades")],
            [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")],
        ]
        
        await save_data(data)
        await query.edit_message_text(
            f"👆 Клик! +{reward}💎\n\n💎 Алмазы: {user['diamond']}\n⚡ Сила: {user['click_power']}\n🤖 Автокликер: {user.get('autoclicker_power', 0)}/мин{ach_text}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    if query.data == "clicker_upgrades":
        user = get_user(user_id, data)
        text = f"""
⚡ Улучшения кликера

👆 Сила клика: {user['click_power']}
🤖 Автокликер: Уровень {user.get('autoclicker_level', 0)} (Сила: {user.get('autoclicker_power', 0)}/мин)
✨ Множитель: x{user.get('upgrades', {}).get('multiplier', 1.0)}
💎 Алмазы: {user['diamond']}
"""
        await query.edit_message_text(text, reply_markup=clicker_upgrades_keyboard())
        await save_data(data)
        return
    
    if query.data == "upgrade_click_power":
        user = get_user(user_id, data)
        if user['diamond'] >= 100:
            user['diamond'] -= 100
            user['click_power'] += 1
            await query.answer("✅ Сила клика улучшена!", show_alert=True)
            await query.edit_message_text(
                f"⚡ Улучшения кликера\n\nСила клика: {user['click_power']}\n💎 Алмазы: {user['diamond']}",
                reply_markup=clicker_upgrades_keyboard()
            )
        else:
            await query.answer("❌ Недостаточно алмазов!", show_alert=True)
        await save_data(data)
        return
    
    if query.data == "buy_autoclicker":
        user = get_user(user_id, data)
        if user['diamond'] >= 500 and user.get('autoclicker_level', 0) == 0:
            user['diamond'] -= 500
            user['autoclicker_level'] = 1
            user['autoclicker_power'] = 1
            await query.answer("✅ Автокликер куплен!", show_alert=True)
            await query.edit_message_text(
                f"🤖 Автокликер\n\nУровень: {user['autoclicker_level']}\nСила: {user['autoclicker_power']}/мин\n💎 Алмазы: {user['diamond']}",
                reply_markup=clicker_upgrades_keyboard()
            )
        elif user.get('autoclicker_level', 0) > 0:
            await query.answer("❌ У вас уже есть автокликер!", show_alert=True)
        else:
            await query.answer("❌ Недостаточно алмазов!", show_alert=True)
        await save_data(data)
        return
    
    if query.data == "upgrade_autoclicker":
        user = get_user(user_id, data)
        if user.get('autoclicker_level', 0) > 0 and user['diamond'] >= 200:
            user['diamond'] -= 200
            user['autoclicker_level'] += 1
            user['autoclicker_power'] += 1
            await query.answer("✅ Автокликер улучшен!", show_alert=True)
            await query.edit_message_text(
                f"🤖 Автокликер\n\nУровень: {user['autoclicker_level']}\nСила: {user['autoclicker_power']}/мин\n💎 Алмазы: {user['diamond']}",
                reply_markup=clicker_upgrades_keyboard()
            )
        else:
            await query.answer("❌ Нет автокликера или недостаточно алмазов!", show_alert=True)
        await save_data(data)
        return
    
    if query.data == "buy_multiplier":
        user = get_user(user_id, data)
        if user['diamond'] >= 1000:
            user['diamond'] -= 1000
            if 'upgrades' not in user:
                user['upgrades'] = {}
            user['upgrades']['multiplier'] = user['upgrades'].get('multiplier', 1.0) * 2
            await query.answer("✅ Множитель куплен!", show_alert=True)
            await query.edit_message_text(
                f"✨ Множитель\n\nТекущий множитель: x{user['upgrades']['multiplier']}\n💎 Алмазы: {user['diamond']}",
                reply_markup=clicker_upgrades_keyboard()
            )
        else:
            await query.answer("❌ Недостаточно алмазов!", show_alert=True)
        await save_data(data)
        return
    
    # Лотерея
    if query.data == "lottery":
        user = get_user(user_id, data)
        tickets = user.get('lottery_tickets', 0)
        pool = data.get('lottery_pool', {'diamond': 0, 'gold': 0, 'crystal': 0})
        text = f"""
🎰 Лотерея

🎫 Ваши билеты: {tickets}
💰 Призовой фонд:
💎 {pool['diamond']} алмазов
🪙 {pool['gold']} золота
💠 {pool['crystal']} кристаллов
"""
        await query.edit_message_text(text, reply_markup=lottery_keyboard())
        await save_data(data)
        return
    
    if query.data == "buy_lottery_ticket":
        user = get_user(user_id, data)
        if user['diamond'] >= 50:
            user['diamond'] -= 50
            user['lottery_tickets'] = user.get('lottery_tickets', 0) + 1
            pool = data.get('lottery_pool', {'diamond': 0, 'gold': 0, 'crystal': 0})
            pool['diamond'] += 30
            pool['gold'] += 50
            data['lottery_pool'] = pool
            await query.answer("✅ Билет куплен!", show_alert=True)
            await query.edit_message_text(
                f"🎰 Лотерея\n\n🎫 Ваши билеты: {user['lottery_tickets']}\n💎 Алмазы: {user['diamond']}",
                reply_markup=lottery_keyboard()
            )
        else:
            await query.answer("❌ Недостаточно алмазов!", show_alert=True)
        await save_data(data)
        return
    
    if query.data == "play_lottery":
        user = get_user(user_id, data)
        tickets = user.get('lottery_tickets', 0)
        if tickets > 0:
            import random
            user['lottery_tickets'] -= 1
            pool = data.get('lottery_pool', {'diamond': 0, 'gold': 0, 'crystal': 0})
            
            # Шансы на выигрыш
            win_chance = random.random()
            if win_chance < 0.1:  # 10% шанс на большой приз
                reward_d = int(pool['diamond'] * 0.3)
                reward_g = int(pool['gold'] * 0.3)
                reward_c = int(pool['crystal'] * 0.3)
                user['diamond'] += reward_d
                user['gold'] += reward_g
                user['crystal'] += reward_c
                pool['diamond'] -= reward_d
                pool['gold'] -= reward_g
                pool['crystal'] -= reward_c
                await query.answer("🎉 Вы выиграли большой приз!", show_alert=True)
                text = f"🎰 Лотерея\n\n🎉 Вы выиграли:\n💎 {reward_d} алмазов\n🪙 {reward_g} золота\n💠 {reward_c} кристаллов\n\n🎫 Осталось билетов: {user['lottery_tickets']}"
            elif win_chance < 0.4:  # 30% шанс на средний приз
                reward_d = int(pool['diamond'] * 0.1)
                reward_g = int(pool['gold'] * 0.1)
                user['diamond'] += reward_d
                user['gold'] += reward_g
                pool['diamond'] -= reward_d
                pool['gold'] -= reward_g
                await query.answer("🎁 Вы выиграли средний приз!", show_alert=True)
                text = f"🎰 Лотерея\n\n🎁 Вы выиграли:\n💎 {reward_d} алмазов\n🪙 {reward_g} золота\n\n🎫 Осталось билетов: {user['lottery_tickets']}"
            else:  # 60% шанс на маленький приз
                reward_d = 10
                user['diamond'] += reward_d
                await query.answer("💰 Вы выиграли маленький приз!", show_alert=True)
                text = f"🎰 Лотерея\n\n💰 Вы выиграли:\n💎 {reward_d} алмазов\n\n🎫 Осталось билетов: {user['lottery_tickets']}"
            
            data['lottery_pool'] = pool
            await query.edit_message_text(text, reply_markup=lottery_keyboard())
        else:
            await query.answer("❌ У вас нет билетов!", show_alert=True)
        await save_data(data)
        return
    
    if query.data == "lottery_stats":
        pool = data.get('lottery_pool', {'diamond': 0, 'gold': 0, 'crystal': 0})
        total_tickets = sum(u.get('lottery_tickets', 0) for u in data['users'].values())
        text = f"""
📊 Статистика лотереи

💰 Призовой фонд:
💎 {pool['diamond']} алмазов
🪙 {pool['gold']} золота
💠 {pool['crystal']} кристаллов

🎫 Всего билетов у игроков: {total_tickets}
"""
        await query.edit_message_text(text, reply_markup=lottery_keyboard())
        return
    
    # Рефералы
    if query.data == "referrals":
        user = get_user(user_id, data)
        ref_code = user.get('referral_code', str(user_id)[-6:])
        referrals_count = len(user.get('referrals', []))
        referred_by = user.get('referred_by')
        
        text = f"""
👥 Реферальная система

🔗 Ваш код: {ref_code}
👥 Приглашено: {referrals_count} человек
"""
        if referred_by:
            text += f"\n✅ Вы приглашены пользователем: {referred_by}"
        text += f"\n\nИспользуйте команду:\n/referral {ref_code}\n\nДля входа по реферальной ссылке"
        
        await query.edit_message_text(text, reply_markup=main_menu_keyboard())
        await save_data(data)
        return
    
    # Задания
    if query.data == "quests":
        user = get_user(user_id, data)
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        if str(week_start) not in data.get('weekly_quests', {}):
            data['weekly_quests'][str(week_start)] = {
                "clicks": {"target": 1000, "reward": 500},
                "mines": {"target": 5, "reward": 200},
                "level": {"target": 5, "reward": 300}
            }
        
        quests = data['weekly_quests'][str(week_start)]
        progress = user.get('weekly_quests_progress', {})
        
        text = "🎯 Еженедельные задания:\n\n"
        for quest_id, quest_data in quests.items():
            current = progress.get(quest_id, 0)
            target = quest_data['target']
            reward = quest_data['reward']
            status = "✅" if current >= target else f"{current}/{target}"
            quest_name = {"clicks": "Клики", "mines": "Шахты", "level": "Уровни"}.get(quest_id, quest_id)
            text += f"{status} {quest_name}: {reward}💎\n"
        
        await query.edit_message_text(text, reply_markup=main_menu_keyboard())
        await save_data(data)
        return
    
    # Боссы
    if query.data == "bosses":
        if not data.get('bosses') or len(data['bosses']) == 0:
            data['bosses'] = [{
                "name": "Дракон Алмазов",
                "hp": 10000,
                "max_hp": 10000,
                "reward_diamond": 1000,
                "reward_gold": 5000,
                "reward_crystal": 100
            }]
        
        boss = data['bosses'][0]
        hp_percent = (boss['hp'] / boss['max_hp']) * 100
        
        text = f"""
👾 Босс: {boss['name']}

❤️ HP: {boss['hp']}/{boss['max_hp']} ({hp_percent:.1f}%)
💎 Награда: {boss['reward_diamond']}💎 {boss['reward_gold']}🪙 {boss['reward_crystal']}💠
"""
        await query.edit_message_text(text, reply_markup=bosses_keyboard())
        await save_data(data)
        return
    
    if query.data == "attack_boss":
        user = get_user(user_id, data)
        if not data.get('bosses') or len(data['bosses']) == 0:
            await query.answer("❌ Нет активных боссов!", show_alert=True)
            return
        
        boss = data['bosses'][0]
        damage = user['click_power'] * 10 + (user.get('autoclicker_power', 0) * 5)
        
        if damage > boss['hp']:
            damage = boss['hp']
        
        boss['hp'] -= damage
        user['boss_damage'] = user.get('boss_damage', 0) + damage
        
        if boss['hp'] <= 0:
            # Босс побежден
            reward_d = boss['reward_diamond']
            reward_g = boss['reward_gold']
            reward_c = boss['reward_crystal']
            
            # Награда распределяется по урону
            total_damage = sum(u.get('boss_damage', 0) for u in data['users'].values())
            user_reward = int((user.get('boss_damage', 0) / total_damage) * reward_d) if total_damage > 0 else 0
            
            user['diamond'] += user_reward
            user['gold'] += int(user_reward * 5)
            user['crystal'] += int(user_reward / 10)
            
            await query.answer(f"🎉 Босс побежден! Вы получили {user_reward}💎", show_alert=True)
            
            # Создаем нового босса
            data['bosses'] = [{
                "name": "Дракон Алмазов",
                "hp": 10000,
                "max_hp": 10000,
                "reward_diamond": 1000,
                "reward_gold": 5000,
                "reward_crystal": 100
            }]
            
            # Сбрасываем урон всех игроков
            for u in data['users'].values():
                u['boss_damage'] = 0
            
            await query.edit_message_text(
                f"👾 Босс побежден!\n\n🎉 Вы получили:\n💎 {user_reward} алмазов\n🪙 {int(user_reward * 5)} золота\n💠 {int(user_reward / 10)} кристаллов",
                reply_markup=bosses_keyboard()
            )
        else:
            await query.answer(f"⚔️ Нанесено {damage} урона!", show_alert=True)
            hp_percent = (boss['hp'] / boss['max_hp']) * 100
            await query.edit_message_text(
                f"👾 Босс: {boss['name']}\n\n❤️ HP: {boss['hp']}/{boss['max_hp']} ({hp_percent:.1f}%)\n💎 Награда: {boss['reward_diamond']}💎",
                reply_markup=bosses_keyboard()
            )
        
        await save_data(data)
        return
    
    if query.data == "boss_status":
        if not data.get('bosses') or len(data['bosses']) == 0:
            await query.edit_message_text("❌ Нет активных боссов!", reply_markup=bosses_keyboard())
            return
        
        boss = data['bosses'][0]
        total_damage = sum(u.get('boss_damage', 0) for u in data['users'].values())
        user_damage = get_user(user_id, data).get('boss_damage', 0)
        
        text = f"""
👾 Статус босса

{boss['name']}
❤️ HP: {boss['hp']}/{boss['max_hp']}
⚔️ Ваш урон: {user_damage}
⚔️ Общий урон: {total_damage}
"""
        await query.edit_message_text(text, reply_markup=bosses_keyboard())
        return
    
    # Магазин
    if query.data == "shop":
        user = get_user(user_id, data)
        text = f"""
🛒 Магазин улучшений

💎 Алмазы: {user['diamond']}
"""
        await query.edit_message_text(text, reply_markup=shop_keyboard())
        await save_data(data)
        return
    
    if query.data == "buy_profile_theme":
        user = get_user(user_id, data)
        if user['diamond'] >= 200:
            user['diamond'] -= 200
            if 'shop_items' not in user:
                user['shop_items'] = []
            if 'profile_theme' not in user['shop_items']:
                user['shop_items'].append('profile_theme')
            await query.answer("✅ Тема профиля куплена!", show_alert=True)
            await query.edit_message_text(
                f"🛒 Магазин\n\n✅ Тема профиля активирована!\n💎 Алмазы: {user['diamond']}",
                reply_markup=shop_keyboard()
            )
        else:
            await query.answer("❌ Недостаточно алмазов!", show_alert=True)
        await save_data(data)
        return
    
    if query.data == "buy_clicker_effect":
        user = get_user(user_id, data)
        if user['diamond'] >= 300:
            user['diamond'] -= 300
            if 'shop_items' not in user:
                user['shop_items'] = []
            if 'clicker_effect' not in user['shop_items']:
                user['shop_items'].append('clicker_effect')
            await query.answer("✅ Эффект кликера куплен!", show_alert=True)
            await query.edit_message_text(
                f"🛒 Магазин\n\n✅ Эффект кликера активирован!\n💎 Алмазы: {user['diamond']}",
                reply_markup=shop_keyboard()
            )
        else:
            await query.answer("❌ Недостаточно алмазов!", show_alert=True)
        await save_data(data)
        return
    
    if query.data == "buy_premium":
        user = get_user(user_id, data)
        if user['diamond'] >= 1000:
            user['diamond'] -= 1000
            if 'shop_items' not in user:
                user['shop_items'] = []
            if 'premium' not in user['shop_items']:
                user['shop_items'].append('premium')
            user['click_power'] += 5
            await query.answer("✅ Премиум статус активирован!", show_alert=True)
            await query.edit_message_text(
                f"🛒 Магазин\n\n🌟 Премиум статус активирован!\n💎 Алмазы: {user['diamond']}\n⚡ Сила клика увеличена!",
                reply_markup=shop_keyboard()
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

# Автоматический доход от майнинга и автокликера
async def mining_income(context: ContextTypes.DEFAULT_TYPE):
    data = await load_data()
    for user_id, user in data['users'].items():
        total_income = 0
        # Доход от шахт и ферм
        for mine in user.get('mines', []):
            total_income += mine.get('income', 0)
        # Доход от автокликера
        autoclicker_power = user.get('autoclicker_power', 0)
        if autoclicker_power > 0:
            multiplier = user.get('upgrades', {}).get('multiplier', 1.0)
            click_power = user.get('click_power', 1)
            total_income += int(autoclicker_power * click_power * multiplier)
        
        if total_income > 0:
            user['diamond'] += total_income
            user['total_mined'] += total_income
            user['total_clicks'] += autoclicker_power
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
    app.add_handler(CommandHandler("referral", referral))
    
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
