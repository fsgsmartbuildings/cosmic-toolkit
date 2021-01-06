import logging
from functools import lru_cache
from inspect import Parameter, signature
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from cosmic_toolkit.models import Event

logger = logging.getLogger(__name__)


class MessageBus:
    def __init__(
        self,
        handlers: Dict[Type[Event], List[Callable]],
        ignore_missing_handlers: Optional[bool] = False,
        lru_cache_size: Optional[int] = 64,
        unit_of_work_kwarg_name: Optional[str] = "uow",
        **dependencies,
    ):
        self._dependencies = dependencies
        self._handlers = handlers

        # If True, RuntimeError will not be raised if there are no handlers for an
        # event
        self._ignore_missing_handlers = ignore_missing_handlers
        self._unit_of_work_kwarg_name = unit_of_work_kwarg_name

        # LRU caching
        self._cached_get_handlers_for_event = lru_cache(lru_cache_size)(
            self._get_handlers_for_event
        )
        self._cached_resolve_dependencies = lru_cache(lru_cache_size)(
            self._resolve_dependencies
        )

    @property
    def dependencies(self) -> Dict[str, Any]:
        return self._dependencies

    @staticmethod
    def _cull_dependencies(
        parameters: Dict[str, Parameter], dependencies: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Find arguments for a handler using signature parameters. Skips the
        event argument since that's expected to be the first argument and is explicitly
        passed by _handle_event()"""
        return {
            name: dependencies.get(name)
            for name, param in parameters.items()
            if name != "event"
        }

    def _get_handlers_for_event(self, event_type: Type[Event]) -> List[Callable]:
        """Return the first list of handlers found for event.
        Searches for handlers using event type and parents' types."""

        for klass in [event_type] + [t for t in event_type.__bases__]:
            handlers = self._handlers.get(klass)

            if handlers:
                return handlers

        raise RuntimeError(f"No handlers found for {event_type}")

    def _resolve_dependencies(
        self, handler: Callable, **dependencies
    ) -> Tuple[list, dict]:
        # Combine all dependencies
        all_provided_deps = {**self._dependencies, **dependencies}

        # Bind dependencies
        sig = signature(handler)
        culled_deps = self._cull_dependencies(sig.parameters, all_provided_deps)
        bounded = sig.bind_partial(**culled_deps)

        # Return args + kwargs
        return list(bounded.args), bounded.kwargs

    async def _handle_event(self, event: Event, **dependencies) -> List[Event]:
        events = []
        handlers = []

        try:
            # This will raise RuntimeError if there are no handlers for the event
            # _ignore_missing_handlers dictates the functionality when this happens
            # Default is to raise RuntimeError but event can be ignored by instantiating
            # message bus with ignore_missing_handlers=True
            handlers = self._cached_get_handlers_for_event(event.__class__)
        except RuntimeError:
            if not self._ignore_missing_handlers:
                raise

        for handler in handlers:
            args, kwargs = self._cached_resolve_dependencies(handler, **dependencies)

            logger.debug("Using %s to handle %s", handler, event)
            await handler(event, *args, **kwargs)

            # Attempt to collect new events published by handler
            # We need a Unit of Work dependency for this
            # Not all use cases require UoW, so if UoW isn't in deps,
            # it's not an issue
            uow = {**self._dependencies, **dependencies}.get(
                self._unit_of_work_kwarg_name
            )

            if uow:
                events.extend(uow.collect_new_events())

        return events

    def add_dependencies(self, **dependencies):
        self._dependencies.update(dependencies)

    async def handle(self, event: Event, **dependencies):
        queue = [event]

        # Domain models can publish new events which is why we use a queue here
        while queue:
            new_events = await self._handle_event(queue.pop(0), **dependencies)
            queue.extend(new_events)
