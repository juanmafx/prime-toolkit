# prime_maker_py

A dependency-free Python toolkit, with a small JavaScript port, for testing primality, enumerating and counting primes, generating primes of an exact bit length, and measuring how primes are distributed.

> **Project history:** originally created in 2019, modernized in 2026.

## Purpose

The project answers five concrete questions about integers:

| Question | Command | Method |
| --- | --- | --- |
| Is this integer prime, and how certain is that? | `check` | Miller-Rabin with an explicit certainty level |
| Which primes lie in a range? | `list` | Segmented, odd-only Sieve of Eratosthenes |
| How many primes are at most `n`? | `count` | Lucy Hedgehog prime-counting recurrence |
| What do the primes in a range look like? | `analyze` | Gap, twin-prime, density, and residue statistics |
| Can I get a prime with exactly `b` bits? | `random` | Rejection sampling, reproducible with a seed |

## Why this project exists

It began in 2019 as two short study scripts that used trial division: one counted the primes below 100 and the other printed the primes below 10,000. Prime numbers are a compact way to study the trade-offs between proof and probability, time and memory, and exact and estimated answers. Version 2 keeps that study focus and replaces the original scripts with algorithms that have documented bounds, verified edge cases, and reproducible runs.

## Architecture

```text
src/prime_maker/
  core/       primality, sieving, counting, generation, input limits
  analysis/   logarithmic integral and range statistics
  storage/    optional SQLite run history
  cli/        command-line interface
javascript/   dependency-free port of the primality test and sieve
db/           canonical SQL schema
tests/        unit, integration, property-based, and statistical suites
reports/      committed output from a real test run
```

Dependencies point inward: `cli` uses `analysis`, `core`, and `storage`; `analysis` uses `core`; `core` depends only on the standard library. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for algorithms, complexity, and design decisions.

## Quick start

Requirements: Python 3.13 or newer and [uv](https://docs.astral.sh/uv/). Node.js 22 or newer is needed only for the JavaScript port.

```bash
git clone https://github.com/juanmafx/prime_maker_py.git
cd prime_maker_py
uv sync --locked
uv run prime-maker check 97
```

```text
number: 97
classification: proven_prime
```

## Usage guide

Global options come before the command: `--json` emits JSON and `--db PATH` records the run.

```bash
uv run prime-maker check 2305843009213693951
uv run prime-maker --json check 170141183460469231731687303715884105727 --seed 7
uv run prime-maker list --low 10 --high 30
uv run prime-maker count 10000000000
uv run prime-maker analyze --high 100 --modulus 10
uv run prime-maker random --bits 64 --seed 2026
uv run prime-maker --db runs.sqlite count 1000
```

`check` reports one of three classifications:

| Classification | Meaning |
| --- | --- |
| `proven_prime` | Prime. The input is below 3,317,044,064,679,887,385,961,981, where the 13 fixed bases are known to be sufficient. |
| `probable_prime` | Passed the fixed bases and every random round. A composite passes `k` independent random rounds with probability at most `4^-k`. |
| `not_prime` | Composite, or less than 2. |

Exit codes: `0` success, `1` when `check` finds a non-prime, and `2` for invalid input or a storage error.

Ranges are half-open, so `list --low 10 --high 30` includes 10 and excludes 30. `count N` includes `N`.

### Library

```python
from prime_maker import Primality, analyze_range, classify, count_primes, random_prime

assert classify(97) is Primality.PROVEN_PRIME
assert count_primes(10**6) == 78_498
assert analyze_range(0, 100).twin_prime_pairs == 8
assert random_prime(128, seed=42) == random_prime(128, seed=42)
```

### JavaScript port

```bash
node javascript/src/cli.js 100
```

The port exports `isPrime` and `primesBelow` from `javascript/src/primes.js`. It has no dependencies. `isPrime` is deterministic across the JavaScript safe integer range.

## Configuration

There are no environment variables or configuration files. Behavior is set through command options, and these input limits are defined in `src/prime_maker/core/limits.py`:

| Limit | Value |
| --- | --- |
| Integer size for `check` and `random` | 4,096 bits |
| Miller-Rabin random rounds | 1 to 256, default 40 |
| Upper bound for `list` and `analyze` | 10^15 |
| Width of a `list` or `analyze` range | 10^9 |
| Limit for `count` | 10^13 |
| Limit for the JavaScript sieve | 10^8 |

## Reproducibility

Pass `--seed` to `check` or `random`, or `seed=` to `random_prime`, to repeat a run on the same Python version. Python's `random` module provides this seeded sequence, so seeded output is for experiments only. Without a seed, randomness comes from the operating system. The test suite uses a derandomized Hypothesis profile and fixed seeds.

## Database (optional)

The toolkit does not need a database. Persistence is used only when `--db PATH` is passed. [db/schema.sql](db/schema.sql) defines a small SQLite table of run results, and the CLI applies it automatically. The file is created with owner-only permissions.

## Testing

```bash
uv sync --locked
uv run pytest
npm test --prefix javascript --ignore-scripts
uv run python scripts/generate_test_report.py
```

The suites cover known values of the prime-counting function, Carmichael numbers, published strong pseudoprimes, Mersenne numbers, property-based agreement between independent algorithms, and statistical checks of generator uniformity and prime distribution. The latest real run is recorded in [reports/tests/latest.md](reports/tests/latest.md).

## Security notes

- **Do not use this project to generate cryptographic keys.** It is a study tool, has not been audited, and its arithmetic is not constant-time.
- All CLI inputs are bounded to limit resource exhaustion.
- SQL statements use bound parameters, and the optional database file refuses symbolic links where the platform supports it.
- See [SECURITY.md](SECURITY.md) and [docs/SECURITY_AUDIT.md](docs/SECURITY_AUDIT.md).

## References

- M. O. Rabin, "Probabilistic algorithm for testing primality," *Journal of Number Theory*, 1980.
- J. Sorenson and J. Webster, "Strong pseudoprimes to twelve prime bases," *Mathematics of Computation*, 2017.
- The prime-counting recurrence is widely known by the name of its popularizer, Lucy Hedgehog, from the Project Euler forums.

## Release and license

The current version is 2.0.0. See [CHANGELOG.md](CHANGELOG.md) and [RELEASE_NOTES.md](RELEASE_NOTES.md). The repository has never included a license file, so no open-source license is granted at this time.
