from typing import Dict, List, Callable, Type, Final, TypeVar
from dataclasses import dataclass

T = TypeVar('T', bound='Event')

@dataclass(frozen=True)
class Event:
    """Базовий клас для всіх подій."""
    pass

@dataclass(frozen=True)
class LogEvent(Event):
    """Подія для логування повідомлення."""
    message: str

@dataclass(frozen=True)
class PortsUpdatedEvent(Event):
    """Подія, що сповіщає про оновлення списку портів."""
    ports: List[str]
    port_map: Dict[str, str]

@dataclass(frozen=True)
class ConnectionStatusEvent(Event):
    """Подія про зміну статусу підключення."""
    is_connected: bool


class EventManager:
    """
    Універсальний менеджер подій.
    Тепер працює з типами подій (класами).
    """
    def __init__(self) -> None:
        self._listeners: Dict[Type[Event], List[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: Type[T], callback: Callable[[T], None]) -> None:
        """Підписує слухача на певний тип події."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)  # type: ignore

    def unsubscribe(self, event_type: Type[T], callback: Callable[[T], None]) -> None:
        """Відписує слухача від події."""
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(callback)  # type: ignore
            except ValueError:
                # Ігноруємо помилку, якщо слухач вже був відписаний
                pass

    def dispatch(self, event: Event) -> None:
        """Сповіщає всіх слухачів про подію, передаючи об'єкт події."""
        event_type = type(event)
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Помилка при виклику слухача для події '{event_type.__name__}': {e}")
