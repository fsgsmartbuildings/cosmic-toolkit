from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List

from pydantic import BaseModel


class Event(BaseModel):
    ...


class Entity(metaclass=ABCMeta):
    _events: List[Event]

    def __init__(self, *args, **kwargs):
        self._events = []

    @classmethod
    @abstractmethod
    def init(cls, *args, **kwargs) -> "Entity":
        ...

    @property
    def events(self) -> List[Event]:
        return self._events

    @abstractmethod
    def dict(self) -> Dict[str, Any]:
        ...

    class DoesNotExist(Exception):
        ...
