#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAMP Arizona RP Admin Tools
Общедоступный помощник для админов сервера SAMP Arizona RP
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import subprocess
import platform
from datetime import datetime

# Попытка импорта pyperclip, если не установлен - используем альтернативу
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

class SAMPAdminTools:
    def __init__(self, root):
        self.root = root
        self.root.title("SAMP Arizona RP - Admin Tools Helper")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        
        # История команд
        self.command_history = []
        
        # Создание интерфейса
        self.create_ui()
        
    def create_ui(self):
        """Создание пользовательского интерфейса"""
        # Меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Инструменты"
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        tools_menu.add_command(label="Справочник команд", command=self.show_commands_reference)
        tools_menu.add_command(label="История команд", command=self.show_history)
        tools_menu.add_separator()
        tools_menu.add_command(label="Очистить историю", command=self.clear_history)
        
        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
        
        # Вкладки для инструментов
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Вкладка "Генератор команд"
        self.commands_frame = ttk.Frame(notebook)
        notebook.add(self.commands_frame, text="Генератор команд")
        self.create_commands_tab()
        
        # Вкладка "Быстрые команды"
        self.quick_frame = ttk.Frame(notebook)
        notebook.add(self.quick_frame, text="Быстрые команды")
        self.create_quick_commands_tab()
        
        # Вкладка "Справочник"
        self.reference_frame = ttk.Frame(notebook)
        notebook.add(self.reference_frame, text="Справочник")
        self.create_reference_tab()
        
        # Вкладка "История"
        self.history_frame = ttk.Frame(notebook)
        notebook.add(self.history_frame, text="История")
        self.create_history_tab()
    
    def create_commands_tab(self):
        """Создание вкладки генератора команд"""
        # Генератор команд для игроков
        players_frame = ttk.LabelFrame(self.commands_frame, text="Команды для игроков", padding=10)
        players_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        commands_grid = ttk.Frame(players_frame)
        commands_grid.pack(fill=tk.BOTH, expand=True)
        
        # Левая колонка
        left_col = ttk.Frame(commands_grid)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Правая колонка
        right_col = ttk.Frame(commands_grid)
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Kick команда
        self.create_command_generator(left_col, "Kick игрока", "kick", ["ID игрока"])
        
        # Ban команда
        self.create_command_generator(left_col, "Ban игрока", "ban", ["ID игрока"])
        
        # Teleport к игроку
        self.create_command_generator(left_col, "Teleport к игроку", "goto", ["ID игрока"])
        
        # Teleport игрока
        self.create_command_generator(left_col, "Teleport игрока ко мне", "gethere", ["ID игрока"])
        
        # Выдать деньги
        self.create_command_generator(right_col, "Выдать деньги", "givemoney", ["ID игрока", "Сумма"])
        
        # Выдать оружие
        self.create_command_generator(right_col, "Выдать оружие", "givegun", ["ID игрока", "ID оружия"])
        
        # Изменить уровень
        self.create_command_generator(right_col, "Изменить уровень", "setlevel", ["ID игрока", "Уровень"])
        
        # Изменить респект
        self.create_command_generator(right_col, "Изменить респект", "setrespect", ["ID игрока", "Респект"])
        
        # Команды для сервера
        server_frame = ttk.LabelFrame(self.commands_frame, text="Команды для сервера", padding=10)
        server_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        server_grid = ttk.Frame(server_frame)
        server_grid.pack(fill=tk.BOTH, expand=True)
        
        server_left = ttk.Frame(server_grid)
        server_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        server_right = ttk.Frame(server_grid)
        server_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Сообщение в чат
        self.create_command_generator(server_left, "Сообщение в чат", "say", ["Текст сообщения"])
        
        # Аннонс
        self.create_command_generator(server_left, "Аннонс", "announce", ["Текст аннонса"])
        
        # Сохранить все
        self.create_command_generator(server_left, "Сохранить все", "saveall", [])
        
        # Перезагрузить сервер
        self.create_command_generator(server_right, "Перезагрузить сервер", "gmx", [])
        
        # Остановить сервер
        self.create_command_generator(server_right, "Остановить сервер", "exit", [])
    
    def create_command_generator(self, parent, label_text, command_base, params):
        """Создание генератора команды"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text=f"{label_text}:").pack(side=tk.LEFT, padx=5)
        
        entries = []
        for param in params:
            entry = ttk.Entry(frame, width=15)
            entry.pack(side=tk.LEFT, padx=2)
            entry.insert(0, param)
            entries.append(entry)
        
        def generate():
            values = [e.get() for e in entries]
            if command_base in ["gmx", "exit", "saveall"]:
                cmd = command_base
            else:
                cmd = f"{command_base} {' '.join(values)}"
            
            self.copy_command(cmd)
            self.add_to_history(cmd)
            messagebox.showinfo("Готово", f"Команда скопирована в буфер обмена:\n{cmd}")
        
        ttk.Button(frame, text="Сгенерировать", command=generate, width=15).pack(side=tk.LEFT, padx=5)
    
    def create_quick_commands_tab(self):
        """Создание вкладки быстрых команд"""
        info_label = ttk.Label(self.quick_frame, 
                              text="Выберите команду и она будет скопирована в буфер обмена",
                              font=("Arial", 10))
        info_label.pack(pady=10)
        
        # Команды для игроков
        players_frame = ttk.LabelFrame(self.quick_frame, text="Быстрые команды для игроков", padding=10)
        players_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        player_commands = [
            ("Kick [ID]", "kick"),
            ("Ban [ID]", "ban"),
            ("Teleport к [ID]", "goto"),
            ("Teleport [ID] ко мне", "gethere"),
            ("Выдать деньги [ID] [сумма]", "givemoney"),
            ("Выдать оружие [ID] [оружие]", "givegun"),
            ("Установить уровень [ID] [уровень]", "setlevel"),
            ("Установить респект [ID] [респект]", "setrespect"),
            ("Забанить IP [IP]", "banip"),
            ("Разбанить IP [IP]", "unbanip"),
        ]
        
        row = 0
        col = 0
        for cmd_text, cmd_base in player_commands:
            btn = ttk.Button(players_frame, text=cmd_text,
                           command=lambda c=cmd_base, t=cmd_text: self.quick_copy(c, t))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky=tk.W+tk.E)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        players_frame.columnconfigure(0, weight=1)
        players_frame.columnconfigure(1, weight=1)
        players_frame.columnconfigure(2, weight=1)
        
        # Команды для сервера
        server_frame = ttk.LabelFrame(self.quick_frame, text="Быстрые команды для сервера", padding=10)
        server_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        server_commands = [
            ("Сообщение в чат [текст]", "say"),
            ("Аннонс [текст]", "announce"),
            ("Сохранить все", "saveall"),
            ("Перезагрузить сервер", "gmx"),
            ("Остановить сервер", "exit"),
            ("Информация о сервере", "info"),
            ("Список игроков", "players"),
            ("Очистить чат", "clear"),
        ]
        
        row = 0
        col = 0
        for cmd_text, cmd_base in server_commands:
            btn = ttk.Button(server_frame, text=cmd_text,
                           command=lambda c=cmd_base, t=cmd_text: self.quick_copy(c, t))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky=tk.W+tk.E)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        server_frame.columnconfigure(0, weight=1)
        server_frame.columnconfigure(1, weight=1)
        server_frame.columnconfigure(2, weight=1)
    
    def create_reference_tab(self):
        """Создание вкладки справочника"""
        scroll_frame = scrolledtext.ScrolledText(self.reference_frame, wrap=tk.WORD, font=("Courier", 10))
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        reference_text = """
╔══════════════════════════════════════════════════════════════╗
║          СПРАВОЧНИК КОМАНД SAMP ARIZONA RP                   ║
╚══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
КОМАНДЫ ДЛЯ УПРАВЛЕНИЯ ИГРОКАМИ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

