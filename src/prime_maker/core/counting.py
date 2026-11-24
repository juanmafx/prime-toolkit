from math import isqrt

from prime_maker.core.limits import MAX_COUNT_LIMIT, require_bounded


def count_primes(limit: int) -> int:
    require_bounded("limit", limit, 0, MAX_COUNT_LIMIT)
    if limit < 2:
        return 0
    root = isqrt(limit)
    small = [max(value - 1, 0) for value in range(root + 1)]
    large = [0] + [limit // index - 1 for index in range(1, root + 1)]
    for prime in range(2, root + 1):
        if small[prime] == small[prime - 1]:
            continue
        primes_before = small[prime - 1]
        square = prime * prime
        for index in range(1, min(root, limit // square) + 1):
            multiple = index * prime
            removed = large[multiple] if multiple <= root else small[limit // multiple]
            large[index] -= removed - primes_before
        for value in range(root, square - 1, -1):
            small[value] -= small[value // prime] - primes_before
    return large[1]
