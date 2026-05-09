import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from src.utils.i18n import translator

class CardNumberDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, text):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x250")
        self.resizable(False, False)
        self.result = None

        self.label = ctk.CTkLabel(self, text=text)
        self.label.pack(padx=20, pady=10)

        self.entry = ctk.CTkEntry(self, width=200)
        self.entry.pack(padx=20, pady=10)
        self.entry.focus_set()

        self.radio_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.radio_frame.pack(padx=20, pady=5)

        self.format_var = tk.StringVar(value="HEX")
        self.hex_radio = ctk.CTkRadioButton(self.radio_frame, text="HEX", variable=self.format_var, value="HEX", width=80)
        self.hex_radio.pack(side="left", padx=10)
        self.dec_radio = ctk.CTkRadioButton(self.radio_frame, text="DEC", variable=self.format_var, value="DEC", width=80)
        self.dec_radio.pack(side="left", padx=10)

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
