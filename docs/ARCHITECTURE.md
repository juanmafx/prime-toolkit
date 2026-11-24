# Architecture

## System overview

`prime_maker` is a local library and command-line tool. It has no network access, no server, and no client application, so it is not divided into `frontend/` and `backend/`.

```text
                +-----------------+
                |   cli/app.py    |
                +--+-----+-----+--+
                   |     |     |
        +----------+     |     +-----------+
        v                v                 v
+---------------+  +-----------+  +-----------------+
|   analysis/   |->|   core/   |  |    storage/     |
| density       |  | limits    |  | run_store       |
| range_report  |  | primality |  | schema.sql      |
+---------------+  | sieve     |  +--------+--------+
                   | counting  |           |
                   | generation|           v
                   +-----------+    optional SQLite
```

## Module structure

```text
src/prime_maker/
  __init__.py            public API and version
  __main__.py            python -m entry point
  core/
    limits.py            resource limits and validation
    primality.py         Miller-Rabin classification
    sieve.py             full and segmented sieves
    counting.py          sublinear prime counting
    generation.py        exact-bit prime generation
  analysis/
    density.py           logarithmic integral
    range_report.py      streaming range statistics
  storage/
    run_store.py         parameterized SQLite persistence
    schema.sql           packaged copy of db/schema.sql
  cli/
    app.py               argument parsing and output
javascript/
  src/primes.js          primality test and sieve
  src/cli.js             command-line entry point
  test/                  node:test suite
tests/
  unit/                  module behavior
  integration/           CLI and process behavior
  property/              Hypothesis invariants
  statistical/           distribution checks with fixed seeds
```

### Dependency rules

1. `core` imports only the standard library and other `core` modules.
2. `analysis` may import `core`.
3. `storage` has no dependency on the mathematics.
4. Only `cli` combines all layers and performs user-facing I/O.

## Algorithms and complexity

Let `n` be the input, `k` the number of random rounds, `L` and `H` the range bounds, and `S` the segment size.

| Operation | Algorithm | Time | Extra memory |
| --- | --- | --- | --- |
| `classify` | Miller-Rabin | `O((13 + k) log^3 n)` with schoolbook multiplication | `O(log n)` |
| `primes_up_to` | Odd-only Sieve of Eratosthenes | `O(n log log n)` | `n / 2` bytes plus the result |
| `iter_primes` | Segmented odd-only sieve | `O((H - L + sqrt(H)) log log H)` | `O(sqrt(H) + S)` |
| `count_primes` | Lucy Hedgehog recurrence | `O(n^(3/4))` | `O(sqrt(n))` |
| `random_prime` | Rejection sampling | Expected `O(b)` candidates for `b` bits | `O(b)` |
| `analyze_range` | Single streaming pass | Same as `iter_primes` | `O(sqrt(H) + S + phi(m))` for modulus `m` |

### Primality certainty

Below 3,317,044,064,679,887,385,961,981, the first 13 prime bases form a deterministic test (Sorenson and Webster). That value is itself the smallest strong pseudoprime to all 13 bases, so at or above it the implementation also runs `k` random-base rounds and returns `probable_prime`. The result type keeps a proof separate from a probabilistic claim.

### Segmented sieve

The sieve stores odd numbers only. Each segment marks multiples starting at `max(p^2, first odd multiple in the segment)`. Output is streamed, so memory depends on the segment and base primes rather than the number of primes emitted.

### Prime counting

Let `S(v, p)` be the count of integers in `[2, v]` that remain after sieving by primes up to `p`. For each prime `p` with `p^2 <= v`:

```text
S(v, p) = S(v, p - 1) - (S(v / p, p - 1) - pi(p - 1))
```

Only the `O(sqrt(n))` distinct values of `floor(n / i)` are needed, which yields the sublinear bound.

### Distribution analysis

`analyze_range` compares the true count with `li(H) - li(max(L, 2))`, records gaps and twin pairs, and computes a chi-square statistic across residue classes coprime to the modulus. Primes are deterministic, so that statistic is a descriptive measure of balance and not a hypothesis test about randomness.

## Persistence

SQLite is optional and is used only with `--db`. The `runs` table keeps JSON parameters and results, the seed, the package version, and timing. Constraints reject unknown commands and malformed JSON. The store opens only regular files, refuses symbolic links where the platform supports it, and connects with `trusted_schema` off and defensive mode on. The store is opened before the command runs, so an unusable path fails without doing the work. `db/schema.sql` is canonical, and a test ensures the packaged copy is identical.

## Recommended evolution

- Keep `core` pure so an accelerated implementation can be swapped in behind the same functions.
- Add a primality certificate, such as ECPP or Pratt, if `probable_prime` needs to become a proof above the deterministic limit.
- Replace the counting recurrence with Meissel-Lehmer or Deleglise-Rivat if limits above `10^13` become necessary.
