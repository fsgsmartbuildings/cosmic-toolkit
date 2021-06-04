from datetime import datetime
from random import randint
from typing import Any, List, Optional, Tuple
from uuid import UUID, uuid4

import pytest

from cosmic_toolkit import AggregateRoot, DefaultJSONSerializer, Entity, Event
from cosmic_toolkit.types import NormalDict

# Aggregates consist of one or more child entities
# We need an aggregate root to create an aggregate
# Aggregates capture domain events


class ConstraintViolation(Exception):
    ...


class ValidationError(Exception):
    ...


class Suite(Entity):
    def __init__(self, number: str, name: str, floor: int, sqft: int, leased: bool):
        self._floor = floor
        self._leased = leased
        self._name = name
        self._number = number
        self._sqft = sqft

    @classmethod
    def init(
        cls,
        number: str,  # str because "number" can include/be letters (e.g. 201B)
        name: str,
        floor: int,
        sqft: int,
        leased: bool,
    ) -> "Suite":
        # Ensure floor makes sense
        if not -25 < floor < 125:
            raise ValueError(f"Floor number {floor} is invalid")

        return cls(
            number,
            name,
            floor,
            sqft,
            leased,
        )

    @property
    def leased(self) -> bool:
        return self._leased

    @property
    def number(self) -> str:
        return self._number

    @property
    def sqft(self) -> int:
        return self._sqft

    def dict(self) -> NormalDict:
        return {
            "name": self._name,
            "number": self._number,
            "floor": self._floor,
            "sqft": self._sqft,
            "leased": self._leased,
        }

    def lease(self):
        if self.leased:
            raise ConstraintViolation("Suite is already leased")

        self._leased = True

    def make_available(self):
        if not self.leased:
            raise ConstraintViolation("Suite is already available")

        self._leased = False


class Address:
    """Address value object"""

    def __init__(
        self,
        street_line_1: str,
        locality: str,
        region: str,
        postal_code: str,
        country_code_iso_alpha_3: str,
        street_line_2: Optional[str] = None,
    ):
        if len(country_code_iso_alpha_3) != 3:
            raise ValueError("Country code is expected to be of len")

        country_code_iso_alpha_3 = country_code_iso_alpha_3.upper()

        if country_code_iso_alpha_3 not in ["AUS", "CAN", "CYM", "LCA", "RWA", "USA"]:
            raise ValueError(f"Country {country_code_iso_alpha_3!r} is not supported")

        self._country_code = country_code_iso_alpha_3
        self._locality = locality
        self._postal_code = postal_code
        self._region = region
        self._street_line_1 = street_line_1
        self._street_line_2 = street_line_2

    def dict(self) -> NormalDict:
        return {
            "street_line_1": self._street_line_1,
            "street_line_2": self._street_line_2,
            "locality": self._locality,
            "region": self._region,
            "postal_code": self._postal_code,
            "country_code_iso_alpha_3": self._country_code,
        }


class SuiteAdded(Event):
    building_id: UUID
    number: str


class SuiteLeased(SuiteAdded):
    ...


class SuiteMadeAvailable(SuiteAdded):
    ...


class SuiteRemoved(Event):
    building_id: UUID
    name: str
    number: str


