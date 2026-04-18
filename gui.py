import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, ttk
from typing import Dict, Optional, Final
import json
import os
import asyncio
import threading

from logic import ReaderService
from events import EventManager, LogEvent, PortsUpdatedEvent, ConnectionStatusEvent

class Translator:
    """
    Клас для локалізації за допомогою JSON файлів.
    """
    def __init__(self, locale_dir: str, language: str = 'uk'):
        self.translations: Dict[str, any] = {}
        self.language = language
        self.locale_dir = locale_dir
        self.load_language(self.language)

    def load_language(self, language: str) -> None:
        """Завантажує файл перекладу для вказаної мови."""
        path = os.path.join(self.locale_dir, f"{language}.json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load translations for '{language}': {e}")
            self.translations = {}

    def get(self, key: str, default: Optional[str] = None) -> str:
        """Отримує переклад за ключем (підтримує вкладені ключі через крапку)."""
        value = self.translations
        try:
            for k in key.split('.'):
                value = value[k]
            return str(value)
        except (KeyError, TypeError):
            return default if default is not None else key

# --- Налаштування локалізації ---
LOCALE_DIR: Final[str] = os.path.join(os.path.dirname(__file__), 'locale')
translator: Final[Translator] = Translator(LOCALE_DIR, language='uk')

class App:
    def __init__(self, root: tk.Tk, loop: asyncio.AbstractEventLoop) -> None:
        self.root: tk.Tk = root
        self.loop: asyncio.AbstractEventLoop = loop
        self.root.title(translator.get("app_title"))
        self.root.geometry("800x600")

        self.events: EventManager = EventManager()
        self.service: ReaderService = ReaderService(self.events)
        self.port_map: Dict[str, str] = {}

        self.create_widgets()
        self.subscribe_to_events()
        
        # Запускаємо початковий пошук портів асинхронно
        self.run_async(self.service.probe_ports_async())

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def run_async(self, coro) -> None:
        """Запускає корутину в циклі подій asyncio."""
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    def subscribe_to_events(self) -> None:
        self.events.subscribe(LogEvent, self.on_log_event)
        self.events.subscribe(PortsUpdatedEvent, self.on_ports_updated_event)
        self.events.subscribe(ConnectionStatusEvent, self.on_connection_status_event)

    def create_widgets(self) -> None:
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        control_frame.grid_columnconfigure(1, weight=1)

        tk.Label(control_frame, text=translator.get("controls.port_label")).grid(row=0, column=0, sticky='w', padx=5)
        self.port_combo = ttk.Combobox(control_frame, state="readonly")
        self.port_combo.grid(row=0, column=1, sticky='we')
        self.port_combo.set(translator.get('controls.scan_text'))
        
        self.refresh_button = tk.Button(control_frame, text=translator.get("controls.refresh_button"), 
                                       command=lambda: self.run_async(self.service.probe_ports_async()))
        self.refresh_button.grid(row=0, column=2, padx=5)

        self.connect_button = tk.Button(control_frame, text=translator.get("controls.connect_button"), 
                                       command=self.toggle_connection)
        self.connect_button.grid(row=0, column=3, padx=10)

        self.log_area = scrolledtext.ScrolledText(self.root, state='disabled', wrap=tk.WORD, height=20)
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        command_frame = tk.Frame(self.root, padx=10, pady=5)
        command_frame.pack(fill=tk.X)
        
        tk.Button(command_frame, text=translator.get("buttons.info"), 
                  command=lambda: self.run_async(self.service.get_device_info_async())).pack(side=tk.LEFT, padx=5)
        tk.Button(command_frame, text=translator.get("buttons.erase_card"), 
                  command=lambda: self.run_async(self.service.erase_mifare_card_async())).pack(side=tk.LEFT, padx=5)
        tk.Button(command_frame, text=translator.get("buttons.set_number"), 
                  command=self.set_start_number).pack(side=tk.LEFT, padx=5)
        tk.Button(command_frame, text=translator.get("buttons.start_issue"), 
                  command=lambda: self.run_async(self.service.start_issue_sl3_async())).pack(side=tk.LEFT, padx=5)
        tk.Button(command_frame, text=translator.get("buttons.stop_issue"), 
                  command=lambda: self.run_async(self.service.stop_issue_async())).pack(side=tk.LEFT, padx=5)
        tk.Button(command_frame, text=translator.get("buttons.set_sl3_key"), 
                  command=self.set_sl3_key).pack(side=tk.LEFT, padx=5)

    def on_log_event(self, event: LogEvent) -> None:
        self.root.after(0, self._update_log_area, event.message)

    def _update_log_area(self, message: str) -> None:
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.configure(state='disabled')
        self.log_area.see(tk.END)

    def on_ports_updated_event(self, event: PortsUpdatedEvent) -> None:
        self.root.after(0, self._update_ports_ui, event)

    def _update_ports_ui(self, event: PortsUpdatedEvent) -> None:
        self.port_map = event.port_map
        self.port_combo['values'] = event.ports
        if event.ports:
            self.port_combo.current(0)
        else:
            self.port_combo.set('')

    def on_connection_status_event(self, event: ConnectionStatusEvent) -> None:
        self.root.after(0, self._update_ui_connection_status, event.is_connected)

    def _update_ui_connection_status(self, is_connected: bool) -> None:
        if is_connected:
            self.connect_button.config(text=translator.get("controls.disconnect_button"))
            self.port_combo.config(state='disabled')
            self.refresh_button.config(state='disabled')
        else:
            self.connect_button.config(text=translator.get("controls.connect_button"))
            self.port_combo.config(state='readonly')
            self.refresh_button.config(state='normal')

    def toggle_connection(self) -> None:
        if not self.service.is_connected:
            selected_desc = self.port_combo.get()
            if not selected_desc or selected_desc == translator.get('controls.scan_text'):
                messagebox.showerror(translator.get("dialogs.error_title"), translator.get("dialogs.no_port_selected"))
                return
            port = self.port_map.get(selected_desc)
            if port:
                self.run_async(self.service.connect_async(port))
        else:
            self.run_async(self.service.disconnect_async())

    def on_closing(self) -> None:
        # Спроба асинхронного відключення перед закриттям
        if self.service.is_connected:
            # Тут ми не можемо використовувати run_async, бо цикл може зупинитися
            # Тому використовуємо синхронний метод або чекаємо завершення
            try:
                # Створюємо новий цикл або використовуємо поточний для швидкої операції
                self.run_async(self.service.disconnect_async())
            except Exception:
                pass
        self.root.destroy()

    def set_sl3_key(self) -> None:
        key = simpledialog.askstring(translator.get("dialogs.input_title"), translator.get("dialogs.sl3_key_prompt"), parent=self.root)
        if key:
            self.run_async(self.service.set_mifare_plus_sl3_encryption_async(key))

    def set_start_number(self) -> None:
        num = simpledialog.askstring(translator.get("dialogs.input_title"), translator.get("dialogs.start_number_prompt"), parent=self.root)
        if num:
            self.run_async(self.service.set_mifare_start_number_async(num))
