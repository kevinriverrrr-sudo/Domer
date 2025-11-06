#!/bin/bash
echo "========================================"
echo "Компиляция SAMP Arizona RP Admin Tools"
echo "========================================"
echo ""

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "ОШИБКА: Python3 не найден!"
    echo "Установите Python3"
    exit 1
fi

echo "Установка зависимостей..."
pip3 install -r requirements.txt

echo ""
echo "Компиляция в EXE файл..."
python3 build_exe.py

echo ""
echo "========================================"
echo "Готово!"
echo "========================================"
