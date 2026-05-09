import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Dict, Optional, Final, Any
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
        self.translations: Dict[str, Any] = {}
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

class CardNumberDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, text):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x250")
        self.result = None

        self.label = ctk.CTkLabel(self, text=text)
        self.label.pack(padx=20, pady=10)

        self.entry = ctk.CTkEntry(self, width=200)
        self.entry.pack(padx=20, pady=10)
        self.entry.focus_set()

        self.format_var = tk.StringVar(value="HEX")
        self.hex_radio = ctk.CTkRadioButton(self, text="HEX", variable=self.format_var, value="HEX")
        self.hex_radio.pack(padx=20, pady=5)
        self.dec_radio = ctk.CTkRadioButton(self, text="DEC", variable=self.format_var, value="DEC")
        self.dec_radio.pack(padx=20, pady=5)

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(padx=20, pady=20)

        self.ok_button = ctk.CTkButton(self.button_frame, text=translator.get("dialogs.ok"), width=80, command=self.on_ok)
        self.ok_button.pack(side="left", padx=10)

        self.cancel_button = ctk.CTkButton(self.button_frame, text=translator.get("dialogs.cancel"), width=80, command=self.on_cancel)
        self.cancel_button.pack(side="left", padx=10)

        self.grab_set()
        self.wait_window()

    def on_ok(self):
        val = self.entry.get().strip()
        fmt = self.format_var.get()
        if val:
            if fmt == "DEC":
                try:
                    # Конвертація з DEC в HEX (10 символів, як очікує протокол)
                    hex_val = hex(int(val))[2:].upper().zfill(10)
                    self.result = hex_val
                except ValueError:
                    messagebox.showerror(translator.get("dialogs.error_title"), translator.get("dialogs.invalid_input"))
                    return
            else:
                self.result = val
        self.destroy()

    def on_cancel(self):
        self.destroy()

