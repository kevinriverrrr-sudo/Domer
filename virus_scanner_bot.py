#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram бот для проверки файлов и ссылок на вирусы через VirusTotal API
"""

import os
import time
import hashlib
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
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
MAX_FILE_SIZE = 600 * 1024 * 1024  # 600 MB


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
    
    def get_file_analysis(self, file_id: str) -> dict:
        """Получает результаты анализа файла по ID"""
        try:
            response = requests.get(
                f"{VIRUSTOTAL_API_URL}/analyses/{file_id}",
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


def format_file_results(data: dict) -> str:
    """Форматирует результаты проверки файла для вывода"""
    if "error" in data:
        return f"❌ Ошибка: {data['error']}"
    
    if "data" not in data:
        return "❌ Не удалось получить данные анализа"
    
    data_obj = data["data"]
    
    # Проверяем статус анализа
    status = data_obj.get("attributes", {}).get("status", "unknown")
    
    if status == "completed":
        stats = data_obj.get("attributes", {}).get("stats", {})
        results = data_obj.get("attributes", {}).get("results", {})
        
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        undetected = stats.get("undetected", 0)
        harmless = stats.get("harmless", 0)
        total = malicious + suspicious + undetected + harmless
        
        # Формируем сообщение
        message = "🔍 **РЕЗУЛЬТАТЫ ПРОВЕРКИ ФАЙЛА**\n\n"
        
        # Статистика
        message += "📊 **Статистика:**\n"
        message += f"✅ Безопасно: {harmless}\n"
        message += f"⚠️ Подозрительно: {suspicious}\n"
        message += f"❌ Вредоносно: {malicious}\n"
        message += f"➖ Не обнаружено: {undetected}\n"
        message += f"📈 Всего проверок: {total}\n\n"
        
        # Определяем общий статус
        if malicious > 0:
            message += "🚨 **СТАТУС: ОПАСНО!**\n\n"
        elif suspicious > 0:
            message += "⚠️ **СТАТУС: ПОДОЗРИТЕЛЬНО**\n\n"
        else:
            message += "✅ **СТАТУС: БЕЗОПАСНО**\n\n"
        
        # Детальные результаты от антивирусов
        if results:
            message += "🛡️ **Детальные результаты антивирусов:**\n\n"
            
            # Сортируем результаты: сначала вредоносные, потом подозрительные
            sorted_results = sorted(
                results.items(),
                key=lambda x: (
                    0 if x[1].get("category") == "malicious" else
                    1 if x[1].get("category") == "suspicious" else 2,
                    x[0]
                )
            )
            
            for engine_name, result in sorted_results[:30]:  # Показываем первые 30
                category = result.get("category", "unknown")
                method = result.get("method", "")
                
                if category == "malicious":
                    message += f"❌ **{engine_name}**: ВРЕДОНОСНО"
                    if method:
                        message += f" ({method})"
                    message += "\n"
                elif category == "suspicious":
                    message += f"⚠️ **{engine_name}**: Подозрительно"
                    if method:
                        message += f" ({method})"
                    message += "\n"
                elif category == "harmless":
                    message += f"✅ **{engine_name}**: Безопасно\n"
            
            if len(results) > 30:
                message += f"\n... и еще {len(results) - 30} антивирусов\n"
        
        # Информация о файле
        file_info = data_obj.get("attributes", {}).get("meaningful_name", "")
        if file_info:
            message += f"\n📄 **Файл**: {file_info}\n"
        
        sha256 = data_obj.get("attributes", {}).get("sha256", "")
        if sha256:
            message += f"🔐 **SHA256**: `{sha256[:16]}...`\n"
        
        return message
    else:
        return f"⏳ Анализ еще выполняется. Статус: {status}"


def format_url_results(data: dict) -> str:
    """Форматирует результаты проверки URL для вывода"""
    if "error" in data:
        return f"❌ Ошибка: {data['error']}"
    
    if "data" not in data:
        return "❌ Не удалось получить данные анализа"
    
    data_obj = data["data"]
    
    # Проверяем статус анализа
    status = data_obj.get("attributes", {}).get("status", "unknown")
    
    if status == "completed":
        stats = data_obj.get("attributes", {}).get("stats", {})
        results = data_obj.get("attributes", {}).get("results", {})
        
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        undetected = stats.get("undetected", 0)
        harmless = stats.get("harmless", 0)
        total = malicious + suspicious + undetected + harmless
        
        # Формируем сообщение
        message = "🔍 **РЕЗУЛЬТАТЫ ПРОВЕРКИ ССЫЛКИ**\n\n"
        
        # Статистика
        message += "📊 **Статистика:**\n"
        message += f"✅ Безопасно: {harmless}\n"
        message += f"⚠️ Подозрительно: {suspicious}\n"
        message += f"❌ Вредоносно: {malicious}\n"
        message += f"➖ Не обнаружено: {undetected}\n"
        message += f"📈 Всего проверок: {total}\n\n"
        
        # Определяем общий статус
        if malicious > 0:
            message += "🚨 **СТАТУС: ОПАСНО!**\n\n"
        elif suspicious > 0:
            message += "⚠️ **СТАТУС: ПОДОЗРИТЕЛЬНО**\n\n"
        else:
            message += "✅ **СТАТУС: БЕЗОПАСНО**\n\n"
        
        # Детальные результаты от антивирусов
        if results:
            message += "🛡️ **Детальные результаты антивирусов:**\n\n"
            
            # Сортируем результаты: сначала вредоносные, потом подозрительные
            sorted_results = sorted(
                results.items(),
                key=lambda x: (
                    0 if x[1].get("category") == "malicious" else
                    1 if x[1].get("category") == "suspicious" else 2,
                    x[0]
                )
            )
            
            for engine_name, result in sorted_results[:30]:  # Показываем первые 30
                category = result.get("category", "unknown")
                method = result.get("method", "")
                
                if category == "malicious":
                    message += f"❌ **{engine_name}**: ВРЕДОНОСНО"
                    if method:
                        message += f" ({method})"
                    message += "\n"
                elif category == "suspicious":
                    message += f"⚠️ **{engine_name}**: Подозрительно"
                    if method:
                        message += f" ({method})"
                    message += "\n"
                elif category == "harmless":
                    message += f"✅ **{engine_name}**: Безопасно\n"
            
            if len(results) > 30:
                message += f"\n... и еще {len(results) - 30} антивирусов\n"
        
        # Информация о ссылке
        url = data_obj.get("attributes", {}).get("url", "")
        if url:
            message += f"\n🔗 **Ссылка**: {url}\n"
        
        return message
    else:
        return f"⏳ Анализ еще выполняется. Статус: {status}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    welcome_message = """
