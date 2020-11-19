# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.4.0] - 19 November 2020
### Added
- **Breaking change!** Added `AggregateRoot` that aggregate roots need to inherit from,
  in addition to Entity; moved domain event logic to AggregateRoot
- `types` module for commonly used types

### Changed
- **Breaking change!** `AbstractRepository`'s entity_type class-level keyword argument
  now expects the entity to be a subclass of AggregateRoot. Each aggregate root should
  have a repository and entities are children of the root entity.
- `BaseUnitOfWork.collect_new_events()` now pops events from `AggregateRoot.events` to
  ensure that no event is double-published

### Fixed
- Incorrectly instantiated entities in a few tests. Entities in `conftest.py` now
  conform to the `AggregateRoot` interface.

## [0.3.0] - 13 November 2020
### Changed
- Updated AbstractRepository to save class-level keyword arguments so they can be used
  by subclasses if needed
- Moved repository instantiation in BaseUnitOfWork from __init__() to __aenter__() to
  allow subclasses to manipulate arguments that are passed into repositories

## [0.2.0] - 12 November 2020
### Added
- add_dependencies() method to MessageBus class
- __repr__() method to AbstractRepository, BaseUnitOfWork, and Entity
