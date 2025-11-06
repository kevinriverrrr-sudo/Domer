#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAMP Arizona RP Admin Tools
Общедоступный помощник для админов сервера SAMP Arizona RP
Современный интерфейс в стиле RoboTools
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
import json
import os
import subprocess
import platform
from datetime import datetime

# Попытка импорта pyperclip
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

# Цветовая схема (темная тема)
COLORS = {
    'bg': '#1e1e1e',
    'fg': '#ffffff',
    'card_bg': '#2d2d2d',
    'card_hover': '#3d3d3d',
    'primary': '#0078d4',
    'primary_hover': '#106ebe',
    'success': '#107c10',
    'danger': '#d13438',
    'warning': '#ffaa44',
    'border': '#404040',
    'text_secondary': '#cccccc',
}

class ModernButton(tk.Canvas):
    """Современная кнопка с эффектом наведения"""
    def __init__(self, parent, text, command, width=200, height=50, 
                 bg_color=COLORS['primary'], hover_color=COLORS['primary_hover'], 
                 text_color=COLORS['fg'], font_size=11):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg=COLORS['card_bg'])
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
        # Создание прямоугольника
        self.rect = self.create_rectangle(2, 2, width-2, height-2, 
                                         fill=bg_color, outline=COLORS['border'], width=1)
        
        # Текст
        self.text_id = self.create_text(width//2, height//2, text=text, 
                                       fill=text_color, font=('Segoe UI', font_size, 'bold'))
        
        # Привязка событий
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        self.bind('<ButtonRelease-1>', self.on_release)
    
    def on_enter(self, event):
        self.is_hovered = True
        self.itemconfig(self.rect, fill=self.hover_color)
    
    def on_leave(self, event):
        self.is_hovered = False
        self.itemconfig(self.rect, fill=self.bg_color)
    
    def on_click(self, event):
        self.itemconfig(self.rect, fill=self.bg_color)
    
    def on_release(self, event):
        if self.is_hovered:
            self.itemconfig(self.rect, fill=self.hover_color)
        if self.command:
            self.command()

class CommandCard(tk.Frame):
    """Карточка команды"""
    def __init__(self, parent, title, command_template, params, icon="⚡", app_instance=None):
        super().__init__(parent, bg=COLORS['card_bg'], relief=tk.RAISED, 
                        bd=1, padx=10, pady=10)
        self.command_template = command_template
        self.params = params
        self.app = app_instance
        
        # Заголовок
        header = tk.Frame(self, bg=COLORS['card_bg'])
        header.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header, text=icon, font=('Segoe UI', 16), 
                bg=COLORS['card_bg'], fg=COLORS['primary']).pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(header, text=title, font=('Segoe UI', 12, 'bold'), 
                bg=COLORS['card_bg'], fg=COLORS['fg']).pack(side=tk.LEFT)
        
        # Поля ввода
        self.entries = []
        params_frame = tk.Frame(self, bg=COLORS['card_bg'])
        params_frame.pack(fill=tk.X, pady=5)
        
        for i, param in enumerate(params):
            row = tk.Frame(params_frame, bg=COLORS['card_bg'])
            row.pack(fill=tk.X, pady=2)
            
            tk.Label(row, text=f"{param}:", font=('Segoe UI', 9), 
                    bg=COLORS['card_bg'], fg=COLORS['text_secondary'], 
                    width=15, anchor='w').pack(side=tk.LEFT)
            
            entry = tk.Entry(row, font=('Segoe UI', 9), bg=COLORS['bg'], 
                           fg=COLORS['fg'], insertbackground=COLORS['fg'],
                           relief=tk.SOLID, bd=1, highlightthickness=1,
                           highlightcolor=COLORS['primary'],
                           highlightbackground=COLORS['border'])
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            self.entries.append(entry)
        
        # Кнопка генерации
        btn_frame = tk.Frame(self, bg=COLORS['card_bg'])
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        def generate_cmd():
            values = [e.get() for e in self.entries]
            if all(values) or len(params) == 0:
                if len(params) == 0:
                    cmd = command_template
                else:
                    cmd = f"{command_template} {' '.join(values)}"
                if self.app:
                    self.app.copy_command(cmd)
                    self.app.add_to_history(cmd)
                messagebox.showinfo("Готово", f"Команда скопирована:\n{cmd}")
            else:
                messagebox.showwarning("Ошибка", "Заполните все поля!")
        
        ModernButton(btn_frame, "Сгенерировать", generate_cmd, 
                    width=150, height=35, font_size=10).pack()

