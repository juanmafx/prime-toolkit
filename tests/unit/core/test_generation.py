import pytest

from prime_maker.core.generation import random_prime
from prime_maker.core.limits import MAX_INPUT_BITS
from prime_maker.core.primality import is_prime


@pytest.mark.parametrize("bits", [2, 3, 4, 8, 16, 32, 64, 128, 256, 512])
def test_has_exact_bit_length_and_is_prime(bits):
    prime = random_prime(bits, seed=2026)
    assert prime.bit_length() == bits
    assert is_prime(prime)


def test_same_seed_reproduces_value():
    assert random_prime(256, seed=99) == random_prime(256, seed=99)


def test_different_seeds_diverge():
    assert len({random_prime(128, seed=seed) for seed in range(8)}) > 1


def test_unseeded_generation_works():
    assert random_prime(64).bit_length() == 64


def test_two_bit_generation_reaches_both_primes():
    assert {random_prime(2, seed=seed) for seed in range(64)} == {2, 3}


@pytest.mark.parametrize("bits", [1, MAX_INPUT_BITS + 1])
def test_rejects_out_of_bounds_bits(bits):
    with pytest.raises(ValueError):
        random_prime(bits)


@pytest.mark.parametrize("bits", [2, 16])
def test_rejects_invalid_rounds_for_every_bit_length(bits):
    with pytest.raises(ValueError, match="rounds"):
        random_prime(bits, rounds=0)
