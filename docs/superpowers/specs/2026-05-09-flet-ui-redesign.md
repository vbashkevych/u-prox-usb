# Flet UI Redesign Specification

## Overview
This document specifies the redesign of the U-Prox-USB application UI using the Flet framework, based on the provided screenshot. The goal is to migrate from Tkinter to a modern, dark-themed Flet interface.

## Visual Design
- **Theme**: `ft.ThemeMode.DARK`
- **Colors**:
    - Primary Background: Dark Grey/Black (approx #121212)
    - Sidebar Background: Slightly lighter Dark Grey (approx #1E1E1E)
    - Borders: Subtle Grey (#333333)
    - Text: White/Off-white
- **Typography**: Sans-serif (default Flet font)
- **Geometry**: Rounded corners (border-radius: 8-12) for containers and buttons.

## Layout Structure
The application window will be divided into two main sections using a horizontal `ft.Row`.

### 1. Sidebar (Left)
- **Width**: Fixed (approx 250px)
- **Components**:
    - Vertical list of actionable items:
        - "Випуск картки" (Icon: CREDIT_CARD)
        - "Зупинити випуск" (Icon: STOP_CIRCLE)
        - "Стирання карти" (Icon: DELETE_OUTLINE)
    - Separator line.
    - "Налаштування" (Icon: SETTINGS) at the bottom or below the separator.

### 2. Main Content (Right)
- **Expansion**: Fills remaining space (`expand=True`).
- **Structure**: Vertical `ft.Column`.
    - **Header Row**:
        - Label: "COM Порт"
        - Dropdown: List of available COM ports.
        - Refresh Button: Circular arrow icon.
        - Connect Button: "Підключити" with a cable/plug icon.
        - Info Button: 'i' icon aligned to the far right.
    - **Log Area**:
        - Title: "Логи"
        - Container: Bordered box with a `ft.ListView` inside.
        - Auto-scrolling enabled for logs.
        - Log format: `[HH:MM:SS] Message`

## Technical Implementation
- **Entry Point**: `flet_main.py`
- **Components**: `ui_components.py`
- **Logic Integration**: 
    - Use `ReaderService` from `logic.py`.
    - Adapt `ReaderService` to emit events or call Flet-compatible callbacks for logging and port updates.
- **State Management**: Reactive UI updates using Flet's `page.update()` or specific component updates.

## Success Criteria
- The UI visually matches the provided screenshot.
- User can select a COM port and connect/disconnect.
- Logs from the device are displayed in real-time.
- All buttons trigger their respective logic in `ReaderService`.
