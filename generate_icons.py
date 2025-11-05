#!/usr/bin/env python3
"""
Скрипт для генерации иконок расширения из SVG
Требует: pip install cairosvg pillow
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    def create_icon(size, filename):
        """Создает простую иконку с градиентом"""
        img = Image.new('RGB', (size, size), color='white')
        draw = ImageDraw.Draw(img)
        
        # Градиентный фон
        for i in range(size):
            r = int(102 + (118 - 102) * i / size)
            g = int(126 + (75 - 126) * i / size)
            b = int(234 + (162 - 234) * i / size)
            draw.rectangle([(0, i), (size, i+1)], fill=(r, g, b))
        
        # Белая буква F
        try:
            font_size = int(size * 0.6)
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        text = "F"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size - text_width) // 2, (size - text_height) // 2 - bbox[1])
        
        draw.text(position, text, fill='white', font=font)
        
        # Сохраняем
        img.save(filename, 'PNG')
        print(f"Создана иконка: {filename} ({size}x{size})")
    
    # Создаем папку icons если её нет
    os.makedirs('icons', exist_ok=True)
    
    # Генерируем иконки разных размеров
    create_icon(16, 'icons/icon16.png')
    create_icon(48, 'icons/icon48.png')
    create_icon(128, 'icons/icon128.png')
    
    print("\nИконки успешно созданы!")
    
except ImportError:
    print("Установите зависимости: pip install pillow")
    print("Или создайте иконки вручную из icon.svg")
