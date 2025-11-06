@echo off
chcp 65001 >nul
echo ========================================
echo Компиляция SAMP Arizona RP Admin Tools
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python с https://www.python.org/
    pause
    exit /b 1
)

echo Установка зависимостей...
pip install -r requirements.txt

echo.
echo Компиляция в EXE файл...
python build_exe.py

echo.
echo ========================================
echo Готово!
echo ========================================
pause
