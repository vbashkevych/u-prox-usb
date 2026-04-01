import threading
import time
from typing import Optional, Dict, List
from serial.tools import list_ports
import serial

from protocol import UProxProtocol, SerialCommunicator
from events import EventManager, LogEvent, PortsUpdatedEvent, ConnectionStatusEvent

# VID та PID для чіпа Silicon Labs CP210x
UPROX_VID: int = 0x10C4
UPROX_PID: int = 0xEA60

class ReaderService:
    """
    Клас бізнес-логіки. Генерує об'єкти подій для UI.
    """
    def __init__(self, event_manager: EventManager) -> None:
        self.events: EventManager = event_manager
        self.communicator: Optional[SerialCommunicator] = None
        self.is_connected: bool = False

    def connect(self, port: str) -> None:
        try:
            self.communicator = SerialCommunicator(port, read_callback=self._handle_incoming_data)
            self.communicator.connect()
            self.is_connected = True
            self.events.dispatch(LogEvent(f"Успішно підключено до {port}."))
            self.events.dispatch(ConnectionStatusEvent(is_connected=True))
            self.get_device_info()
        except serial.SerialException as e:
            self.is_connected = False
            self.events.dispatch(LogEvent(f"Помилка: не вдалося відкрити порт {port}. {e}"))

    def disconnect(self) -> None:
        if self.communicator:
            self.communicator.disconnect()
        self.is_connected = False
        self.communicator = None
        self.events.dispatch(LogEvent("Порт закрито."))
        self.events.dispatch(ConnectionStatusEvent(is_connected=False))

    def _handle_incoming_data(self, data: bytes) -> None:
        if data == b'--SERIAL_ERROR--':
            self.events.dispatch(LogEvent("Помилка читання порту. З'єднання втрачено."))
            self.disconnect()
            return
        
        line = data.decode('utf-8', errors='ignore').rstrip()
        if line:
            self.events.dispatch(LogEvent(f"<- {line}"))

    def _send_command(self, command_bytes: bytes, command_name: str) -> None:
        if not self.is_connected or not self.communicator:
            self.events.dispatch(LogEvent("Помилка: немає підключення до пристрою."))
            return
        self.communicator.send(command_bytes)
        self.events.dispatch(LogEvent(f"-> {command_name}"))

    # --- Публічні методи для виклику з UI ---

    def get_device_info(self) -> None:
        self._send_command(UProxProtocol.get_device_info(), "Get Info")

    def set_mifare_plus_sl3_encryption(self, password: str) -> None:
        if len(password) != 32:
            self.events.dispatch(LogEvent("Помилка: Пароль для SL3 повинен мати довжину 32 HEX-символи."))
            return
        command = UProxProtocol.set_mifare_plus_sl3_encryption(password)
        self._send_command(command, f"Set SL3 Key (mp{password[:4]}...)")

    def set_mifare_start_number(self, start_number: str) -> None:
        if len(start_number) != 10:
            self.events.dispatch(LogEvent("Помилка: Стартовий номер повинен мати довжину 10 HEX-символів."))
            return
        command = UProxProtocol.set_mifare_start_number(start_number)
        self._send_command(command, f"Set Start Num (ms{start_number})")

    def start_issue_sl3(self) -> None:
        self._send_command(UProxProtocol.start_issue_sl3(), "Start Issue SL3")

    def erase_mifare_card(self) -> None:
        self._send_command(UProxProtocol.erase_mifare_card(), "Erase Card")

    def stop_issue(self) -> None:
        self._send_command(UProxProtocol.stop_issue(), "Stop Issue")

    def probe_ports(self) -> None:
        threading.Thread(target=self._probe_ports_worker, daemon=True).start()

    def _probe_ports_worker(self) -> None:
        self.events.dispatch(LogEvent("Пошук COM портів..."))
        ports = list_ports.comports()
        potential_ports = [p for p in ports if p.vid == UPROX_VID and p.pid == UPROX_PID]
        other_ports = [p for p in ports if p.vid != UPROX_VID or p.pid != UPROX_PID]
        
        confirmed_port_info: Optional[Dict[str, any]] = None
        for port in potential_ports:
            try:
                temp_ser = serial.Serial(port.device, 9600, timeout=0.2)
                temp_ser.write(UProxProtocol.get_device_info())
                time.sleep(0.1)
                response = temp_ser.read(200).decode('utf-8', errors='ignore')
                if "MODEL DESKTOP READER" in response:
                    serial_num = next((line.split()[-1] for line in response.splitlines() if line.startswith("SERIAL")), "N/A")
                    confirmed_port_info = {"port": port, "serial": serial_num}
                    break
            except (OSError, serial.SerialException):
                continue
            finally:
                if 'temp_ser' in locals() and temp_ser.is_open:
                    temp_ser.close()

        port_list_for_ui: List[str] = []
        port_map: Dict[str, str] = {}

        if confirmed_port_info:
            p = confirmed_port_info["port"]
            desc = f"{p.device} - DESKTOP READER (SN: {confirmed_port_info['serial']})"
            port_list_for_ui.append(desc)
            port_map[desc] = p.device
            potential_ports = [port for port in potential_ports if port.device != p.device]

        for p in potential_ports:
            desc = f"{p.device} - {p.description} [РЕКОМЕНДОВАНО]"
            port_list_for_ui.append(desc)
            port_map[desc] = p.device
            
        for p in other_ports:
            desc = f"{p.device} - {p.description}"
            port_list_for_ui.append(desc)
            port_map[desc] = p.device

        self.events.dispatch(PortsUpdatedEvent(ports=port_list_for_ui, port_map=port_map))
