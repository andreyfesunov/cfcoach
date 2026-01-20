from typing import Callable, Type, TypeVar, Dict, List, Any
from collections import defaultdict
import asyncio

T = TypeVar("T")


class EventBus:
    def __init__(self) -> None:
        self._handlers: Dict[Type[Any], List[Callable[[Any], Any]]] = defaultdict(list)

    def subscribe(self, event_type: Type[T], handler: Callable[[T], Any]) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: T) -> None:
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            result = handler(event)
            if asyncio.iscoroutine(result):
                asyncio.create_task(result)
