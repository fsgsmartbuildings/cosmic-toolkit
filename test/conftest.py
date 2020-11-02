from typing import Dict, Type

import pytest

from src.models import Entity, Event
from src.repository import AbstractRepository
from src.unit_of_work import BaseUnitOfWork


class EntityA(Entity):
    ...


class EntityB(EntityA):
    ...


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
