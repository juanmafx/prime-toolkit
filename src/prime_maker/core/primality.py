import random
import secrets
from enum import StrEnum
from typing import Final

from prime_maker.core.limits import DEFAULT_ROUNDS, MAX_INPUT_BITS, MAX_ROUNDS, require_bounded

DETERMINISTIC_BASES: Final = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
DETERMINISTIC_LIMIT: Final = 3_317_044_064_679_887_385_961_981


class Primality(StrEnum):
    NOT_PRIME = "not_prime"
    PROVEN_PRIME = "proven_prime"
    PROBABLE_PRIME = "probable_prime"


def _is_strong_probable_prime(number: int, base: int, odd_part: int, twos: int) -> bool:
    witness = pow(base, odd_part, number)
    if witness in (1, number - 1):
        return True
    for _ in range(twos - 1):
        witness = witness * witness % number
        if witness == number - 1:
            return True
    return False


def classify(
    number: int,
    *,
    rounds: int = DEFAULT_ROUNDS,
    rng: random.Random | None = None,
) -> Primality:
    require_bounded("rounds", rounds, 1, MAX_ROUNDS)
    if isinstance(number, bool) or not isinstance(number, int):
        raise TypeError("number must be an integer")
    if number.bit_length() > MAX_INPUT_BITS:
        raise ValueError(f"number must fit in {MAX_INPUT_BITS} bits")
    if number < 2:
        return Primality.NOT_PRIME
    for prime in DETERMINISTIC_BASES:
        if number % prime == 0:
            return Primality.PROVEN_PRIME if number == prime else Primality.NOT_PRIME

    twos = ((number - 1) & -(number - 1)).bit_length() - 1
    odd_part = (number - 1) >> twos
    for base in DETERMINISTIC_BASES:
        if not _is_strong_probable_prime(number, base, odd_part, twos):
            return Primality.NOT_PRIME
    if number < DETERMINISTIC_LIMIT:
        return Primality.PROVEN_PRIME

    source = rng if rng is not None else secrets.SystemRandom()
    for _ in range(rounds):
        base = source.randrange(2, number - 1)
        if not _is_strong_probable_prime(number, base, odd_part, twos):
            return Primality.NOT_PRIME
    return Primality.PROBABLE_PRIME


def is_prime(
    number: int,
    *,
    rounds: int = DEFAULT_ROUNDS,
    rng: random.Random | None = None,
) -> bool:
    return classify(number, rounds=rounds, rng=rng) is not Primality.NOT_PRIME
