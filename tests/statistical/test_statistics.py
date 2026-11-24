import random
from collections import Counter
from math import log

import pytest

from prime_maker.analysis.range_report import analyze_range
from prime_maker.core.generation import random_prime
from prime_maker.core.primality import Primality, classify
from prime_maker.core.sieve import iter_primes

CHI_SQUARE_CRITICAL_DF22_P001 = 48.268


def test_generated_primes_are_uniform_over_eight_bit_primes():
    candidates = list(iter_primes(128, 256))
    assert len(candidates) == 23
    samples = 23_000
    master = random.Random(20_260_101)
    counts = Counter(random_prime(8, seed=master.getrandbits(63)) for _ in range(samples))
    assert set(counts) == set(candidates)
    expected = samples / len(candidates)
    statistic = sum((counts[prime] - expected) ** 2 / expected for prime in candidates)
    assert statistic < CHI_SQUARE_CRITICAL_DF22_P001


@pytest.mark.parametrize("modulus", [3, 4, 8, 10, 12, 30])
def test_primes_equidistribute_across_coprime_residues(modulus):
    report = analyze_range(0, 2_000_000, modulus=modulus)
    expected = sum(report.residue_counts.values()) / len(report.residue_counts)
    for count in report.residue_counts.values():
        assert count == pytest.approx(expected, rel=0.01)


@pytest.mark.parametrize("exponent", [4, 5, 6, 7])
def test_prime_number_theorem_estimates_bracket_truth(exponent):
    limit = 10**exponent
    report = analyze_range(0, limit)
    assert limit / log(limit) < report.prime_count < report.logarithmic_integral_estimate + 2


def test_mean_gap_tracks_logarithm():
    low = 10_000_000
    report = analyze_range(low, low + 2_000_000)
    assert report.mean_gap == pytest.approx(log(low + 1_000_000), rel=0.03)


def test_random_composites_are_rejected_at_rate_one():
    source = random.Random(314_159)
    for _ in range(500):
        left = source.getrandbits(80) | (1 << 79) | 1
        right = source.getrandbits(80) | (1 << 79) | 1
        assert classify(left * right, rounds=8, rng=source) is Primality.NOT_PRIME
