# Architecture Refactoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the project structure to a standard modular `src/` layout for better maintainability.

**Architecture:** 
- `src/main.py`: Entry point.
- `src/core/`: Business logic (`events.py`, `logic.py`, `protocol.py`).
- `src/gui/`: UI components (`app_window.py`, `dialogs.py`).
- `src/utils/`: Utilities (`i18n.py`).
- `assets/`: Static files (`icon.ico`).
- `locale/`: Translations (remains in root).

**Tech Stack:** Python 3.10+, CustomTkinter.

---

### Task 1: Create Directories and Move Static Files

**Files:**
- Create directories: `src/core`, `src/gui`, `src/utils`, `assets`
- Move: `icon.ico` -> `assets/icon.ico`
- Modify: `build.bat` (update paths)

- [ ] **Step 1: Create directory structure**
    ```bash
    mkdir -p src/core src/gui src/utils assets
    ```

- [ ] **Step 2: Move icon to assets**
    ```bash
    mv icon.ico assets/icon.ico
    ```

- [ ] **Step 3: Update `build.bat`**
    ```bat
    rd /s /q build
    rd /s /q dist
    pyinstaller --clean --onefile --windowed --add-data "locale;locale" --icon=assets/icon.ico --name U-Prox-USB src/main.py
    ```

- [ ] **Step 4: Commit**
    ```bash
    git add src/ assets/ build.bat
    git rm icon.ico
    git commit -m "chore: setup new directory structure and move assets"
    ```

---

### Task 2: Extract Utils and Core Logic

**Files:**
- Create/Move: `src/utils/i18n.py`
- Move: `events.py` -> `src/core/events.py`
- Move: `protocol.py` -> `src/core/protocol.py`
- Move: `logic.py` -> `src/core/logic.py`

- [ ] **Step 1: Extract `Translator` to `src/utils/i18n.py`**
    Create `src/utils/i18n.py` and copy `Translator` class and `translator` instance from `gui.py`. 
    Update `LOCALE_DIR` path calculation to point to the root `locale/` directory correctly (e.g. `os.path.join(os.path.dirname(__file__), '..', '..', 'locale')`).

- [ ] **Step 2: Move Core files**
    ```bash
    mv events.py src/core/events.py
    mv protocol.py src/core/protocol.py
    mv logic.py src/core/logic.py
    ```

- [ ] **Step 3: Update imports in `src/core/logic.py`**
    Change imports to reflect the new structure:
    ```python
    from core.protocol import UProxProtocol, SerialCommunicator
    from core.events import EventManager, LogEvent, PortsUpdatedEvent, ConnectionStatusEvent
    ```

- [ ] **Step 4: Commit**
    ```bash
    git add src/utils/i18n.py src/core/
    git rm events.py protocol.py logic.py
    git commit -m "refactor: move core logic and extract i18n utility"
    ```

---

### Task 3: Extract GUI Components and Main

**Files:**
- Create/Move: `src/gui/dialogs.py`
- Create/Move: `src/gui/app_window.py`
- Move: `main.py` -> `src/main.py`

- [ ] **Step 1: Extract `CardNumberDialog` to `src/gui/dialogs.py`**
    Create the file, import `customtkinter as ctk`, `tkinter as tk`, `messagebox`, and `translator` from `utils.i18n`. Copy the `CardNumberDialog` class from `gui.py`.

- [ ] **Step 2: Extract `App` to `src/gui/app_window.py`**
    Create the file, import required libraries, `translator` from `utils.i18n`, `ReaderService` from `core.logic`, Events from `core.events`, and `CardNumberDialog` from `gui.dialogs`. Copy the `App` class from `gui.py`.

- [ ] **Step 3: Move and update `main.py`**
    ```bash
    mv main.py src/main.py
    ```
    Update imports in `src/main.py`:
    ```python
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    from gui.app_window import App
    ```

- [ ] **Step 4: Cleanup root `gui.py`**
    ```bash
    git rm gui.py
    ```

- [ ] **Step 5: Verify Application Starts**
    ```bash
    python src/main.py
    ```

- [ ] **Step 6: Commit**
    ```bash
    git add src/gui/ src/main.py
    git commit -m "refactor: modularize gui components and main entry point"
    ```
