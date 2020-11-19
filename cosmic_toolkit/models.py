import inspect
import json
from abc import ABCMeta, abstractmethod
from typing import Generator, List

from pydantic import BaseModel

from cosmic_toolkit.types import NormalDict


class Event(BaseModel):
    ...


class AggregateRoot:
    _events: List[Event]

    def __init__(self, *args, **kwargs):
        self._events = []

    @property
    def events(self) -> Generator[Event, None, None]:
        while self._events:
            yield self._events.pop(0)

    def _add_event(self, event: Event):
        self._events.append(event)


class Entity(metaclass=ABCMeta):
    def __eq__(self, other: "Entity") -> bool:
        return self.dict() == other.dict()

    def __hash__(self) -> int:
        return hash(json.dumps(self.dict()).encode("utf-8"))

    def __repr__(self) -> str:
        """Create entity representation. Searches for entity properties to create
        repr"""
        props = []

        # The next few lines feel hacky but there doesn't seem to be a clear way to
        # find an object's properties.
        # To ensure that properties are found, be sure that @property getters
        # match argument names in __init__().
        #
        # E.g.
        #
        # class User:
        #     def __init__(self, id: int, name: str, is_active: bool):
        #         ...
        #
        #     @property
        #     def id(self) -> int:
        #         ...
        #
        #     @property
        #     def name(self) -> str:
        #         ...
        #
        # >>> user.__repr__()
        # User(id=987, name='Random User')
        constructor_param_names = inspect.signature(self.__init__).parameters.keys()

        for p in dir(self):
            if not callable(p) and p in constructor_param_names:
                props.append(f"{p}={getattr(self, p)!r}")

        return f"{self.__class__.__name__}({', '.join(props)})"

    @classmethod
    @abstractmethod
    def init(cls, *args, **kwargs) -> "Entity":
        ...

    @abstractmethod
    def dict(self) -> NormalDict:
        ...

    class DoesNotExist(Exception):
        ...
