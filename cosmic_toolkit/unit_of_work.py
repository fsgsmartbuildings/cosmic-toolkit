from abc import ABCMeta, abstractmethod
from typing import Generator, List

from cosmic_toolkit.models import Event
from cosmic_toolkit.repository import AbstractRepository


class BaseUnitOfWork(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        """Instantiate Unit of Work - arguments are passed into constructors of
        repositories"""
        # Instantiate repositories
        self._repositories = {
            k: v(*args, **kwargs) for k, v in self._repositories.items()
        }

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        cls._repositories = {
            k: v for k, v in kwargs.items() if issubclass(v, AbstractRepository)
        }

    async def __aenter__(self) -> "BaseUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc, tb):
        # If transaction is committed, rollback shouldn't error
        # This is here as a fallback
        await self.rollback()

    def __getattr__(self, item: str) -> AbstractRepository:
        # Enable accessing repositories as attributes
        # E.g. uow.customers.add()
        return self._repositories[item]

    def collect_new_events(self) -> Generator[List[Event], None, None]:
        for repository in self._repositories.values():
            for entity in repository.seen:
                while entity.events:
                    yield entity.events.pop(0)

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...
