# Changelog

This project follows [Semantic Versioning](https://semver.org/). The 2019 scripts were never versioned and are treated as the 1.x line.

## 2.0.0 - Unreleased (prepared 2026-11-23)

### Added

- `prime_maker` package with `core`, `analysis`, `storage`, and `cli` layers.
- Miller-Rabin classification that distinguishes proven from probable primes.
- Segmented sieve, sublinear prime counting, exact-bit prime generation, and range statistics.
- Seeded runs, optional SQLite run history, and `db/schema.sql`.
- Unit, integration, property-based, and statistical tests with a committed report.
- CI, architecture documentation, security policy, and security audit.

### Changed

- **Breaking:** `primer_maker.py` is replaced by the `prime-maker` command.
- **Breaking:** `index.js` moved to `javascript/src/primes.js` and is now an ES module. Its command-line entry point is `javascript/src/cli.js`.
- **Breaking:** the JavaScript command prints one bare prime per line instead of `<n> It is prime`.
- All documentation and identifiers are in English.

### Fixed

- Negative integers are no longer reported as prime in Python.
- 0 and 1 are no longer reported as prime in JavaScript.
- `logarithmic_integral` rejects infinity, NaN, and values beyond the float range instead of never returning.
- `--db` rejects non-regular files and reports storage errors before the command runs.

### Security

- SQLite connections run with `trusted_schema` off and defensive mode on.
- A database path replaced by a symbolic link while opening is refused.
- The `primes_up_to` library limit is lowered from 10^10 to 10^9 to bound memory use.
