# Flet UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the U-Prox-USB interface from Tkinter to Flet, matching the design in the provided screenshot.

**Architecture:** Component-based Flet application using `ft.Row` for the main layout, custom containers for the sidebar, and an auto-scrolling log view. Logic is handled by the existing `ReaderService`.

**Tech Stack:** Python, Flet, Asyncio.

---

### Task 1: Environment Setup

**Files:**
- Modify: `requirements.txt`
- Create: `flet_main.py` (basic scaffold)

- [ ] **Step 1: Update requirements.txt**
    ```bash
    echo flet >> requirements.txt
    pip install -r requirements.txt
    ```

- [ ] **Step 2: Create flet_main.py with basic dark theme**
    ```python
    import flet as ft
    import asyncio

    async def main(page: ft.Page):
        page.title = "U-Prox USB"
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#121212"
        page.window_width = 900
        page.window_height = 600
        page.padding = 0 # Padding handled by components
        
        await page.add_async(ft.Text("Flet App Started", color="white"))

    if __name__ == "__main__":
        ft.app(target=main)
    ```

- [ ] **Step 3: Run to verify**
    `python flet_main.py`

- [ ] **Step 4: Commit**
    `git add requirements.txt flet_main.py && git commit -m "chore: setup flet environment"`

---

### Task 2: Sidebar Component

**Files:**
- Create: `ui_components.py`

- [ ] **Step 1: Implement Sidebar component**
    ```python
    import flet as ft

    class Sidebar(ft.UserControl):
        def __init__(self, on_issue, on_stop, on_erase, on_settings):
            super().__init__()
            self.on_issue = on_issue
            self.on_stop = on_stop
            self.on_erase = on_erase
            self.on_settings = on_settings

        def build(self):
            def sidebar_item(icon, text, on_click):
                return ft.Container(
                    content=ft.Row([
                        ft.Icon(icon, color=ft.colors.WHITE70),
                        ft.Text(text, color=ft.colors.WHITE, size=16),
                    ], spacing=15),
                    padding=ft.padding.all(15),
                    border_radius=10,
                    on_click=on_click,
                    hover_color=ft.colors.WHITE10,
                )

            return ft.Container(
                width=250,
                bgcolor="#1E1E1E",
                padding=ft.padding.only(top=20, left=10, right=10),
                content=ft.Column([
                    sidebar_item(ft.icons.CREDIT_CARD, "Випуск картки", self.on_issue),
                    sidebar_item(ft.icons.STOP_CIRCLE, "Зупинити випуск", self.on_stop),
                    sidebar_item(ft.icons.DELETE_OUTLINE, "Стирання карти", self.on_erase),
                    ft.Divider(color=ft.colors.WHITE10),
                    sidebar_item(ft.icons.SETTINGS, "Налаштування", self.on_settings),
                ], spacing=5)
            )
    ```

- [ ] **Step 2: Update flet_main.py to use Sidebar**
    ```python
    from ui_components import Sidebar
    # ... inside main ...
    sidebar = Sidebar(
        on_issue=lambda _: print("Issue"),
        on_stop=lambda _: print("Stop"),
        on_erase=lambda _: print("Erase"),
        on_settings=lambda _: print("Settings")
    )
    await page.add_async(ft.Row([sidebar], expand=True))
    ```

- [ ] **Step 3: Commit**
    `git add ui_components.py flet_main.py && git commit -m "feat: add sidebar component"`

---

### Task 3: Header Component

**Files:**
- Modify: `ui_components.py`

