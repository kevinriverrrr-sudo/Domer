#!/usr/bin/env python3
"""
Простой скрипт для создания EXE через PyInstaller
Можно запустить на Windows для создания EXE
"""
import subprocess
import sys
import os

def create_exe():
    print("Создание EXE файла...")
    
    # Команда PyInstaller
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=SAMP_Arizona_RP_Admin_Tools',
        '--noconsole',
        '--clean',
        'admin_tools.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ EXE файл создан в папке dist/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    except FileNotFoundError:
        print("\n❌ PyInstaller не найден!")
        print("Установите: pip install pyinstaller")
        return False

if __name__ == "__main__":
    create_exe()
