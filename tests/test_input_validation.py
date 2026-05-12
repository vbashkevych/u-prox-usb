import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock translator
import src.utils.i18n
src.utils.i18n.translator = MagicMock()
src.utils.i18n.translator.get.side_effect = lambda x: x

from src.gui.dialogs import CardNumberDialog

class TestCardNumberValidation(unittest.TestCase):
    @patch('customtkinter.CTkToplevel.grab_set')
    @patch('customtkinter.CTkToplevel.wait_window')
    def setUp(self, mock_wait, mock_grab):
        self.root = tk.Tk()
        self.dialog = CardNumberDialog(self.root, "Title", "Text")

    def tearDown(self):
        self.root.destroy()

    def test_validate_input_dec(self):
        self.dialog.format_var.set("DEC")
        self.assertTrue(self.dialog.validate_input("123"))
        self.assertTrue(self.dialog.validate_input(""))
        self.assertFalse(self.dialog.validate_input("abc"))

    def test_validate_input_hex(self):
        self.dialog.format_var.set("HEX")
        self.assertTrue(self.dialog.validate_input("123"))
        self.assertTrue(self.dialog.validate_input("ABC"))
        self.assertTrue(self.dialog.validate_input("abc"))
        self.assertTrue(self.dialog.validate_input(""))
        self.assertFalse(self.dialog.validate_input("xyz"))

if __name__ == "__main__":
    unittest.main()
