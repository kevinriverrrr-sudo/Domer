#!/bin/bash
set -e

echo "🔧 Создание правильного APK с компиляцией Java кода"
echo "===================================================="

BUILD_DIR="apk-proper"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR/{src,bin,res/{values,layout,drawable},assets/www,gen}

# Копируем веб-файлы
echo "📋 Копирование игровых файлов..."
cp -r www/* $BUILD_DIR/assets/www/

# Создаем ресурсы
echo "🎨 Создание ресурсов..."
cat > $BUILD_DIR/res/values/strings.xml << 'XMLEOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">ХроноКолода</string>
</resources>
XMLEOF

cat > $BUILD_DIR/res/layout/activity_main.xml << 'XMLEOF'
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

# Создаем Java исходник
echo "💻 Создание Java класса..."
mkdir -p $BUILD_DIR/src/com/chronodeck/game
cat > $BUILD_DIR/src/com/chronodeck/game/MainActivity.java << 'JAVAEOF'
package com.chronodeck.game;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebSettings;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        webView = (WebView) findViewById(R.id.webview);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        
        webView.setWebViewClient(new WebViewClient());
        webView.loadUrl("file:///android_asset/www/index.html");
    }
    
    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
JAVAEOF

# Создаем AndroidManifest
cat > $BUILD_DIR/AndroidManifest.xml << 'XMLEOF'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.chronodeck.game"
    android:versionCode="1"
    android:versionName="1.0.0">
    
    <uses-sdk android:minSdkVersion="22" android:targetSdkVersion="33" />
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

cd $BUILD_DIR

# Поиск Android SDK
ANDROID_JAR=""
for path in \
    "/usr/lib/android-sdk/platforms/android-33/android.jar" \
    "/usr/lib/android-sdk/platforms/android-29/android.jar" \
    "/usr/lib/android-sdk/platforms/android-28/android.jar" \
    "$ANDROID_HOME/platforms/android-33/android.jar" \
    "$ANDROID_HOME/platforms/android-29/android.jar"; do
    if [ -f "$path" ]; then
        ANDROID_JAR="$path"
        echo "✅ Найден Android JAR: $path"
        break
    fi
done

if [ -z "$ANDROID_JAR" ]; then
    echo "⚠️  Android SDK не найден, создаем упрощенный APK..."
    cd ..
    ./build-webview-apk.sh
    exit 0
fi

# Компилируем ресурсы
echo "🔨 Компиляция ресурсов..."
aapt package -f -m -J gen -M AndroidManifest.xml -S res -I "$ANDROID_JAR"

# Компилируем Java код
echo "☕ Компиляция Java кода..."
mkdir -p bin/classes
javac -d bin/classes -classpath "$ANDROID_JAR" -sourcepath src src/com/chronodeck/game/*.java gen/com/chronodeck/game/R.java

# Создаем DEX файл
echo "📦 Создание DEX файла..."
if command -v dx &> /dev/null; then
    dx --dex --output=bin/classes.dex bin/classes
else
    # Используем d8 если dx недоступен
    if command -v d8 &> /dev/null; then
        d8 --output bin/ bin/classes/com/chronodeck/game/*.class
        mv bin/classes.dex bin/classes.dex 2>/dev/null || true
    else
        echo "❌ Не найден dx или d8 для создания DEX файла"
        echo "📝 Устанавливаем android-sdk-build-tools-common..."
        cd ..
        ./build-webview-apk.sh
        exit 0
    fi
fi

# Собираем APK
echo "📦 Сборка APK..."
aapt package -f -M AndroidManifest.xml -S res -I "$ANDROID_JAR" -F bin/app-unsigned.apk

# Добавляем DEX и assets
cd bin
if [ -f "classes.dex" ]; then
    aapt add app-unsigned.apk classes.dex
fi
cd ..
aapt add bin/app-unsigned.apk -A assets

# Выравнивание
echo "📏 Выравнивание APK..."
zipalign -f 4 bin/app-unsigned.apk bin/app-aligned.apk

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
    echo "✅ APK успешно создан!"
    echo "📦 Файл: ChronoDeck-Fixed.apk"
    echo "📊 Размер: $(du -h ChronoDeck-Fixed.apk | cut -f1)"
    echo ""
    echo "Установка: adb install ChronoDeck-Fixed.apk"
else
    echo "❌ Ошибка создания APK"
    exit 1
fi
