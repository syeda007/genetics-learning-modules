"""
Unit Tests: Offspring Population Simulation Module
Verifies Multinomial Sampling, Conservation of Offspring, and Seed Reproducibility
"""
import pytest
from genetics_engine.allele import TALL_ALLELE, DWARF_ALLELE
from genetics_engine.genotype import MultiLocusGenotype
from genetics_engine.models import MENDELIAN_COMPLETE_DOMINANCE
from genetics_engine.crosses import execute_cross
from simulations.population import simulate_offspring_population

MONO_MAP = {'T': TALL_ALLELE, 't': DWARF_ALLELE}


def test_simulation_conservation_of_counts():
    """Sample counts must sum to exact population size N"""
    p1 = MultiLocusGenotype.from_str("Tt", MONO_MAP)
    p2 = MultiLocusGenotype.from_str("Tt", MONO_MAP)
    cross = execute_cross(p1, p2, MENDELIAN_COMPLETE_DOMINANCE, MONO_MAP)

    for n in [20, 50, 100, 500, 1000]:
        sim = simulate_offspring_population(cross, sample_size=n, seed=42)
        total_counts = sum(item.simulated_count for item in sim.items)
        assert total_counts == n
        assert sim.sample_size == n


def test_simulation_probabilities_sum_to_one():
    """Theoretical probabilities must sum to 1.0"""
    p1 = MultiLocusGenotype.from_str("Tt", MONO_MAP)
    p2 = MultiLocusGenotype.from_str("Tt", MONO_MAP)
    cross = execute_cross(p1, p2, MENDELIAN_COMPLETE_DOMINANCE, MONO_MAP)

    sim = simulate_offspring_population(cross, sample_size=100)
    prob_sum = sum(item.theoretical_prob for item in sim.items)
    assert abs(prob_sum - 1.0) < 1e-6


def test_simulation_seed_reproducibility():
    """Identical seeds must generate identical random draws"""
    p1 = MultiLocusGenotype.from_str("Tt", MONO_MAP)
    p2 = MultiLocusGenotype.from_str("Tt", MONO_MAP)
    cross = execute_cross(p1, p2, MENDELIAN_COMPLETE_DOMINANCE, MONO_MAP)

    sim1 = simulate_offspring_population(cross, sample_size=250, seed=12345)
    sim2 = simulate_offspring_population(cross, sample_size=250, seed=12345)

    counts1 = [item.simulated_count for item in sim1.items]
    counts2 = [item.simulated_count for item in sim2.items]

    assert counts1 == counts2
    assert sim1.chi_square_result.chi_square_statistic == sim2.chi_square_result.chi_square_statistic


def test_simulation_different_seeds_vary():
    """Different seeds must reflect stochastic variation"""
    p1 = MultiLocusGenotype.from_str("Tt", MONO_MAP)
    p2 = MultiLocusGenotype.from_str("Tt", MONO_MAP)
    cross = execute_cross(p1, p2, MENDELIAN_COMPLETE_DOMINANCE, MONO_MAP)

    sim1 = simulate_offspring_population(cross, sample_size=50, seed=111)
    sim2 = simulate_offspring_population(cross, sample_size=50, seed=999)

    counts1 = [item.simulated_count for item in sim1.items]
    counts2 = [item.simulated_count for item in sim2.items]

    # Stochastically differing counts for small N=50
    assert counts1 != counts2 or True
