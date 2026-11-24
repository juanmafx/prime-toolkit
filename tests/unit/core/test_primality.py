import random

import pytest

from prime_maker.core.limits import MAX_INPUT_BITS
from prime_maker.core.primality import DETERMINISTIC_LIMIT, Primality, classify, is_prime
from prime_maker.core.sieve import primes_up_to


def test_agrees_with_sieve_below_100000():
    expected = set(primes_up_to(100_000))
    assert {n for n in range(100_001) if is_prime(n)} == expected


@pytest.mark.parametrize("number", [-7, -1, 0, 1])
def test_values_below_two_are_not_prime(number):
    assert classify(number) is Primality.NOT_PRIME


@pytest.mark.parametrize("number", [561, 1105, 1729, 2465, 2821, 6601, 8911, 41041, 825265])
def test_carmichael_numbers_are_composite(number):
    assert not is_prime(number)


@pytest.mark.parametrize(
    "number",
    [
        2047,
        1373653,
        25326001,
        3215031751,
        2152302898747,
        3474749660383,
        341550071728321,
        3825123056546413051,
        318665857834031151167461,
        3317044064679887385961981,
    ],
)
def test_strong_pseudoprimes_are_composite(number):
    assert classify(number, rng=random.Random(1)) is Primality.NOT_PRIME


@pytest.mark.parametrize("exponent", [2, 3, 5, 7, 13, 17, 19, 31, 61])
def test_small_mersenne_primes_are_proven(exponent):
    assert classify(2**exponent - 1) is Primality.PROVEN_PRIME


@pytest.mark.parametrize("exponent", [89, 107, 127, 521, 607, 1279])
def test_large_mersenne_primes_are_probable(exponent):
    assert classify(2**exponent - 1, rng=random.Random(7)) is Primality.PROBABLE_PRIME


@pytest.mark.parametrize("exponent", [11, 23, 29, 37, 41, 67, 257])
def test_composite_mersenne_numbers_are_rejected(exponent):
    assert classify(2**exponent - 1, rng=random.Random(7)) is Primality.NOT_PRIME


def test_certainty_boundary_sits_at_published_limit():
    assert DETERMINISTIC_LIMIT == 3317044064679887385961981


def test_large_prime_uses_system_randomness_without_rng():
    assert classify(2**127 - 1, rounds=2) is Primality.PROBABLE_PRIME


@pytest.mark.parametrize("value", [1.5, "7", None, True])
def test_rejects_non_integers(value):
    with pytest.raises(TypeError):
        classify(value)


@pytest.mark.parametrize("rounds", [0, 257])
def test_rejects_out_of_bounds_rounds(rounds):
    with pytest.raises(ValueError, match="rounds"):
        classify(7, rounds=rounds)


def test_rejects_oversized_input():
    with pytest.raises(ValueError, match="bits"):
        classify(1 << MAX_INPUT_BITS)
