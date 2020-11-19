from abc import ABCMeta, abstractmethod
from typing import Dict, Generator, List

from cosmic_toolkit.models import Event
from cosmic_toolkit.repository import AbstractRepository


class BaseUnitOfWork(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        """Instantiate Unit of Work - arguments are passed into constructors of
        repositories"""
        self._args = args
        self._kwargs = kwargs
        self._repositories: Dict[str, AbstractRepository] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        cls._repository_classes = {
            k: v for k, v in kwargs.items() if issubclass(v, AbstractRepository)
        }

    async def __aenter__(self) -> "BaseUnitOfWork":
        # Instantiate repositories if they haven't been instantiated
        if not self._repositories:
            self._repositories = {
                k: v(*self._args, **self._kwargs)
                for k, v in self._repository_classes.items()
            }

        return self

    async def __aexit__(self, exc_type, exc, tb):
        # If transaction is committed, rollback shouldn't error
        # This is here as a fallback
        await self.rollback()

    def __eq__(self, other: "BaseUnitOfWork") -> bool:
        return self.__repr__() == other.__repr__()

    def __getattr__(self, item: str) -> AbstractRepository:
        # Enable accessing repositories as attributes
        # E.g. uow.customers.add()
        try:
            return self._repositories[item]
        except KeyError:
            raise AttributeError(
                f"{self.__class__.__name__} does not have {item!r} repository"
            )

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}, "
            f"repositories={[r.__repr__() for r in self._repositories.values()]}>"
        )

    def collect_new_events(self) -> Generator[List[Event], None, None]:
        for repository in self._repositories.values():
            for entity in repository.seen:
                yield from entity.events

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...
