#!/bin/bash
echo "🔐 Подпись APK файла..."
echo "================================"

KEYSTORE_FILE="chrono-deck.keystore"
KEY_ALIAS="chrono-deck-key"
APK_UNSIGNED="android/app/build/outputs/apk/release/app-release-unsigned.apk"
APK_SIGNED="ChronoDeck-v1.0.0-signed.apk"

# Проверка наличия неподписанного APK
if [ ! -f "$APK_UNSIGNED" ]; then
    echo "❌ Неподписанный APK не найден. Сначала запустите сборку release версии."
    echo "Запустите: cd android && ./gradlew assembleRelease"
    exit 1
fi

# Создание keystore если его нет
if [ ! -f "$KEYSTORE_FILE" ]; then
    echo "🔑 Создание нового keystore..."
    keytool -genkey -v -keystore $KEYSTORE_FILE -alias $KEY_ALIAS \
        -keyalg RSA -keysize 2048 -validity 10000 \
        -dname "CN=ChronoDeck, OU=Game, O=ChronoDeck Team, L=City, ST=State, C=RU" \
        -storepass chronodeck123 -keypass chronodeck123
    
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка создания keystore"
        exit 1
    fi
    echo "✅ Keystore создан"
fi

# Подпись APK
echo "✍️  Подписываем APK..."
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
    -keystore $KEYSTORE_FILE -storepass chronodeck123 -keypass chronodeck123 \
    $APK_UNSIGNED $KEY_ALIAS

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при подписи APK"
    exit 1
fi

# Проверка наличия zipalign
if command -v zipalign &> /dev/null; then
    echo "📦 Выравнивание APK..."
    zipalign -v 4 $APK_UNSIGNED $APK_SIGNED
    echo "✅ APK подписан и выровнен: $APK_SIGNED"
else
    echo "⚠️  zipalign не найден, пропускаем этап выравнивания"
    cp $APK_UNSIGNED $APK_SIGNED
    echo "✅ APK подписан: $APK_SIGNED"
fi

echo "================================"
echo "🎉 Готово!"
echo "📦 Подписанный APK: $APK_SIGNED"
