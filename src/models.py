from typing import List

from pydantic import BaseModel


class Event(BaseModel):
    ...


class Entity:
    _events: List[Event]

    def __init__(self, *args, **kwargs):
        self._events = []

    @property
    def events(self) -> List[Event]:
        return self._events
