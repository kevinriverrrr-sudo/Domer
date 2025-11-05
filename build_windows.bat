@echo off
chcp 65001 >nul
echo ========================================
echo Компиляция SAMP Arizona RP Admin Tools
echo Версия для Windows - Современный интерфейс
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
pip install pyinstaller pyperclip

echo.
echo Очистка старых файлов...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

echo.
echo Компиляция в EXE файл...
pyinstaller --onefile --windowed --name=SAMP_Arizona_RP_Admin_Tools --icon=NONE --noconsole admin_tools.py

if exist dist\SAMP_Arizona_RP_Admin_Tools.exe (
    echo.
    echo ========================================
    echo УСПЕШНО!
    echo ========================================
    echo EXE файл создан: dist\SAMP_Arizona_RP_Admin_Tools.exe
    echo.
    echo Программа готова к использованию!
    echo Не требует подключения к серверу или RCON пароля.
) else (
    echo.
    echo ========================================
    echo ОШИБКА КОМПИЛЯЦИИ!
    echo ========================================
)

pause
