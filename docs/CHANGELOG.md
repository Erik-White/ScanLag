# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Full unit test coverage
- Type annotations on all functions

## [0.3.1] - 2019-11-04
### Fixed
- Adjust setup to correctly find packages in implicit namespaces

## [0.3.0] - 2019-11-04
### Added
- Added changelog
### Changed
- Update package to use src structure
- Update setup for readme compatability with PyPi

## [0.2.2] - 2019-11-02
### Added
- GitHub action for automatically linting and testing pushes
- GitHub action for building and releasing package to PyPi
### Fixed
- Linting errors highlighted by flake8

## [0.2.1] - 2019-10-31
### Added
- Graceful exit if no colonies are found
- Workaround function to ensure correct plates are found in images
### Changed
- Improve Timepoint grouping by using distance comparison instead of rounding
- Updated Scikit-image to v0.16
### Removed
- Depreciated Tk import
- Removed depreciated regionprop coordinates

## [0.2.0] - 2019-10-28
### Added
- Multiprocessing: greatly improves image processing speed
- Now shows a progress bar when processing images
- Snyk security checks for dependencies
### Changed
- Per image processing: now processes a single image at a time
- Improve colony filtering, removes virtually all merged colonies
- Updated readme with images and code examples
### Fixed
- Greatly reduced memory usage by using per-image processing
- Filter out system files when locating images to process
- Rare divide by zero error when processing colony object data

## [0.1.2] - 2019-10-13
Inital release
### Added
- Image processing, plotting and data aggregation
- Python package uploaded to PyPi