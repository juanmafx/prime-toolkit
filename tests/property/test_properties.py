import random
from bisect import bisect_right

from hypothesis import given
from hypothesis import strategies as st

from prime_maker.analysis.range_report import analyze_range
from prime_maker.core.counting import count_primes
from prime_maker.core.generation import random_prime
from prime_maker.core.primality import Primality, classify, is_prime
from prime_maker.core.sieve import iter_primes, primes_up_to

REFERENCE_LIMIT = 200_000
REFERENCE = primes_up_to(REFERENCE_LIMIT)
REFERENCE_SET = set(REFERENCE)
bounded = st.integers(min_value=0, max_value=REFERENCE_LIMIT)


def trial_division(number):
    if number < 2:
        return False
    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 1
    return True


@given(st.integers(min_value=-1_000, max_value=10_000_000))
def test_miller_rabin_agrees_with_trial_division(number):
    assert is_prime(number) == trial_division(number)


@given(
    st.integers(min_value=2, max_value=2**64),
    st.integers(min_value=2, max_value=2**64),
)
def test_products_are_never_prime(left, right):
    assert classify(left * right, rng=random.Random(0)) is Primality.NOT_PRIME


@given(bounded, bounded)
def test_segmented_sieve_matches_reference(low, high):
    expected = REFERENCE[bisect_right(REFERENCE, low - 1) : bisect_right(REFERENCE, high - 1)]
    assert list(iter_primes(low, high)) == (expected if low < high else [])


@given(bounded, st.integers(min_value=1, max_value=512))
def test_segment_size_is_irrelevant(high, segment_odds):
    assert list(iter_primes(0, high, segment_odds=segment_odds)) == list(iter_primes(0, high))


@given(bounded)
def test_count_matches_reference(limit):
    assert count_primes(limit) == bisect_right(REFERENCE, limit)


@given(bounded, bounded, bounded)
def test_ranges_are_additive(first, second, third):
    low, middle, high = sorted((first, second, third))
    left = analyze_range(low, middle).prime_count
    right = analyze_range(middle, high).prime_count
    assert left + right == analyze_range(low, high).prime_count


@given(st.integers(min_value=2, max_value=128), st.integers(min_value=0, max_value=2**32))
def test_generation_is_deterministic_and_exact(bits, seed):
    value = random_prime(bits, seed=seed)
    assert value == random_prime(bits, seed=seed)
    assert value.bit_length() == bits
    assert is_prime(value)


@given(st.integers(min_value=3, max_value=REFERENCE_LIMIT))
def test_bertrand_postulate(number):
    assert any(True for _ in iter_primes(number + 1, 2 * number))
