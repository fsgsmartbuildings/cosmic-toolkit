# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.6.0] - 04 June 2021
### Changed
- Remove orjson dependency and use built-in json encoder

## [0.5.1] - 04 June 2021
### Changed
- Update dependencies to latest versions

## [0.5.0] - 06 March 2021
### Changed
- `pydantic` and `orjson` version requirements eased
- Changed signature of `AbstractRepository.get()` and `AbstractRepository._get()` to
  enable greater flexibility

### Fixed
- Tests workflow was broken due to an issue with a dependency

## [0.4.2] - 06 January 2021
### Added
- Implemented `lru_cache` for `MessageBus._get_handlers_for_event()` and
  `MessageBus._resolve_dependencies()` to reduce redundant calls.

## [0.4.1] - 20 November 2020
### Added
- `.json()` method to `Entity`

### Fixed
- Swapped the standard JSON dumps function for orjson.dumps to get datetime and UUID
  serialization support out-of-the-box

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
