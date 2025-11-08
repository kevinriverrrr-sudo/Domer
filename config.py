"""
Конфигурация бота
"""

# Telegram Bot Token
BOT_TOKEN = "7560458678:AAHbtiK7z0QiII5Iz3fzo17cReOaDS-2tBU"

# PayPal API Credentials
# ВАЖНО: Замените на свои реальные credentials от PayPal
PAYPAL_CLIENT_ID = "your_paypal_client_id_here"
PAYPAL_SECRET = "your_paypal_secret_here"

# PayPal API URLs
# Для тестирования используйте sandbox
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"  # sandbox
# PAYPAL_API_BASE = "https://api-m.paypal.com"  # production

# Настройки проверки
CHECK_AMOUNT = "1.00"  # Сумма для проверки карты в USD
CURRENCY_CODE = "USD"

# Администраторы бота (Telegram User IDs)
ADMIN_IDS = []  # Добавьте ID администраторов, например: [123456789, 987654321]