class Building(AggregateRoot, Entity):
    def __init__(self, id: UUID, name: str, address: Address, suites: List[Suite]):
        super().__init__()
        self._id = id
        self._address = address
        self._name = name
        self._suites = {s.number: s for s in suites}

    @classmethod
    def init(
        cls,
        name: str,
        address: Address,
        id: Optional[UUID] = None,
        suites: Optional[List[Suite]] = None,
    ) -> "Building":
        if not id:
            id = uuid4()

        return cls(
            id,
            name,
            address,
            suites or [],
        )

    @property
    def suites(self) -> List[Suite]:
        return [v for v in self._suites.values()]

    def _get_suite(self, suite: Suite) -> Suite:
        _suite = self._suites.get(suite.number)

        if not _suite:
            raise ValueError(f"Suite {suite!r} does not exist")

        return _suite

    def add_suite(self, suite: Suite):
        if suite.number not in self._suites:
            self._suites[suite.number] = suite

            self._add_event(SuiteAdded(building_id=self._id, number=suite.number))
        else:
            raise ConstraintViolation("Suite already exists; update if need be")

    def lease_suite(self, suite: Suite):
        _suite = self._get_suite(suite)
        _suite.lease()

        self._add_event(SuiteLeased(building_id=self._id, number=suite.number))

    def make_suite_available(self, suite: Suite):
        _suite = self._get_suite(suite)
        _suite.make_available()

        self._add_event(SuiteMadeAvailable(building_id=self._id, number=suite.number))

    def remove_suite(self, suite: Suite):
        if suite.number not in self._suites:
            raise ValueError(f"Suite {suite!r} does not exist")

        suite_data = self._suites[suite.number].dict()
        del self._suites[suite.number]

        self._add_event(
            SuiteRemoved(
                building_id=self._id,
                name=suite_data["name"],
                number=suite_data["number"],
            )
        )

    def dict(self) -> NormalDict:
        return {
            "id": self._id,
            "address": self._address,
            "name": self._name,
            "suites": self.suites,
        }


def test_aggregate_root():
    # Create instance of building and its child entities/VOs
    address = Address(
        street_line_1="30 Rockefeller Plaza",
        locality="New York",
        region="NY",
        postal_code="10111",
        country_code_iso_alpha_3="USA",
    )

    suite_a = Suite.init("6700", "Top of the Rock", 67, 755602, True)
    suite_b = Suite.init("1280", "Suite 1280", 12, 1995, True)

    thirty_rock = Building.init(
        "30 Rockefeller Center",
        address,
        suites=[suite_a, suite_b],
    )

    # Test domain events
    with pytest.raises(ConstraintViolation):
        thirty_rock.lease_suite(suite_a)

    thirty_rock.make_suite_available(suite_b)

    suite_c = Suite.init("1735", "Suite 1735", 17, 1735, False)
    thirty_rock.add_suite(suite_c)

    thirty_rock.lease_suite(suite_c)

    suite_d = Suite.init("109", "Lobby Concessions", 1, 144, False)
    thirty_rock.add_suite(suite_d)

    thirty_rock.remove_suite(suite_d)

    # We expect five domain events
    event_1 = next(thirty_rock.events)
    event_2 = next(thirty_rock.events)
    event_3 = next(thirty_rock.events)
    event_4 = next(thirty_rock.events)
    event_5 = next(thirty_rock.events)

    event_5_data = event_5.dict()

    assert event_5_data["name"] == "Lobby Concessions"
    assert event_5_data["number"] == "109"

    # Now there shouldn't be any more events

    with pytest.raises(StopIteration):
        next(thirty_rock.events)

    assert isinstance(event_1, SuiteMadeAvailable)
    assert isinstance(event_2, SuiteAdded)
    assert isinstance(event_3, SuiteLeased)
    assert isinstance(event_4, SuiteAdded)
    assert isinstance(event_5, SuiteRemoved)


# Sample entities and tests
# Test basic entity functionality sans AggregateRoot


class Sensor(Entity):
    def __init__(self, id: UUID, name: str, installed_on: datetime):
        self._id = id
        self._name = name
        self._installed_on = installed_on

    @classmethod
    def init(
        cls,
        name: str,
        installed_on: datetime,
        id: Optional[UUID] = None,
    ) -> "Sensor":
        if not id:
            id = uuid4()

        return cls(id, name, installed_on)

    def dict(self) -> NormalDict:
        return {
            "id": self._id,
            "name": self._name,
            "installed_on": self._installed_on,
        }


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

    def dict(self) -> NormalDict:
        return {"id": self._id, "name": self._name}


class Vehicle(Entity):
    def __init__(self, color: str):
        super().__init__()
        self._color = color

    @classmethod
    def init(cls, color: str) -> "Vehicle":
        return cls(color)

    def dict(self) -> NormalDict:
        return {
            "color": self._color,
        }


