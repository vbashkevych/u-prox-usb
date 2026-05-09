# CustomTkinter UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the application UI using CustomTkinter to match the modern dark-themed look with a sidebar and header as shown in the screenshot.

**Architecture:** Transition the `App` class from standard `tk.Tk` to `customtkinter.CTk`. Use `customtkinter` frames and widgets to create a grid-based layout (Sidebar + Header + Log View). Maintain existing logic integration via `ReaderService`.

**Tech Stack:** Python 3.10+, CustomTkinter, Asyncio.

---

### Task 1: Environment Setup and App Base

**Files:**
- Modify: `main.py`
- Modify: `gui.py`

- [ ] **Step 1: Update `main.py` to handle CustomTkinter window**
    Ensure `customtkinter` appearance mode is set at startup.

```python
import customtkinter as ctk
# ... inside main()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
root = ctk.CTk()
app = App(root, new_loop)
root.mainloop()
```

- [ ] **Step 2: Update `App` class inheritance and base configuration**
    Change `App` to work with `ctk.CTk`.

```python
class App:
    def __init__(self, root: ctk.CTk, loop: asyncio.AbstractEventLoop) -> None:
        self.root: ctk.CTk = root
        # ...
        self.root.geometry("1000x700") # Increased size for new layout
```

- [ ] **Step 3: Commit**

```bash
git add main.py gui.py
git commit -m "feat: switch to CustomTkinter base"
```

---

### Task 2: Implement Sidebar Actions

**Files:**
- Modify: `gui.py`

- [ ] **Step 1: Create Sidebar Frame**
    Add a vertical frame on the left.

```python
self.sidebar_frame = ctk.CTkFrame(self.root, width=200, corner_radius=0)
self.sidebar_frame.pack(side="left", fill="y")
```

- [ ] **Step 2: Add Action Buttons to Sidebar**
    Use `ctk.CTkButton` with icons (or placeholders).

```python
self.issue_button = ctk.CTkButton(self.sidebar_frame, text=translator.get("buttons.start_issue"), command=...)
self.issue_button.pack(padx=20, pady=10)
# Repeat for Stop Issue, Erase Card, and Settings (at the bottom)
```

- [ ] **Step 3: Commit**

```bash
git add gui.py
git commit -m "ui: add sidebar with action buttons"
```

---

### Task 3: Implement Header and Log View

**Files:**
- Modify: `gui.py`

- [ ] **Step 1: Create Header Frame**
    Row at the top of the main area.

```python
self.main_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
self.main_frame.pack(side="right", fill="both", expand=True)

self.header_frame = ctk.CTkFrame(self.main_frame, height=60)
self.header_frame.pack(fill="x", padx=20, pady=(20, 0))
```

- [ ] **Step 2: Add Connection Controls to Header**
    Dropdown, Refresh, and Connect button.

```python
self.port_combo = ctk.CTkOptionMenu(self.header_frame, values=[])
self.port_combo.pack(side="left", padx=10)
# Add Refresh and Connect buttons
```

- [ ] **Step 3: Create Log View**
    A large `CTkTextbox` inside a bordered frame.

```python
self.log_container = ctk.CTkFrame(self.main_frame)
self.log_container.pack(fill="both", expand=True, padx=20, pady=20)

self.log_area = ctk.CTkTextbox(self.log_container, activate_scroll=True)
self.log_area.pack(fill="both", expand=True, padx=2, pady=2)
```

- [ ] **Step 4: Commit**

```bash
git add gui.py
git commit -m "ui: implement header and log view"
```

---

### Task 4: Final Integration and Refinement

**Files:**
- Modify: `gui.py`
- Modify: `locale/uk.json` (if needed)

- [ ] **Step 1: Link all UI events to `ReaderService`**
    Ensure buttons call the correct async methods.

- [ ] **Step 2: Refine styling (padding, colors, icons)**
    Match colors to screenshot (#1A1C1E background, etc.).

- [ ] **Step 3: Final Verification**
    Run the app, test connection, and log output.

- [ ] **Step 4: Commit**

```bash
git commit -m "ui: final polish and integration"
```
