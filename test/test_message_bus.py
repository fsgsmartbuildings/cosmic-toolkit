from typing import List, Optional, Tuple

import pytest

from cosmic_toolkit import (
    AbstractRepository,
    AggregateRoot,
    BaseUnitOfWork,
    Entity,
    Event,
    MessageBus,
)
from cosmic_toolkit.types import NormalDict

pytestmark = pytest.mark.asyncio


class TelemetryReceived(Event):
    message: str


class Telemetry(AggregateRoot):
    def __init__(self, id: int, message: str):
        super().__init__()

        self._id = id
        self._message = message

    @classmethod
    def init(cls, message: str, id: Optional[int] = None) -> "Telemetry":
        if not id:
            id = hash(message)

        return cls(id, message)

    @property
    def id(self) -> int:
        return self._id

    @property
    def message(self) -> str:
        return self._message

    def dict(self) -> NormalDict:
        return {
            "id": self._id,
            "message": self._message,
        }


class TelemetryRepository(AbstractRepository, entity_type=Telemetry):
    def __init__(self):
        super().__init__()

        self._items = {}

    async def _add(self, entity: Telemetry):
        self._items[hash(entity.message)] = entity

    async def _get(self, id: str) -> Telemetry:
        return self._items[id]

    async def _update(self, entity: Telemetry):
        return self._add(entity)


class UnitOfWork(BaseUnitOfWork, telemetry=TelemetryRepository):
    async def commit(self):
        ...

    async def rollback(self):
        ...


Log = List[Tuple[int, str]]


class TelemetryLog:
    _log: Log

    def __init__(self):
        self._log = []

    @property
    def log(self) -> Log:
        return self._log

    def add(self, id: int, message: str):
        self._log.append((id, message))


async def record_telemetry(event: TelemetryReceived, uow: BaseUnitOfWork):
    async with uow:
        point = Telemetry.init(event.message)

        await uow.telemetry.add(point)
        await uow.commit()


async def update_log(event: TelemetryReceived, uow: BaseUnitOfWork, log: TelemetryLog):
    telemetry_id = hash(event.message)

    async with uow:
        point = await uow.telemetry.get(telemetry_id)

    log.add(telemetry_id, point.message)


async def test_message_bus_handle():
    log = TelemetryLog()
    uow = UnitOfWork()

    message_bus = MessageBus(
        {
            TelemetryReceived: [record_telemetry, update_log],
        },
        log=log,
        uow=uow,
    )
    event_a = TelemetryReceived(message="test123")
    event_a_id = hash(event_a.message)

    # Publish message to bus and expect it to be handled
    await message_bus.handle(event_a)

    # Check that telemetry was saved
    expected_data_point = await uow.telemetry.get(event_a_id)
    data = expected_data_point.dict()

    assert data["id"] == event_a_id
    assert data["message"] == event_a.message

    # Publish another message
    event_b = TelemetryReceived(message="hello_world")
    event_b_id = hash(event_b.message)

    await message_bus.handle(event_b)

    # Check that log was updated
    assert len(log.log) == 2
    assert log.log[0] == (event_a_id, event_a.message)
    assert log.log[1] == (event_b_id, event_b.message)


def test_message_bus_add_dependencies():
    log = TelemetryLog()
    uow = UnitOfWork()

    message_bus = MessageBus({}, uow=uow)

    assert len(message_bus.dependencies.values()) == 1
    assert message_bus.dependencies["uow"] == UnitOfWork()

    # Now add a dependency
    message_bus.add_dependencies(log=log)

    assert len(message_bus.dependencies.values()) == 2
    assert message_bus.dependencies["log"] == log


async def test_message_bus_handle_ignore_missing_handler():
    message_bus = MessageBus({}, ignore_missing_handlers=True)
    event_a = TelemetryReceived(message="test123")

    # Nothing happens
    await message_bus.handle(event_a)


async def test_message_bus_handle_raise_error_on_missing_handler():
    # By default, ignore_missing_handlers=False
    message_bus = MessageBus({})
    event_a = TelemetryReceived(message="test123")

    with pytest.raises(RuntimeError):
        await message_bus.handle(event_a)
