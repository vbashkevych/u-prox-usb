import serial
import threading
import asyncio
from typing import Optional, Callable, Final

class UProxProtocol:
    """
    Формує команди протоколу U-Prox Desktop.
    Не знає нічого про серійний порт, тільки про байти.
    """
    
    # Команди як константи
    CMD_INFO: Final[bytes] = b'i'
    CMD_ERASE: Final[bytes] = b'z\r\n'
    CMD_STOP: Final[bytes] = b'stop\r\n'
    CMD_START_SL3: Final[bytes] = b'sl3\r\n'

    @staticmethod
    def get_device_info() -> bytes:
        """Отримати інформацію про пристрій."""
        return UProxProtocol.CMD_INFO

    @staticmethod
    def set_mifare_plus_sl3_encryption(password: str, diversification: bool = False) -> bytes:
        """Встановити ключ шифрування Mifare Plus SL3."""
        div_param = ',1' if diversification else ''
        return f"mp{password}{div_param}\r\n".encode('utf-8')

    @staticmethod
    def set_mifare_start_number(start_number: str) -> bytes:
        """Встановити стартовий номер Mifare."""
        return f"ms{start_number}\r\n".encode('utf-8')

    @staticmethod
    def start_issue_sl3() -> bytes:
        """Почати емісію SL3."""
        return UProxProtocol.CMD_START_SL3

    @staticmethod
    def erase_mifare_card() -> bytes:
        """Стерти картку Mifare."""
        return UProxProtocol.CMD_ERASE

    @staticmethod
    def stop_issue() -> bytes:
        """Зупинити емісію."""
        return UProxProtocol.CMD_STOP


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

    async def __aenter__(self) -> 'SerialCommunicator':
        await self.connect_async()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.disconnect_async()

    def connect(self) -> None:
        """Синхронне підключення."""
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=0.1)
            self._is_running = True
            self._reader_thread = threading.Thread(target=self._read_loop, name=f"ReaderThread-{self.port}")
            self._reader_thread.daemon = True
            self._reader_thread.start()
        except serial.SerialException as e:
            raise e

    async def connect_async(self) -> None:
        """Асинхронне підключення."""
        await asyncio.to_thread(self.connect)

    def disconnect(self) -> None:
        """Синхронне відключення."""
        self._is_running = False
        if self._reader_thread:
            self._reader_thread.join(timeout=1.0)
        if self.ser and self.ser.is_open:
            self.ser.close()

    async def disconnect_async(self) -> None:
        """Асинхронне відключення."""
        await asyncio.to_thread(self.disconnect)

    def send(self, data: bytes) -> None:
        """Синхронна відправка даних."""
        if self.ser and self.ser.is_open:
            self.ser.write(data)

    async def send_async(self, data: bytes) -> None:
        """Асинхронна відправка даних."""
        await asyncio.to_thread(self.send, data)

    def _read_loop(self) -> None:
        """Цикл читання (виконується в окремому потоці)."""
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
