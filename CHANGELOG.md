# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic
Versioning once public releases begin.

## [Unreleased]

### Added

- Configurable slice boundary effects including borders, opacity controls,
  auto and gradient seam colors, highlights, feathering, shadows, and curve
  shaping.
- Explicit still-image and progression-GIF export workflows with automatic
  `out/` directory handling.
- Smooth-loop progression GIF rendering and file-output integration tests.
- GitHub Actions CI covering lint, type checking, tests, package builds, and
  `twine check`.
- Runtime version export at `pytimeslice.__version__`.

### Changed

- Renamed the public package, distribution, and CLI to `pytimeslice`.
