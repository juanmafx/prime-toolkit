from dataclasses import dataclass
from math import gcd

from prime_maker.analysis.density import logarithmic_integral
from prime_maker.core.limits import require_bounded
from prime_maker.core.sieve import iter_primes


@dataclass(frozen=True, slots=True)
class RangeReport:
    low: int
    high: int
    prime_count: int
    twin_prime_pairs: int
    max_gap: int | None
    max_gap_start: int | None
    mean_gap: float | None
    density: float
    logarithmic_integral_estimate: float
    modulus: int
    residue_counts: dict[int, int]
    residue_chi_square: float


def _estimate_count(low: int, high: int) -> float:
    if high <= 2 or high <= low:
        return 0.0
    return logarithmic_integral(high) - logarithmic_integral(max(low, 2))


def _chi_square(counts: dict[int, int]) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    expected = total / len(counts)
    return sum((count - expected) ** 2 / expected for count in counts.values())


def analyze_range(low: int, high: int, *, modulus: int = 10) -> RangeReport:
    require_bounded("modulus", modulus, 2, 10_000)
    residue_counts = {residue: 0 for residue in range(1, modulus) if gcd(residue, modulus) == 1}
    prime_count = 0
    twin_prime_pairs = 0
    max_gap: int | None = None
    max_gap_start: int | None = None
    first_prime: int | None = None
    previous: int | None = None
    for prime in iter_primes(low, high):
        prime_count += 1
        residue = prime % modulus
        if residue in residue_counts:
            residue_counts[residue] += 1
        if previous is None:
            first_prime = prime
        else:
            gap = prime - previous
            if gap == 2:
                twin_prime_pairs += 1
            if max_gap is None or gap > max_gap:
                max_gap = gap
                max_gap_start = previous
        previous = prime
    mean_gap = None
    if first_prime is not None and previous is not None and prime_count > 1:
        mean_gap = (previous - first_prime) / (prime_count - 1)
    span = max(high - low, 0)
    return RangeReport(
        low=low,
        high=high,
        prime_count=prime_count,
        twin_prime_pairs=twin_prime_pairs,
        max_gap=max_gap,
        max_gap_start=max_gap_start,
        mean_gap=mean_gap,
        density=prime_count / span if span else 0.0,
        logarithmic_integral_estimate=_estimate_count(low, high),
        modulus=modulus,
        residue_counts=residue_counts,
        residue_chi_square=_chi_square(residue_counts),
    )
