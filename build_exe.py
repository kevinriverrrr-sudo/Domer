#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для компиляции Admin Tools в EXE файл
"""

import subprocess
import sys
import os

def build_exe():
    """Компиляция программы в EXE"""
    print("Начинаю компиляцию Admin Tools...")
    
    # Команда для PyInstaller
    cmd = [
        'pyinstaller',
        '--onefile',  # Один файл
        '--windowed',  # Без консоли
        '--name=SAMP_Arizona_RP_Admin_Tools',  # Имя exe файла
        '--icon=NONE',  # Без иконки (можно добавить .ico файл)
        '--add-data=config.json;.' if os.path.exists('config.json') else '',
        'admin_tools.py'
    ]
    
    # Удаляем пустые элементы
    cmd = [c for c in cmd if c]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✓ Компиляция завершена успешно!")
        print("EXE файл находится в папке 'dist'")
        print("Имя файла: SAMP_Arizona_RP_Admin_Tools.exe")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Ошибка компиляции: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n✗ PyInstaller не найден!")
        print("Установите его командой: pip install pyinstaller")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
