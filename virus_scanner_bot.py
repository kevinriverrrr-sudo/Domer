#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram бот для проверки файлов и ссылок на вирусы через VirusTotal API
С красивым интерфейсом и интерактивными кнопками
"""

import os
import time
import hashlib
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы
VIRUSTOTAL_API_KEY = "b3c6edf1e32e42feebebd9d485205b3f748e36cf1be71e1c6c9c5bda181c6af6"
TELEGRAM_BOT_TOKEN = "7560458678:AAHbtiK7z0QiII5Iz3fzo17cReOaDS-2tBU"
VIRUSTOTAL_API_URL = "https://www.virustotal.com/api/v3"
MAX_FILE_SIZE = 32 * 1024 * 1024  # 32 MB (лимит VirusTotal)


class VirusTotalScanner:
    """Класс для работы с VirusTotal API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-apikey": api_key
        }
    
    def upload_file(self, file_path: str) -> dict:
        """Загружает файл в VirusTotal для анализа"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{VIRUSTOTAL_API_URL}/files",
                    headers=self.headers,
                    files=files
                )
                return response.json()
        except Exception as e:
            logger.error(f"Ошибка при загрузке файла: {e}")
            return {"error": str(e)}
    
    def get_file_analysis(self, analysis_id: str) -> dict:
        """Получает результаты анализа файла по ID"""
        try:
            response = requests.get(
                f"{VIRUSTOTAL_API_URL}/analyses/{analysis_id}",
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка при получении анализа файла: {e}")
            return {"error": str(e)}
    
    def get_file_report(self, file_hash: str) -> dict:
        """Получает отчет о файле по хешу"""
        try:
            response = requests.get(
                f"{VIRUSTOTAL_API_URL}/files/{file_hash}",
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка при получении отчета о файле: {e}")
            return {"error": str(e)}
    
    def scan_url(self, url: str) -> dict:
        """Сканирует URL через VirusTotal"""
        try:
            data = {"url": url}
            response = requests.post(
                f"{VIRUSTOTAL_API_URL}/urls",
                headers=self.headers,
                data=data
            )
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка при сканировании URL: {e}")
            return {"error": str(e)}
    
    def get_url_analysis(self, analysis_id: str) -> dict:
        """Получает результаты анализа URL"""
        try:
            response = requests.get(
                f"{VIRUSTOTAL_API_URL}/analyses/{analysis_id}",
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка при получении анализа URL: {e}")
            return {"error": str(e)}


def format_file_results_summary(data: dict) -> tuple:
    """Форматирует краткую сводку результатов проверки файла"""
    if "error" in data:
        return f"❌ Ошибка: {data['error']}", None, None
    
    if "data" not in data:
        return "❌ Не удалось получить данные анализа", None, None
    
    data_obj = data["data"]
    attributes = data_obj.get("attributes", {})
    
    status = attributes.get("status", None)
    
    if status is None or status == "completed":
        stats = attributes.get("stats", {}) or attributes.get("last_analysis_stats", {})
        results = attributes.get("results", {}) or attributes.get("last_analysis_results", {})
        
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        undetected = stats.get("undetected", 0)
        harmless = stats.get("harmless", 0)
        total = malicious + suspicious + undetected + harmless
        
        # Формируем сообщение
        message = "🔍 *РЕЗУЛЬТАТЫ ПРОВЕРКИ ФАЙЛА*\n\n"
        
        # Статистика с эмодзи
        if malicious > 0:
            message += "🚨 *СТАТУС: ОПАСНО!*\n\n"
        elif suspicious > 0:
            message += "⚠️ *СТАТУС: ПОДОЗРИТЕЛЬНО*\n\n"
        else:
            message += "✅ *СТАТУС: БЕЗОПАСНО*\n\n"
        
        message += "📊 *Статистика:*\n"
        message += f"✅ Безопасно: `{harmless}`\n"
        message += f"⚠️ Подозрительно: `{suspicious}`\n"
        message += f"❌ Вредоносно: `{malicious}`\n"
        message += f"➖ Не обнаружено: `{undetected}`\n"
        message += f"📈 Всего проверок: `{total}`\n\n"
        
        # Информация о файле
        file_info = attributes.get("meaningful_name", "") or (attributes.get("names", [""])[0] if attributes.get("names") else "")
        sha256 = attributes.get("sha256", "")
        
        if file_info:
            message += f"📄 *Файл:* `{file_info}`\n"
        if sha256:
            message += f"🔐 *SHA256:* `{sha256[:32]}...`\n"
        
        # Создаем кнопки для детального просмотра
        keyboard = []
        
        if malicious > 0:
            keyboard.append([InlineKeyboardButton("🚨 Вредоносные обнаружения", callback_data=f"file_malicious_{sha256[:16]}")])
        if suspicious > 0:
            keyboard.append([InlineKeyboardButton("⚠️ Подозрительные обнаружения", callback_data=f"file_suspicious_{sha256[:16]}")])
        if harmless > 0:
            keyboard.append([InlineKeyboardButton("✅ Безопасные результаты", callback_data=f"file_harmless_{sha256[:16]}")])
        
        keyboard.append([InlineKeyboardButton("📋 Все результаты", callback_data=f"file_all_{sha256[:16]}")])
        keyboard.append([InlineKeyboardButton("🔗 Открыть в VirusTotal", url=f"https://www.virustotal.com/gui/file/{sha256}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        return message, reply_markup, results
    else:
        return f"⏳ Анализ еще выполняется. Статус: {status}", None, None


def format_detailed_results(results: dict, filter_type: str = "all") -> str:
    """Форматирует детальные результаты по типу"""
    if not results:
        return "❌ Результаты не найдены"
    
    message = ""
    
    if filter_type == "malicious":
        message = "🚨 *ВРЕДОНОСНЫЕ ОБНАРУЖЕНИЯ:*\n\n"
        filtered = {k: v for k, v in results.items() if v.get("category") == "malicious"}
    elif filter_type == "suspicious":
        message = "⚠️ *ПОДОЗРИТЕЛЬНЫЕ ОБНАРУЖЕНИЯ:*\n\n"
        filtered = {k: v for k, v in results.items() if v.get("category") == "suspicious"}
    elif filter_type == "harmless":
        message = "✅ *БЕЗОПАСНЫЕ РЕЗУЛЬТАТЫ:*\n\n"
        filtered = {k: v for k, v in results.items() if v.get("category") == "harmless"}
    else:
        message = "📋 *ВСЕ РЕЗУЛЬТАТЫ АНТИВИРУСОВ:*\n\n"
        filtered = results
    
    # Сортируем результаты
    sorted_results = sorted(
        filtered.items(),
        key=lambda x: (
            0 if x[1].get("category") == "malicious" else
            1 if x[1].get("category") == "suspicious" else 2,
            x[0]
        )
    )
    
    for engine_name, result in sorted_results:
        category = result.get("category", "unknown")
        method = result.get("method", "")
        result_text = result.get("result", "")
        
        if category == "malicious":
            message += f"❌ *{engine_name}*\n"
            if result_text:
                message += f"   🦠 Угроза: `{result_text}`\n"
            if method:
                message += f"   🔧 Метод: `{method}`\n"
            message += "\n"
        elif category == "suspicious":
            message += f"⚠️ *{engine_name}*\n"
            if result_text:
                message += f"   ⚠️ Результат: `{result_text}`\n"
            if method:
                message += f"   🔧 Метод: `{method}`\n"
            message += "\n"
        elif category == "harmless":
            message += f"✅ *{engine_name}*\n"
            if result_text:
                message += f"   ✓ Результат: `{result_text}`\n"
            message += "\n"
    
    if not sorted_results:
        message += "Нет результатов для отображения"
    
    return message


def format_url_results_summary(data: dict) -> tuple:
    """Форматирует краткую сводку результатов проверки URL"""
    if "error" in data:
        return f"❌ Ошибка: {data['error']}", None, None
    
    if "data" not in data:
        return "❌ Не удалось получить данные анализа", None, None
    
    data_obj = data["data"]
    attributes = data_obj.get("attributes", {})
    
    status = attributes.get("status", "unknown")
    
    if status == "completed":
        stats = attributes.get("stats", {})
        results = attributes.get("results", {})
        
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        undetected = stats.get("undetected", 0)
        harmless = stats.get("harmless", 0)
        total = malicious + suspicious + undetected + harmless
        
        message = "🔍 *РЕЗУЛЬТАТЫ ПРОВЕРКИ ССЫЛКИ*\n\n"
        
        if malicious > 0:
            message += "🚨 *СТАТУС: ОПАСНО!*\n\n"
        elif suspicious > 0:
            message += "⚠️ *СТАТУС: ПОДОЗРИТЕЛЬНО*\n\n"
        else:
            message += "✅ *СТАТУС: БЕЗОПАСНО*\n\n"
        
        message += "📊 *Статистика:*\n"
        message += f"✅ Безопасно: `{harmless}`\n"
        message += f"⚠️ Подозрительно: `{suspicious}`\n"
        message += f"❌ Вредоносно: `{malicious}`\n"
        message += f"➖ Не обнаружено: `{undetected}`\n"
        message += f"📈 Всего проверок: `{total}`\n\n"
        
        url = attributes.get("url", "")
        url_id = attributes.get("url_id", "")
        
        if url:
            message += f"🔗 *Ссылка:* `{url}`\n"
        
        keyboard = []
        
        if malicious > 0:
            keyboard.append([InlineKeyboardButton("🚨 Вредоносные обнаружения", callback_data=f"url_malicious_{url_id[:16]}")])
        if suspicious > 0:
            keyboard.append([InlineKeyboardButton("⚠️ Подозрительные обнаружения", callback_data=f"url_suspicious_{url_id[:16]}")])
        if harmless > 0:
            keyboard.append([InlineKeyboardButton("✅ Безопасные результаты", callback_data=f"url_harmless_{url_id[:16]}")])
        
        keyboard.append([InlineKeyboardButton("📋 Все результаты", callback_data=f"url_all_{url_id[:16]}")])
        if url_id:
            keyboard.append([InlineKeyboardButton("🔗 Открыть в VirusTotal", url=f"https://www.virustotal.com/gui/url/{url_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        return message, reply_markup, results
    else:
        return f"⏳ Анализ еще выполняется. Статус: {status}", None, None


# Хранилище результатов (в продакшене лучше использовать БД)
results_cache = {}  # {key: results_dict}
summary_cache = {}  # {key: (message_text, reply_markup)}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("📎 Проверить файл", callback_data="help_file")],
        [InlineKeyboardButton("🔗 Проверить ссылку", callback_data="help_url")],
        [InlineKeyboardButton("ℹ️ Справка", callback_data="help_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = """
