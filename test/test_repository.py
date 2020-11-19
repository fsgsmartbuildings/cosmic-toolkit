import pytest

from cosmic_toolkit import AbstractRepository, AggregateRoot

pytestmark = pytest.mark.asyncio


def test_abstract_repository_incorrect_entity_type():
    class Item:
        ...

    with pytest.raises(TypeError) as e:

        class ItemRepository(AbstractRepository, entity_type=Item):
            async def _add(self, entity: AggregateRoot):
                ...

            async def _get(self, id: str) -> AggregateRoot:
                ...

            async def _update(self, entity: AggregateRoot):
                ...

    assert str(e.value) == "Entity must inherit from AggregateRoot"


async def test_abstract_repository_add_update_enforces_entity(
    test_entities, test_repositories
):
    entity_a = test_entities["EntityA"].init("hello")
    entity_b = test_entities["EntityB"].init("world")
    repository_a = test_repositories["TestRepositoryA"]()

    await repository_a.add(entity_a)

    with pytest.raises(TypeError) as e:
        await repository_a.add(entity_b)

    assert str(e.value) == "Expecting entity of type EntityA"
    assert list(repository_a.seen)[0] == entity_a


def test_abstract_repository_subclass_kwargs(test_entities):
    """Ensure that class-level keyword arguments are captured and stored so they can
    be used by subclasses"""

    class ARepository(
        AbstractRepository,
        entity_type=test_entities["EntityA"],
        collection_name="test",
    ):
        async def _add(self, entity: AggregateRoot):
            ...

        async def _get(self, id: str) -> AggregateRoot:
            ...

        async def _update(self, entity: AggregateRoot):
            ...

    a_repository = ARepository()

    assert a_repository._init_kwargs == {"collection_name": "test"}
