#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматическое создание EXE файла
Запустите этот скрипт на Windows для создания EXE
"""
import subprocess
import sys
import os

def main():
    print("="*60)
    print("Создание EXE файла для SAMP Arizona RP Admin Tools")
    print("="*60)
    print()
    
    # Проверка Python
    print(f"Python версия: {sys.version}")
    print()
    
    # Проверка PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller установлен")
    except ImportError:
        print("❌ PyInstaller не найден, устанавливаю...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "pyperclip"], check=True)
        print("✅ PyInstaller установлен")
    
    print()
    print("Начинаю компиляцию...")
    print()
    
    # Очистка
    if os.path.exists("build"):
        import shutil
        shutil.rmtree("build")
    if os.path.exists("dist"):
        import shutil
        shutil.rmtree("dist")
    for f in os.listdir("."):
        if f.endswith(".spec"):
            os.remove(f)
    
    # Компиляция
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=SAMP_Arizona_RP_Admin_Tools",
        "--noconsole",
        "--clean",
        "admin_tools.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print()
        print("="*60)
        print("✅ КОМПИЛЯЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("="*60)
        print()
        print("EXE файл находится в папке: dist\\SAMP_Arizona_RP_Admin_Tools.exe")
        print()
        return True
    except subprocess.CalledProcessError as e:
        print()
        print("="*60)
        print("❌ ОШИБКА КОМПИЛЯЦИИ")
        print("="*60)
        print(f"Код ошибки: {e.returncode}")
        return False

if __name__ == "__main__":
    success = main()
    input("\nНажмите Enter для выхода...")
    sys.exit(0 if success else 1)
