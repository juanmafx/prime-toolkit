import random
import secrets

from prime_maker.core.limits import (
    DEFAULT_ROUNDS,
    MAX_INPUT_BITS,
    MAX_ROUNDS,
    require_bounded,
)
from prime_maker.core.primality import is_prime


def random_prime(bits: int, *, seed: int | None = None, rounds: int = DEFAULT_ROUNDS) -> int:
    require_bounded("bits", bits, 2, MAX_INPUT_BITS)
    require_bounded("rounds", rounds, 1, MAX_ROUNDS)
    source: random.Random = random.Random(seed) if seed is not None else secrets.SystemRandom()
    if bits == 2:
        return source.choice((2, 3))
    top_bit = 1 << (bits - 1)
    while True:
        candidate = source.getrandbits(bits) | top_bit | 1
        if is_prime(candidate, rounds=rounds, rng=source):
            return candidate
