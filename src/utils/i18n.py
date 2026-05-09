import os
import json
from typing import Dict, Optional, Final, Any

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
LOCALE_DIR: Final[str] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'locale'))
translator: Final[Translator] = Translator(LOCALE_DIR, language='uk')
