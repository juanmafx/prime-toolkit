from collections.abc import Iterator
from math import isqrt
from typing import Final

from prime_maker.core.limits import (
    MAX_RANGE_HIGH,
    MAX_RANGE_SPAN,
    MAX_SIEVE_LIMIT,
    require_bounded,
)

DEFAULT_SEGMENT_ODDS: Final = 1 << 18


def primes_up_to(limit: int) -> list[int]:
    require_bounded("limit", limit, 0, MAX_SIEVE_LIMIT)
    if limit < 2:
        return []
    size = (limit + 1) // 2
    flags = bytearray(b"\x01") * size
    flags[0] = 0
    for index in range(1, (isqrt(limit) + 1) // 2):
        if flags[index]:
            step = 2 * index + 1
            start = 2 * index * (index + 1)
            flags[start::step] = bytes(len(range(start, size, step)))
    primes = [2]
    position = flags.find(1)
    while position != -1:
        primes.append(2 * position + 1)
        position = flags.find(1, position + 1)
    return primes


def _sieve_segment(start: int, stop: int, base_primes: list[int]) -> bytearray:
    size = (stop - start + 1) // 2
    flags = bytearray(b"\x01") * size
    for prime in base_primes:
        square = prime * prime
        if square >= stop:
            break
        first = max(square, (start + prime - 1) // prime * prime)
        if first % 2 == 0:
            first += prime
        index = (first - start) // 2
        if index < size:
            flags[index::prime] = bytes(len(range(index, size, prime)))
    return flags


def iter_primes(
    low: int,
    high: int,
    *,
    segment_odds: int = DEFAULT_SEGMENT_ODDS,
) -> Iterator[int]:
    require_bounded("low", low, 0, MAX_RANGE_HIGH)
    require_bounded("high", high, 0, MAX_RANGE_HIGH)
    require_bounded("segment_odds", segment_odds, 1, 1 << 26)
    if high - low > MAX_RANGE_SPAN:
        raise ValueError(f"range span must not exceed {MAX_RANGE_SPAN}")
    return _generate_primes(low, high, segment_odds)


def _generate_primes(low: int, high: int, segment_odds: int) -> Iterator[int]:
    if high <= 2 or high <= low:
        return
    if low <= 2:
        yield 2
    first_odd = max(low, 3) | 1
    if first_odd >= high:
        return
    base_primes = primes_up_to(isqrt(high - 1))[1:]
    for start in range(first_odd, high, 2 * segment_odds):
        stop = min(start + 2 * segment_odds, high)
        flags = _sieve_segment(start, stop, base_primes)
        position = flags.find(1)
        while position != -1:
            yield start + 2 * position
            position = flags.find(1, position + 1)
