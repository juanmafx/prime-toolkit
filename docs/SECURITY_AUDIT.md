# Security Audit

Audit date: 2026-11-23. Scope: all tracked files on `modernize/2026`, plus a credential scan of the full Git history. This was an engineering self-review and not an independent third-party audit.

## Result

No open findings remain in the current tree.

| Area | Result |
| --- | --- |
| Hardcoded secrets and credentials | None found in the tree or history |
| Private keys | None tracked |
| Committed dependencies or build artifacts | None tracked |
| SQL injection | Not applicable to the original code; new storage uses bound parameters |
| XSS and CSRF | Not applicable: no web interface |
| Unsafe evaluation or shell execution | None in the toolkit |
| Weak hashing | None. SHA-256 is used only for the test report source digest |
| Known dependency vulnerabilities | `pip-audit` reported none for the locked development dependencies |
| Runtime dependencies | None |

## Fixed during modernization

| Severity | Issue | Resolution |
| --- | --- | --- |
| Low | Correctness: the Python check treated negative integers as prime | Values below 2 are rejected |
| Low | Correctness: the JavaScript check treated 0 and 1 as prime | Values below 2 are rejected |
| Low | Resource use: quadratic-style trial division with no input bounds | Efficient algorithms and explicit limits |

## Hardening added

- Bounded inputs for every command.
- Owner-only database files that refuse symbolic links on supported platforms.
- Operating system randomness whenever no seed is supplied.
- Hash-locked Python dependencies.
- CI with read-only token permissions, actions pinned to commit SHAs, no persisted checkout credentials, and a dependency audit.

## Accepted limitations

- `probable_prime` results above the deterministic limit are probabilistic.
- The arithmetic is not constant-time, so the toolkit must not process secret values or generate production keys.
- Large permitted inputs can still use significant CPU time. Callers exposing this tool to untrusted users should add their own timeouts.
