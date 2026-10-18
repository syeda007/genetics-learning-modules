"""
Simulations: Offspring Population Sampling and Stochastic Variation Module
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np

from genetics_engine.crosses import CrossResult
from biostatistics.chi_square import calculate_chi_square, ChiSquareResult


@dataclass
class PopulationSampleItem:
    category: str
    theoretical_prob: float
    expected_count: float
    simulated_count: int
    simulated_percentage: float
    percentage_deviation: float  # |Obs - Exp| / Exp * 100%


@dataclass
class PopulationSimulationResult:
    sample_size: int
    random_seed: Optional[int]
    items: List[PopulationSampleItem]
    chi_square_result: ChiSquareResult
    scientific_summary: str


def simulate_offspring_population(cross_result: CrossResult,
                                  sample_size: int,
                                  seed: Optional[int] = None,
                                  use_phenotypes: bool = True) -> PopulationSimulationResult:
    """
    Performs stochastic multinomial sampling of offspring based on theoretical Mendelian cross probabilities.
    
    Demonstrates:
    - Bernoulli/Multinomial sampling variability in finite biological populations.
    - Convergence towards theoretical expectation as sample size N increases (Law of Large Numbers).
    - Statistical goodness-of-fit validation on simulated experimental cohorts.
    """
    if sample_size <= 0:
        raise ValueError(f"Sample size must be positive, got {sample_size}")
    
    freq_dict = cross_result.phenotype_frequencies if use_phenotypes else cross_result.genotype_frequencies
    categories = list(freq_dict.keys())
    probabilities = [freq_dict[c] for c in categories]
    
    # Normalize probabilities to avoid slight floating-point drift
    prob_sum = sum(probabilities)
    norm_probs = [p / prob_sum for p in probabilities]
    
    # Initialize random generator
    rng = np.random.default_rng(seed)
    
    # Multinomial draw
    counts = rng.multinomial(sample_size, norm_probs)
    
    items: List[PopulationSampleItem] = []
    observed_counts_dict: Dict[str, float] = {}
    expected_props_dict: Dict[str, float] = {}
    
    for cat, p, count in zip(categories, norm_probs, counts):
        exp_count = sample_size * p
        sim_pct = (count / sample_size) * 100.0
        # Percentage deviation relative to expected count
        pct_dev = (abs(count - exp_count) / exp_count * 100.0) if exp_count > 0 else 0.0
        
        items.append(PopulationSampleItem(
            category=cat,
            theoretical_prob=p,
            expected_count=exp_count,
            simulated_count=int(count),
            simulated_percentage=sim_pct,
            percentage_deviation=pct_dev
        ))
        
        observed_counts_dict[cat] = float(count)
        expected_props_dict[cat] = p

    # Perform Chi-Square goodness-of-fit on the simulated sample
    chi2_res = calculate_chi_square(observed_counts_dict, expected_props_dict)
    
    avg_dev = np.mean([item.percentage_deviation for item in items])
    
    summary = (
        f"Population Simulation (N = {sample_size:,}, Seed = {seed if seed is not None else 'Unspecified'}).\n"
        f"Average class deviation from expectation: {avg_dev:.2f}%.\n"
        f"Goodness-of-Fit: χ² = {chi2_res.chi_square_statistic:.3f}, p = {chi2_res.p_value:.4f} "
        f"({chi2_res.conclusion})."
    )
    if sample_size < 100:
        summary += " Note: In small sample cohorts (N < 100), stochastic sampling fluctuations frequently cause observable percentage deviations despite adherence to true underlying Mendelian probabilities."
    else:
        summary += " Note: As sample size N increases, observed percentages asymptotically converge toward theoretical probabilities as predicted by the Law of Large Numbers."

    return PopulationSimulationResult(
        sample_size=sample_size,
        random_seed=seed,
        items=items,
        chi_square_result=chi2_res,
        scientific_summary=summary
    )