- [ ] **Step 1: Implement Header component**
    ```python
    class Header(ft.UserControl):
        def __init__(self, on_refresh, on_connect, on_info):
            super().__init__()
            self.on_refresh = on_refresh
            self.on_connect = on_connect
            self.on_info = on_info
            self.port_dropdown = ft.Dropdown(
                label="COM Порт",
                width=200,
                options=[],
                text_size=14,
                dense=True,
            )

        def build(self):
            return ft.Container(
                padding=ft.padding.only(left=20, right=20, top=10, bottom=10),
                content=ft.Row([
                    ft.Text("COM Порт", size=16, weight=ft.FontWeight.BOLD),
                    self.port_dropdown,
                    ft.IconButton(ft.icons.REFRESH, on_click=self.on_refresh),
                    ft.ElevatedButton(
                        "Підключити",
                        icon=ft.icons.CABLE,
                        on_click=self.on_connect,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                        )
                    ),
                    ft.VerticalDivider(width=1, color=ft.colors.TRANSPARENT),
                    ft.IconButton(ft.icons.INFO_OUTLINE, on_click=self.on_info),
                ], alignment=ft.MainAxisAlignment.START, spacing=10)
            )
    ```

- [ ] **Step 2: Commit**
    `git add ui_components.py && git commit -m "feat: add header component"`

---

### Task 4: Log Area Component

**Files:**
- Modify: `ui_components.py`

- [ ] **Step 1: Implement LogArea component**
    ```python
    class LogArea(ft.UserControl):
        def __init__(self):
            super().__init__()
            self.log_list = ft.ListView(expand=True, spacing=5, auto_scroll=True)

        def build(self):
            return ft.Container(
                expand=True,
                padding=20,
                content=ft.Column([
                    ft.Text("Логи", size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        expand=True,
                        border=ft.border.all(1, ft.colors.WHITE10),
                        border_radius=10,
                        padding=10,
                        content=self.log_list
                    )
                ])
            )

        def append_log(self, message):
            import datetime
            now = datetime.datetime.now().strftime("%H:%M:%S")
            self.log_list.controls.append(ft.Text(f"[{now}] {message}", size=14))
            self.update()
    ```

- [ ] **Step 2: Commit**
    `git add ui_components.py && git commit -m "feat: add log area component"`

---

### Task 5: Integration and Logic

**Files:**
- Modify: `flet_main.py`
- Modify: `logic.py` (if needed)

- [ ] **Step 1: Integrate all components in flet_main.py**
    ```python
    import flet as ft
    from ui_components import Sidebar, Header, LogArea
    from logic import ReaderService
    from events import EventManager, LogEvent, PortsUpdatedEvent, ConnectionStatusEvent

    async def main(page: ft.Page):
        page.title = "U-Prox USB"
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#121212"
        
        events = EventManager()
        service = ReaderService(events)
        
        log_area = LogArea()
        
        async def on_log(event):
            log_area.append_log(event.message)
            await page.update_async()

        async def on_ports_updated(event):
            header.port_dropdown.options = [ft.dropdown.Option(p) for p in event.ports]
            if event.ports:
                header.port_dropdown.value = event.ports[0]
            await page.update_async()

        events.subscribe(LogEvent, lambda e: asyncio.create_task(on_log(e)))
        events.subscribe(PortsUpdatedEvent, lambda e: asyncio.create_task(on_ports_updated(e)))

        sidebar = Sidebar(
            on_issue=lambda _: asyncio.create_task(service.start_issue_sl3_async()),
            on_stop=lambda _: asyncio.create_task(service.stop_issue_async()),
            on_erase=lambda _: asyncio.create_task(service.erase_mifare_card_async()),
            on_settings=lambda _: print("Settings clicked")
        )
        
        header = Header(
            on_refresh=lambda _: asyncio.create_task(service.probe_ports_async()),
            on_connect=lambda _: asyncio.create_task(service.connect_async(header.port_dropdown.value)),
            on_info=lambda _: asyncio.create_task(service.get_device_info_async())
        )

        main_view = ft.Row([
            sidebar,
            ft.Column([
                header,
                log_area
            ], expand=True)
        ], expand=True)

        await page.add_async(main_view)
        await service.probe_ports_async()

    if __name__ == "__main__":
        ft.app(target=main)
    ```

- [ ] **Step 2: Verify functionality**
    Run `python flet_main.py` and test port scanning, connecting, and logging.

- [ ] **Step 3: Commit**
    `git add flet_main.py && git commit -m "feat: integrate logic with flet UI"`
