from random import randint
from typing import Any, Dict, Optional

from cosmic_toolkit.models import Entity


class User(Entity):
    def __init__(self, id: int, name: str, is_active: bool):
        super().__init__()
        self._id = id
        self._is_active = is_active
        self._name = name

    @classmethod
    def init(
        cls, name: str, id: Optional[int] = None, is_active: Optional[bool] = True
    ) -> "User":
        if not id:
            id = randint(100, 10000)

        return cls(id, name, is_active)

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    def dict(self) -> Dict[str, Any]:
        return {"id": self._id, "name": self._name}


class Vehicle(Entity):
    def __init__(self, color: str):
        super().__init__()
        self._color = color

    @classmethod
    def init(cls, color: str) -> "Vehicle":
        return cls(color)

    def dict(self) -> Dict[str, Any]:
        return {
            "color": self._color,
        }


def test_entity_repr():
    user = User.init("Gemma G")
    id = user.id

    assert user.__repr__() == f"User(id={id}, name='Gemma G')"


def test_entity_repr_no_properties():
    vehicle = Vehicle.init("red")

    assert vehicle.__repr__() == f"Vehicle()"
