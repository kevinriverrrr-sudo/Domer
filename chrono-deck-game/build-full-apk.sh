#!/bin/bash
set -e

echo "🚀 Полная сборка APK с компиляцией"
echo "===================================="

BUILD_DIR="apk-full"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR/{src/com/chronodeck/game,bin,res/{values,layout},assets/www,gen/com/chronodeck/game}

# Копируем веб-файлы
echo "📋 Копирование игровых файлов..."
cp -r www/* $BUILD_DIR/assets/www/

cd $BUILD_DIR

# Создаем ресурсы
echo "🎨 Создание ресурсов..."
cat > res/values/strings.xml << 'XMLEOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">ХроноКолода</string>
</resources>
XMLEOF

cat > res/layout/activity_main.xml << 'XMLEOF'
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">
    <WebView
        android:id="@+id/webview"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
</LinearLayout>
XMLEOF

# Создаем AndroidManifest
cat > AndroidManifest.xml << 'XMLEOF'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.chronodeck.game"
    android:versionCode="1"
    android:versionName="1.0.0">
    
    <uses-sdk android:minSdkVersion="22" android:targetSdkVersion="29" />
    <uses-permission android:name="android.permission.INTERNET" />
    
    <application
        android:label="@string/app_name"
        android:allowBackup="true"
        android:theme="@android:style/Theme.NoTitleBar.Fullscreen">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
XMLEOF

# Создаем Java класс
cat > src/com/chronodeck/game/MainActivity.java << 'JAVAEOF'
package com.chronodeck.game;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebSettings;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        WebView webView = new WebView(this);
        setContentView(webView);
        
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        
        webView.setWebViewClient(new WebViewClient());
        webView.loadUrl("file:///android_asset/www/index.html");
    }
}
JAVAEOF

# Поиск android.jar
ANDROID_JAR=""
for path in \
    "/usr/share/google-android-platform-29/android.jar" \
    "/usr/share/java/android-23.jar" \
    "/usr/share/java/android.jar" \
    "/usr/lib/android-sdk/platforms/android-29/android.jar" \
    "/usr/share/android-23/android.jar"; do
    if [ -f "$path" ]; then
        ANDROID_JAR="$path"
        echo "✅ Найден android.jar: $path"
        break
    fi
done

if [ -z "$ANDROID_JAR" ]; then
    echo "❌ android.jar не найден!"
    echo "📝 Установите: sudo apt-get install google-android-platform-29-installer"
    echo ""
    echo "💡 АЛЬТЕРНАТИВА: Используйте онлайн-конвертер для создания APK:"
    echo "   → https://appsgeyser.com"
    echo "   → https://app.webintoapp.com"
    exit 1
fi

# Генерируем R.java
echo "🔧 Генерация R.java..."
aapt package -f -m -J gen -M AndroidManifest.xml -S res -I "$ANDROID_JAR"

# Компилируем Java
echo "☕ Компиляция Java..."
mkdir -p bin/classes
javac -source 1.8 -target 1.8 -d bin/classes -classpath "$ANDROID_JAR" -sourcepath src:gen \
    src/com/chronodeck/game/MainActivity.java \
    gen/com/chronodeck/game/R.java

# Создаем DEX
echo "📦 Создание classes.dex..."
DX="/usr/lib/android-sdk/build-tools/debian/dx"
$DX --dex --output=bin/classes.dex bin/classes

# Создаем базовый APK с assets
echo "🔨 Создание базового APK..."
aapt package -f -M AndroidManifest.xml -S res -A assets -I "$ANDROID_JAR" -F bin/app-unaligned.apk

# Добавляем DEX
echo "📦 Добавление DEX..."
cd bin
aapt add app-unaligned.apk classes.dex
cd ..

# Выравнивание
echo "📏 Выравнивание APK..."
zipalign -f -v 4 bin/app-unaligned.apk bin/app-aligned.apk

# Подпись
echo "✍️  Подпись APK..."
DEBUG_KEYSTORE="$HOME/.android/debug.keystore"
if [ ! -f "$DEBUG_KEYSTORE" ]; then
    mkdir -p "$HOME/.android"
    keytool -genkey -v -keystore "$DEBUG_KEYSTORE" \
        -storepass android -alias androiddebugkey \
        -keypass android -keyalg RSA -keysize 2048 -validity 10000 \
        -dname "CN=Android Debug,O=Android,C=US" 2>/dev/null
fi

apksigner sign --ks "$DEBUG_KEYSTORE" \
    --ks-key-alias androiddebugkey \
    --ks-pass pass:android \
    --key-pass pass:android \
    --out ../ChronoDeck-Fixed.apk bin/app-aligned.apk

cd ..

if [ -f "ChronoDeck-Fixed.apk" ]; then
    echo ""
    echo "=========================================="
    echo "✅ APK УСПЕШНО СОЗДАН!"
    echo "=========================================="
    echo ""
    echo "📦 Файл: ChronoDeck-Fixed.apk"
    echo "📊 Размер: $(du -h ChronoDeck-Fixed.apk | cut -f1)"
    echo ""
    echo "📱 Установка:"
    echo "   adb install ChronoDeck-Fixed.apk"
    echo ""
    echo "   Или скопируйте на Android и установите вручную"
    echo ""
    # Проверка APK
    echo "🔍 Проверка APK..."
    aapt dump badging ChronoDeck-Fixed.apk | head -5
else
    echo "❌ Ошибка создания APK"
    exit 1
fi
