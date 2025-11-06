# -*- coding: utf-8 -*-
import logging
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode

# Íàñòðîéêè
BOT_TOKEN = "8588890122:AAF870IhnaQRmo_pn8OIVj_xH6skyNwVZy0"
ADMIN_ID = 7694543415

# Ôàéëû äëÿ õðàíåíèÿ äàííûõ
CODES_FILE = "shared_codes.json"
BLOCKED_USERS_FILE = "blocked_users.json"
BOT_STATUS_FILE = "bot_status.json"

# Íàñòðîéêà ëîãèðîâàíèÿ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Çàãðóçêà äàííûõ
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

# Çàãðóçêà äàííûõ ïðè ñòàðòå (íå èñïîëüçóåòñÿ íàïðÿìóþ, äàííûå çàãðóæàþòñÿ ïðè êàæäîì îáðàùåíèè)

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

# Ãëàâíîå ìåíþ
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("?? Ïîëó÷èòü êîä")],
        [KeyboardButton("?? Ïîäåëèòüñÿ êîäîì")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Àäìèí ïàíåëü
def get_admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("?? Ïîñìîòðåòü êîäû", callback_data="admin_view_codes")],
        [InlineKeyboardButton("?? Çàáëîêèðîâàòü ïîëüçîâàòåëÿ", callback_data="admin_block_user")],
        [InlineKeyboardButton("? Ðàçáëîêèðîâàòü ïîëüçîâàòåëÿ", callback_data="admin_unblock_user")],
        [InlineKeyboardButton("?? Òåõíè÷åñêîå îáñëóæèâàíèå", callback_data="admin_maintenance")],
        [InlineKeyboardButton("? Âûêëþ÷èòü áîòà", callback_data="admin_disable_bot")],
        [InlineKeyboardButton("?? Âêëþ÷èòü áîòà", callback_data="admin_enable_bot")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Îáðàáîò÷èê êîìàíäû /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_blocked(user_id):
        await update.message.reply_text("? Âû çàáëîêèðîâàíû è íå ìîæåòå èñïîëüçîâàòü áîòà.")
        return
    
    if not is_bot_enabled():
        await update.message.reply_text("? Áîò âðåìåííî âûêëþ÷åí.")
        return
    
    if is_maintenance_mode():
        await update.message.reply_text("?? Áîò íàõîäèòñÿ íà òåõíè÷åñêîì îáñëóæèâàíèè. Ïîæàëóéñòà, ïîïðîáóéòå ïîçæå.")
        return
    
    # Ïðèâåòñòâåííûé ñìàéëèê Telegram
    welcome_text = "?? Äîáðî ïîæàëîâàòü!\n\nÂûáåðèòå äåéñòâèå:"
    
    if is_admin(user_id):
        welcome_text += "\n\n?? Äîñòóïíà àäìèí ïàíåëü: /admin"
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

# Îáðàáîò÷èê êîìàíäû /admin
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("? Ó âàñ íåò äîñòóïà ê àäìèí ïàíåëè.")
        return
    
    await update.message.reply_text(
        "?? Àäìèí ïàíåëü",
        reply_markup=get_admin_keyboard()
    )

# Îáðàáîò÷èê êíîïêè "Ïîëó÷èòü êîä"
async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    first_name = update.effective_user.first_name or "Ïîëüçîâàòåëü"
    
    if is_blocked(user_id):
        await update.message.reply_text("? Âû çàáëîêèðîâàíû è íå ìîæåòå èñïîëüçîâàòü áîòà.")
        return
    
    if not is_bot_enabled():
        await update.message.reply_text("? Áîò âðåìåííî âûêëþ÷åí.")
        return
    
    if is_maintenance_mode():
        await update.message.reply_text("?? Áîò íàõîäèòñÿ íà òåõíè÷åñêîì îáñëóæèâàíèè. Ïîæàëóéñòà, ïîïðîáóéòå ïîçæå.")
        return
    
    message_text = f"Óâàæàåìûé @{username} ({first_name}), õîòèì ñîîáùèòü âàì, ÷òî åñëè âäðóã âû ïîëó÷èòå êîä, âû äîëæíû âûñëàòü â îòâåò."
    
    keyboard = [
        [InlineKeyboardButton("? Äà", callback_data=f"code_confirm_yes_{user_id}")],
        [InlineKeyboardButton("? Íåò", callback_data=f"code_confirm_no_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

# Îáðàáîò÷èê ïîäòâåðæäåíèÿ ïîëó÷åíèÿ êîäà
async def code_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data.split("_")
    action = data[2]  # yes èëè no
    
    if action == "yes":
        # Ãåíåðèðóåì êîä (â ðåàëüíîñòè çäåñü äîëæåí áûòü çàïðîñ ê cto.new API)
        # Äëÿ ïðèìåðà èñïîëüçóåì ïðîñòîé ôîðìàò
        code = f"CTO-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        await query.edit_message_text(
            f"? Êîä óñïåøíî âûäàí!\n\n?? Âàø êîä: <code>{code}</code>\n\nÈñïîëüçóéòå åãî íà ñàéòå cto.new",
            parse_mode=ParseMode.HTML
        )
    else:
        await query.edit_message_text("? Âû îòêàçàëèñü îò ïîëó÷åíèÿ êîäà.")

# Îáðàáîò÷èê êíîïêè "Ïîäåëèòüñÿ êîäîì"
async def share_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_blocked(user_id):
        await update.message.reply_text("? Âû çàáëîêèðîâàíû è íå ìîæåòå èñïîëüçîâàòü áîòà.")
        return
    
    if not is_bot_enabled():
        await update.message.reply_text("? Áîò âðåìåííî âûêëþ÷åí.")
        return
    
    if is_maintenance_mode():
        await update.message.reply_text("?? Áîò íàõîäèòñÿ íà òåõíè÷åñêîì îáñëóæèâàíèè. Ïîæàëóéñòà, ïîïðîáóéòå ïîçæå.")
        return
    
    await update.message.reply_text(
        "?? Ïîäåëèòåñü êîäîì:\n\nÎòïðàâüòå êîä, êîòîðûì õîòèòå ïîäåëèòüñÿ ñ äðóãèìè ïîëüçîâàòåëÿìè."
    )
    context.user_data['waiting_for_code'] = True

# Îáðàáîò÷èê òåêñòîâûõ ñîîáùåíèé
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # Ïðîâåðêà àäìèíñêèõ äåéñòâèé (ïðèîðèòåò)
    if is_admin(user_id):
        admin_action = context.user_data.get('admin_action')
        if admin_action == 'block':
            try:
                target_id = int(text)
                blocked_users_list = load_json(BLOCKED_USERS_FILE, [])
                if str(target_id) not in blocked_users_list:
                    blocked_users_list.append(str(target_id))
                    save_json(BLOCKED_USERS_FILE, blocked_users_list)
                    await update.message.reply_text(
                        f"? Ïîëüçîâàòåëü {target_id} çàáëîêèðîâàí.",
                        reply_markup=get_admin_keyboard()
                    )
                else:
                    await update.message.reply_text(
                        f"?? Ïîëüçîâàòåëü {target_id} óæå çàáëîêèðîâàí.",
                        reply_markup=get_admin_keyboard()
                    )
            except ValueError:
                await update.message.reply_text(
                    "? Íåâåðíûé ôîðìàò ID. Îòïðàâüòå ÷èñëîâîé ID.",
                    reply_markup=get_admin_keyboard()
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
                        f"? Ïîëüçîâàòåëü {target_id} ðàçáëîêèðîâàí.",
                        reply_markup=get_admin_keyboard()
                    )
                else:
                    await update.message.reply_text(
                        f"?? Ïîëüçîâàòåëü {target_id} íå áûë çàáëîêèðîâàí.",
                        reply_markup=get_admin_keyboard()
                    )
            except:
                await update.message.reply_text(
                    "? Îøèáêà ïðè ðàçáëîêèðîâêå.",
                    reply_markup=get_admin_keyboard()
                )
            context.user_data['admin_action'] = None
            return
    
    if is_blocked(user_id):
        return
    
    if not is_bot_enabled() or is_maintenance_mode():
        return
    
    # Åñëè ïîëüçîâàòåëü äåëèòñÿ êîäîì
    if context.user_data.get('waiting_for_code'):
        username = update.effective_user.username or update.effective_user.first_name
        first_name = update.effective_user.first_name or "Ïîëüçîâàòåëü"
        
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
            "? Êîä óñïåøíî äîáàâëåí! Äðóãèå ïîëüçîâàòåëè ñìîãóò åãî èñïîëüçîâàòü.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Îáðàáîòêà îáû÷íûõ ñîîáùåíèé
    if text == "?? Ïîëó÷èòü êîä":
        await get_code(update, context)
    elif text == "?? Ïîäåëèòüñÿ êîäîì":
        await share_code(update, context)
    else:
        await update.message.reply_text(
            "Èñïîëüçóéòå êíîïêè äëÿ íàâèãàöèè.",
            reply_markup=get_main_keyboard()
        )

# Îáðàáîò÷èêè àäìèí ïàíåëè
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.edit_message_text("? Ó âàñ íåò äîñòóïà ê àäìèí ïàíåëè.")
        return
    
    data = query.data
    
    if data == "admin_view_codes":
        codes_list = load_json(CODES_FILE, [])
        if not codes_list:
            await query.edit_message_text(
                "?? Ñïèñîê êîäîâ ïóñò.",
                reply_markup=get_admin_keyboard()
            )
        else:
            codes_text = "?? Ïîäåëåííûå êîäû:\n\n"
            for idx, code_data in enumerate(codes_list[-20:], 1):  # Ïîñëåäíèå 20 êîäîâ
                codes_text += f"{idx}. Êîä: <code>{code_data['code']}</code>\n"
                codes_text += f"   Ïîëüçîâàòåëü: @{code_data.get('username', 'N/A')} ({code_data.get('first_name', 'N/A')})\n"
                codes_text += f"   ID: {code_data['user_id']}\n"
                codes_text += f"   Âðåìÿ: {code_data.get('timestamp', 'N/A')}\n\n"
            
            await query.edit_message_text(
                codes_text,
                parse_mode=ParseMode.HTML,
                reply_markup=get_admin_keyboard()
            )
    
    elif data == "admin_block_user":
        await query.edit_message_text(
            "?? Îòïðàâüòå ID ïîëüçîâàòåëÿ äëÿ áëîêèðîâêè:\n\nÈñïîëüçóéòå /cancel äëÿ îòìåíû.",
            reply_markup=None
        )
        context.user_data['admin_action'] = 'block'
    
    elif data == "admin_unblock_user":
        blocked_users_list = load_json(BLOCKED_USERS_FILE, [])
        if not blocked_users_list:
            await query.edit_message_text(
                "? Çàáëîêèðîâàííûõ ïîëüçîâàòåëåé íåò.",
                reply_markup=get_admin_keyboard()
            )
        else:
            blocked_text = "?? Çàáëîêèðîâàííûå ïîëüçîâàòåëè:\n\n"
            for user_id in blocked_users_list:
                blocked_text += f"ID: {user_id}\n"
            
            await query.edit_message_text(
                blocked_text + "\nÎòïðàâüòå ID ïîëüçîâàòåëÿ äëÿ ðàçáëîêèðîâêè:\n\nÈñïîëüçóéòå /cancel äëÿ îòìåíû.",
                reply_markup=None
            )
            context.user_data['admin_action'] = 'unblock'
    
    elif data == "admin_maintenance":
        bot_status_data = load_json(BOT_STATUS_FILE, {"maintenance": False, "enabled": True})
        bot_status_data["maintenance"] = not bot_status_data["maintenance"]
        save_json(BOT_STATUS_FILE, bot_status_data)
        status_text = "âêëþ÷åí" if bot_status_data["maintenance"] else "âûêëþ÷åí"
        await query.edit_message_text(
            f"?? Ðåæèì òåõíè÷åñêîãî îáñëóæèâàíèÿ {status_text}.",
            reply_markup=get_admin_keyboard()
        )
    
    elif data == "admin_disable_bot":
        bot_status_data = load_json(BOT_STATUS_FILE, {"maintenance": False, "enabled": True})
        bot_status_data["enabled"] = False
        save_json(BOT_STATUS_FILE, bot_status_data)
        await query.edit_message_text(
            "? Áîò âûêëþ÷åí.",
            reply_markup=get_admin_keyboard()
        )
    
    elif data == "admin_enable_bot":
        bot_status_data = load_json(BOT_STATUS_FILE, {"maintenance": False, "enabled": True})
        bot_status_data["enabled"] = True
        bot_status_data["maintenance"] = False
        save_json(BOT_STATUS_FILE, bot_status_data)
        await query.edit_message_text(
            "?? Áîò âêëþ÷åí.",
            reply_markup=get_admin_keyboard()
        )

# Îáðàáîò÷èê àäìèíñêèõ äåéñòâèé ÷åðåç ñîîáùåíèÿ
async def handle_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return
    
    admin_action = context.user_data.get('admin_action')
    
    if not admin_action:
        return
    
    if admin_action == 'block':
        try:
            target_id = int(update.message.text)
            if str(target_id) not in blocked_users:
                blocked_users.append(str(target_id))
                save_json(BLOCKED_USERS_FILE, blocked_users)
                await update.message.reply_text(
                    f"? Ïîëüçîâàòåëü {target_id} çàáëîêèðîâàí.",
                    reply_markup=get_admin_keyboard()
                )
            else:
                await update.message.reply_text(
                    f"?? Ïîëüçîâàòåëü {target_id} óæå çàáëîêèðîâàí.",
                    reply_markup=get_admin_keyboard()
                )
        except ValueError:
            await update.message.reply_text(
                "? Íåâåðíûé ôîðìàò ID. Îòïðàâüòå ÷èñëîâîé ID.",
                reply_markup=get_admin_keyboard()
            )
        context.user_data['admin_action'] = None
    
    elif admin_action == 'unblock':
        try:
            target_id = str(update.message.text)
            if target_id in blocked_users:
                blocked_users.remove(target_id)
                save_json(BLOCKED_USERS_FILE, blocked_users)
                await update.message.reply_text(
                    f"? Ïîëüçîâàòåëü {target_id} ðàçáëîêèðîâàí.",
                    reply_markup=get_admin_keyboard()
                )
            else:
                await update.message.reply_text(
                    f"?? Ïîëüçîâàòåëü {target_id} íå áûë çàáëîêèðîâàí.",
                    reply_markup=get_admin_keyboard()
                )
        except:
            await update.message.reply_text(
                "? Îøèáêà ïðè ðàçáëîêèðîâêå.",
                reply_markup=get_admin_keyboard()
            )
        context.user_data['admin_action'] = None

# Êîìàíäà îòìåíû
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if is_admin(user_id) and context.user_data.get('admin_action'):
        context.user_data['admin_action'] = None
        await update.message.reply_text(
            "? Äåéñòâèå îòìåíåíî.",
            reply_markup=get_admin_keyboard()
        )
    elif context.user_data.get('waiting_for_code'):
        context.user_data['waiting_for_code'] = False
        await update.message.reply_text(
            "? Îòìåíåíî.",
            reply_markup=get_main_keyboard()
        )

def main():
    # Ñîçäàíèå ïðèëîæåíèÿ
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Ðåãèñòðàöèÿ îáðàáîò÷èêîâ
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CallbackQueryHandler(code_confirm, pattern="^code_confirm_"))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    
    # Îáðàáîò÷èê ñîîáùåíèé äîëæåí áûòü ïîñëåäíèì
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Çàïóñê áîòà
    logger.info("Áîò çàïóùåí!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
