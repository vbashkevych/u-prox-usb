# U-Prox USB Flet Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Переписати інтерфейс програми з Tkinter на Flet, зберігши існуючу логіку протоколу та сервісів, згідно з новим дизайном.

**Architecture:** Перехід на асинхронну модель Flet (asyncio). Розділення UI (Flet views/components) та Logic (Service/Protocol). Використання вбудованого в Flet механізму подій та реактивного оновлення UI.

**Tech Stack:** Python 3.10+, Flet, PySerial, Asyncio.

---

### Task 1: Підготовка середовища та структури проекту

**Files:**
- Create: `flet_main.py` (нова точка входу)
- Create: `ui_components.py` (окремі компоненти інтерфейсу)
- Modify: `requirements.txt`

- [ ] **Step 1: Додати flet у залежності**
    ```bash
    echo flet >> requirements.txt
    pip install -r requirements.txt
    ```

- [ ] **Step 2: Створити базовий каркас flet_main.py з темною темою**
    ```python
    import flet as ft

    async def main(page: ft.Page):
        page.title = "U-Prox USB Desktop"
        page.theme_mode = ft.ThemeMode.DARK
        page.window_width = 900
        page.window_height = 600
        page.padding = 20
        
        await page.add_async(ft.Text("U-Prox Flet App Started"))

    if __name__ == "__main__":
        ft.app(target=main)
    ```

- [ ] **Step 3: Запустити для перевірки**
    `python flet_main.py`

---

### Task 2: Рефакторинг `ReaderService` для роботи з Flet

Оскільки Flet асинхронний "з коробки", нам треба адаптувати `EventManager` або використовувати прямі виклики/стани Flet.

**Files:**
- Modify: `logic.py` (адаптація до асинхронності Flet)

- [ ] **Step 1: Оновити ReaderService для прийняття колбеку логів**
    ```python
    # В logic.py змінити __init__ або додати методи підписки
    class ReaderService:
        def __init__(self, event_manager: EventManager):
            self.events = event_manager
            # ...
    ```

---

### Task 3: Створення компонентів інтерфейсу (Sidebar та Header)

**Files:**
- Create: `ui_components.py`

- [ ] **Step 1: Реалізувати Sidebar з кнопками дій**
    Створити вертикальний `ft.Column` з `ft.ElevatedButton` або `ft.Container` для кастомного дизайну як на скріншоті.

- [ ] **Step 2: Реалізувати Header з Dropdown для портів та кнопкою Connect**
    Використати `ft.Row`, `ft.Dropdown`, `ft.IconButton` та `ft.FilledButton`.

---

### Task 4: Реалізація вікна логів (Log View)

**Files:**
- Modify: `ui_components.py`

- [ ] **Step 1: Створити ListView для логів з автоскролом**
    ```python
    log_view = ft.ListView(expand=True, spacing=5, auto_scroll=True)
    ```

- [ ] **Step 2: Додати форматування часових міток [HH:MM:SS] у колбек логів**

---

### Task 5: Інтеграція Logic та UI

**Files:**
- Modify: `flet_main.py`

- [ ] **Step 1: Ініціалізація ReaderService всередині `main(page)`**
- [ ] **Step 2: Підключення подій (OnClick) до методів сервісу**
- [ ] **Step 3: Реалізація логіки оновлення списку портів через `service.probe_ports_async()`**

---

### Task 6: Тестування та фіналізація

- [ ] **Step 1: Перевірка підключення до реального пристрою**
- [ ] **Step 2: Перевірка функцій емісії та стирання**
- [ ] **Step 3: Оновлення локалізації (JSON файли) для нових елементів UI**
