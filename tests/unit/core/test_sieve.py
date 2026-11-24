import pytest

from prime_maker.core.limits import MAX_RANGE_HIGH, MAX_RANGE_SPAN, MAX_SIEVE_LIMIT
from prime_maker.core.sieve import iter_primes, primes_up_to


@pytest.mark.parametrize(
    ("limit", "expected"),
    [(0, []), (1, []), (2, [2]), (3, [2, 3]), (4, [2, 3]), (10, [2, 3, 5, 7])],
)
def test_primes_up_to_small_limits(limit, expected):
    assert primes_up_to(limit) == expected


@pytest.mark.parametrize(
    ("limit", "count"),
    [(10, 4), (100, 25), (1_000, 168), (10_000, 1_229), (100_000, 9_592), (1_000_000, 78_498)],
)
def test_primes_up_to_matches_known_counts(limit, count):
    assert len(primes_up_to(limit)) == count


def test_legacy_python_script_result_is_preserved():
    assert sum(1 for _ in iter_primes(2, 100)) == 25


def test_legacy_javascript_range_excludes_zero_and_one():
    primes = list(iter_primes(0, 10_000))
    assert primes[0] == 2
    assert len(primes) == 1_229


@pytest.mark.parametrize(
    ("low", "high", "expected"),
    [
        (0, 0, []),
        (0, 2, []),
        (0, 3, [2]),
        (2, 3, [2]),
        (3, 4, [3]),
        (4, 5, []),
        (10, 30, [11, 13, 17, 19, 23, 29]),
        (30, 10, []),
    ],
)
def test_iter_primes_is_half_open(low, high, expected):
    assert list(iter_primes(low, high)) == expected


@pytest.mark.parametrize("segment_odds", [1, 2, 3, 7, 64, 1024])
def test_segment_size_does_not_change_result(segment_odds):
    assert list(iter_primes(0, 5_000, segment_odds=segment_odds)) == primes_up_to(4_999)


def test_window_near_range_ceiling():
    window = list(iter_primes(MAX_RANGE_HIGH - 100, MAX_RANGE_HIGH))
    assert window[-1] == 999_999_999_999_989


@pytest.mark.parametrize(
    ("low", "high"),
    [(-1, 10), (0, MAX_RANGE_HIGH + 1), (0, MAX_RANGE_SPAN + 1)],
)
def test_iter_primes_rejects_invalid_bounds_eagerly(low, high):
    with pytest.raises(ValueError):
        iter_primes(low, high)


@pytest.mark.parametrize("limit", [-1, MAX_SIEVE_LIMIT + 1])
def test_primes_up_to_rejects_invalid_limit(limit):
    with pytest.raises(ValueError):
        primes_up_to(limit)
