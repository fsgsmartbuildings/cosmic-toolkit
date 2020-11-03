from typing import Any, Dict, Type

import pytest

from cosmic_toolkit import (
    AbstractRepository,
    BaseUnitOfWork,
    Entity,
    Event,
)


class EntityA(Entity):
    def init(cls, *args, **kwargs) -> "Entity":
        return cls()

    def dict(self) -> Dict[str, Any]:
        return {}


class EntityB(EntityA):
    def init(cls, *args, **kwargs) -> "Entity":
        return cls()

    def dict(self) -> Dict[str, Any]:
        return {}


class ATriggered(Event):
    ...


class BTriggered(Event):
    ...


class TestRepositoryA(AbstractRepository, entity_type=EntityA):
    async def _add(self, entity: EntityA):
        ...

    async def _get(self, id: str) -> EntityA:
        ...

    async def _update(self, entity: EntityA):
        ...


class TestRepositoryB(AbstractRepository, entity_type=EntityB):
    async def _add(self, entity: EntityA):
        ...

    async def _get(self, id: str) -> EntityA:
        ...

    async def _update(self, entity: EntityA):
        ...


class TestUnitOfWork(
    BaseUnitOfWork,
    a_items=TestRepositoryA,
    b_items=TestRepositoryB,
):
    async def commit(self):
        ...

    async def rollback(self):
        ...


@pytest.fixture
def test_entities() -> Dict[str, Type[Entity]]:
    return {
        "EntityA": EntityA,
        "EntityB": EntityB,
    }


@pytest.fixture
def test_events() -> Dict[str, Type[Event]]:
    return {
        "ATriggered": ATriggered,
        "BTriggered": BTriggered,
    }


@pytest.fixture
def test_repositories() -> Dict[str, Type[TestRepositoryA]]:
    return {
        "TestRepositoryA": TestRepositoryA,
        "TestRepositoryB": TestRepositoryB,
    }


@pytest.fixture
def test_unit_of_work() -> Type[TestUnitOfWork]:
    return TestUnitOfWork