🤖 **Добро пожаловать в Virus Scanner Bot!**

Я помогу вам проверить файлы и ссылки на вирусы через VirusTotal.

**Как использовать:**
📎 Отправьте мне файл для проверки
🔗 Отправьте ссылку (URL) для проверки

**Команды:**
/start - Показать это сообщение
/help - Справка

Бот использует более 70 антивирусов для максимально точной проверки!
"""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = """
📖 **Справка по использованию бота:**

**Проверка файлов:**
1. Отправьте файл боту (до 600 МБ)
2. Бот загрузит файл в VirusTotal
3. Дождитесь результатов анализа
4. Получите детальный отчет от всех антивирусов

**Проверка ссылок:**
1. Отправьте ссылку боту (начинается с http:// или https://)
2. Бот просканирует ссылку через VirusTotal
3. Дождитесь результатов анализа
4. Получите детальный отчет от всех антивирусов

**Статусы:**
✅ Безопасно - файл/ссылка не содержит угроз
⚠️ Подозрительно - некоторые антивирусы обнаружили подозрительную активность
❌ Вредоносно - файл/ссылка содержит вредоносный код

Бот проверяет через все доступные антивирусы в VirusTotal!
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик загрузки файлов"""
    # Проверяем различные типы файлов
    file = None
    file_name = None
    
    if update.message.document:
        # Документы (APK, ZIP, EXE и т.д.)
        file = update.message.document
        file_name = file.file_name
    elif update.message.video:
        # Видео файлы
        file = update.message.video
        file_name = file.file_name or "video.mp4"
    elif update.message.audio:
        # Аудио файлы
        file = update.message.audio
        file_name = file.file_name or "audio.mp3"
    elif update.message.voice:
        # Голосовые сообщения
        file = update.message.voice
        file_name = "voice.ogg"
    elif update.message.video_note:
        # Кружочки (видео заметки)
        file = update.message.video_note
        file_name = "video_note.mp4"
    elif update.message.animation:
        # GIF и анимации
        file = update.message.animation
        file_name = file.file_name or "animation.gif"
    elif update.message.photo:
        # Фотографии (берем самое большое качество)
        file = update.message.photo[-1]
        file_name = "photo.jpg"
    
    if not file:
        await update.message.reply_text(
            "❌ Не удалось получить файл.\n\n"
            "Пожалуйста, отправьте файл как документ (APK, ZIP, EXE и другие форматы поддерживаются)."
        )
        return
    
    # Проверяем размер файла
    if file.file_size and file.file_size > MAX_FILE_SIZE:
        await update.message.reply_text(
            f"❌ Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024*1024)} МБ"
        )
        return
    
    # Отправляем сообщение о начале проверки
    status_msg = await update.message.reply_text("⏳ Загружаю файл и начинаю проверку...")
    
    try:
        # Скачиваем файл
        file_obj = await context.bot.get_file(file.file_id)
        # Используем имя файла если есть, иначе генерируем по file_id
        safe_file_name = file_name or f"file_{file.file_id}"
        # Убираем небезопасные символы из имени файла
        safe_file_name = "".join(c for c in safe_file_name if c.isalnum() or c in "._-")
        file_path = f"/tmp/{file.file_id}_{safe_file_name}"
        await file_obj.download_to_drive(file_path)
        
        # Инициализируем сканер
        scanner = VirusTotalScanner(VIRUSTOTAL_API_KEY)
        
        # Загружаем файл в VirusTotal
        await status_msg.edit_text("📤 Загружаю файл в VirusTotal...")
        upload_result = scanner.upload_file(file_path)
        
        if "error" in upload_result:
            await status_msg.edit_text(f"❌ Ошибка при загрузке файла: {upload_result['error']}")
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
                    results_text = format_file_results(analysis_result)
                    await status_msg.edit_text(results_text, parse_mode='Markdown')
                    os.remove(file_path)
                    return
                elif status == "queued":
                    await status_msg.edit_text(f"⏳ Файл в очереди на анализ... (попытка {attempt + 1}/{max_attempts})")
                else:
                    await status_msg.edit_text(f"⏳ Анализ выполняется... Статус: {status}")
        
        # Если анализ не завершился, пытаемся получить отчет по хешу
        await status_msg.edit_text("⏳ Анализ занимает больше времени. Пытаюсь получить отчет по хешу файла...")
        
        # Вычисляем SHA256 файла
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        file_hash = sha256_hash.hexdigest()
        
        # Получаем отчет по хешу
        report_result = scanner.get_file_report(file_hash)
        if "error" not in report_result:
            results_text = format_file_results(report_result)
            await status_msg.edit_text(results_text, parse_mode='Markdown')
        else:
            await status_msg.edit_text(
                "⏳ Анализ еще выполняется. Пожалуйста, попробуйте проверить файл позже через несколько минут."
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
    
    # Проверяем, что это URL
    if not (text.startswith("http://") or text.startswith("https://")):
        await update.message.reply_text("❌ Пожалуйста, отправьте корректную ссылку (начинается с http:// или https://)")
        return
    
    # Отправляем сообщение о начале проверки
    status_msg = await update.message.reply_text("⏳ Начинаю проверку ссылки...")
    
    try:
        # Инициализируем сканер
        scanner = VirusTotalScanner(VIRUSTOTAL_API_KEY)
        
        # Сканируем URL
        await status_msg.edit_text("📤 Отправляю ссылку в VirusTotal для анализа...")
        scan_result = scanner.scan_url(text)
        
        if "error" in scan_result:
            await status_msg.edit_text(f"❌ Ошибка при сканировании ссылки: {scan_result['error']}")
            return
        
        analysis_id = scan_result.get("data", {}).get("id")
        if not analysis_id:
            await status_msg.edit_text("❌ Не удалось получить ID анализа")
            return
        
        # Ждем завершения анализа
        await status_msg.edit_text("🔍 Анализирую ссылку через все антивирусы... Это может занять несколько секунд.")
        
        max_attempts = 30
        for attempt in range(max_attempts):
            time.sleep(2)
            analysis_result = scanner.get_url_analysis(analysis_id)
            
            if "error" not in analysis_result:
                status = analysis_result.get("data", {}).get("attributes", {}).get("status", "")
                if status == "completed":
                    # Форматируем и отправляем результаты
                    results_text = format_url_results(analysis_result)
                    await status_msg.edit_text(results_text, parse_mode='Markdown')
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
    
    # Проверяем, является ли сообщение URL
    if text.startswith("http://") or text.startswith("https://"):
        await handle_url(update, context)
    else:
        await update.message.reply_text(
            "❓ Не понял ваше сообщение.\n\n"
            "Отправьте мне:\n"
            "📎 Файл для проверки\n"
            "🔗 Ссылку (URL) для проверки\n\n"
            "Используйте /help для справки."
        )


def main() -> None:
    """Основная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Регистрируем обработчики (важен порядок!)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Обработчики файлов (все типы)
    # Используем комбинированный фильтр для всех типов медиа
    file_filter = (
        filters.Document.ALL |
        filters.VIDEO |
        filters.AUDIO |
        filters.VOICE |
        filters.VIDEO_NOTE |
        filters.ANIMATION |
        filters.PHOTO |
        filters.Document.ALL
    )
    application.add_handler(MessageHandler(file_filter, handle_file))
    
    # Обработчик текстовых сообщений (должен быть последним)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logger.info("Бот запущен и готов к работе!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
