# Security Audit

Review date: 2026-11-24. Scope: all tracked files on `modernize/2026`, plus a credential scan of the full Git history. This was an engineering self-review and not an independent third-party audit.

## Result

No high or medium findings remain in the current tree. The remaining low-severity items are listed under accepted limitations.

| Area | Result |
| --- | --- |
| Hardcoded secrets and credentials | None found in the tree or history |
| Private keys | None tracked |
| Committed dependencies or build artifacts | None tracked |
| SQL injection | Not applicable to the original code; new storage uses bound parameters |
| XSS and CSRF | Not applicable: no web interface |
| Authentication, sessions, and 2FA | Not applicable: no accounts, server, or network access |
| Unsafe evaluation or shell execution | None in the toolkit |
| Weak hashing | None. SHA-256 is used only for the test report source digest |
| Known dependency vulnerabilities | `pip-audit` reported none for the locked development dependencies |
| Workflow analysis | `actionlint` and `zizmor` reported no errors or default-profile findings |
| Runtime dependencies | None |

## Fixed during modernization

| Severity | Issue | Resolution |
| --- | --- | --- |
| Low | Correctness: the Python check treated negative integers as prime | Values below 2 are rejected |
| Low | Correctness: the JavaScript check treated 0 and 1 as prime | Values below 2 are rejected |
| Low | Resource use: quadratic-style trial division with no input bounds | Efficient algorithms and explicit limits |
| Medium | Denial of service: `logarithmic_integral` never returned for infinity, NaN, or integers beyond the float range | Those values are rejected |
| Low | `--db` passed FIFOs and device files to SQLite | Only regular files are accepted |
| Low | A path swapped for a symbolic link after the first check was followed by SQLite | The opened file is compared with the path and a mismatch is refused |
| Low | Database files were opened with SQLite schema trust enabled | `trusted_schema` is off and defensive mode is on |
| Low | Storage errors surfaced only after the full computation | The store is opened first |
| Low | `primes_up_to` allowed a limit needing many gigabytes of memory | Limit lowered to 10^9 |

## Hardening added

- Explicit size limits for every command.
- New database files are owner-only on POSIX systems, and symbolic links are refused on supported platforms.
- Operating system randomness whenever no seed is supplied.
- Hash-locked Python dependencies.
- CI with read-only token permissions, actions pinned to commit SHAs, no persisted checkout credentials, and a dependency audit.

## Accepted limitations

- `probable_prime` results above the deterministic limit are probabilistic.
- The arithmetic is not constant-time, so the toolkit must not process secret values or generate production keys.
- Large permitted inputs can still use significant CPU time. Callers exposing this tool to untrusted users should add their own timeouts.
- The mode of an existing database file is not changed, so a file made readable by others stays readable.
- SQLite opens the path by name, so a very small race remains if another user can write to the database directory.
- The build backend and the CI `pip-audit` tool are pinned by version but not by hash.