def test_entity_eq():
    assert Vehicle.init("green") == Vehicle.init("green")


def test_entity_hash_uuid_datetime():
    sensor = Sensor.init(
        "Humidity",
        datetime.now(),
    )

    # This checks that the json serialize used by Entity.__hash__ supports
    # datetime.datetime and UUID
    assert isinstance(hash(sensor), int)


def test_entity_repr():
    user = User.init("Gemma G")
    id = user.id

    assert user.__repr__() == f"User(id={id}, name='Gemma G')"


def test_entity_repr_no_properties():
    vehicle = Vehicle.init("red")

    assert vehicle.__repr__() == f"Vehicle()"


# Test using a custom serializer for hashing
# A custom serializer is necessary for types not supported by the json serializer


class Astronaut(Entity):
    def __init__(self, id: UUID, name: str):
        self._id = id
        self._name = name

    @classmethod
    def init(cls, name: str, id: Optional[UUID] = None) -> "Astronaut":
        if not id:
            id = uuid4()

        return cls(id, name)

    def dict(self) -> NormalDict:
        return {
            "id": self._id,
            "name": self._name,
        }


class RocketType:
    def __init__(self, name: str):
        if name not in ["falcon_9", "falcon_heavy", "starship"]:
            raise ValueError(f"Unknown rocket type {name!r}")

        self._name = name

    def __str__(self) -> str:
        return self._name


class SpaceDomainSerializer(DefaultJSONSerializer):
    def __call__(self, obj: Any) -> Any:
        if isinstance(obj, Astronaut):
            return obj.dict()
        elif isinstance(obj, RocketType):
            return str(obj)
        else:
            return super().__call__(obj)


class Rocket(AggregateRoot, Entity):
    def __init__(self, name: str, rocket_type: RocketType, astronauts: List[Astronaut]):
        super().__init__()
        self._astronauts = astronauts
        self._name = name
        self._rocket_type = rocket_type

    @classmethod
    def init(
        cls,
        name: str,
        rocket_type: RocketType,
        astronauts: Optional[List[Astronaut]] = None,
    ) -> "Rocket":
        return cls(
            name,
            rocket_type,
            astronauts or [],
        )

    def dict(self) -> NormalDict:
        return {
            "name": self._name,
            "rocket_type": self._rocket_type,
            "astronauts": self._astronauts,
        }


class SpaceShip(AggregateRoot, Entity, default_json_serializer=SpaceDomainSerializer):
    def __init__(self, name: str, rocket_type: RocketType, astronauts: List[Astronaut]):
        super().__init__()
        self._astronauts = astronauts
        self._name = name
        self._rocket_type = rocket_type

    @classmethod
    def init(
        cls,
        name: str,
        rocket_type: RocketType,
        astronauts: Optional[List[Astronaut]] = None,
    ) -> "SpaceShip":
        return cls(
            name,
            rocket_type,
            astronauts or [],
        )

    def dict(self) -> NormalDict:
        return {
            "name": self._name,
            "rocket_type": self._rocket_type,
            "astronauts": self._astronauts,
        }


def _set_up_deps() -> Tuple[Astronaut, RocketType]:
    astronaut = Astronaut.init("Albert II")
    rocket_type = RocketType("falcon_9")

    return astronaut, rocket_type


def test_entity_hash_custom_serializer():
    astronaut, rocket_type = _set_up_deps()
    space_ship = SpaceShip.init("Explorer", rocket_type, [astronaut])

    json = (
        '{"name": "Explorer", "rocket_type": "falcon_9", '
        '"astronauts": [{"id": "%s", "name": "Albert II"}]}'
    ) % (str(astronaut.dict()["id"]))

    assert space_ship.json() == json
    assert isinstance(hash(space_ship), int)


def test_entity_no_custom_serializer_type_error():
    """Not using a custom serializer will raise a type error upon trying to hash"""
    astronaut, rocket_type = _set_up_deps()
    rocket = Rocket.init("Explorer", rocket_type, [astronaut])

    with pytest.raises(TypeError):
        hash(rocket)