kick [ID]                    - Кикнуть игрока с сервера
ban [ID]                     - Забанить игрока
goto [ID]                    - Телепортироваться к игроку
gethere [ID]                 - Телепортировать игрока к себе
givemoney [ID] [сумма]       - Выдать деньги игроку
givegun [ID] [оружие]        - Выдать оружие игроку
setlevel [ID] [уровень]      - Установить уровень игрока
setrespect [ID] [респект]    - Установить респект игрока
banip [IP]                   - Забанить IP адрес
unbanip [IP]                 - Разбанить IP адрес
freeze [ID]                  - Заморозить игрока
unfreeze [ID]                - Разморозить игрока
slap [ID]                    - Ударить игрока
explode [ID]                 - Взорвать игрока
sethealth [ID] [HP]          - Установить здоровье
setarmour [ID] [броня]       - Установить броню
setweather [ID] [погода]     - Установить погоду для игрока
settime [ID] [час]           - Установить время для игрока


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
КОМАНДЫ ДЛЯ УПРАВЛЕНИЯ СЕРВЕРОМ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

say [текст]                  - Отправить сообщение в чат
announce [текст]             - Отправить аннонс всем игрокам
saveall                      - Сохранить всех игроков
gmx                          - Перезагрузить игровой режим
exit                         - Остановить сервер
info                         - Информация о сервере
players                      - Список игроков онлайн
clear                        - Очистить чат
changemode [текст]           - Изменить название режима
password [пароль]            - Установить пароль сервера
password 0                   - Убрать пароль сервера


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID ОРУЖИЙ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0  - Кулаки
1  - Кастет
2  - Гольф клюшка
3  - Нож
4  - Бейсбольная бита
5  - Лопата
6  - Кий
7  - Катана
8  - Топор
9  - Бита
10 - Огнетушитель
11 - Пистолет
12 - Пистолет с глушителем
13 - Desert Eagle
14 - Дробовик
15 - Sawnoff
16 - SPAS-12
17 - Uzi
18 - MP5
19 - AK-47
20 - M4
21 - Технический карабин
22 - Снайперская винтовка
23 - Ракетница
24 - Тепловая ракета
25 - Огнемет
26 - Миниган
27 - Бомба
28 - Баллончик
29 - Огнетушитель
30 - Фотоаппарат
31 - Ночное видение
32 - Тепловизор
33 - Парашют


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ПОЛЕЗНЫЕ СОВЕТЫ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Все команды вводятся в консоль сервера или через RCON
• ID игрока можно узнать командой /players или через админ панель
• Используйте эту программу для быстрого создания команд
• Скопированные команды можно вставить в консоль сервера
• История команд сохраняется для удобства повторного использования

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        scroll_frame.insert("1.0", reference_text)
        scroll_frame.config(state=tk.DISABLED)
    
    def create_history_tab(self):
        """Создание вкладки истории"""
        info_label = ttk.Label(self.history_frame, 
                              text="История сгенерированных команд (двойной клик для копирования)",
                              font=("Arial", 10))
        info_label.pack(pady=5)
        
        # Список истории
        list_frame = ttk.Frame(self.history_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Courier", 10))
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)
        
        self.history_listbox.bind('<Double-Button-1>', self.copy_from_history)
        
        # Кнопки управления историей
        buttons_frame = ttk.Frame(self.history_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Копировать выбранное", 
                  command=self.copy_selected_from_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Очистить историю", 
                  command=self.clear_history).pack(side=tk.LEFT, padx=5)
    
    def copy_command(self, command):
        """Копирование команды в буфер обмена"""
        try:
            if HAS_PYPERCLIP:
                pyperclip.copy(command)
            else:
                # Альтернативный способ копирования
                self.copy_to_clipboard(command)
            self.log(f"Команда скопирована: {command}")
        except Exception as e:
            # Если не удалось скопировать, показываем команду для ручного копирования
            dialog = tk.Toplevel(self.root)
            dialog.title("Команда")
            dialog.geometry("500x150")
            dialog.transient(self.root)
            
            ttk.Label(dialog, text="Скопируйте команду вручную:").pack(pady=10)
            text_widget = tk.Text(dialog, height=3, font=("Courier", 12))
            text_widget.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
            text_widget.insert("1.0", command)
            text_widget.select_range("1.0", tk.END)
            text_widget.focus()
            
            ttk.Button(dialog, text="Закрыть", command=dialog.destroy).pack(pady=5)
    
    def copy_to_clipboard(self, text):
        """Альтернативный способ копирования в буфер обмена"""
        try:
            if platform.system() == 'Windows':
                subprocess.run(['clip'], input=text.encode('utf-8'), check=True, shell=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['pbcopy'], input=text.encode('utf-8'), check=True)
            else:
                # Linux
                try:
                    subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'), check=True)
                except FileNotFoundError:
                    try:
                        subprocess.run(['xsel', '--clipboard', '--input'], input=text.encode('utf-8'), check=True)
                    except FileNotFoundError:
                        raise Exception("Установите xclip или xsel для Linux")
        except Exception as e:
            raise Exception(f"Не удалось скопировать: {str(e)}")
    
    def quick_copy(self, command_base, command_text):
        """Быстрое копирование команды с подсказкой"""
        # Показываем диалог для ввода параметров
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Команда: {command_text}")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Определяем параметры команды
        if "[ID]" in command_text:
            params = ["ID игрока"]
        elif "[текст]" in command_text:
            params = ["Текст"]
        elif "[сумма]" in command_text:
            params = ["ID игрока", "Сумма"]
        elif "[оружие]" in command_text:
            params = ["ID игрока", "ID оружия"]
        elif "[уровень]" in command_text:
            params = ["ID игрока", "Уровень"]
        elif "[респект]" in command_text:
            params = ["ID игрока", "Респект"]
        elif "[IP]" in command_text:
            params = ["IP адрес"]
        else:
            params = []
        
        entries = []
        for i, param in enumerate(params):
            ttk.Label(dialog, text=f"{param}:").pack(pady=5)
            entry = ttk.Entry(dialog, width=30)
            entry.pack(pady=2)
            entries.append(entry)
        
        def execute():
            if command_base in ["gmx", "exit", "saveall", "info", "players", "clear"]:
                cmd = command_base
            else:
                values = [e.get() for e in entries]
                if not all(values):
                    messagebox.showerror("Ошибка", "Заполните все поля!")
                    return
                cmd = f"{command_base} {' '.join(values)}"
            
            self.copy_command(cmd)
            self.add_to_history(cmd)
            dialog.destroy()
            messagebox.showinfo("Готово", f"Команда скопирована:\n{cmd}")
        
        if not params:
            # Команда без параметров
            ttk.Label(dialog, text="Команда без параметров").pack(pady=20)
            execute()
        else:
            ttk.Button(dialog, text="Сгенерировать и скопировать", command=execute).pack(pady=10)
    
    def add_to_history(self, command):
        """Добавление команды в историю"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        history_entry = f"[{timestamp}] {command}"
        self.command_history.append(command)
        self.history_listbox.insert(tk.END, history_entry)
        self.history_listbox.see(tk.END)
    
    def copy_from_history(self, event):
        """Копирование команды из истории по двойному клику"""
        selection = self.history_listbox.curselection()
        if selection:
            index = selection[0]
            command = self.command_history[index]
            self.copy_command(command)
            messagebox.showinfo("Готово", f"Команда скопирована:\n{command}")
    
    def copy_selected_from_history(self):
        """Копирование выбранной команды из истории"""
        selection = self.history_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите команду из списка!")
            return
        index = selection[0]
        command = self.command_history[index]
        self.copy_command(command)
        messagebox.showinfo("Готово", f"Команда скопирована:\n{command}")
    
    def clear_history(self):
        """Очистка истории команд"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю команд?"):
            self.command_history.clear()
            self.history_listbox.delete(0, tk.END)
            messagebox.showinfo("Готово", "История очищена!")
    
    def show_commands_reference(self):
        """Показать справочник команд"""
        # Переключение на вкладку справочника
        pass
    
    def show_history(self):
        """Показать историю"""
        # Переключение на вкладку истории
        pass
    
    def log(self, message):
        """Логирование (можно добавить в будущем)"""
        pass
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = """SAMP Arizona RP Admin Tools Helper
Версия 2.0

Общедоступный помощник для админов сервера SAMP Arizona RP.
Программа помогает быстро генерировать команды для управления сервером.

Функции:
• Генератор команд с формами ввода
• Быстрые команды для частых действий
• Справочник всех команд
• История команд для повторного использования
• Копирование команд в буфер обмена

Использование:
1. Выберите нужную команду
2. Заполните параметры (если требуется)
3. Команда будет скопирована в буфер обмена
4. Вставьте команду в консоль сервера

© 2024"""
        messagebox.showinfo("О программе", about_text)

def main():
    root = tk.Tk()
    app = SAMPAdminTools(root)
    root.mainloop()

if __name__ == "__main__":
    main()
