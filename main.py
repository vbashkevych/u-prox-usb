import serial
import threading
import time
import sys
from queue import Queue

class UProxDesktopReader:
    """
    Клас для взаємодії зі зчитувачем U-Prox Desktop по RS232.
    Працює з чергою для асинхронної передачі повідомлень в UI.
    """
    def __init__(self, port, baud_rate=9600, message_queue=None):
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self._is_running = False
        self._reader_thread = None
        self.queue = message_queue if message_queue else Queue()

    def connect(self):
        """Встановлює з'єднання з портом та запускає потік для читання."""
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=0.1)
            self._is_running = True
            self._reader_thread = threading.Thread(target=self._read_loop)
            self._reader_thread.daemon = True
            self._reader_thread.start()
            self.queue.put(f"Успішно підключено до {self.port}.")
            return True
        except serial.SerialException as e:
            self.queue.put(f"Помилка: не вдалося відкрити порт {self.port}. {e}")
            return False

    def disconnect(self):
        """Закриває з'єднання."""
        if self._is_running:
            self._is_running = False
            if self._reader_thread:
                self._reader_thread.join(timeout=1.0)
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.queue.put("Порт закрито.")

    def _read_loop(self):
        """Цикл, що виконується в окремому потоці та читає дані з порту."""
        self.queue.put("Потік для читання запущено.")
        while self._is_running:
            try:
                if self.ser and self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').rstrip()
                    if line:
                        self.queue.put(f"<- {line}")
            except serial.SerialException:
                self.queue.put("Помилка читання порту. Потік зупинено.")
                break
        self.queue.put("Потік для читання зупинено.")

    def _send_command(self, command, add_crlf=False):
        """Внутрішній метод для відправки команд."""
        if self.ser and self.ser.is_open:
            cmd_to_send = command + ('\r\n' if add_crlf else '')
            self.ser.write(cmd_to_send.encode('utf-8'))
            self.queue.put(f"-> {command.strip()}")
        else:
            self.queue.put("Помилка: порт не відкрито.")

    # --- Команди протоколу ---
    def get_device_info(self):
        self._send_command('i')

    def set_mifare_plus_sl3_encryption(self, password, diversification=False):
        if len(password) != 32:
            self.queue.put("Помилка: Пароль для SL3 повинен мати довжину 32 HEX-символи.")
            return
        div_param = ',1' if diversification else ''
        self._send_command(f"mp{password}{div_param}", add_crlf=True)

    def set_mifare_start_number(self, start_number):
        if len(start_number) != 10:
            self.queue.put("Помилка: Стартовий номер повинен мати довжину 10 HEX-символів.")
            return
        self._send_command(f"ms{start_number}", add_crlf=True)

    def start_issue_sl3(self):
        self._send_command('sl3', add_crlf=True)

    def erase_mifare_card(self):
        self._send_command('z', add_crlf=True)

    def stop_issue(self):
        self._send_command('stop', add_crlf=True)


def console_main():
    """Приклад роботи з класом в консольному режимі (для демонстрації)."""
    PORT = "COM3"
    msg_queue = Queue()
    reader = UProxDesktopReader(port=PORT, message_queue=msg_queue)

    if not reader.connect():
        # Виводимо повідомлення з черги, якщо не вдалося підключитися
        while not msg_queue.empty():
            print(msg_queue.get_nowait())
        sys.exit(1)

    # Потік для виводу повідомлень з черги в консоль
    def print_from_queue():
        while reader._is_running:
            try:
                msg = msg_queue.get(timeout=0.1)
                print(msg)
            except Exception:
                continue

    printer_thread = threading.Thread(target=print_from_queue)
    printer_thread.daemon = True
    printer_thread.start()

    print("\n--- Інтерактивна консоль U-Prox Desktop ---")
    print("Введіть команду або 'exit' для виходу.")
    
    try:
        reader.get_device_info()
        while True:
            cmd_input = input("> ").strip()
            if cmd_input.lower() == "exit":
                break
            if cmd_input:
                # Відправка будь-якої команди напряму
                reader._send_command(cmd_input, add_crlf=(len(cmd_input) > 1))
    except KeyboardInterrupt:
        print("\nЗавершення роботи...")
    finally:
        reader.disconnect()
        time.sleep(0.2) # Дати час на вивід останніх повідомлень

if __name__ == '__main__':
    # Запускаємо консольну версію для перевірки
    console_main()
