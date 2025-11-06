# Telegram Manga Downloader Bot

Бот для скачивания манги из Telegram.

## Использование

1. Отправьте боту команду `/start` для начала работы
2. Отправьте URL страницы с мангой
3. Бот скачает все изображения и отправит их в виде ZIP архива

## Команды

- `/start` - Начать работу с ботом
- `/help` - Показать справку

## Запуск

```bash
export BOT_TOKEN="your_bot_token"
python3 app/main.py
```

Или через Docker:

```bash
docker build -t manga-bot .
docker run -e BOT_TOKEN="your_bot_token" manga-bot
```
