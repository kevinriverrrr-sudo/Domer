#!/bin/bash
# Создание простой иконки приложения используя ImageMagick
# Если ImageMagick не установлен, создаем placeholder иконку

ICON_DIR="android/app/src/main/res"

# Создаем SVG иконку
cat > icon.svg << 'SVGEOF'
<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="80" fill="url(#grad1)"/>
  <text x="256" y="320" font-size="200" text-anchor="middle" fill="white">⏳</text>
</svg>
SVGEOF

echo "✅ Иконка создана (SVG)"

# Если есть ImageMagick или convert, конвертируем в PNG
if command -v convert &> /dev/null; then
    echo "📐 Создание PNG иконок разных размеров..."
    convert -background none icon.svg -resize 48x48 $ICON_DIR/mipmap-mdpi/ic_launcher.png
    convert -background none icon.svg -resize 72x72 $ICON_DIR/mipmap-hdpi/ic_launcher.png
    convert -background none icon.svg -resize 96x96 $ICON_DIR/mipmap-xhdpi/ic_launcher.png
    convert -background none icon.svg -resize 144x144 $ICON_DIR/mipmap-xxhdpi/ic_launcher.png
    convert -background none icon.svg -resize 192x192 $ICON_DIR/mipmap-xxxhdpi/ic_launcher.png
    echo "✅ PNG иконки созданы"
else
    echo "⚠️  ImageMagick не найден, используем placeholder иконки"
    # Создаем пустые файлы для placeholder
    touch $ICON_DIR/mipmap-mdpi/ic_launcher.png
    touch $ICON_DIR/mipmap-hdpi/ic_launcher.png
    touch $ICON_DIR/mipmap-xhdpi/ic_launcher.png
    touch $ICON_DIR/mipmap-xxhdpi/ic_launcher.png
    touch $ICON_DIR/mipmap-xxxhdpi/ic_launcher.png
fi