🤖 *Добро пожаловать в Virus Scanner Bot!*

Я помогу вам проверить файлы и ссылки на вирусы через VirusTotal.

*Возможности:*
✅ Проверка файлов (до 32 МБ)
✅ Проверка ссылок (URL)
✅ Детальные результаты от всех антивирусов
✅ Интерактивное меню для просмотра результатов

*Выберите действие:*
"""
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    keyboard = [
        [InlineKeyboardButton("📎 Проверить файл", callback_data="help_file")],
        [InlineKeyboardButton("🔗 Проверить ссылку", callback_data="help_url")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    help_text = """
📖 *Справка по использованию бота:*

*Проверка файлов:*
1️⃣ Отправьте файл боту (до 32 МБ)
2️⃣ Бот загрузит файл в VirusTotal
3️⃣ Дождитесь результатов анализа
4️⃣ Используйте кнопки для просмотра деталей

*Проверка ссылок:*
1️⃣ Отправьте ссылку боту (http:// или https://)
2️⃣ Бот просканирует ссылку через VirusTotal
3️⃣ Дождитесь результатов анализа
4️⃣ Используйте кнопки для просмотра деталей

*Статусы:*
✅ Безопасно - файл/ссылка не содержит угроз
⚠️ Подозрительно - некоторые антивирусы обнаружили подозрительную активность
❌ Вредоносно - файл/ссылка содержит вредоносный код

Бот проверяет через все доступные антивирусы в VirusTotal!
"""
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("📎 Проверить файл", callback_data="help_file")],
            [InlineKeyboardButton("🔗 Проверить ссылку", callback_data="help_url")],
            [InlineKeyboardButton("ℹ️ Справка", callback_data="help_info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🏠 *Главное меню*\n\nВыберите действие:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return
    
    if data == "help_file":
        await query.edit_message_text(
            "📎 *Проверка файла*\n\nОтправьте файл боту (до 32 МБ). Поддерживаются все форматы: APK, ZIP, EXE и другие.",
            parse_mode='Markdown'
        )
        return
    
    if data == "help_url":
        await query.edit_message_text(
            "🔗 *Проверка ссылки*\n\nОтправьте ссылку боту (начинается с http:// или https://).",
            parse_mode='Markdown'
        )
        return
    
    if data == "help_info":
        help_text = """
📖 *Справка по использованию бота:*

*Проверка файлов:*
1️⃣ Отправьте файл боту (до 32 МБ)
2️⃣ Бот загрузит файл в VirusTotal
3️⃣ Дождитесь результатов анализа
4️⃣ Используйте кнопки для просмотра деталей

*Проверка ссылок:*
1️⃣ Отправьте ссылку боту (http:// или https://)
2️⃣ Бот просканирует ссылку через VirusTotal
3️⃣ Дождитесь результатов анализа
4️⃣ Используйте кнопки для просмотра деталей

*Статусы:*
✅ Безопасно - файл/ссылка не содержит угроз
⚠️ Подозрительно - некоторые антивирусы обнаружили подозрительную активность
❌ Вредоносно - файл/ссылка содержит вредоносный код
"""
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
        return
    
    # Обработка возврата к сводке
    if data.startswith("file_summary_"):
        file_hash_prefix = data.replace("file_summary_", "")
        cache_key = f"file_{file_hash_prefix}"
        
        if cache_key in summary_cache:
            message_text, reply_markup = summary_cache[cache_key]
            await query.edit_message_text(message_text, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await query.answer("Сводка не найдена. Пожалуйста, проверьте файл снова.", show_alert=True)
        return
    
    if data.startswith("url_summary_"):
        url_id_prefix = data.replace("url_summary_", "")
        cache_key = f"url_{url_id_prefix}"
        
        if cache_key in summary_cache:
            message_text, reply_markup = summary_cache[cache_key]
            await query.edit_message_text(message_text, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await query.answer("Сводка не найдена. Пожалуйста, проверьте ссылку снова.", show_alert=True)
        return
    
    # Обработка детальных результатов
    if data.startswith("file_"):
        parts = data.split("_")
        if len(parts) >= 3:
            filter_type = parts[1]  # malicious, suspicious, harmless, all
            file_hash_prefix = parts[2]
            cache_key = f"file_{file_hash_prefix}"
            
            # Ищем результаты в кэше
            results = results_cache.get(cache_key)
            
            if results:
                detailed = format_detailed_results(results, filter_type)
                
                keyboard = [
                    [InlineKeyboardButton("🔙 К сводке", callback_data=f"file_summary_{file_hash_prefix}")],
                    [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    detailed,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await query.answer("Результаты не найдены. Пожалуйста, проверьте файл снова.", show_alert=True)
    
    elif data.startswith("url_"):
        parts = data.split("_")
        if len(parts) >= 3:
            filter_type = parts[1]
            url_id_prefix = parts[2]
            cache_key = f"url_{url_id_prefix}"
            
            results = results_cache.get(cache_key)
            
            if results:
                detailed = format_detailed_results(results, filter_type)
                
                keyboard = [
                    [InlineKeyboardButton("🔙 К сводке", callback_data=f"url_summary_{url_id_prefix}")],
                    [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    detailed,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await query.answer("Результаты не найдены. Пожалуйста, проверьте ссылку снова.", show_alert=True)


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик загрузки файлов"""
    file = None
    file_name = None
    
    if update.message.document:
        file = update.message.document
        file_name = file.file_name
    elif update.message.video:
        file = update.message.video
        file_name = file.file_name or "video.mp4"
    elif update.message.audio:
        file = update.message.audio
        file_name = file.file_name or "audio.mp3"
    elif update.message.voice:
        file = update.message.voice
        file_name = "voice.ogg"
    elif update.message.video_note:
        file = update.message.video_note
        file_name = "video_note.mp4"
    elif update.message.animation:
        file = update.message.animation
        file_name = file.file_name or "animation.gif"
    elif update.message.photo:
        file = update.message.photo[-1]
        file_name = "photo.jpg"
    
    if not file:
        keyboard = [[InlineKeyboardButton("ℹ️ Справка", callback_data="help_info")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ Не удалось получить файл.\n\nПожалуйста, отправьте файл как документ (APK, ZIP, EXE и другие форматы поддерживаются).",
            reply_markup=reply_markup
        )
        return
    
    # Проверяем размер файла
    if file.file_size and file.file_size > MAX_FILE_SIZE:
        await update.message.reply_text(
            f"❌ Файл слишком большой.\n\nМаксимальный размер: {MAX_FILE_SIZE // (1024*1024)} МБ\n\n"
            f"Размер вашего файла: {file.file_size // (1024*1024)} МБ"
        )
        return
    
    # Отправляем сообщение о начале проверки
    status_msg = await update.message.reply_text("⏳ Загружаю файл и начинаю проверку...")
    
    try:
        # Скачиваем файл
        file_obj = await context.bot.get_file(file.file_id)
        safe_file_name = file_name or f"file_{file.file_id}"
        safe_file_name = "".join(c for c in safe_file_name if c.isalnum() or c in "._-")
        file_path = f"/tmp/{file.file_id}_{safe_file_name}"
        await file_obj.download_to_drive(file_path)
        
        # Инициализируем сканер
        scanner = VirusTotalScanner(VIRUSTOTAL_API_KEY)
        
        # Загружаем файл в VirusTotal
        await status_msg.edit_text("📤 Загружаю файл в VirusTotal...")
        upload_result = scanner.upload_file(file_path)
        
        if "error" in upload_result:
            error_msg = str(upload_result.get("error", "")).lower()
            if "too big" in error_msg or "file is too big" in error_msg:
                await status_msg.edit_text(
                    f"❌ Файл слишком большой для загрузки.\n\n"
                    f"Максимальный размер: {MAX_FILE_SIZE // (1024*1024)} МБ"
                )
            else:
                await status_msg.edit_text(f"❌ Ошибка при загрузке файла: {upload_result.get('error', 'Неизвестная ошибка')}")
            os.remove(file_path)
            return
        
        analysis_id = upload_result.get("data", {}).get("id")
        if not analysis_id:
            await status_msg.edit_text("❌ Не удалось получить ID анализа")
            os.remove(file_path)
            return
        
        # Ждем завершения анализа
        await status_msg.edit_text("🔍 Анализирую файл через все антивирусы... Это может занять несколько секунд.")
        
        max_attempts = 30
        for attempt in range(max_attempts):
            time.sleep(2)
            analysis_result = scanner.get_file_analysis(analysis_id)
            
            if "error" not in analysis_result:
                status = analysis_result.get("data", {}).get("attributes", {}).get("status", "")
                if status == "completed":
                    # Форматируем и отправляем результаты
                    results_text, reply_markup, results = format_file_results_summary(analysis_result)
                    
                    # Сохраняем результаты в кэш
                    sha256 = analysis_result.get("data", {}).get("attributes", {}).get("sha256", "")
                    if sha256 and results:
                        cache_key = f"file_{sha256[:16]}"
                        results_cache[cache_key] = results
                        summary_cache[cache_key] = (results_text, reply_markup)
                    
                    await status_msg.edit_text(results_text, parse_mode='Markdown', reply_markup=reply_markup)
                    os.remove(file_path)
                    return
                elif status == "queued":
                    await status_msg.edit_text(f"⏳ Файл в очереди на анализ... (попытка {attempt + 1}/{max_attempts})")
                else:
                    await status_msg.edit_text(f"⏳ Анализ выполняется... Статус: {status}")
        
        await status_msg.edit_text(
            "⏳ Анализ занимает больше времени. Пожалуйста, попробуйте проверить файл позже через несколько минут."
        )
        os.remove(file_path)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {e}")
        await status_msg.edit_text(f"❌ Произошла ошибка: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик проверки URL"""
    text = update.message.text.strip()
    
    if not (text.startswith("http://") or text.startswith("https://")):
        keyboard = [[InlineKeyboardButton("ℹ️ Справка", callback_data="help_info")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте корректную ссылку (начинается с http:// или https://)",
            reply_markup=reply_markup
        )
        return
    
    status_msg = await update.message.reply_text("⏳ Начинаю проверку ссылки...")
    
    try:
        scanner = VirusTotalScanner(VIRUSTOTAL_API_KEY)
        
        await status_msg.edit_text("📤 Отправляю ссылку в VirusTotal для анализа...")
        scan_result = scanner.scan_url(text)
        
        if "error" in scan_result:
            await status_msg.edit_text(f"❌ Ошибка при сканировании ссылки: {scan_result.get('error', 'Неизвестная ошибка')}")
            return
        
        analysis_id = scan_result.get("data", {}).get("id")
        if not analysis_id:
            await status_msg.edit_text("❌ Не удалось получить ID анализа")
            return
        
        await status_msg.edit_text("🔍 Анализирую ссылку через все антивирусы... Это может занять несколько секунд.")
        
        max_attempts = 30
        for attempt in range(max_attempts):
            time.sleep(2)
            analysis_result = scanner.get_url_analysis(analysis_id)
            
            if "error" not in analysis_result:
                status = analysis_result.get("data", {}).get("attributes", {}).get("status", "")
                if status == "completed":
                    results_text, reply_markup, results = format_url_results_summary(analysis_result)
                    
                    # Сохраняем результаты в кэш
                    url_id = analysis_result.get("data", {}).get("attributes", {}).get("url_id", "")
                    if url_id and results:
                        cache_key = f"url_{url_id[:16]}"
                        results_cache[cache_key] = results
                        summary_cache[cache_key] = (results_text, reply_markup)
                    
                    await status_msg.edit_text(results_text, parse_mode='Markdown', reply_markup=reply_markup)
                    return
                elif status == "queued":
                    await status_msg.edit_text(f"⏳ Ссылка в очереди на анализ... (попытка {attempt + 1}/{max_attempts})")
                else:
                    await status_msg.edit_text(f"⏳ Анализ выполняется... Статус: {status}")
        
        await status_msg.edit_text(
            "⏳ Анализ еще выполняется. Пожалуйста, попробуйте проверить ссылку позже через несколько минут."
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке URL: {e}")
        await status_msg.edit_text(f"❌ Произошла ошибка: {str(e)}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    text = update.message.text.strip()
    
    if text.startswith("http://") or text.startswith("https://"):
        await handle_url(update, context)
    else:
        keyboard = [
            [InlineKeyboardButton("📎 Проверить файл", callback_data="help_file")],
            [InlineKeyboardButton("🔗 Проверить ссылку", callback_data="help_url")],
            [InlineKeyboardButton("ℹ️ Справка", callback_data="help_info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❓ Не понял ваше сообщение.\n\nОтправьте мне:\n📎 Файл для проверки\n🔗 Ссылку (URL) для проверки",
            reply_markup=reply_markup
        )


def main() -> None:
    """Основная функция запуска бота"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Обработчики файлов
    file_filter = (
        filters.Document.ALL |
        filters.VIDEO |
        filters.AUDIO |
        filters.VOICE |
        filters.VIDEO_NOTE |
        filters.ANIMATION |
        filters.PHOTO
    )
    application.add_handler(MessageHandler(file_filter, handle_file))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запущен и готов к работе!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
