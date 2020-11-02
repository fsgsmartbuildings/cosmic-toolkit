import pytest

pytestmark = pytest.mark.asyncio


def test_base_unit_of_work_repository_attributes(test_unit_of_work):
    # Ensure repos can be accessed as attributes
    uow = test_unit_of_work()

    assert hasattr(uow, "a_items")
    assert hasattr(uow, "b_items")

    assert isinstance(uow.a_items.seen, set)


async def test_base_unit_of_work_collect_new_events(
    test_entities, test_events, test_unit_of_work
):
    uow = test_unit_of_work()

    # Add entities
    async with uow:
        entity_a = test_entities["EntityA"]()
        entity_a._events.append(test_events["ATriggered"]())
        entity_a._events.append(test_events["BTriggered"]())
        entity_b = test_entities["EntityB"]()
        entity_b._events.append(test_events["BTriggered"]())

        await uow.a_items.add(entity_a)
        await uow.b_items.add(entity_b)

        await uow.commit()

    # Collect events
    events = list(uow.collect_new_events())

    assert len(events) == 3
    assert isinstance(events[0], test_events["ATriggered"])
    assert isinstance(events[1], test_events["BTriggered"])
    assert isinstance(events[2], test_events["BTriggered"])
