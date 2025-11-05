#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAMP Arizona RP Admin Tools
Программа для администрирования сервера SAMP Arizona RP
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import struct
import threading
import json
import os
from datetime import datetime

class SAMPAdminTools:
    def __init__(self, root):
        self.root = root
        self.root.title("SAMP Arizona RP - Admin Tools")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Переменные подключения
        self.socket = None
        self.connected = False
        self.server_ip = ""
        self.server_port = 7777
        self.rcon_password = ""
        
        # Загрузка конфигурации
        self.load_config()
        
        # Создание интерфейса
        self.create_ui()
        
    def load_config(self):
        """Загрузка конфигурации из файла"""
        config_file = "config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.server_ip = config.get('server_ip', '')
                    self.server_port = config.get('server_port', 7777)
                    self.rcon_password = config.get('rcon_password', '')
            except:
                pass
    
    def save_config(self):
        """Сохранение конфигурации в файл"""
        config = {
            'server_ip': self.server_ip,
            'server_port': self.server_port,
            'rcon_password': self.rcon_password
        }
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    
    def create_ui(self):
        """Создание пользовательского интерфейса"""
        # Меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Настройки", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню "Инструменты"
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        tools_menu.add_command(label="Управление игроками", command=self.show_player_management)
        tools_menu.add_command(label="Управление сервером", command=self.show_server_management)
        tools_menu.add_command(label="Статистика", command=self.show_statistics)
        
        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
        
        # Панель подключения
        connection_frame = ttk.LabelFrame(self.root, text="Подключение к серверу", padding=10)
        connection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(connection_frame, text="IP сервера:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.ip_entry = ttk.Entry(connection_frame, width=20)
        self.ip_entry.insert(0, self.server_ip)
        self.ip_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(connection_frame, text="Порт:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.port_entry = ttk.Entry(connection_frame, width=10)
        self.port_entry.insert(0, str(self.server_port))
        self.port_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(connection_frame, text="RCON пароль:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.rcon_entry = ttk.Entry(connection_frame, width=20, show="*")
        self.rcon_entry.insert(0, self.rcon_password)
        self.rcon_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.connect_btn = ttk.Button(connection_frame, text="Подключиться", command=self.connect_server)
        self.connect_btn.grid(row=1, column=2, columnspan=2, padx=5, pady=5)
        
        self.status_label = ttk.Label(connection_frame, text="Статус: Отключено", foreground="red")
        self.status_label.grid(row=2, column=0, columnspan=4, pady=5)
        
        # Вкладки для инструментов
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Вкладка "Быстрые команды"
        self.quick_commands_frame = ttk.Frame(notebook)
        notebook.add(self.quick_commands_frame, text="Быстрые команды")
        self.create_quick_commands_tab()
        
        # Вкладка "Игроки"
        self.players_frame = ttk.Frame(notebook)
        notebook.add(self.players_frame, text="Игроки")
        self.create_players_tab()
        
        # Вкладка "RCON команды"
        self.rcon_frame = ttk.Frame(notebook)
        notebook.add(self.rcon_frame, text="RCON команды")
        self.create_rcon_tab()
        
        # Вкладка "Логи"
        self.logs_frame = ttk.Frame(notebook)
        notebook.add(self.logs_frame, text="Логи")
        self.create_logs_tab()
    
    def create_quick_commands_tab(self):
        """Создание вкладки быстрых команд"""
        # Команды для игроков
        players_frame = ttk.LabelFrame(self.quick_commands_frame, text="Команды для игроков", padding=10)
        players_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        commands = [
            ("Kick игрока", "kick"),
            ("Ban игрока", "ban"),
            ("Teleport к игроку", "goto"),
            ("Teleport игрока", "gethere"),
            ("Выдать деньги", "givemoney"),
            ("Выдать оружие", "givegun"),
            ("Изменить уровень", "setlevel"),
            ("Изменить респект", "setrespect"),
        ]
        
        row = 0
        col = 0
        for cmd_name, cmd_base in commands:
            btn = ttk.Button(players_frame, text=cmd_name, 
                           command=lambda c=cmd_base: self.show_command_dialog(c))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky=tk.W+tk.E)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # Команды для сервера
        server_frame = ttk.LabelFrame(self.quick_commands_frame, text="Команды для сервера", padding=10)
        server_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        server_commands = [
            ("Перезагрузить сервер", "gmx"),
            ("Остановить сервер", "exit"),
            ("Сохранить все", "saveall"),
            ("Чат в игру", "say"),
            ("Аннонс", "announce"),
        ]
        
        row = 0
        col = 0
        for cmd_name, cmd_base in server_commands:
            btn = ttk.Button(server_frame, text=cmd_name,
                           command=lambda c=cmd_base: self.show_command_dialog(c))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky=tk.W+tk.E)
            col += 1
            if col > 2:
                col = 0
                row += 1
    
    def create_players_tab(self):
        """Создание вкладки управления игроками"""
        # Поиск игрока
        search_frame = ttk.Frame(self.players_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Поиск игрока:").pack(side=tk.LEFT, padx=5)
        self.player_search_entry = ttk.Entry(search_frame, width=30)
        self.player_search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Найти", command=self.search_player).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Обновить список", command=self.refresh_players).pack(side=tk.LEFT, padx=5)
        
        # Список игроков
        list_frame = ttk.Frame(self.players_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("ID", "Имя", "IP", "Пинг")
        self.players_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.players_tree.heading(col, text=col)
            self.players_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.players_tree.yview)
        self.players_tree.configure(yscrollcommand=scrollbar.set)
        
        self.players_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Действия с игроком
        actions_frame = ttk.LabelFrame(self.players_frame, text="Действия", padding=10)
        actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        action_buttons = [
            ("Kick", self.kick_selected_player),
            ("Ban", self.ban_selected_player),
            ("Teleport к", self.goto_selected_player),
            ("Teleport сюда", self.gethere_selected_player),
            ("Дать деньги", self.give_money_selected),
            ("Дать оружие", self.give_weapon_selected),
        ]
        
        for btn_text, btn_cmd in action_buttons:
            ttk.Button(actions_frame, text=btn_text, command=btn_cmd).pack(side=tk.LEFT, padx=5)
    
    def create_rcon_tab(self):
        """Создание вкладки RCON команд"""
        # Поле ввода команды
        input_frame = ttk.Frame(self.rcon_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(input_frame, text="RCON команда:").pack(side=tk.LEFT, padx=5)
        self.rcon_command_entry = ttk.Entry(input_frame, width=50)
        self.rcon_command_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.rcon_command_entry.bind('<Return>', lambda e: self.execute_rcon_command())
        
        ttk.Button(input_frame, text="Выполнить", command=self.execute_rcon_command).pack(side=tk.LEFT, padx=5)
        
        # История команд
        history_frame = ttk.LabelFrame(self.rcon_frame, text="История команд", padding=5)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.command_history = scrolledtext.ScrolledText(history_frame, height=10, width=80)
        self.command_history.pack(fill=tk.BOTH, expand=True)
        
        # Быстрые команды
        quick_frame = ttk.LabelFrame(self.rcon_frame, text="Быстрые команды", padding=5)
        quick_frame.pack(fill=tk.X, padx=5, pady=5)
        
        quick_cmds = [
            ("Список игроков", "players"),
            ("Информация о сервере", "info"),
            ("Загрузить GMX", "gmx"),
            ("Сохранить все", "saveall"),
        ]
        
        for cmd_text, cmd in quick_cmds:
            btn = ttk.Button(quick_frame, text=cmd_text,
                           command=lambda c=cmd: self.rcon_command_entry.insert(0, c))
            btn.pack(side=tk.LEFT, padx=5)
    
    def create_logs_tab(self):
        """Создание вкладки логов"""
        logs_text = scrolledtext.ScrolledText(self.logs_frame, height=30, width=80)
        logs_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.logs_text = logs_text
    
    def log(self, message):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.logs_text.insert(tk.END, log_message)
        self.logs_text.see(tk.END)
    
    def connect_server(self):
        """Подключение к серверу"""
        if self.connected:
            self.disconnect_server()
            return
        
        self.server_ip = self.ip_entry.get()
        try:
            self.server_port = int(self.port_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный порт!")
            return
        
        self.rcon_password = self.rcon_entry.get()
        
        if not self.server_ip or not self.rcon_password:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5)
            
            # Проверка подключения
            packet = self.build_info_packet()
            self.socket.sendto(packet, (self.server_ip, self.server_port))
            
            data, addr = self.socket.recvfrom(4096)
            
            self.connected = True
            self.status_label.config(text="Статус: Подключено", foreground="green")
            self.connect_btn.config(text="Отключиться")
            self.save_config()
            self.log(f"Подключено к серверу {self.server_ip}:{self.server_port}")
            messagebox.showinfo("Успех", "Успешно подключено к серверу!")
            
        except Exception as e:
            self.log(f"Ошибка подключения: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {str(e)}")
            if self.socket:
                self.socket.close()
                self.socket = None
    
    def disconnect_server(self):
        """Отключение от сервера"""
        if self.socket:
            self.socket.close()
            self.socket = None
        self.connected = False
        self.status_label.config(text="Статус: Отключено", foreground="red")
        self.connect_btn.config(text="Подключиться")
        self.log("Отключено от сервера")
    
    def build_info_packet(self):
        """Построение пакета запроса информации"""
        packet = b'SAMP'
        packet += struct.pack('4B', *[int(x) for x in self.server_ip.split('.')])
        packet += struct.pack('<H', self.server_port)
        packet += b'i'
        return packet
    
    def build_rcon_packet(self, command):
        """Построение RCON пакета"""
        packet = b'SAMP'
        packet += struct.pack('4B', *[int(x) for x in self.server_ip.split('.')])
        packet += struct.pack('<H', self.server_port)
        packet += b'r'
        packet += struct.pack('<H', len(self.rcon_password))
        packet += self.rcon_password.encode('utf-8')
        packet += struct.pack('<H', len(command))
        packet += command.encode('utf-8')
        return packet
    
    def send_rcon_command(self, command):
        """Отправка RCON команды"""
        if not self.connected:
            messagebox.showerror("Ошибка", "Не подключено к серверу!")
            return None
        
        try:
            packet = self.build_rcon_packet(command)
            self.socket.sendto(packet, (self.server_ip, self.server_port))
            
            data, addr = self.socket.recvfrom(4096)
            
            if len(data) > 11:
                response_length = struct.unpack('<H', data[11:13])[0]
                response = data[13:13+response_length].decode('utf-8', errors='ignore')
                return response
            return ""
        except Exception as e:
            self.log(f"Ошибка выполнения команды: {str(e)}")
            return None
    
    def execute_rcon_command(self):
        """Выполнение RCON команды"""
        command = self.rcon_command_entry.get()
        if not command:
            return
        
        self.log(f"Выполнение команды: {command}")
        response = self.send_rcon_command(command)
        
        if response is not None:
            self.command_history.insert(tk.END, f"> {command}\n")
            if response:
                self.command_history.insert(tk.END, f"{response}\n")
            self.command_history.insert(tk.END, "\n")
            self.command_history.see(tk.END)
            self.log(f"Ответ: {response}")
        else:
            self.log("Ошибка выполнения команды")
        
        self.rcon_command_entry.delete(0, tk.END)
    
    def show_command_dialog(self, command_type):
        """Показать диалог для ввода параметров команды"""
        if not self.connected:
            messagebox.showerror("Ошибка", "Не подключено к серверу!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Команда: {command_type}")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="ID игрока:").pack(pady=5)
        player_id_entry = ttk.Entry(dialog, width=20)
        player_id_entry.pack(pady=5)
        
        if command_type in ["givemoney", "setlevel", "setrespect"]:
            ttk.Label(dialog, text="Значение:").pack(pady=5)
            value_entry = ttk.Entry(dialog, width=20)
            value_entry.pack(pady=5)
        elif command_type == "givegun":
            ttk.Label(dialog, text="ID оружия:").pack(pady=5)
            value_entry = ttk.Entry(dialog, width=20)
            value_entry.pack(pady=5)
        else:
            value_entry = None
        
        def execute():
            player_id = player_id_entry.get()
            if not player_id:
                messagebox.showerror("Ошибка", "Введите ID игрока!")
                return
            
            if value_entry:
                value = value_entry.get()
                if not value:
                    messagebox.showerror("Ошибка", "Введите значение!")
                    return
                cmd = f"{command_type} {player_id} {value}"
            else:
                cmd = f"{command_type} {player_id}"
            
            self.send_rcon_command(cmd)
            self.log(f"Выполнено: {cmd}")
            dialog.destroy()
            messagebox.showinfo("Успех", "Команда выполнена!")
        
        ttk.Button(dialog, text="Выполнить", command=execute).pack(pady=10)
    
    def search_player(self):
        """Поиск игрока"""
        search_term = self.player_search_entry.get()
        if not search_term:
            return
        
        # Обновление списка игроков
        self.refresh_players()
    
    def refresh_players(self):
        """Обновление списка игроков"""
        if not self.connected:
            messagebox.showerror("Ошибка", "Не подключено к серверу!")
            return
        
        # Очистка списка
        for item in self.players_tree.get_children():
            self.players_tree.delete(item)
        
        # Получение списка игроков
        response = self.send_rcon_command("players")
        if response:
            lines = response.split('\n')
            for line in lines[1:]:  # Пропускаем заголовок
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        player_id = parts[0]
                        player_name = ' '.join(parts[1:-2])
                        ip = parts[-2] if len(parts) > 2 else "N/A"
                        ping = parts[-1] if len(parts) > 1 else "N/A"
                        self.players_tree.insert("", tk.END, values=(player_id, player_name, ip, ping))
        
        self.log("Список игроков обновлен")
    
    def kick_selected_player(self):
        """Kick выбранного игрока"""
        selection = self.players_tree.selection()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите игрока!")
            return
        
        item = self.players_tree.item(selection[0])
        player_id = item['values'][0]
        self.send_rcon_command(f"kick {player_id}")
        self.log(f"Игрок {player_id} кикнут")
        messagebox.showinfo("Успех", f"Игрок {player_id} кикнут!")
    
    def ban_selected_player(self):
        """Ban выбранного игрока"""
        selection = self.players_tree.selection()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите игрока!")
            return
        
        item = self.players_tree.item(selection[0])
        player_id = item['values'][0]
        self.send_rcon_command(f"ban {player_id}")
        self.log(f"Игрок {player_id} забанен")
        messagebox.showinfo("Успех", f"Игрок {player_id} забанен!")
    
    def goto_selected_player(self):
        """Teleport к выбранному игроку"""
        selection = self.players_tree.selection()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите игрока!")
            return
        
        item = self.players_tree.item(selection[0])
        player_id = item['values'][0]
        self.send_rcon_command(f"goto {player_id}")
        self.log(f"Teleport к игроку {player_id}")
    
    def gethere_selected_player(self):
        """Teleport выбранного игрока"""
        selection = self.players_tree.selection()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите игрока!")
            return
        
        item = self.players_tree.item(selection[0])
        player_id = item['values'][0]
        self.send_rcon_command(f"gethere {player_id}")
        self.log(f"Игрок {player_id} телепортирован")
    
    def give_money_selected(self):
        """Выдать деньги выбранному игроку"""
        selection = self.players_tree.selection()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите игрока!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Выдать деньги")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="Сумма:").pack(pady=10)
        amount_entry = ttk.Entry(dialog, width=20)
        amount_entry.pack(pady=5)
        
        def execute():
            amount = amount_entry.get()
            if not amount:
                messagebox.showerror("Ошибка", "Введите сумму!")
                return
            
            item = self.players_tree.item(selection[0])
            player_id = item['values'][0]
            self.send_rcon_command(f"givemoney {player_id} {amount}")
            self.log(f"Игроку {player_id} выдано {amount} денег")
            dialog.destroy()
            messagebox.showinfo("Успех", "Деньги выданы!")
        
        ttk.Button(dialog, text="Выдать", command=execute).pack(pady=10)
    
    def give_weapon_selected(self):
        """Выдать оружие выбранному игроку"""
        selection = self.players_tree.selection()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите игрока!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Выдать оружие")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="ID оружия:").pack(pady=10)
        weapon_entry = ttk.Entry(dialog, width=20)
        weapon_entry.pack(pady=5)
        
        def execute():
            weapon_id = weapon_entry.get()
            if not weapon_id:
                messagebox.showerror("Ошибка", "Введите ID оружия!")
                return
            
            item = self.players_tree.item(selection[0])
            player_id = item['values'][0]
            self.send_rcon_command(f"givegun {player_id} {weapon_id}")
            self.log(f"Игроку {player_id} выдано оружие {weapon_id}")
            dialog.destroy()
            messagebox.showinfo("Успех", "Оружие выдано!")
        
        ttk.Button(dialog, text="Выдать", command=execute).pack(pady=10)
    
    def show_settings(self):
        """Показать настройки"""
        messagebox.showinfo("Настройки", "Настройки сохранены автоматически при подключении.")
    
    def show_player_management(self):
        """Показать управление игроками"""
        # Переключение на вкладку игроков
        pass
    
    def show_server_management(self):
        """Показать управление сервером"""
        pass
    
    def show_statistics(self):
        """Показать статистику"""
        if not self.connected:
            messagebox.showerror("Ошибка", "Не подключено к серверу!")
            return
        
        info = self.send_rcon_command("info")
        if info:
            messagebox.showinfo("Информация о сервере", info)
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = """SAMP Arizona RP Admin Tools
Версия 1.0

Программа для администрирования сервера SAMP Arizona RP.
Включает в себя все необходимые инструменты для управления сервером и игроками.

© 2024"""
        messagebox.showinfo("О программе", about_text)
    
    def __del__(self):
        """Деструктор"""
        self.disconnect_server()

def main():
    root = tk.Tk()
    app = SAMPAdminTools(root)
    root.mainloop()

if __name__ == "__main__":
    main()
