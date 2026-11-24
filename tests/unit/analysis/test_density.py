import pytest

from prime_maker.analysis.density import logarithmic_integral


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (2, 1.04516378011749),
        (10, 6.16559950478730),
        (1_000, 177.609657990152),
        (1_000_000, 78_627.5491594622),
    ],
)
def test_matches_reference_values(value, expected):
    assert logarithmic_integral(value) == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize("value", [1, 0.5, 0, -3])
def test_rejects_domain_errors(value):
    with pytest.raises(ValueError):
        logarithmic_integral(value)


@pytest.mark.parametrize("value", [float("inf"), float("nan"), 10**400])
def test_rejects_values_without_a_finite_result(value):
    with pytest.raises(ValueError):
        logarithmic_integral(value)
