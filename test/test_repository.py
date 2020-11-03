import pytest

from cosmic_toolkit import AbstractRepository, Entity

pytestmark = pytest.mark.asyncio


def test_abstract_repository_incorrect_entity_type():
    class Item:
        ...

    with pytest.raises(TypeError) as e:

        class ItemRepository(AbstractRepository, entity_type=Item):
            async def _add(self, entity: Entity):
                ...

            async def _get(self, id: str) -> Entity:
                ...

            async def _update(self, entity: Entity):
                ...

    assert str(e.value) == "Entity must inherit from Entity"


async def test_abstract_repository_add_update_enforces_entity(
    test_entities, test_repositories
):
    entity_a = test_entities["EntityA"]()
    entity_b = test_entities["EntityB"]()
    repository_a = test_repositories["TestRepositoryA"]()

    await repository_a.add(entity_a)

    with pytest.raises(TypeError) as e:
        await repository_a.add(entity_b)

    assert str(e.value) == "Expecting entity of type EntityA"
    assert list(repository_a.seen)[0] == entity_a
