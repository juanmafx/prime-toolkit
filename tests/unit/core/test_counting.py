import pytest

from prime_maker.core.counting import count_primes
from prime_maker.core.limits import MAX_COUNT_LIMIT
from prime_maker.core.sieve import primes_up_to


@pytest.mark.parametrize(
    ("limit", "expected"),
    [
        (0, 0),
        (1, 0),
        (2, 1),
        (3, 2),
        (10, 4),
        (99, 25),
        (10**3, 168),
        (10**6, 78_498),
        (10**8, 5_761_455),
        (10**9, 50_847_534),
        (10**10, 455_052_511),
    ],
)
def test_matches_published_pi_values(limit, expected):
    assert count_primes(limit) == expected


def test_agrees_with_sieve_for_every_limit_to_3000():
    primes = set(primes_up_to(3_000))
    running = 0
    for limit in range(3_001):
        running += limit in primes
        assert count_primes(limit) == running


@pytest.mark.parametrize("limit", [-1, MAX_COUNT_LIMIT + 1])
def test_rejects_out_of_bounds(limit):
    with pytest.raises(ValueError):
        count_primes(limit)
