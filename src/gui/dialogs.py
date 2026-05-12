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

        # Save default border color for validation highlighting
        self.default_border_color = self.entry.cget("border_color")

        # Bind events for real-time validation highlighting
        self.entry.bind("<KeyRelease>", self.check_validation)

        # Bind Ctrl+V to the entry widget's internal entry for better compatibility
        # We use keycode 86 (physical 'V' key on Windows) to support multiple layouts
        self.entry._entry.bind("<Control-KeyPress>", self._on_control_key)

        self.radio_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.radio_frame.pack(padx=20, pady=5)

        self.format_var = tk.StringVar(value="HEX")
        self.hex_radio = ctk.CTkRadioButton(self.radio_frame, text="HEX", variable=self.format_var, value="HEX", width=80, command=self.on_mode_change)
        self.hex_radio.pack(side="left", padx=10)
        self.dec_radio = ctk.CTkRadioButton(self.radio_frame, text="DEC", variable=self.format_var, value="DEC", width=80, command=self.on_mode_change)
        self.dec_radio.pack(side="left", padx=10)

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(padx=20, pady=20)

        self.ok_button = ctk.CTkButton(self.button_frame, text=translator.get("dialogs.ok"), width=80, command=self.on_ok)
        self.ok_button.pack(side="left", padx=10)

        self.cancel_button = ctk.CTkButton(self.button_frame, text=translator.get("dialogs.cancel"), width=80, command=self.on_cancel)
        self.cancel_button.pack(side="left", padx=10)

        # Initial validation check
        self.check_validation()

        self.grab_set()
        self.wait_window()

    def on_ok(self):
        val = self.entry.get().strip()
        fmt = self.format_var.get()
        if val:
            if fmt == "DEC":
                try:
                    hex_val = hex(int(val))[2:].upper().zfill(10)
                    self.result = hex_val
                except ValueError:
                    messagebox.showerror(translator.get("dialogs.error_title"), translator.get("dialogs.invalid_input"))
                    return
            else:
                # Validate HEX format
                if all(c in "0123456789abcdefABCDEF" for c in val):
                    self.result = val.upper().zfill(10)
                else:
                    messagebox.showerror(translator.get("dialogs.error_title"), translator.get("dialogs.invalid_input"))
                    return
        self.destroy()

    def on_cancel(self):
        self.destroy()

    def on_mode_change(self):
        """Handle radio button mode change."""
        self.check_validation()

    def _on_control_key(self, event):
        """Handle Control + Key events using keycodes for layout independence."""
        # keycode 86 is 'V' on Windows
        if event.keycode == 86:
            self._on_paste()
            return "break"
        # keycode 65 is 'A' (Select All)
        elif event.keycode == 65:
            self.entry._entry.selection_range(0, tk.END)
            self.entry._entry.icursor(tk.END)
            return "break"

    def _on_paste(self):
        """Explicitly handle paste with whitespace trimming."""
        try:
            text = self.clipboard_get()
            if text:
                text = text.strip()
                self.entry.insert(tk.INSERT, text)
                self.check_validation()
        except Exception:
            pass
        return "break"

    def check_validation(self, event=None):
        """Check input validity and update UI state."""
        # Use after(1) if called from a key event to ensure entry.get() is updated
        if event:
            self.after(1, self._perform_validation)
        else:
            self._perform_validation()

    def _perform_validation(self):
        """Internal validation logic."""
        val = self.entry.get().strip()
        fmt = self.format_var.get()
        is_valid = True

        if not val:
            is_valid = False
        elif fmt == "DEC":
            # Only digits and max 13 chars
            is_valid = val.isdigit() and len(val) <= 13
        else: # HEX
            # Only hex chars and max 10 chars
            is_valid = all(c in "0123456789abcdefABCDEF" for c in val) and len(val) <= 10

        if is_valid:
            self.entry.configure(border_color=self.default_border_color)
            self.ok_button.configure(state="normal")
        else:
            self.entry.configure(border_color="red")
            self.ok_button.configure(state="disabled")

