# Release Notes: 2.0.0

Status: prepared and not yet tagged or published.

Version 2.0.0 turns two 2019 study scripts into a tested, documented prime-number toolkit.

## Highlights

- Primality results state whether they are proven or probabilistic.
- Primes can be streamed from ranges up to 10^15 and counted up to 10^13.
- Generated primes have an exact bit length and can be reproduced with a seed.
- Range reports cover gaps, twin primes, density, and residue classes.
- The Python package has no runtime dependencies.

## Upgrading

| Before | After |
| --- | --- |
| `python primer_maker.py` | `uv run prime-maker count 99` |
| `node index.js` | `node javascript/src/cli.js 10000` |

The JavaScript command now prints only the prime on each line. Values 0 and 1 are no longer listed as prime.

## Verification

The results of the test run for this version are in [reports/tests/latest.md](reports/tests/latest.md).
