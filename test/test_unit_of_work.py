import pytest

from cosmic_toolkit import AbstractRepository

pytestmark = pytest.mark.asyncio


async def test_base_unit_of_work_repository_attributes(test_unit_of_work):
    uow = test_unit_of_work()

    # Ensure repos can be accessed as attributes, but only after the uow is used as a
    # context manager
    assert not hasattr(uow, "a_items")
    assert not hasattr(uow, "b_items")

    with pytest.raises(AttributeError) as e:
        uow.a_items

    assert str(e.value) == "TestUnitOfWork does not have 'a_items' repository"

    # Now we can access repositories
    async with uow:
        assert hasattr(uow, "a_items")
        assert hasattr(uow, "b_items")

        assert isinstance(uow.a_items.seen, set)

    # uow has been used as context manager so now we expect repositories to be
    # instantiated
    assert isinstance(uow.a_items, AbstractRepository)


async def test_base_unit_of_work_collect_new_events(
    test_entities, test_events, test_unit_of_work
):
    uow = test_unit_of_work()

    # Add entities
    async with uow:
        entity_a = test_entities["EntityA"].init("hello")
        entity_a._add_event(test_events["ATriggered"]())
        entity_a._add_event(test_events["BTriggered"]())
        entity_b = test_entities["EntityB"].init("world")
        entity_b._add_event(test_events["BTriggered"]())

        await uow.a_items.add(entity_a)
        await uow.b_items.add(entity_b)

        await uow.commit()

    # Collect events
    events = list(uow.collect_new_events())

    assert len(events) == 3
    assert isinstance(events[0], test_events["ATriggered"])
    assert isinstance(events[1], test_events["BTriggered"])
    assert isinstance(events[2], test_events["BTriggered"])

    # Events should be cleared out
    assert len(list(uow.collect_new_events())) == 0
