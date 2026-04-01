import serial
import threading
from typing import Optional, Callable

class UProxProtocol:
    """
    Формує команди протоколу U-Prox Desktop.
    Не знає нічого про серійний порт, тільки про байти.
    """
    @staticmethod
    def get_device_info() -> bytes:
        return b'i'

    @staticmethod
    def set_mifare_plus_sl3_encryption(password: str, diversification: bool = False) -> bytes:
        div_param = ',1' if diversification else ''
        return f"mp{password}{div_param}\r\n".encode('utf-8')

    @staticmethod
    def set_mifare_start_number(start_number: str) -> bytes:
        return f"ms{start_number}\r\n".encode('utf-8')

    @staticmethod
    def start_issue_sl3() -> bytes:
        return b'sl3\r\n'

    @staticmethod
    def erase_mifare_card() -> bytes:
        return b'z\r\n'

    @staticmethod
    def stop_issue() -> bytes:
        return b'stop\r\n'


class SerialCommunicator:
    """
    Керує низькорівневою взаємодією з COM-портом.
    Нічого не знає про протокол U-Prox.
    """
    def __init__(self, port: str, baud_rate: int = 9600, read_callback: Optional[Callable[[bytes], None]] = None) -> None:
        self.port: str = port
        self.baud_rate: int = baud_rate
        self.ser: Optional[serial.Serial] = None
        self._is_running: bool = False
        self._reader_thread: Optional[threading.Thread] = None
        self.read_callback: Optional[Callable[[bytes], None]] = read_callback

    def connect(self) -> None:
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=0.1)
            self._is_running = True
            self._reader_thread = threading.Thread(target=self._read_loop)
            self._reader_thread.daemon = True
            self._reader_thread.start()
        except serial.SerialException as e:
            raise e

    def disconnect(self) -> None:
        self._is_running = False
        if self._reader_thread:
            self._reader_thread.join(timeout=1.0)
        if self.ser and self.ser.is_open:
            self.ser.close()

    def send(self, data: bytes) -> None:
        if self.ser and self.ser.is_open:
            self.ser.write(data)

    def _read_loop(self) -> None:
        while self._is_running:
            try:
                if self.ser and self.ser.in_waiting > 0:
                    line = self.ser.readline()
                    if line and self.read_callback:
                        self.read_callback(line)
            except serial.SerialException:
                if self.read_callback:
                    self.read_callback(b'--SERIAL_ERROR--')
                break
