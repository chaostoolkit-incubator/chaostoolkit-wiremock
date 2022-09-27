### Changelog

## [Unreleased][]

[Unreleased]: https://github.com/chaostoolkit-incubator/chaostoolkit-wiremock/compare/0.1.2...HEAD

### Added

- add new actions `update_mappings_status_code_and_body`, `update_mappings_fault`, `delete_all_mappings`, `reset_mappings`
- update mappings filtering function to filter by any metadata in stub mappings (non-strict filtering). Strict (legacy) filtering will still be used by default for backward compatibility
- improved stubs mapping filter available for existing `delete_mappings`, `fixed_delay` actions
- now wiremock full `url` can be used in configuration instead of `host` and `port` combination. Useful when wiremock URL uses https
- updated wiremock version used in continuous integration to latest stable `2.33.2`
- updated dependency management using **Pipenv**. `requirements.txt` and `requirements-dev.txt` files can now be generated from requirements lock file with `make requirements` (Python >= 3.9 only)
- general code formatting using **black** and linting fixes

### Fixed

- fixes to `chaosaws/probes.py` to read from chaostoolkit configuration object
- fixed major linting issues with `chaoswm.driver` module
- `fixed_delay` action updates all stub mappings matching the filter
- `delete_mappings` mappings filter now works the same as all other actions

### Changed

- moved from `setup.py` to `setup.cfg`
- added a build system section to `pyproject.toml`

## [0.1.2][] - 2020-04-22

[0.1.2]: https://github.com/chaostoolkit-incubator/chaostoolkit-wiremock/compare/0.1.1...0.1.2

### Added

- `requirements.txt` and `requirement-dev.txt`  files to `MANIFEST.in` so they
  get distributed too.


## [0.1.1][]

[0.1.1]: https://github.com/chaostoolkit-incubator/chaostoolkit-wiremock/tree/0.1.1


- Initial commit [Marco Masetti]
