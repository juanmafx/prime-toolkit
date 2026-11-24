import pytest

from prime_maker.analysis.range_report import analyze_range


def test_reports_known_statistics_below_100():
    report = analyze_range(0, 100)
    assert report.prime_count == 25
    assert report.twin_prime_pairs == 8
    assert report.max_gap == 8
    assert report.max_gap_start == 89
    assert report.mean_gap == pytest.approx((97 - 2) / 24)
    assert report.density == pytest.approx(0.25)
    assert report.residue_counts == {1: 5, 3: 7, 7: 6, 9: 5}


def test_single_prime_has_no_gap():
    report = analyze_range(13, 14)
    assert report.prime_count == 1
    assert report.max_gap is None
    assert report.mean_gap is None


@pytest.mark.parametrize(("low", "high"), [(0, 0), (0, 2), (24, 29), (30, 10)])
def test_empty_ranges_are_well_formed(low, high):
    report = analyze_range(low, high)
    assert report.prime_count == 0
    assert report.residue_chi_square == 0.0


def test_estimate_tracks_true_count():
    report = analyze_range(0, 1_000_000)
    assert report.logarithmic_integral_estimate == pytest.approx(report.prime_count, rel=0.01)


@pytest.mark.parametrize("modulus", [1, 10_001])
def test_rejects_invalid_modulus(modulus):
    with pytest.raises(ValueError):
        analyze_range(0, 10, modulus=modulus)
