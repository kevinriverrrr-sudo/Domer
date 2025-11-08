"""
Telegram Bot для проверки карт через PayPal API
Card Checker Bot
"""

import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from paypal_checker import PayPalChecker
from config import BOT_TOKEN, ADMIN_IDS

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация чекера
checker = PayPalChecker()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    welcome_text = f"""
🎴 <b>Card Checker Bot - PayPal API</b>

Привет, {user.mention_html()}!

Этот бот проверяет валидность карт через PayPal API.

<b>📋 Команды:</b>
/check - Проверить одну карту
/mass - Массовая проверка карт
/help - Помощь
/stats - Статистика

<b>📝 Формат карты:</b>
<code>4111111111111111|12|2025|123</code>
или
<code>4111111111111111|12/2025|123</code>

<b>⚡ Возможности:</b>
✅ Проверка валидности карты
✅ Определение типа карты (VISA/MC/AMEX)
✅ Массовая проверка (до 50 карт)
✅ Детальная информация о результате

<b>⚠️ Важно:</b>
Используйте бота только для легальных целей!
"""
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Проверить карту", callback_data="cmd_check"),
            InlineKeyboardButton("📦 Массовая проверка", callback_data="cmd_mass")
        ],
        [
            InlineKeyboardButton("❓ Помощь", callback_data="cmd_help"),
            InlineKeyboardButton("📊 Статистика", callback_data="cmd_stats")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='HTML',
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
<b>📖 Руководство по использованию</b>

<b>Формат данных карты:</b>
Поддерживаются следующие форматы:

1️⃣ <code>4111111111111111|12|2025|123</code>
2️⃣ <code>4111111111111111|12/2025|123</code>
3️⃣ <code>4111111111111111 12 2025 123</code>

Где:
• 4111111111111111 - номер карты
• 12 - месяц истечения (MM)
• 2025 - год истечения (YYYY)
• 123 - CVV код

<b>🔍 Одиночная проверка:</b>
Используйте команду /check, затем отправьте данные карты.
Или просто отправьте данные карты в любой момент.

<b>📦 Массовая проверка:</b>
Используйте команду /mass, затем отправьте список карт.
Каждая карта на новой строке (максимум 50 карт).

Пример:
<code>4111111111111111|12|2025|123
5555555555554444|01|2026|456
378282246310005|11/2024|1234</code>

<b>📊 Результаты проверки:</b>
✅ LIVE - Карта валидна и активна
⚠️ DECLINED - Карта валидна, но платеж отклонен
🔐 3DS - Требуется 3D Secure
❌ DEAD - Карта невалидна
❓ UNKNOWN - Неизвестный статус
⏱️ TIMEOUT - Превышено время ожидания

<b>⚙️ Технические детали:</b>
• API: PayPal REST API v2
• Проверка: через создание заказа и capture
• Лимиты: зависят от настроек PayPal аккаунта
"""
    
    await update.message.reply_text(help_text, parse_mode='HTML')


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /check"""
    await update.message.reply_text(
        "💳 <b>Проверка карты</b>\n\n"
        "Отправьте данные карты в формате:\n"
        "<code>4111111111111111|12|2025|123</code>\n\n"
        "Или:\n"
        "<code>4111111111111111|12/2025|123</code>",
        parse_mode='HTML'
    )
    context.user_data['waiting_for'] = 'single_card'


async def mass_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /mass"""
    await update.message.reply_text(
        "📦 <b>Массовая проверка карт</b>\n\n"
        "Отправьте список карт (каждая на новой строке).\n"
        "Максимум 50 карт за раз.\n\n"
        "<b>Пример:</b>\n"
        "<code>4111111111111111|12|2025|123\n"
        "5555555555554444|01|2026|456\n"
        "378282246310005|11/2024|1234</code>",
        parse_mode='HTML'
    )
    context.user_data['waiting_for'] = 'mass_cards'


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stats"""
    user_data = context.user_data
    
    total_checks = user_data.get('total_checks', 0)
    live_cards = user_data.get('live_cards', 0)
    dead_cards = user_data.get('dead_cards', 0)
    declined_cards = user_data.get('declined_cards', 0)
    
    stats_text = f"""
📊 <b>Ваша статистика</b>

🔢 Всего проверок: <code>{total_checks}</code>
✅ LIVE: <code>{live_cards}</code>
❌ DEAD: <code>{dead_cards}</code>
⚠️ DECLINED: <code>{declined_cards}</code>

💡 <i>Статистика обновляется в реальном времени</i>
"""
    
    await update.message.reply_text(stats_text, parse_mode='HTML')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    text = update.message.text.strip()
    
    # Проверяем, содержит ли сообщение данные карты
    if '|' in text or (text.count(' ') >= 3 and any(c.isdigit() for c in text)):
        # Если несколько строк - массовая проверка
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if len(lines) > 1:
            await process_mass_check(update, context, lines)
        else:
            await process_single_check(update, context, text)
    else:
        await update.message.reply_text(
            "❓ Не могу распознать формат.\n\n"
            "Используйте:\n"
            "/check - для одиночной проверки\n"
            "/mass - для массовой проверки\n"
            "/help - для помощи"
        )


async def process_single_check(update: Update, context: ContextTypes.DEFAULT_TYPE, card_line: str):
    """Обработка одиночной проверки карты"""
    # Показываем что бот работает
    processing_msg = await update.message.reply_text("🔄 Проверяю карту...")
    
    # Парсим данные карты
    card_data = checker.parse_card_line(card_line)
    
    if not card_data:
        await processing_msg.edit_text(
            "❌ <b>Ошибка парсинга</b>\n\n"
            "Неверный формат данных карты.\n\n"
            "<b>Правильный формат:</b>\n"
            "<code>4111111111111111|12|2025|123</code>",
            parse_mode='HTML'
        )
        return
    
    card_number, exp_month, exp_year, cvv = card_data
    
    # Получаем тип карты
    card_brand = checker.get_card_bin_info(card_number)
    
    # Проверяем карту
    status, message, response_data = checker.check_card(
        card_number, exp_month, exp_year, cvv
    )
    
    # Обновляем статистику
    update_user_stats(context.user_data, status)
    
    # Маскируем номер карты
    masked_card = f"{card_number[:4]}••••••{card_number[-4:]}"
    
    # Формируем результат
    result_text = f"""
🎴 <b>Результат проверки</b>

💳 Карта: <code>{masked_card}</code>
🏦 Тип: <b>{card_brand}</b>
📅 Срок: <code>{exp_month}/{exp_year}</code>
🔐 CVV: <code>{'•' * len(cvv)}</code>

━━━━━━━━━━━━━━━━
<b>Статус:</b> {status}
<b>Результат:</b> {message}
━━━━━━━━━━━━━━━━

⏱️ Время проверки: PayPal API
"""
    
    # Добавляем дополнительную информацию если есть
    if response_data.get('payment_source', {}).get('card'):
        card_info = response_data['payment_source']['card']
        if 'last_digits' in card_info:
            result_text += f"\n🔢 Последние цифры (API): {card_info['last_digits']}"
    
    await processing_msg.edit_text(result_text, parse_mode='HTML')


async def process_mass_check(update: Update, context: ContextTypes.DEFAULT_TYPE, lines: list):
    """Обработка массовой проверки карт"""
    # Ограничение на количество карт
    max_cards = 50
    if len(lines) > max_cards:
        await update.message.reply_text(
            f"⚠️ Слишком много карт!\n\n"
            f"Максимум {max_cards} карт за раз.\n"
            f"Вы отправили: {len(lines)}"
        )
        return
    
    processing_msg = await update.message.reply_text(
        f"🔄 Начинаю массовую проверку...\n"
        f"📦 Карт в очереди: {len(lines)}"
    )
    
    results = []
    live_count = 0
    dead_count = 0
    declined_count = 0
    error_count = 0
    
    for idx, line in enumerate(lines, 1):
        # Обновляем статус каждые 5 карт
        if idx % 5 == 0:
            await processing_msg.edit_text(
                f"🔄 Проверяю карты...\n"
                f"📊 Прогресс: {idx}/{len(lines)}\n"
                f"✅ LIVE: {live_count} | ❌ DEAD: {dead_count}"
            )
        
        # Парсим карту
        card_data = checker.parse_card_line(line)
        
        if not card_data:
            error_count += 1
            results.append(f"{idx}. ❌ Ошибка парсинга: {line[:20]}...")
            continue
        
        card_number, exp_month, exp_year, cvv = card_data
        card_brand = checker.get_card_bin_info(card_number)
        masked_card = f"{card_number[:4]}••••{card_number[-4:]}"
        
        # Проверяем карту
        status, message, _ = checker.check_card(
            card_number, exp_month, exp_year, cvv
        )
        
        # Обновляем статистику
        update_user_stats(context.user_data, status)
        
        # Подсчет результатов
        if "LIVE" in status:
            live_count += 1
        elif "DEAD" in status or "ERROR" in status:
            dead_count += 1
        elif "DECLINED" in status:
            declined_count += 1
        
        # Сохраняем результат
        results.append(
            f"{idx}. {status} | {card_brand} {masked_card} | {exp_month}/{exp_year}"
        )
        
        # Небольшая задержка чтобы не перегружать API
        await asyncio.sleep(1)
    
    # Формируем итоговый отчет
    report = f"""
📦 <b>Массовая проверка завершена</b>

📊 <b>Статистика:</b>
━━━━━━━━━━━━━━━━
🔢 Всего карт: {len(lines)}
✅ LIVE: {live_count}
❌ DEAD: {dead_count}
⚠️ DECLINED: {declined_count}
🚫 Ошибки: {error_count}
━━━━━━━━━━━━━━━━

<b>Результаты:</b>
"""
    
    # Добавляем результаты (ограничение на длину сообщения)
    results_text = "\n".join(results[:30])  # Первые 30 результатов
    
    if len(results) > 30:
        report += f"\n{results_text}\n\n<i>... и еще {len(results) - 30} карт</i>"
    else:
        report += f"\n{results_text}"
    
    # Если сообщение слишком длинное, отправляем файлом
    if len(report) > 4000:
        # Отправляем краткую статистику
        summary = f"""
📦 <b>Массовая проверка завершена</b>

📊 Статистика:
🔢 Всего: {len(lines)}
✅ LIVE: {live_count}
❌ DEAD: {dead_count}
⚠️ DECLINED: {declined_count}
🚫 Ошибки: {error_count}

📄 Полный отчет отправлен файлом
"""
        await processing_msg.edit_text(summary, parse_mode='HTML')
        
        # Отправляем полный отчет файлом
        full_report = "\n".join(results)
        await update.message.reply_document(
            document=full_report.encode('utf-8'),
            filename="check_results.txt",
            caption="📄 Полные результаты проверки"
        )
    else:
        await processing_msg.edit_text(report, parse_mode='HTML')


def update_user_stats(user_data: dict, status: str):
    """Обновление статистики пользователя"""
    user_data['total_checks'] = user_data.get('total_checks', 0) + 1
    
    if "LIVE" in status:
        user_data['live_cards'] = user_data.get('live_cards', 0) + 1
    elif "DEAD" in status or "ERROR" in status:
        user_data['dead_cards'] = user_data.get('dead_cards', 0) + 1
    elif "DECLINED" in status:
        user_data['declined_cards'] = user_data.get('declined_cards', 0) + 1


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cmd_check":
        await query.message.reply_text(
            "💳 <b>Проверка карты</b>\n\n"
            "Отправьте данные карты в формате:\n"
            "<code>4111111111111111|12|2025|123</code>",
            parse_mode='HTML'
        )
    
    elif query.data == "cmd_mass":
        await query.message.reply_text(
            "📦 <b>Массовая проверка</b>\n\n"
            "Отправьте список карт (каждая на новой строке).\n"
            "Максимум 50 карт за раз.",
            parse_mode='HTML'
        )
    
    elif query.data == "cmd_help":
        await help_command(update, context)
    
    elif query.data == "cmd_stats":
        user_data = context.user_data
        total_checks = user_data.get('total_checks', 0)
        live_cards = user_data.get('live_cards', 0)
        dead_cards = user_data.get('dead_cards', 0)
        declined_cards = user_data.get('declined_cards', 0)
        
        stats_text = f"""
📊 <b>Ваша статистика</b>

🔢 Всего проверок: <code>{total_checks}</code>
✅ LIVE: <code>{live_cards}</code>
❌ DEAD: <code>{dead_cards}</code>
⚠️ DECLINED: <code>{declined_cards}</code>
"""
        await query.message.reply_text(stats_text, parse_mode='HTML')


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Запуск бота"""
    print("🚀 Запуск Card Checker Bot...")
    print(f"📱 Bot Token: {BOT_TOKEN[:20]}...")
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("mass", mass_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("✅ Бот запущен и готов к работе!")
    print("⏳ Ожидание сообщений...")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
