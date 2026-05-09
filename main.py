import customtkinter as ctk
import asyncio
import threading
import sys
from gui import App

def main() -> None:
    """Головна точка входу в програму."""
    # Налаштування CustomTkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Створюємо цикл подій asyncio в окремому потоці
    # Це дозволяє нам виконувати асинхронні операції без блокування UI
    def start_async_loop(loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()

    new_loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_async_loop, args=(new_loop,), daemon=True, name="AsyncLoopThread")
    t.start()

    # Запускаємо CustomTkinter mainloop
    try:
        root = ctk.CTk()
        app = App(root, new_loop)
        root.mainloop()
    except Exception as e:
        print(f"Критична помилка при запуску програми: {e}")
        sys.exit(1)
    finally:
        # Зупиняємо цикл подій при виході
        new_loop.call_soon_threadsafe(new_loop.stop)

if __name__ == "__main__":
    main()
