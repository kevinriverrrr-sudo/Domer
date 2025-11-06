import os
import io
import asyncio
import logging
import traceback
import aiohttp
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.types import BufferedInputFile, FSInputFile
from aiogram.exceptions import TelegramRetryAfter
from aiogram.filters import Command

if not os.environ.get("BOT_TOKEN"):
    raise Exception('provide BOT_TOKEN in env')

logging.basicConfig(
    format='%(levelname)s: %(name)s[%(process)d] - %(asctime)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT = Bot(os.environ.get("BOT_TOKEN"))
DP = Dispatcher()
router = Router()

# Парсер манги
async def download_manga_chapter(url: str) -> tuple[str, bytes]:
    """Скачивает главу манги и возвращает (имя_файла, zip_данные)"""
    import zipfile
    from bs4 import BeautifulSoup
    import re
    
    async with aiohttp.ClientSession() as session:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                # Ищем изображения манги
                images = []
                
                # Попытка найти изображения в различных форматах
                # Вариант 1: прямые ссылки на изображения в img тегах
                img_tags = soup.find_all('img')
                for img in img_tags:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if src:
                        # Преобразуем относительные URL в абсолютные
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            from urllib.parse import urljoin
                            src = urljoin(url, src)
                        elif not src.startswith('http'):
                            from urllib.parse import urljoin
                            src = urljoin(url, src)
                        
                        # Фильтруем только изображения манги (обычно jpg, png, webp)
                        if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                            if 'manga' in src.lower() or 'chapter' in src.lower() or 'page' in src.lower() or 'img' in src.lower():
                                images.append(src)
                
                # Вариант 2: поиск в JavaScript данных
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        # Ищем массивы изображений в JS
                        matches = re.findall(r'["\']([^"\']*\.(?:jpg|jpeg|png|webp|gif)[^"\']*)["\']', script.string, re.IGNORECASE)
                        for match in matches:
                            if any(keyword in match.lower() for keyword in ['manga', 'chapter', 'page', 'img']):
                                if match.startswith('//'):
                                    match = 'https:' + match
                                elif match.startswith('/'):
                                    from urllib.parse import urljoin
                                    match = urljoin(url, match)
                                elif not match.startswith('http'):
                                    from urllib.parse import urljoin
                                    match = urljoin(url, match)
                                if match not in images:
                                    images.append(match)
                
                # Если не нашли изображения, пробуем скачать страницу как есть
                if not images:
                    # Создаем ZIP с HTML страницей
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        zip_file.writestr("page.html", html.encode('utf-8'))
                        zip_file.writestr("readme.txt", f"Manga page downloaded from: {url}\n\nThis is a basic downloader. For full functionality, add a specific parser for your manga source.")
                    zip_buffer.seek(0)
                    filename = "manga_page.zip"
                    return filename, zip_buffer.read()
                
                # Скачиваем изображения
                zip_buffer = io.BytesIO()
                downloaded_count = 0
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for i, img_url in enumerate(images[:50], 1):  # Ограничиваем до 50 изображений
                        try:
                            async with session.get(img_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as img_response:
                                if img_response.status == 200:
                                    img_data = await img_response.read()
                                    if len(img_data) > 1000:  # Проверяем, что это реальное изображение
                                        ext = '.jpg'
                                        if '.png' in img_url.lower():
                                            ext = '.png'
                                        elif '.webp' in img_url.lower():
                                            ext = '.webp'
                                        elif '.gif' in img_url.lower():
                                            ext = '.gif'
                                        
                                        zip_file.writestr(f"{i:03d}{ext}", img_data)
                                        downloaded_count += 1
                        except Exception as e:
                            logger.warning(f"Failed to download image {img_url}: {e}")
                            continue
                
                if downloaded_count == 0:
                    raise Exception("Не удалось скачать изображения манги")
                
                zip_buffer.seek(0)
                filename = f"manga_chapter_{downloaded_count}_pages.zip"
                return filename, zip_buffer.read()
                
        except Exception as e:
            logger.error(f"Error downloading manga: {e}")
            raise

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(
        "Привет! Я бот для скачивания манги.\n\n"
        "Отправь мне URL манги или используй команду /help для справки."
    )

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    await message.answer(
        "📚 <b>Бот для скачивания манги</b>\n\n"
        "Отправь мне URL манги, и я скачаю её для тебя.\n\n"
        "Примеры:\n"
        "• Отправь ссылку на главу манги\n"
        "• Бот скачает все страницы и отправит ZIP архив\n\n"
        "Команды:\n"
        "/start - Начать работу\n"
        "/help - Показать эту справку",
        parse_mode="HTML"
    )

@router.message(F.text & F.text.startswith("http"))
async def handle_url(message: types.Message):
    """Обработчик URL манги"""
    url = message.text.strip()
    
    # Отправляем сообщение о начале загрузки
    status_msg = await message.answer("⏳ Начинаю скачивание манги...")
    
    try:
        filename, zip_data = await download_manga_chapter(url)
        
        # Отправляем ZIP файл
        document = BufferedInputFile(zip_data, filename)
        await BOT.send_document(
            chat_id=message.chat.id,
            document=document,
            caption=f"📦 Манга скачана\nURL: {url}",
            request_timeout=600
        )
        
        # Удаляем сообщение о статусе
        await status_msg.delete()
        
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await handle_url(message)
    except Exception as e:
        logger.error(f"Error processing manga URL: {e}")
        traceback.print_exc()
        await status_msg.edit_text(f"❌ Ошибка при скачивании манги: {str(e)}")

@router.message()
async def handle_other(message: types.Message):
    """Обработчик прочих сообщений"""
    await message.answer(
        "Пожалуйста, отправь мне URL манги для скачивания.\n"
        "Используй /help для справки."
    )

async def main() -> None:
    DP.include_router(router)
    await DP.start_polling(BOT, polling_timeout=5, handle_signals=False)

if __name__ == "__main__":
    asyncio.run(main())
