from abc import ABCMeta, abstractmethod
from typing import Any, Type

from cosmic_toolkit.models import AggregateRoot


class AbstractRepository(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        self.seen = set()

    def __init_subclass__(cls, entity_type: Type[AggregateRoot], **kwargs):
        if not issubclass(entity_type, AggregateRoot):
            raise TypeError(f"Entity must inherit from {AggregateRoot.__name__}")

        cls._entity_type = entity_type
        cls._init_kwargs = kwargs

    def __repr__(self):
        return f"<{self.__class__.__name__}, entity_type={self._entity_type.__name__}>"

    def _check_entity_type(self, entity):
        if not type(entity) == self._entity_type:
            raise TypeError(f"Expecting entity of type {self._entity_type.__name__}")

    async def add(self, entity: AggregateRoot):
        self._check_entity_type(entity)

        await self._add(entity)
        self.seen.add(entity)

    async def get(self, *args: Any, **kwargs: Any) -> AggregateRoot:
        entity = await self._get(*args, **kwargs)

        if entity:
            self.seen.add(entity)

        return entity

    async def update(self, entity):
        self._check_entity_type(entity)

        await self._update(entity)
        self.seen.add(entity)

    @abstractmethod
    async def _add(self, entity: AggregateRoot):
        ...

    @abstractmethod
    async def _get(self, *args: Any, **kwargs: Any) -> AggregateRoot:
        ...

    @abstractmethod
    async def _update(self, entity: AggregateRoot):
        ...
