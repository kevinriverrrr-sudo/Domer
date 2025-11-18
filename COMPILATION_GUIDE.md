# Руководство по компиляции Admin Tools

## Для Windows (создание EXE файла)

### Требования:
1. Windows 7 или выше
2. Python 3.8 или выше
3. Интернет для установки зависимостей

### Шаги:

1. **Установите Python** (если еще не установлен):
   - Скачайте с https://www.python.org/downloads/
   - При установке отметьте "Add Python to PATH"

2. **Откройте командную строку** в папке с программой:
   - Нажмите Shift + ПКМ в папке с файлами
   - Выберите "Открыть окно PowerShell здесь" или "Открыть командную строку"

3. **Запустите сборку**:
   ```cmd
   build_windows.bat
   ```

4. **Готово!** EXE файл будет в папке `dist\SAMP_Arizona_RP_Admin_Tools.exe`

### Альтернативный способ (вручную):

```cmd
pip install pyinstaller
pyinstaller --onefile --windowed --name=SAMP_Arizona_RP_Admin_Tools admin_tools.py
```

## Для Linux

```bash
chmod +x build.sh
./build.sh
```

## Важные примечания:

- **Windows EXE можно создать ТОЛЬКО на Windows системе**
- Если вы на Linux/Mac, используйте Wine или виртуальную машину Windows
- После компиляции скопируйте `config.json` в ту же папку, что и EXE (если используется)

## Использование без компиляции:

Просто запустите:
```bash
python admin_tools.py
```

Требуется установленный Python и библиотека tkinter (обычно идет в комплекте с Python).
