[app]

# Название приложения
title = SAMP Arizona RP Admin Tools

# Имя пакета
package.name = sampadmintools

# Домен приложения
package.domain = org.samp

# Версия
version = 2.0

# Организация
org.name = SAMP Arizona RP

# Исходный код
source.dir = .

# Исходный файл
source.include_exts = py,png,jpg,kv,atlas,json

# Главный файл
main = admin_tools_android.py

# Иконка (нужно создать icon.png размером 512x512)
# icon.filename = icon.png

# Разрешения Android
android.permissions = INTERNET

# Требования Android
android.api = 27
android.minapi = 21

# Ориентация
orientation = portrait

# Полноэкранный режим
fullscreen = 0

# Включить Kivy и зависимости
requirements = python3,kivy,pyperclip

# Разрешить армеби
android.archs = armeabi-v7a,arm64-v8a,x86,x86_64

# Логирование
log_level = 2

# Оптимизация
# android.ndk = 21
# android.sdk = 30
