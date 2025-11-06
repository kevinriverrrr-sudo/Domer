# -*- coding: utf-8 -*-
"""
SAMP Arizona RP Admin Tools - Android версия
Использует Kivy для интерфейса
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.core.clipboard import Clipboard
from kivy.utils import platform
import pyperclip
from datetime import datetime

# Цветовая схема
COLORS = {
    'bg': '#1e1e1e',
    'fg': '#ffffff',
    'card_bg': '#2d2d2d',
    'primary': '#0078d4',
    'success': '#107c10',
    'danger': '#d13438',
}

class CommandCard(BoxLayout):
    """Карточка команды"""
    def __init__(self, title, command_template, params, icon="⚡", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 200
        self.padding = 10
        self.spacing = 10
        
        self.command_template = command_template
        self.params = params
        
        # Заголовок
        header = BoxLayout(size_hint_y=None, height=40)
        header.add_widget(Label(text=icon, font_size=24, size_hint_x=0.2))
        header.add_widget(Label(text=title, font_size=16, bold=True, size_hint_x=0.8))
        self.add_widget(header)
        
        # Поля ввода
        self.entries = []
        for param in params:
            row = BoxLayout(size_hint_y=None, height=40, spacing=10)
            row.add_widget(Label(text=f"{param}:", size_hint_x=0.4))
            entry = TextInput(size_hint_x=0.6, multiline=False)
            self.entries.append(entry)
            row.add_widget(entry)
            self.add_widget(row)
        
        # Кнопка
        btn = Button(text="Сгенерировать", size_hint_y=None, height=40,
                    background_color=(0, 0.47, 0.83, 1))
        btn.bind(on_press=self.generate_command)
        self.add_widget(btn)
    
    def generate_command(self, instance):
        values = [e.text for e in self.entries]
        if all(values) or len(self.params) == 0:
            if len(self.params) == 0:
                cmd = self.command_template
            else:
                cmd = f"{self.command_template} {' '.join(values)}"
            app = App.get_running_app()
            app.copy_command(cmd)
            app.add_to_history(cmd)
            self.show_popup("Готово", f"Команда скопирована:\n{cmd}")
        else:
            self.show_popup("Ошибка", "Заполните все поля!")
    
    def show_popup(self, title, text):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=text, text_size=(300, None)))
        btn = Button(text="OK", size_hint_y=None, height=40)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

class CommandsTab(ScrollView):
    """Вкладка генератора команд"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # Заголовок
        title = Label(text="Генератор команд", font_size=24, bold=True,
                     size_hint_y=None, height=50)
        main_layout.add_widget(title)
        
        # Команды для игроков
        main_layout.add_widget(Label(text="Команды для игроков", font_size=18,
                                    size_hint_y=None, height=40))
        
        commands = [
            ("Kick игрока", "kick", ["ID игрока"], "🚫"),
            ("Ban игрока", "ban", ["ID игрока"], "⛔"),
            ("Teleport к игроку", "goto", ["ID игрока"], "📍"),
            ("Teleport игрока", "gethere", ["ID игрока"], "✈️"),
            ("Выдать деньги", "givemoney", ["ID игрока", "Сумма"], "💰"),
            ("Выдать оружие", "givegun", ["ID игрока", "ID оружия"], "🔫"),
            ("Изменить уровень", "setlevel", ["ID игрока", "Уровень"], "⬆️"),
            ("Изменить респект", "setrespect", ["ID игрока", "Респект"], "⭐"),
        ]
        
        for title, cmd, params, icon in commands:
            card = CommandCard(title, cmd, params, icon)
            card.size_hint_y = None
            main_layout.add_widget(card)
        
        # Команды для сервера
        main_layout.add_widget(Label(text="Команды для сервера", font_size=18,
                                    size_hint_y=None, height=40))
        
        server_commands = [
            ("Сообщение в чат", "say", ["Текст"], "💬"),
            ("Аннонс", "announce", ["Текст"], "📢"),
            ("Сохранить все", "saveall", [], "💾"),
            ("Перезагрузить сервер", "gmx", [], "🔄"),
            ("Остановить сервер", "exit", [], "⏹️"),
        ]
        
        for title, cmd, params, icon in server_commands:
            card = CommandCard(title, cmd, params, icon)
            card.size_hint_y = None
            main_layout.add_widget(card)
        
        self.add_widget(main_layout)

