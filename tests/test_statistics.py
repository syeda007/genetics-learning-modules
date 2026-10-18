"""
Unit Tests: Biostatistical Analysis Module
Verifies Pearson Chi-Square Goodness-of-Fit, Degrees of Freedom, p-values, and Cochran Warnings
"""
import pytest
from biostatistics.chi_square import calculate_chi_square


def test_mendel_monohybrid_chi_square():
    """
    Mendel's historical pea tall/dwarf F2 observation:
    Observed: Tall = 556, Dwarf = 184 (N = 740)
    Hypothesized ratio: 3:1 (0.75, 0.25)
    Expected: Tall = 555.0, Dwarf = 185.0
    χ² = (556 - 555)²/555 + (184 - 185)²/185 = 1/555 + 1/185 ≈ 0.007207
    df = 2 - 1 = 1
    p-value ≈ 0.9323 (Fail to reject H0)
    """
    obs = {"Tall": 556, "Dwarf": 184}
    exp_props = {"Tall": 0.75, "Dwarf": 0.25}

    result = calculate_chi_square(obs, exp_props, alpha=0.05)

    assert result.total_observed == 740
    assert result.degrees_of_freedom == 1
    assert abs(result.chi_square_statistic - 0.007207) < 1e-4
    assert result.p_value > 0.90
    assert not result.is_significant
    assert "Fail to Reject" in result.conclusion
    assert not result.warning_small_counts


def test_dihybrid_degrees_of_freedom():
    """k = 4 categories → df = 4 - 1 = 3"""
    obs = {"AB": 315, "Ab": 108, "aB": 101, "ab": 32}
    exp_props = {"AB": 9/16, "Ab": 3/16, "aB": 3/16, "ab": 1/16}

    result = calculate_chi_square(obs, exp_props, alpha=0.05)
    assert result.degrees_of_freedom == 3
    assert result.p_value > 0.05
    assert not result.is_significant


def test_significant_departure_rejection():
    """Severe departure (e.g. complete linkage or lethal allele) must reject H0"""
    obs = {"Class A": 900, "Class B": 100}
    exp_props = {"Class A": 0.50, "Class B": 0.50}

    result = calculate_chi_square(obs, exp_props, alpha=0.05)
    assert result.is_significant
    assert result.p_value < 1e-10
    assert "Reject Null Hypothesis" in result.conclusion


def test_cochran_small_count_warning():
    """Expected count < 5 triggers Cochran rule warning"""
    obs = {"Class A": 18, "Class B": 2}
    exp_props = {"Class A": 0.90, "Class B": 0.10}  # N=20 -> Exp B = 2.0 < 5.0

    result = calculate_chi_square(obs, exp_props, alpha=0.05)
    assert result.warning_small_counts
    assert result.warning_message is not None
    assert "Cochran" in result.warning_message
