# -*- coding: utf-8 -*-
"""
Скрипт для создания и запуска копии бота
Использование: python3 create_copy.py <TOKEN>
"""
import sys
import os
import json
import glob

if len(sys.argv) < 2:
    print("Использование: python3 create_copy.py <TOKEN>")
    sys.exit(1)

NEW_TOKEN = sys.argv[1]

# Ищем файл с информацией об оригинале
copy_info_files = glob.glob(f"copy_info_{NEW_TOKEN.replace(':', '_')}.json")

if not copy_info_files:
    print(f"? Файл с информацией об оригинале не найден для токена {NEW_TOKEN}")
    print("Сначала создайте копию через админ панель бота.")
    sys.exit(1)

# Читаем информацию об оригинале
with open(copy_info_files[0], 'r', encoding='utf-8') as f:
    original_info = json.load(f)

# Читаем основной файл бота
with open('bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Заменяем токен
content = content.replace(
    'BOT_TOKEN = "8588890122:AAF870IhnaQRmo_pn8OIVj_xH6skyNwVZy0"',
    f'BOT_TOKEN = "{NEW_TOKEN}"'
)

# Заменяем путь к файлу информации об оригинале
content = content.replace(
    'ORIGINAL_BOT_INFO_FILE = "original_bot_info.json"',
    f'ORIGINAL_BOT_INFO_FILE = "{copy_info_files[0]}"'
)

# Сохраняем измененный файл
copy_bot_file = f'bot_copy_{NEW_TOKEN.split(":")[0]}.py'
with open(copy_bot_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"? Копия бота создана: {copy_bot_file}")
print(f"?? Оригинальный бот: @{original_info.get('original_username', 'N/A')}")
print(f"?? Создатель: @{original_info.get('creator_username', 'N/A')}")
print(f"\n?? Запуск: python3 {copy_bot_file}")
