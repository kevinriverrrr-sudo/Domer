#!/bin/bash
echo "🔧 Создание APK вручную для ХроноКолода"
echo "=========================================="

# Проверяем наличие необходимых инструментов
if ! command -v java &> /dev/null; then
    echo "❌ Java не установлена"
    exit 1
fi

echo "✅ Java найдена: $(java -version 2>&1 | head -1)"

# Создаем минимальный APK используя подход с WebView
echo ""
echo "📦 Создание структуры APK..."

APK_DIR="apk-build"
rm -rf $APK_DIR
mkdir -p $APK_DIR/{assets/www,res/{layout,values,drawable},META-INF,lib}

# Копируем web контент
echo "📋 Копирование файлов игры..."
cp -r www/* $APK_DIR/assets/www/

# Создаем resources
cat > $APK_DIR/res/values/strings.xml << 'XMLEOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">ХроноКолода</string>
</resources>
XMLEOF

# Создаем манифест
cat > $APK_DIR/AndroidManifest.xml << 'XMLEOF'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.chronodeck.game"
    android:versionCode="1"
    android:versionName="1.0.0">
    <uses-sdk android:minSdkVersion="22" android:targetSdkVersion="33"/>
    <uses-permission android:name="android.permission.INTERNET"/>
    <application android:label="@string/app_name" android:allowBackup="true">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
XMLEOF

echo "✅ Структура создана"

# Инструкции для финальной сборки
cat > $APK_DIR/BUILD_INSTRUCTIONS.txt << 'INSTEOF'
================================
ИНСТРУКЦИИ ПО СБОРКЕ APK
================================

Этот каталог содержит все необходимые файлы для создания APK.

СПОСОБ 1 - Используйте Android Studio (РЕКОМЕНДУЕТСЯ):
1. Откройте Android Studio
2. File → New → Import Project
3. Выберите папку '../android/'
4. Подождите синхронизации Gradle
5. Build → Build Bundle(s) / APK(s) → Build APK(s)
6. APK будет в: android/app/build/outputs/apk/

СПОСОБ 2 - Используйте онлайн-конвертеры:
Самый простой способ! Создайте ZIP из папки assets/www/

1. AppsGeyser (https://appsgeyser.com):
   - Выберите "Website to App"
   - Загрузите файлы или укажите URL
   - Скачайте APK

2. WebIntoApp (https://app.webintoapp.com):
   - Загрузите ZIP с веб-файлами
   - Настройте параметры
   - Получите APK

СПОСОБ 3 - Командная строка (требуется Android SDK):

# Если у вас установлен Android SDK:
export ANDROID_HOME=/path/to/android/sdk
export PATH=$PATH:$ANDROID_HOME/build-tools/33.0.0

# Компиляция ресурсов
aapt2 compile --dir res -o compiled.zip
aapt2 link compiled.zip --manifest AndroidManifest.xml \
  -o unaligned.apk -I $ANDROID_HOME/platforms/android-33/android.jar

# Добавление assets
cd assets && zip -r ../unaligned.apk * && cd ..

# Выравнивание
zipalign -v 4 unaligned.apk app-unsigned.apk

# Подпись (debug)
apksigner sign --ks ~/.android/debug.keystore \
  --ks-pass pass:android app-unsigned.apk

СПОСОБ 4 - Используйте готовые скрипты проекта:
../build.sh - автоматическая сборка через Gradle

================================
INSTEOF

echo "✅ APK структура готова в папке: $APK_DIR/"
echo ""
echo "📖 Читайте BUILD_INSTRUCTIONS.txt для детальных инструкций"
echo ""
echo "🚀 БЫСТРЫЙ СПОСОБ:"
echo "   1. Откройте папку 'build/' в браузере"
echo "   2. Играйте в index.html прямо сейчас!"
echo ""
echo "📱 ДЛЯ ANDROID APK:"
echo "   → Используйте Android Studio (папка 'android/')"
echo "   → Или онлайн-конвертер (загрузите ChronoDeck-WebGame-v1.0.0.zip)"
echo ""
echo "=========================================="