class App:
    def __init__(self, root: ctk.CTk, loop: asyncio.AbstractEventLoop) -> None:
        self.root: ctk.CTk = root
        self.loop: asyncio.AbstractEventLoop = loop
        self.root.title(translator.get("app_title"))
        self.root.geometry("1000x700")

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
        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self.root, width=200, corner_radius=0, fg_color=("gray85", "gray15"))
        self.sidebar_frame.pack(side="left", fill="y")
        
        self.sidebar_label = ctk.CTkLabel(self.sidebar_frame, text=translator.get("app_title"), font=ctk.CTkFont(size=20, weight="bold"))
        self.sidebar_label.pack(padx=20, pady=(20, 20))

        self.issue_button = ctk.CTkButton(self.sidebar_frame, text="💳 " + translator.get("buttons.start_issue"),
                                         anchor="w", state="disabled",
                                         command=lambda: self.run_async(self.service.start_issue_sl3_async()))
        self.issue_button.pack(padx=20, pady=10, fill="x")

        self.stop_button = ctk.CTkButton(self.sidebar_frame, text="⏹ " + translator.get("buttons.stop_issue"),
                                        anchor="w", state="disabled",
                                        command=lambda: self.run_async(self.service.stop_issue_async()))
        self.stop_button.pack(padx=20, pady=10, fill="x")

        self.erase_button = ctk.CTkButton(self.sidebar_frame, text="🗑 " + translator.get("buttons.erase_card"),
                                         anchor="w", state="disabled",
                                         command=lambda: self.run_async(self.service.erase_mifare_card_async()))
        self.erase_button.pack(padx=20, pady=10, fill="x")

        self.set_number_button = ctk.CTkButton(self.sidebar_frame, text="🔢 " + translator.get("buttons.set_number"),
                                              anchor="w", state="disabled",
                                              command=self.set_start_number)
        self.set_number_button.pack(padx=20, pady=10, fill="x")

        # Language Selection
        self.lang_label = ctk.CTkLabel(self.sidebar_frame, text=translator.get("dialogs.language_label"))
        self.lang_label.pack(padx=20, pady=(20, 0))
        self.lang_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["uk", "en"], command=self.on_lang_change)
        self.lang_menu.set(translator.language)
        self.lang_menu.pack(padx=20, pady=5, fill="x")

        # Theme Selection
        self.theme_label = ctk.CTkLabel(self.sidebar_frame, text=translator.get("dialogs.theme_label"))
        self.theme_label.pack(padx=20, pady=(10, 0))
        self.theme_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["System", "Light", "Dark"], command=self.on_theme_change)
        self.theme_menu.set(ctk.get_appearance_mode())
        self.theme_menu.pack(padx=20, pady=(5, 20), fill="x")

        # --- Main Content Area ---
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True)

        # --- Header Frame ---
        self.header_frame = ctk.CTkFrame(self.main_frame, height=60, corner_radius=10)
        self.header_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        # Connection Controls
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        self.port_label = ctk.CTkLabel(self.header_frame, text=translator.get("controls.port_label"), font=ctk.CTkFont(weight="bold"))
        self.port_label.grid(row=0, column=0, padx=(20, 10), pady=15)
        
        self.port_combo = ctk.CTkOptionMenu(self.header_frame, values=[translator.get('controls.scan_text')], width=200)
        self.port_combo.grid(row=0, column=1, sticky='we', padx=5, pady=15)
        self.port_combo.set(translator.get('controls.scan_text'))
        
        self.refresh_button = ctk.CTkButton(self.header_frame, text="⟳", width=40,
                                           font=ctk.CTkFont(size=20),
                                           command=lambda: self.run_async(self.service.probe_ports_async()))
        self.refresh_button.grid(row=0, column=2, padx=5, pady=15)

        self.connect_button = ctk.CTkButton(self.header_frame, text="🔌̶ " + translator.get("controls.connect_button"),
                                           fg_color="#1f538d", hover_color="#14375e",
                                           command=self.toggle_connection)
        self.connect_button.grid(row=0, column=3, padx=10, pady=15)
        
        self.info_button = ctk.CTkButton(self.header_frame, text="ℹ " + translator.get("buttons.info"), width=100,
                                        state="disabled",
                                        command=lambda: self.run_async(self.service.get_device_info_async()))
        self.info_button.grid(row=0, column=4, padx=(10, 20), pady=15)

        # --- Log View ---
        self.log_container = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.log_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.log_label = ctk.CTkLabel(self.log_container, text="📜 " + translator.get("logs.title"), font=ctk.CTkFont(weight="bold"))
        self.log_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.log_area = ctk.CTkTextbox(self.log_container, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_area.pack(fill="both", expand=True, padx=2, pady=2)
        self.log_area.configure(state='disabled')

    def on_log_event(self, event: LogEvent) -> None:
        self.root.after(0, self._update_log_area, event.message)

    def _update_log_area(self, message: str) -> None:
        self.log_area.configure(state='normal')
        self.log_area.insert("end", f"{message}\n")
        self.log_area.configure(state='disabled')
        self.log_area.see("end")

    def on_ports_updated_event(self, event: PortsUpdatedEvent) -> None:
        self.root.after(0, self._update_ports_ui, event)

    def _update_ports_ui(self, event: PortsUpdatedEvent) -> None:
        self.port_map = event.port_map
        self.port_combo.configure(values=event.ports)
        if event.ports:
            self.port_combo.set(event.ports[0])
        else:
            self.port_combo.set('')

    def on_connection_status_event(self, event: ConnectionStatusEvent) -> None:
        self.root.after(0, self._update_ui_connection_status, event.is_connected)

    def _update_ui_connection_status(self, is_connected: bool) -> None:
        if is_connected:
            self.connect_button.configure(
                text="🔌 " + translator.get("controls.disconnect_button"),
                fg_color="#28a745",  # Зелений
                hover_color="#218838"
            )
            self.port_combo.configure(state='disabled')
            self.refresh_button.configure(state='disabled')
            
            # Активація всіх кнопок дій
            self.issue_button.configure(state="normal")
            self.stop_button.configure(state="normal")
            self.erase_button.configure(state="normal")
            self.set_number_button.configure(state="normal")
            self.settings_button.configure(state="normal")
            self.info_button.configure(state="normal")
        else:
            self.connect_button.configure(
                text="🔌̶ " + translator.get("controls.connect_button"),
                fg_color="#1f538d",   # Синій (стандартний CTk Blue)
                hover_color="#14375e"
            )
            self.port_combo.configure(state='normal')
            self.refresh_button.configure(state='normal')
            
            # Деактивація кнопок дій при відсутності з'єднання
            self.issue_button.configure(state="disabled")
            self.stop_button.configure(state="disabled")
            self.erase_button.configure(state="disabled")
            self.set_number_button.configure(state="disabled")
            self.settings_button.configure(state="disabled")
            self.info_button.configure(state="disabled")

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
        """Обробник закриття вікна."""
        if self.service.is_connected:
            try:
                # Використовуємо threadsafe для відключення
                future = asyncio.run_coroutine_threadsafe(self.service.disconnect_async(), self.loop)
                # Чекаємо зовсім трохи, щоб дати шанс команді піти
                future.result(timeout=0.5)
            except Exception:
                pass
        self.root.destroy()

    def set_sl3_key(self) -> None:
        dialog = ctk.CTkInputDialog(text=translator.get("dialogs.sl3_key_prompt"), title=translator.get("dialogs.input_title"))
        key = dialog.get_input()
        if key:
            self.run_async(self.service.set_mifare_plus_sl3_encryption_async(key))

    def set_start_number(self) -> None:
        dialog = CardNumberDialog(self.root, title=translator.get("dialogs.input_title"), text=translator.get("dialogs.start_number_prompt"))
        num = dialog.result
        if num:
            self.run_async(self.service.set_mifare_start_number_async(num))

    def on_lang_change(self, new_lang):
        translator.load_language(new_lang)
        self.refresh_ui_text()

    def on_theme_change(self, new_theme):
        ctk.set_appearance_mode(new_theme)

    def refresh_ui_text(self) -> None:
        """Оновлює текст на всіх віджетах після зміни мови."""
        self.root.title(translator.get("app_title"))
        self.sidebar_label.configure(text=translator.get("app_title"))
        self.issue_button.configure(text="💳 " + translator.get("buttons.start_issue"))
        self.stop_button.configure(text="⏹ " + translator.get("buttons.stop_issue"))
        self.erase_button.configure(text="🗑 " + translator.get("buttons.erase_card"))
        self.set_number_button.configure(text="🔢 " + translator.get("buttons.set_number"))
        self.lang_label.configure(text=translator.get("dialogs.language_label"))
        self.theme_label.configure(text=translator.get("dialogs.theme_label"))
        
        # Header
        self.port_label.configure(text=translator.get("controls.port_label"))
        self.refresh_button.configure(text="⟳") 
        self._update_ui_connection_status(self.service.is_connected)
        self.info_button.configure(text="ℹ " + translator.get("buttons.info"))
        self.log_label.configure(text="📜 " + translator.get("logs.title"))
        
        if not self.service.is_connected:
             self.port_combo.set(translator.get('controls.scan_text'))