class QuickCommandsTab(ScrollView):
    """Вкладка быстрых команд"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = GridLayout(cols=2, spacing=10, padding=10)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        commands = [
            ("Kick [ID]", "kick", ["ID игрока"]),
            ("Ban [ID]", "ban", ["ID игрока"]),
            ("Teleport к [ID]", "goto", ["ID игрока"]),
            ("Teleport [ID]", "gethere", ["ID игрока"]),
            ("Деньги [ID] [сумма]", "givemoney", ["ID игрока", "Сумма"]),
            ("Оружие [ID] [оружие]", "givegun", ["ID игрока", "ID оружия"]),
            ("Уровень [ID] [уровень]", "setlevel", ["ID игрока", "Уровень"]),
            ("Респект [ID] [респект]", "setrespect", ["ID игрока", "Респект"]),
            ("Сообщение [текст]", "say", ["Текст"]),
            ("Аннонс [текст]", "announce", ["Текст"]),
            ("Сохранить все", "saveall", []),
            ("Перезагрузить", "gmx", []),
        ]
        
        for cmd_text, cmd_base, params in commands:
            btn = Button(text=cmd_text, size_hint_y=None, height=60)
            btn.bind(on_press=lambda x, c=cmd_base, p=params, t=cmd_text: 
                    self.quick_command(c, p, t))
            main_layout.add_widget(btn)
        
        self.add_widget(main_layout)
    
    def quick_command(self, cmd_base, params, cmd_text):
        app = App.get_running_app()
        
        if len(params) == 0:
            cmd = cmd_base
            app.copy_command(cmd)
            app.add_to_history(cmd)
            self.show_popup("Готово", f"Команда скопирована:\n{cmd}")
        else:
            # Диалог ввода
            content = BoxLayout(orientation='vertical', padding=10, spacing=10)
            content.add_widget(Label(text=cmd_text, font_size=16, bold=True))
            
            entries = []
            for param in params:
                row = BoxLayout(size_hint_y=None, height=50, spacing=10)
                row.add_widget(Label(text=f"{param}:"))
                entry = TextInput(multiline=False)
                entries.append(entry)
                row.add_widget(entry)
                content.add_widget(row)
            
            btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
            
            def generate():
                values = [e.text for e in entries]
                if all(values):
                    cmd = f"{cmd_base} {' '.join(values)}"
                    app.copy_command(cmd)
                    app.add_to_history(cmd)
                    popup.dismiss()
                    self.show_popup("Готово", f"Команда скопирована:\n{cmd}")
                else:
                    self.show_popup("Ошибка", "Заполните все поля!")
            
            btn = Button(text="Сгенерировать", size_hint_y=None, height=50)
            btn.bind(on_press=lambda x: generate())
            btn_layout.add_widget(btn)
            
            cancel_btn = Button(text="Отмена", size_hint_y=None, height=50)
            cancel_btn.bind(on_press=popup.dismiss)
            btn_layout.add_widget(cancel_btn)
            
            content.add_widget(btn_layout)
            
            popup = Popup(title="Команда", content=content, size_hint=(0.9, 0.7))
            popup.open()
    
    def show_popup(self, title, text):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=text, text_size=(300, None)))
        btn = Button(text="OK", size_hint_y=None, height=40)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

class ReferenceTab(ScrollView):
    """Вкладка справочника"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        content = Label(
            text="""
СПРАВОЧНИК КОМАНД SAMP ARIZONA RP

КОМАНДЫ ДЛЯ УПРАВЛЕНИЯ ИГРОКАМИ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

kick [ID]                    - Кикнуть игрока
ban [ID]                     - Забанить игрока
goto [ID]                    - Телепортироваться к игроку
gethere [ID]                 - Телепортировать игрока к себе
givemoney [ID] [сумма]       - Выдать деньги
givegun [ID] [оружие]        - Выдать оружие
setlevel [ID] [уровень]      - Установить уровень
setrespect [ID] [респект]    - Установить респект

КОМАНДЫ ДЛЯ СЕРВЕРА:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

say [текст]                  - Сообщение в чат
announce [текст]             - Аннонс
saveall                      - Сохранить всех
gmx                          - Перезагрузить сервер
exit                         - Остановить сервер

ID ОРУЖИЙ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0-9   - Холодное оружие
11-22 - Пистолеты и винтовки
23-26 - Тяжелое оружие
27-33 - Специальные предметы
            """,
            text_size=(None, None),
            halign='left',
            valign='top',
            padding=10
        )
        content.bind(text_size=content.setter('size'))
        self.add_widget(content)

