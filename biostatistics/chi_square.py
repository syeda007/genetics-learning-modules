"""
Statistical Analysis: Pearson Chi-Square Goodness-of-Fit Module
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


@dataclass
class ChiSquareCategoryResult:
    category: str
    observed: float
    expected: float
    difference: float
    squared_diff: float
    chi_square_contribution: float


@dataclass
class ChiSquareResult:
    categories: List[ChiSquareCategoryResult]
    total_observed: float
    total_expected: float
    chi_square_statistic: float
    degrees_of_freedom: int
    p_value: float
    alpha: float
    is_significant: bool
    warning_small_counts: bool
    warning_message: Optional[str]
    interpretation: str
    conclusion: str


def _chi2_sf_fallback(x: float, df: int) -> float:
    """
    Analytical survival function (1 - CDF) for chi-square distribution
    used as a fallback when scipy is not available.
    Uses regularized upper incomplete gamma function: Q(s, x/2) = Gamma(s, x/2) / Gamma(s) where s = df / 2.
    """
    if x <= 0:
        return 1.0
    if df <= 0:
        return 0.0
    
    s = df / 2.0
    z = x / 2.0
    
    # Series expansion for lower incomplete gamma P(s, z), then Q = 1 - P
    # P(s, z) = (z^s * e^(-z) / Gamma(s)) * sum_{n=0}^inf (z^n / (s * (s+1) * ... * (s+n)))
    try:
        sum_term = 0.0
        term = 1.0 / s
        sum_term = term
        for n in range(1, 150):
            term = term * z / (s + n)
            sum_term += term
            if abs(term) < 1e-12:
                break
        log_prefix = s * math.log(z) - z - math.lgamma(s)
        p_lower = math.exp(log_prefix) * sum_term
        q_upper = max(0.0, min(1.0, 1.0 - p_lower))
        return q_upper
    except (OverflowError, ValueError):
        return 0.0


def calculate_chi_square(observed_counts: Dict[str, float],
                         expected_proportions: Dict[str, float],
                         alpha: float = 0.05) -> ChiSquareResult:
    """
    Performs Pearson's Chi-Square Goodness-of-Fit test on categorical genetic offspring data.
    
    Formula:
        χ² = Σ [ (Observed_i - Expected_i)² / Expected_i ]
        df = k - 1 (for k fully prespecified phenotypic/genotypic classes)
    
    Args:
        observed_counts: Dict mapping category name to observed count.
        expected_proportions: Dict mapping category name to theoretical proportion (must sum to ~1.0).
        alpha: Significance threshold (default 0.05).
    """
    categories = list(expected_proportions.keys())
    total_obs = sum(observed_counts.get(cat, 0.0) for cat in categories)
    
    # Validate categories
    if len(categories) < 2:
        raise ValueError("Chi-square goodness-of-fit requires at least k = 2 categories.")
    
    # Check normalization of proportions
    prop_sum = sum(expected_proportions.values())
    norm_props = {k: v / prop_sum for k, v in expected_proportions.items()}
    
    cat_results: List[ChiSquareCategoryResult] = []
    total_chi2 = 0.0
    small_count_flag = False
    small_count_categories = []
    
    for cat in categories:
        obs = float(observed_counts.get(cat, 0.0))
        exp = total_obs * norm_props[cat]
        
        if exp < 5.0:
            small_count_flag = True
            small_count_categories.append(f"{cat} (E={exp:.1f})")
            
        diff = obs - exp
        sq_diff = diff ** 2
        contrib = sq_diff / exp if exp > 0 else 0.0
        total_chi2 += contrib
        
        cat_results.append(ChiSquareCategoryResult(
            category=cat,
            observed=obs,
            expected=exp,
            difference=diff,
            squared_diff=sq_diff,
            chi_square_contribution=contrib
        ))
        
    df = len(categories) - 1
    
    # Compute p-value
    if SCIPY_AVAILABLE:
        p_val = float(stats.chi2.sf(total_chi2, df))
    else:
        p_val = _chi2_sf_fallback(total_chi2, df)
        
    is_sig = p_val < alpha
    
    # Warnings
    warning_msg = None
    if small_count_flag:
        warning_msg = (
            f"WARNING (Cochran's Rule): Expected frequency < 5 in class(es): {', '.join(small_count_categories)}. "
            "The asymptotic chi-square continuous approximation may be unreliable for small expected cell counts."
        )
    if total_obs < 20:
        extra = f" Total sample size N = {total_obs:.0f} is small (< 20)."
        warning_msg = (warning_msg + extra) if warning_msg else extra

    # Academic statistical interpretations
    if is_sig:
        conclusion = "Reject Null Hypothesis (H₀)"
        interpretation = (
            f"Statistically significant discrepancy detected (χ² = {total_chi2:.4f}, df = {df}, p = {p_val:.4e} < α = {alpha}). "
            "The observed phenotypic frequencies differ significantly from the expected Mendelian inheritance proportions. "
            "Potential biological causes include genetic linkage, differential zygotic or gametic viability, meiotic drive, "
            "epistasis, or non-random fertilization."
        )
    else:
        conclusion = "Fail to Reject Null Hypothesis (H₀)"
        interpretation = (
            f"No statistically significant discrepancy detected (χ² = {total_chi2:.4f}, df = {df}, p = {p_val:.4f} ≥ α = {alpha}). "
            "The observed counts are statistically consistent with the hypothesized Mendelian inheritance model. "
            "Scientific Caveat: In formal biostatistical inference, failing to reject H₀ does NOT prove that the null hypothesis "
            "is true with absolute certainty; rather, the data provide insufficient evidence to rule out the proposed model."
        )

    return ChiSquareResult(
        categories=cat_results,
        total_observed=total_obs,
        total_expected=total_obs,
        chi_square_statistic=total_chi2,
        degrees_of_freedom=df,
        p_value=p_val,
        alpha=alpha,
        is_significant=is_sig,
        warning_small_counts=small_count_flag,
        warning_message=warning_msg,
        interpretation=interpretation,
        conclusion=conclusion
    )
