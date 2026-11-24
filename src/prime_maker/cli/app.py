import argparse
import json
import os
import random
import sqlite3
import sys
import time
from collections.abc import Sequence
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from prime_maker import __version__
from prime_maker.analysis.range_report import analyze_range
from prime_maker.core.counting import count_primes
from prime_maker.core.generation import random_prime
from prime_maker.core.limits import DEFAULT_ROUNDS
from prime_maker.core.primality import Primality, classify
from prime_maker.core.sieve import iter_primes
from prime_maker.storage.run_store import RunRecord, RunStore

MAX_SEED = 2**63 - 1
EXIT_OK = 0
EXIT_NOT_PRIME = 1
EXIT_USAGE = 2


def _seed(text: str) -> int:
    value = int(text)
    if not 0 <= value <= MAX_SEED:
        raise argparse.ArgumentTypeError(f"seed must be between 0 and {MAX_SEED}")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prime-maker", description="Prime number toolkit.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    parser.add_argument("--db", type=Path, help="record the run in this SQLite file")
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("check", help="classify one integer")
    check.add_argument("number", type=int)
    check.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS)
    check.add_argument("--seed", type=_seed)

    listing = commands.add_parser("list", help="stream primes in [low, high)")
    listing.add_argument("--low", type=int, default=0)
    listing.add_argument("--high", type=int, required=True)

    count = commands.add_parser("count", help="count primes less than or equal to a limit")
    count.add_argument("limit", type=int)

    analyze = commands.add_parser("analyze", help="report prime statistics for [low, high)")
    analyze.add_argument("--low", type=int, default=0)
    analyze.add_argument("--high", type=int, required=True)
    analyze.add_argument("--modulus", type=int, default=10)

    generate = commands.add_parser("random", help="generate a prime with an exact bit length")
    generate.add_argument("--bits", type=int, required=True)
    generate.add_argument("--seed", type=_seed)
    generate.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS)
    return parser


def _emit(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, sort_keys=True))
        return
    for key, value in payload.items():
        print(f"{key}: {value}")


def _run_check(args: argparse.Namespace) -> tuple[int, dict[str, Any], dict[str, Any]]:
    rng = random.Random(args.seed) if args.seed is not None else None
    verdict = classify(args.number, rounds=args.rounds, rng=rng)
    parameters = {"number": str(args.number), "rounds": args.rounds}
    result = {"number": str(args.number), "classification": verdict.value}
    _emit(result, as_json=args.json)
    return (EXIT_NOT_PRIME if verdict is Primality.NOT_PRIME else EXIT_OK), parameters, result


def _run_list(args: argparse.Namespace) -> tuple[int, dict[str, Any], dict[str, Any]]:
    primes = iter_primes(args.low, args.high)
    total = 0
    if args.json:
        sys.stdout.write("[")
    for prime in primes:
        if args.json:
            sys.stdout.write(f"{',' if total else ''}{prime}")
        else:
            sys.stdout.write(f"{prime}\n")
        total += 1
    if args.json:
        sys.stdout.write("]\n")
    return EXIT_OK, {"low": args.low, "high": args.high}, {"prime_count": total}


def _run_count(args: argparse.Namespace) -> tuple[int, dict[str, Any], dict[str, Any]]:
    result = {"limit": args.limit, "prime_count": count_primes(args.limit)}
    _emit(result, as_json=args.json)
    return EXIT_OK, {"limit": args.limit}, result


def _run_analyze(args: argparse.Namespace) -> tuple[int, dict[str, Any], dict[str, Any]]:
    report = asdict(analyze_range(args.low, args.high, modulus=args.modulus))
    report["residue_counts"] = {str(key): value for key, value in report["residue_counts"].items()}
    _emit(report, as_json=args.json)
    parameters = {"low": args.low, "high": args.high, "modulus": args.modulus}
    return EXIT_OK, parameters, report


def _run_random(args: argparse.Namespace) -> tuple[int, dict[str, Any], dict[str, Any]]:
    prime = random_prime(args.bits, seed=args.seed, rounds=args.rounds)
    result = {"bits": args.bits, "prime": str(prime)}
    _emit(result, as_json=args.json)
    return EXIT_OK, {"bits": args.bits, "rounds": args.rounds}, result


HANDLERS = {
    "check": _run_check,
    "list": _run_list,
    "count": _run_count,
    "analyze": _run_analyze,
    "random": _run_random,
}


def _execute(args: argparse.Namespace) -> int:
    started_at = datetime.now(UTC).isoformat()
    started = time.perf_counter()
    exit_code, parameters, result = HANDLERS[args.command](args)
    duration_ms = (time.perf_counter() - started) * 1000
    if args.db is not None:
        with RunStore(args.db) as store:
            store.record(
                RunRecord(
                    command=args.command,
                    parameters=parameters,
                    result=result,
                    seed=getattr(args, "seed", None),
                    package_version=__version__,
                    started_at=started_at,
                    duration_ms=duration_ms,
                )
            )
    return exit_code


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        exit_code = _execute(args)
        sys.stdout.flush()
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return EXIT_OK
    except (ValueError, TypeError, OSError, sqlite3.Error) as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_USAGE
    return exit_code