class HistoryTab(BoxLayout):
    """Вкладка истории"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.history_list = Label(text="История команд:\n\n", 
                                 text_size=(None, None),
                                 halign='left', valign='top')
        self.history_list.bind(text_size=self.history_list.setter('size'))
        
        scroll = ScrollView()
        scroll.add_widget(self.history_list)
        self.add_widget(scroll)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        clear_btn = Button(text="Очистить историю", size_hint_x=0.5)
        clear_btn.bind(on_press=self.clear_history)
        btn_layout.add_widget(clear_btn)
        
        copy_btn = Button(text="Копировать последнюю", size_hint_x=0.5)
        copy_btn.bind(on_press=self.copy_last)
        btn_layout.add_widget(copy_btn)
        
        self.add_widget(btn_layout)
    
    def add_command(self, command):
        timestamp = datetime.now().strftime("%H:%M:%S")
        current_text = self.history_list.text
        self.history_list.text = f"{current_text}[{timestamp}] {command}\n"
    
    def clear_history(self, instance):
        self.history_list.text = "История команд:\n\n"
        app = App.get_running_app()
        app.command_history.clear()
    
    def copy_last(self, instance):
        app = App.get_running_app()
        if app.command_history:
            app.copy_command(app.command_history[-1])

class AdminToolsApp(App):
    """Главное приложение"""
    def build(self):
        self.command_history = []
        
        # Создание вкладок
        tabs = TabbedPanel(do_default_tab=False)
        
        # Вкладка генератора команд
        tab1 = TabbedPanelItem(text='📝 Команды')
        tab1.add_widget(CommandsTab())
        tabs.add_widget(tab1)
        
        # Вкладка быстрых команд
        tab2 = TabbedPanelItem(text='⚡ Быстрые')
        tab2.add_widget(QuickCommandsTab())
        tabs.add_widget(tab2)
        
        # Вкладка справочника
        tab3 = TabbedPanelItem(text='📚 Справочник')
        tab3.add_widget(ReferenceTab())
        tabs.add_widget(tab3)
        
        # Вкладка истории
        tab4 = TabbedPanelItem(text='🕒 История')
        self.history_tab = HistoryTab()
        tab4.add_widget(self.history_tab)
        tabs.add_widget(tab4)
        
        return tabs
    
    def copy_command(self, command):
        """Копирование команды в буфер обмена"""
        try:
            if platform == 'android':
                Clipboard.put(command, 'text/plain')
            else:
                try:
                    pyperclip.copy(command)
                except:
                    Clipboard.put(command, 'text/plain')
        except Exception as e:
            print(f"Ошибка копирования: {e}")
    
    def add_to_history(self, command):
        """Добавление в историю"""
        self.command_history.append(command)
        if hasattr(self, 'history_tab'):
            self.history_tab.add_command(command)

if __name__ == '__main__':
    AdminToolsApp().run()
