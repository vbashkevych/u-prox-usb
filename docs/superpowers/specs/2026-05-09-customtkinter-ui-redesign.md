# Spec: CustomTkinter UI Redesign for U-Prox USB

## 1. Goal
Redesign the existing Tkinter UI using `customtkinter` to match the provided screenshot (`docs/Screenshot 2026-05-09 172910.png`). The new UI should be modern, dark-themed, and feature a sidebar for actions and a dedicated header for connection management.

## 2. Visual Design
- **Theme:** Dark mode (`customtkinter.set_appearance_mode("dark")`).
- **Color Palette:**
    - Background: Deep dark gray/blue (#1A1C1E or similar).
    - Sidebar/Header accents: Slightly lighter gray (#24272B).
    - Highlight/Accent color: Standard CTk Blue or custom muted blue.
- **Layout:**
    - **Sidebar (Left):** Fixed width (approx. 200-250px). Vertical stack of large buttons with icons.
    - **Main Content (Right):**
        - **Header (Top):** Row with COM port selection, refresh icon, "Connect" button with icon, and Info icon.
        - **Log Area (Center):** Large frame with rounded corners and a thin border (#3E444B), containing the scrolling log text.

## 3. Component Breakdown

### 3.1 Sidebar Actions
- **Issue Card (Випуск):** Button with credit card icon.
- **Stop Issue (Зупинити випуск):** Button with "STOP" icon.
- **Erase Card (Стирання карти):** Button with trash/broom icon.
- **Settings (Налаштування):** Bottom-aligned button with gear icon.

### 3.2 Header (Connection)
- **Port Label:** "COM Порт".
- **Port Selector:** `CTkOptionMenu` for selecting available ports.
- **Refresh Button:** `CTkButton` with circular arrow icon (no text).
- **Connect Button:** `CTkButton` with plug icon and text "Підключити" / "Відключити".
- **Info Button:** `CTkButton` (or Label) with "i" icon at the far right.

### 3.3 Log View
- **Title:** "Логи" label above the text area.
- **Text Area:** `CTkTextbox` set to read-only, dark background, supporting auto-scroll.
- **Format:** `[HH:MM:SS] Message`.

## 4. Implementation Details
- **Library:** `customtkinter` (already installed).
- **Icons:** Use `CTkImage` with standard icons (can use unicode characters or placeholder images if external assets are not available, but prefer standard icons).
- **Integration:** Maintain existing `ReaderService` and `EventManager` logic. Update `App` class in `gui.py` to inherit or use CTk components.

## 5. Success Criteria
- [ ] UI looks modern and matches the layout of the screenshot.
- [ ] All existing functionality (Connect, Issue, Erase, Info) works correctly.
- [ ] Dark theme is applied consistently.
- [ ] Responsive layout (widgets resize correctly with the window).
- [ ] Localization is maintained for all new/updated strings.
