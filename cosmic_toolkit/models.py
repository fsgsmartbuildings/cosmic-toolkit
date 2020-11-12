import inspect
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List

from pydantic import BaseModel


class Event(BaseModel):
    ...


class Entity(metaclass=ABCMeta):
    _events: List[Event]

    def __init__(self, *args, **kwargs):
        self._events = []

    def __repr__(self):
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

    @property
    def events(self) -> List[Event]:
        return self._events

    @abstractmethod
    def dict(self) -> Dict[str, Any]:
        ...

    class DoesNotExist(Exception):
        ...
