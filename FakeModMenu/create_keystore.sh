#!/bin/bash

# Script to create keystore for APK signing

echo "=========================================="
echo "   Создание keystore для подписи APK"
echo "=========================================="
echo ""

# Check if keytool is available
if ! command -v keytool &> /dev/null; then
    echo "ERROR: keytool не найден! Установите JDK."
    exit 1
fi

# Keystore details
KEYSTORE_FILE="keystore.jks"
KEY_ALIAS="modmenu"
VALIDITY=10000

echo "Будет создан keystore с параметрами:"
echo "  Файл: $KEYSTORE_FILE"
echo "  Алиас: $KEY_ALIAS"
echo "  Срок действия: $VALIDITY дней"
echo ""

# Generate keystore
keytool -genkeypair \
    -v \
    -keystore "$KEYSTORE_FILE" \
    -alias "$KEY_ALIAS" \
    -keyalg RSA \
    -keysize 2048 \
    -validity $VALIDITY

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Keystore успешно создан!"
    echo ""
    echo "Теперь создайте файл keystore.properties с содержимым:"
    echo "----------------------------------------"
    echo "storePassword=ваш_пароль_хранилища"
    echo "keyPassword=ваш_пароль_ключа"
    echo "keyAlias=$KEY_ALIAS"
    echo "storeFile=$KEYSTORE_FILE"
    echo "----------------------------------------"
else
    echo ""
    echo "✗ Ошибка при создании keystore"
    exit 1
fi