class SAMPAdminTools:
    def __init__(self, root):
        self.root = root
        self.root.title("SAMP Arizona RP - Admin Tools")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        self.root.configure(bg=COLORS['bg'])
        
        # История команд
        self.command_history = []
        
        # Настройка стиля
        self.setup_style()
        
        # Создание интерфейса
        self.create_ui()
        
    def setup_style(self):
        """Настройка стилей ttk"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка цветов для ttk
        style.configure('TNotebook', background=COLORS['bg'], borderwidth=0)
        style.configure('TNotebook.Tab', background=COLORS['card_bg'], 
                       foreground=COLORS['fg'], padding=[20, 10])
        style.map('TNotebook.Tab', 
                 background=[('selected', COLORS['primary'])],
                 foreground=[('selected', COLORS['fg'])])
        
        style.configure('TFrame', background=COLORS['bg'])
        style.configure('TLabel', background=COLORS['bg'], foreground=COLORS['fg'])
        style.configure('TEntry', fieldbackground=COLORS['bg'], foreground=COLORS['fg'])
        
    def create_ui(self):
        """Создание пользовательского интерфейса"""
        # Верхняя панель
        self.create_header()
        
        # Основной контент
        self.create_main_content()
        
        # Нижняя панель статуса
        self.create_footer()
    
    def create_header(self):
        """Создание верхней панели"""
        header = tk.Frame(self.root, bg=COLORS['card_bg'], height=80)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        # Логотип и название
        title_frame = tk.Frame(header, bg=COLORS['card_bg'])
        title_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(title_frame, text="⚡", font=('Segoe UI', 24), 
                bg=COLORS['card_bg'], fg=COLORS['primary']).pack(side=tk.LEFT, padx=(0, 10))
        
        title_text = tk.Frame(title_frame, bg=COLORS['card_bg'])
        title_text.pack(side=tk.LEFT)
        
        tk.Label(title_text, text="SAMP Arizona RP", font=('Segoe UI', 18, 'bold'), 
                bg=COLORS['card_bg'], fg=COLORS['fg']).pack(anchor='w')
        tk.Label(title_text, text="Admin Tools Helper", font=('Segoe UI', 11), 
                bg=COLORS['card_bg'], fg=COLORS['text_secondary']).pack(anchor='w')
        
        # Кнопки в правой части
        buttons_frame = tk.Frame(header, bg=COLORS['card_bg'])
        buttons_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        ModernButton(buttons_frame, "Справочник", self.show_reference_tab, 
                    width=120, height=40, font_size=10).pack(side=tk.LEFT, padx=5)
        ModernButton(buttons_frame, "История", self.show_history_tab, 
                    width=120, height=40, font_size=10).pack(side=tk.LEFT, padx=5)
        ModernButton(buttons_frame, "О программе", self.show_about, 
                    width=120, height=40, font_size=10).pack(side=tk.LEFT, padx=5)
    
    def create_main_content(self):
        """Создание основного контента"""
        # Контейнер с прокруткой
        canvas = tk.Canvas(self.root, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Привязка прокрутки колесиком мыши
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        self.main_frame = scrollable_frame
        
        # Создание вкладок через радиокнопки
        self.create_tab_selector(scrollable_frame)
        
        # Контент вкладок
        self.content_frame = tk.Frame(scrollable_frame, bg=COLORS['bg'])
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.current_tab = "commands"
        self.show_commands_tab()
    
    def create_tab_selector(self, parent):
        """Создание селектора вкладок"""
        tabs_frame = tk.Frame(parent, bg=COLORS['bg'])
        tabs_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        self.tab_var = tk.StringVar(value="commands")
        
        tabs = [
            ("Генератор команд", "commands", "📝"),
            ("Быстрые команды", "quick", "⚡"),
            ("Справочник", "reference", "📚"),
            ("История", "history", "🕒"),
        ]
        
        for text, value, icon in tabs:
            tab_btn = tk.Radiobutton(
                tabs_frame, text=f"{icon} {text}", variable=self.tab_var,
                value=value, command=self.on_tab_change,
                font=('Segoe UI', 11, 'bold'),
                bg=COLORS['card_bg'], fg=COLORS['fg'],
                selectcolor=COLORS['primary'],
                activebackground=COLORS['card_hover'],
                activeforeground=COLORS['fg'],
                indicatoron=False,
                relief=tk.RAISED, bd=1,
                padx=20, pady=10,
                width=15
            )
            tab_btn.pack(side=tk.LEFT, padx=5)
    
    def on_tab_change(self):
        """Обработка смены вкладки"""
        tab = self.tab_var.get()
        self.current_tab = tab
        
        # Очистка контента
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Показ нужной вкладки
        if tab == "commands":
            self.show_commands_tab()
        elif tab == "quick":
            self.show_quick_tab()
        elif tab == "reference":
            self.show_reference_tab()
        elif tab == "history":
            self.show_history_tab()
    
    def show_commands_tab(self):
        """Показ вкладки генератора команд"""
        # Заголовок
        tk.Label(self.content_frame, text="Генератор команд", 
                font=('Segoe UI', 20, 'bold'), bg=COLORS['bg'], 
                fg=COLORS['fg']).pack(anchor='w', pady=(0, 20))
        
        # Команды для игроков
        tk.Label(self.content_frame, text="Команды для игроков", 
                font=('Segoe UI', 14, 'bold'), bg=COLORS['bg'], 
                fg=COLORS['text_secondary']).pack(anchor='w', pady=(10, 10))
        
        players_grid = tk.Frame(self.content_frame, bg=COLORS['bg'])
        players_grid.pack(fill=tk.BOTH, expand=True)
        
        # Левая колонка
        left_col = tk.Frame(players_grid, bg=COLORS['bg'])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Правая колонка
        right_col = tk.Frame(players_grid, bg=COLORS['bg'])
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Команды
        commands = [
            (left_col, "Kick игрока", "kick", ["ID игрока"], "🚫"),
            (left_col, "Ban игрока", "ban", ["ID игрока"], "⛔"),
            (left_col, "Teleport к игроку", "goto", ["ID игрока"], "📍"),
            (left_col, "Teleport игрока", "gethere", ["ID игрока"], "✈️"),
            (right_col, "Выдать деньги", "givemoney", ["ID игрока", "Сумма"], "💰"),
            (right_col, "Выдать оружие", "givegun", ["ID игрока", "ID оружия"], "🔫"),
            (right_col, "Изменить уровень", "setlevel", ["ID игрока", "Уровень"], "⬆️"),
            (right_col, "Изменить респект", "setrespect", ["ID игрока", "Респект"], "⭐"),
        ]
        
        for parent, title, cmd, params, icon in commands:
            card = CommandCard(parent, title, cmd, params, icon, self)
            card.pack(fill=tk.X, pady=10)
        
        # Команды для сервера
        tk.Label(self.content_frame, text="Команды для сервера", 
                font=('Segoe UI', 14, 'bold'), bg=COLORS['bg'], 
                fg=COLORS['text_secondary']).pack(anchor='w', pady=(30, 10))
        
        server_grid = tk.Frame(self.content_frame, bg=COLORS['bg'])
        server_grid.pack(fill=tk.BOTH, expand=True)
        
        server_left = tk.Frame(server_grid, bg=COLORS['bg'])
        server_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        server_right = tk.Frame(server_grid, bg=COLORS['bg'])
        server_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        server_commands = [
            (server_left, "Сообщение в чат", "say", ["Текст"], "💬"),
            (server_left, "Аннонс", "announce", ["Текст"], "📢"),
            (server_left, "Сохранить все", "saveall", [], "💾"),
            (server_right, "Перезагрузить сервер", "gmx", [], "🔄"),
            (server_right, "Остановить сервер", "exit", [], "⏹️"),
        ]
        
        for parent, title, cmd, params, icon in server_commands:
            card = CommandCard(parent, title, cmd, params, icon, self)
            card.pack(fill=tk.X, pady=10)
    
    def show_quick_tab(self):
        """Показ вкладки быстрых команд"""
        tk.Label(self.content_frame, text="Быстрые команды", 
                font=('Segoe UI', 20, 'bold'), bg=COLORS['bg'], 
                fg=COLORS['fg']).pack(anchor='w', pady=(0, 10))
        
        tk.Label(self.content_frame, 
                text="Выберите команду и заполните параметры. Команда будет скопирована автоматически.",
                font=('Segoe UI', 10), bg=COLORS['bg'], 
                fg=COLORS['text_secondary']).pack(anchor='w', pady=(0, 20))
        
        # Игроки
        tk.Label(self.content_frame, text="Игроки", 
                font=('Segoe UI', 14, 'bold'), bg=COLORS['bg'], 
                fg=COLORS['text_secondary']).pack(anchor='w', pady=(10, 10))
        
        players_frame = tk.Frame(self.content_frame, bg=COLORS['bg'])
        players_frame.pack(fill=tk.X, pady=10)
        
        player_commands = [
            ("Kick [ID]", "kick", ["ID игрока"]),
            ("Ban [ID]", "ban", ["ID игрока"]),
            ("Teleport к [ID]", "goto", ["ID игрока"]),
            ("Teleport [ID]", "gethere", ["ID игрока"]),
            ("Деньги [ID] [сумма]", "givemoney", ["ID игрока", "Сумма"]),
            ("Оружие [ID] [оружие]", "givegun", ["ID игрока", "ID оружия"]),
            ("Уровень [ID] [уровень]", "setlevel", ["ID игрока", "Уровень"]),
            ("Респект [ID] [респект]", "setrespect", ["ID игрока", "Респект"]),
        ]
        
        row = 0
        col = 0
        for cmd_text, cmd_base, params in player_commands:
            btn = ModernButton(players_frame, cmd_text, 
                             lambda c=cmd_base, p=params, t=cmd_text: self.quick_command(c, p, t),
                             width=180, height=45, font_size=10)
            btn.grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        # Сервер
        tk.Label(self.content_frame, text="Сервер", 
                font=('Segoe UI', 14, 'bold'), bg=COLORS['bg'], 
                fg=COLORS['text_secondary']).pack(anchor='w', pady=(20, 10))
        
        server_frame = tk.Frame(self.content_frame, bg=COLORS['bg'])
        server_frame.pack(fill=tk.X, pady=10)
        
        server_commands = [
            ("Сообщение [текст]", "say", ["Текст"]),
            ("Аннонс [текст]", "announce", ["Текст"]),
            ("Сохранить все", "saveall", []),
            ("Перезагрузить", "gmx", []),
            ("Остановить", "exit", []),
        ]
        
        row = 0
        col = 0
        for cmd_text, cmd_base, params in server_commands:
            btn = ModernButton(server_frame, cmd_text,
                             lambda c=cmd_base, p=params, t=cmd_text: self.quick_command(c, p, t),
                             width=180, height=45, font_size=10)
            btn.grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col > 3:
                col = 0
                row += 1
    
    def show_reference_tab(self):
        """Показ вкладки справочника"""
        tk.Label(self.content_frame, text="Справочник команд", 
                font=('Segoe UI', 20, 'bold'), bg=COLORS['bg'], 
                fg=COLORS['fg']).pack(anchor='w', pady=(0, 20))
        
        # Текст справочника
        text_frame = tk.Frame(self.content_frame, bg=COLORS['card_bg'], relief=tk.RAISED, bd=1)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scroll_text = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD, font=('Consolas', 10),
            bg=COLORS['bg'], fg=COLORS['fg'],
            insertbackground=COLORS['fg'],
            selectbackground=COLORS['primary'],
            selectforeground=COLORS['fg'],
            relief=tk.FLAT, bd=0, padx=10, pady=10
        )
        scroll_text.pack(fill=tk.BOTH, expand=True)
        
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

0  - Кулаки                 17 - Uzi
1  - Кастет                 18 - MP5
2  - Гольф клюшка           19 - AK-47
3  - Нож                    20 - M4
4  - Бейсбольная бита       21 - Технический карабин
5  - Лопата                 22 - Снайперская винтовка
6  - Кий                    23 - Ракетница
7  - Катана                 24 - Тепловая ракета
8  - Топор                  25 - Огнемет
9  - Бита                   26 - Миниган
10 - Огнетушитель           27 - Бомба
11 - Пистолет               28 - Баллончик
12 - Пистолет с глушителем  29 - Огнетушитель
13 - Desert Eagle           30 - Фотоаппарат
14 - Дробовик               31 - Ночное видение
15 - Sawnoff                32 - Тепловизор
16 - SPAS-12                33 - Парашют


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
        scroll_text.insert("1.0", reference_text)
        scroll_text.config(state=tk.DISABLED)
    
    def show_history_tab(self):
        """Показ вкладки истории"""
        tk.Label(self.content_frame, text="История команд", 
                font=('Segoe UI', 20, 'bold'), bg=COLORS['bg'], 
                fg=COLORS['fg']).pack(anchor='w', pady=(0, 10))
        
        tk.Label(self.content_frame, 
                text="Двойной клик по команде для копирования",
                font=('Segoe UI', 10), bg=COLORS['bg'], 
                fg=COLORS['text_secondary']).pack(anchor='w', pady=(0, 20))
        
        # Список истории
        list_frame = tk.Frame(self.content_frame, bg=COLORS['card_bg'], 
                              relief=tk.RAISED, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set,
            font=('Consolas', 10), bg=COLORS['bg'], fg=COLORS['fg'],
            selectbackground=COLORS['primary'], selectforeground=COLORS['fg'],
            relief=tk.FLAT, bd=0, highlightthickness=0
        )
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)
        
        self.history_listbox.bind('<Double-Button-1>', self.copy_from_history)
        
        # Кнопки
        buttons_frame = tk.Frame(self.content_frame, bg=COLORS['bg'])
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ModernButton(buttons_frame, "Копировать выбранное", 
                    self.copy_selected_from_history, width=180, height=40).pack(side=tk.LEFT, padx=5)
        ModernButton(buttons_frame, "Очистить историю", 
                    self.clear_history, width=180, height=40,
                    bg_color=COLORS['danger'], hover_color='#b02a2e').pack(side=tk.LEFT, padx=5)
    
    def create_footer(self):
        """Создание нижней панели"""
        footer = tk.Frame(self.root, bg=COLORS['card_bg'], height=30)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        tk.Label(footer, text="Готов к работе • Команды копируются в буфер обмена", 
                font=('Segoe UI', 9), bg=COLORS['card_bg'], 
                fg=COLORS['text_secondary']).pack(side=tk.LEFT, padx=20, pady=5)
        
        tk.Label(footer, text="SAMP Arizona RP Admin Tools v2.0", 
                font=('Segoe UI', 9), bg=COLORS['card_bg'], 
                fg=COLORS['text_secondary']).pack(side=tk.RIGHT, padx=20, pady=5)
    
    def quick_command(self, command_base, params, command_text):
        """Быстрая команда с диалогом"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Команда: {command_text}")
        dialog.geometry("400x250")
        dialog.configure(bg=COLORS['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Центрирование окна
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"400x250+{x}+{y}")
        
        tk.Label(dialog, text=command_text, font=('Segoe UI', 12, 'bold'),
                bg=COLORS['bg'], fg=COLORS['fg']).pack(pady=20)
        
        entries = []
        for param in params:
            frame = tk.Frame(dialog, bg=COLORS['bg'])
            frame.pack(pady=5)
            
            tk.Label(frame, text=f"{param}:", font=('Segoe UI', 9),
                    bg=COLORS['bg'], fg=COLORS['text_secondary'], 
                    width=15, anchor='w').pack(side=tk.LEFT, padx=10)
            
            entry = tk.Entry(frame, font=('Segoe UI', 9), width=25,
                           bg=COLORS['card_bg'], fg=COLORS['fg'],
                           insertbackground=COLORS['fg'],
                           relief=tk.SOLID, bd=1)
            entry.pack(side=tk.LEFT)
            entries.append(entry)
        
        def execute():
            if len(params) == 0:
                cmd = command_base
            else:
                values = [e.get() for e in entries]
                if not all(values):
                    messagebox.showwarning("Ошибка", "Заполните все поля!", parent=dialog)
                    return
                cmd = f"{command_base} {' '.join(values)}"
            
            self.copy_command(cmd)
            self.add_to_history(cmd)
            dialog.destroy()
            messagebox.showinfo("Готово", f"Команда скопирована:\n{cmd}")
        
        if len(params) == 0:
            execute()
        else:
            btn_frame = tk.Frame(dialog, bg=COLORS['bg'])
            btn_frame.pack(pady=20)
            
            ModernButton(btn_frame, "Сгенерировать", execute, 
                        width=150, height=40).pack()
    
    def copy_command(self, command):
        """Копирование команды в буфер обмена"""
        try:
            if HAS_PYPERCLIP:
                pyperclip.copy(command)
            else:
                self.copy_to_clipboard(command)
        except Exception as e:
            # Показываем окно с командой для ручного копирования
            dialog = tk.Toplevel(self.root)
            dialog.title("Команда")
            dialog.geometry("500x150")
            dialog.configure(bg=COLORS['bg'])
            dialog.transient(self.root)
            
            tk.Label(dialog, text="Скопируйте команду вручную:", 
                    font=('Segoe UI', 10), bg=COLORS['bg'], 
                    fg=COLORS['fg']).pack(pady=10)
            
            text_widget = tk.Text(dialog, height=3, font=('Consolas', 12),
                                bg=COLORS['card_bg'], fg=COLORS['fg'],
                                insertbackground=COLORS['fg'],
                                relief=tk.SOLID, bd=1, padx=10, pady=5)
            text_widget.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
            text_widget.insert("1.0", command)
            text_widget.select_range("1.0", tk.END)
            text_widget.focus()
            
            ModernButton(dialog, "Закрыть", dialog.destroy, 
                        width=100, height=35).pack(pady=5)
    
    def copy_to_clipboard(self, text):
        """Альтернативный способ копирования"""
        try:
            if platform.system() == 'Windows':
                subprocess.run(['clip'], input=text.encode('utf-8'), 
                             check=True, shell=True)
            elif platform.system() == 'Darwin':
                subprocess.run(['pbcopy'], input=text.encode('utf-8'), check=True)
            else:
                try:
                    subprocess.run(['xclip', '-selection', 'clipboard'], 
                                 input=text.encode('utf-8'), check=True)
                except FileNotFoundError:
                    subprocess.run(['xsel', '--clipboard', '--input'], 
                                 input=text.encode('utf-8'), check=True)
        except:
            raise
    
    def add_to_history(self, command):
        """Добавление в историю"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        history_entry = f"[{timestamp}] {command}"
        self.command_history.append(command)
        self.history_listbox.insert(tk.END, history_entry)
        self.history_listbox.see(tk.END)
    
    def copy_from_history(self, event):
        """Копирование из истории"""
        selection = self.history_listbox.curselection()
        if selection:
            index = selection[0]
            command = self.command_history[index]
            self.copy_command(command)
            messagebox.showinfo("Готово", f"Команда скопирована:\n{command}")
    
    def copy_selected_from_history(self):
        """Копирование выбранного"""
        selection = self.history_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите команду из списка!")
            return
        index = selection[0]
        command = self.command_history[index]
        self.copy_command(command)
        messagebox.showinfo("Готово", f"Команда скопирована:\n{command}")
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю команд?"):
            self.command_history.clear()
            self.history_listbox.delete(0, tk.END)
            messagebox.showinfo("Готово", "История очищена!")
    
    def show_about(self):
        """О программе"""
        about_text = """SAMP Arizona RP Admin Tools Helper
Версия 2.0

Общедоступный помощник для админов сервера SAMP Arizona RP.
Программа помогает быстро генерировать команды для управления сервером.

Функции:
• Генератор команд с формами ввода
• Быстрые команды для частых действий
• Полный справочник команд
• История команд
• Автоматическое копирование в буфер обмена
• Работает БЕЗ подключения к серверу

© 2024"""
        messagebox.showinfo("О программе", about_text)

def main():
    root = tk.Tk()
    app = SAMPAdminTools(root)
    root.mainloop()

if __name__ == "__main__":
    main()
