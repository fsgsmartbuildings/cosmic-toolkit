from abc import ABCMeta, abstractmethod
from typing import Any, Type

from cosmic_toolkit.models import Entity


class AbstractRepository(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        self.seen = set()

    def __init_subclass__(cls, entity_type: Type[Entity], **kwargs):
        if not issubclass(entity_type, Entity):
            raise TypeError(f"Entity must inherit from {Entity.__name__}")

        cls._entity_type = entity_type

    def _check_entity_type(self, entity):
        if not type(entity) == self._entity_type:
            raise TypeError(f"Expecting entity of type {self._entity_type.__name__}")

    async def add(self, entity: Entity):
        self._check_entity_type(entity)

        await self._add(entity)
        self.seen.add(entity)

    async def get(self, id: Any) -> Entity:
        entity = await self._get(id)

        if entity:
            self.seen.add(entity)

        return entity

    async def update(self, entity):
        self._check_entity_type(entity)

        await self._update(entity)
        self.seen.add(entity)

    @abstractmethod
    async def _add(self, entity: Entity):
        ...

    @abstractmethod
    async def _get(self, id: str) -> Entity:
        ...

    @abstractmethod
    async def _update(self, entity: Entity):
        ...
