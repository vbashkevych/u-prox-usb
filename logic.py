import threading
import time
import asyncio
from typing import Optional, Dict, List, Final
from dataclasses import dataclass
from serial.tools import list_ports
import serial

from protocol import UProxProtocol, SerialCommunicator
from events import EventManager, LogEvent, PortsUpdatedEvent, ConnectionStatusEvent

# VID та PID для чіпа Silicon Labs CP210x
UPROX_VID: Final[int] = 0x10C4
UPROX_PID: Final[int] = 0xEA60

@dataclass(frozen=True)
class PortInfo:
    """Інформація про COM-порт."""
    device: str
    description: str
    serial_number: Optional[str] = None
    is_recommended: bool = False

class ReaderServiceError(Exception):
    """Базовий виняток для сервісу зчитувача."""
    pass

class ReaderConnectionError(ReaderServiceError):
    """Помилка підключення до зчитувача."""
    pass

class ReaderService:
    """
    Клас бізнес-логіки. Генерує об'єкти подій для UI.
    """
    def __init__(self, event_manager: EventManager) -> None:
        self.events: EventManager = event_manager
        self.communicator: Optional[SerialCommunicator] = None
        self.is_connected: bool = False

    async def connect_async(self, port: str) -> None:
        """Асинхронне підключення до зчитувача."""
        try:
            self.communicator = SerialCommunicator(port, read_callback=self._handle_incoming_data)
            await self.communicator.connect_async()
            self.is_connected = True
            self.events.dispatch(LogEvent(f"Успішно підключено до {port}."))
            self.events.dispatch(ConnectionStatusEvent(is_connected=True))
            await self.get_device_info_async()
        except serial.SerialException as e:
            self.is_connected = False
            self.events.dispatch(LogEvent(f"Помилка: не вдалося відкрити порт {port}. {e}"))
            raise ReaderConnectionError(str(e))

    async def disconnect_async(self) -> None:
        """Асинхронне відключення."""
        if self.communicator:
            await self.communicator.disconnect_async()
        self.is_connected = False
        self.communicator = None
        self.events.dispatch(LogEvent("Порт закрито."))
        self.events.dispatch(ConnectionStatusEvent(is_connected=False))

    def _handle_incoming_data(self, data: bytes) -> None:
        """Обробка вхідних даних (викликається з потоку читання)."""
        if data == b'--SERIAL_ERROR--':
            self.events.dispatch(LogEvent("Помилка читання порту. З'єднання втрачено."))
            # Оскільки це викликається з потоку, ми використовуємо root.after в GUI
            # або диспетчеризацію події, яка ініціює disconnect_async
            # Для простоти поки просто диспатчимо подію
            self.events.dispatch(ConnectionStatusEvent(is_connected=False))
            return
        
        line = data.decode('utf-8', errors='ignore').rstrip()
        if line:
            self.events.dispatch(LogEvent(f"<- {line}"))

    async def _send_command_async(self, command_bytes: bytes, command_name: str) -> None:
        """Внутрішній асинхронний метод для відправки команд."""
        if not self.is_connected or not self.communicator:
            self.events.dispatch(LogEvent("Помилка: немає підключення до пристрою."))
            return
        await self.communicator.send_async(command_bytes)
        self.events.dispatch(LogEvent(f"-> {command_name}"))

    # --- Публічні асинхронні методи для виклику з UI ---

    async def get_device_info_async(self) -> None:
        await self._send_command_async(UProxProtocol.get_device_info(), "Get Info")

    async def set_mifare_plus_sl3_encryption_async(self, password: str) -> None:
        if len(password) != 32:
            self.events.dispatch(LogEvent("Помилка: Пароль для SL3 повинен мати довжину 32 HEX-символи."))
            return
        command = UProxProtocol.set_mifare_plus_sl3_encryption(password)
        await self._send_command_async(command, f"Set SL3 Key (mp{password[:4]}...)")

    async def set_mifare_start_number_async(self, start_number: str) -> None:
        if len(start_number) != 10:
            self.events.dispatch(LogEvent("Помилка: Стартовий номер повинен мати довжину 10 HEX-символів."))
            return
        command = UProxProtocol.set_mifare_start_number(start_number)
        await self._send_command_async(command, f"Set Start Num (ms{start_number})")

    async def start_issue_sl3_async(self) -> None:
        await self._send_command_async(UProxProtocol.start_issue_sl3(), "Start Issue SL3")

    async def erase_mifare_card_async(self) -> None:
        await self._send_command_async(UProxProtocol.erase_mifare_card(), "Erase Card")

    async def stop_issue_async(self) -> None:
        await self._send_command_async(UProxProtocol.stop_issue(), "Stop Issue")

    async def probe_ports_async(self) -> None:
        """Асинхронний пошук портів."""
        self.events.dispatch(LogEvent("Пошук COM портів..."))
        
        ports = await asyncio.to_thread(list_ports.comports)
        potential_ports = [p for p in ports if p.vid == UPROX_VID and p.pid == UPROX_PID]
        other_ports = [p for p in ports if p.vid != UPROX_VID or p.pid != UPROX_PID]
        
        confirmed_port: Optional[PortInfo] = None
        
        # Перевіряємо потенційні порти паралельно (або послідовно, але асинхронно)
        for port in potential_ports:
            info = await self._check_port_for_reader(port.device)
            if info:
                confirmed_port = info
                break

        # Формуємо список для UI
        port_list_for_ui: List[str] = []
        port_map: Dict[str, str] = {}

        if confirmed_port:
            desc = f"{confirmed_port.device} - DESKTOP READER (SN: {confirmed_port.serial_number})"
            port_list_for_ui.append(desc)
            port_map[desc] = confirmed_port.device
            potential_ports = [p for p in potential_ports if p.device != confirmed_port.device]

        for p in potential_ports:
            desc = f"{p.device} - {p.description} [РЕКОМЕНДОВАНО]"
            port_list_for_ui.append(desc)
            port_map[desc] = p.device
            
        for p in other_ports:
            desc = f"{p.device} - {p.description}"
            port_list_for_ui.append(desc)
            port_map[desc] = p.device

        self.events.dispatch(PortsUpdatedEvent(ports=port_list_for_ui, port_map=port_map))

    async def _check_port_for_reader(self, port_device: str) -> Optional[PortInfo]:
        """Допоміжний метод для перевірки, чи є на порту зчитувач."""
        try:
            # Використовуємо SerialCommunicator для перевірки
            async with SerialCommunicator(port_device, 9600) as sc:
                # Оскільки читання асинхронне через колбек, нам треба почекати відповіді
                # Для простоти тут використаємо пряме читання в потоці
                def check():
                    with serial.Serial(port_device, 9600, timeout=0.2) as ser:
                        ser.write(UProxProtocol.get_device_info())
                        time.sleep(0.1)
                        response = ser.read(200).decode('utf-8', errors='ignore')
                        if "MODEL DESKTOP READER" in response:
                            serial_num = next((line.split()[-1] for line in response.splitlines() if line.startswith("SERIAL")), "N/A")
                            return serial_num
                    return None
                
                serial_num = await asyncio.to_thread(check)
                if serial_num:
                    return PortInfo(device=port_device, description="U-Prox Desktop Reader", serial_number=serial_num, is_recommended=True)
        except (OSError, serial.SerialException):
            pass
        return None
