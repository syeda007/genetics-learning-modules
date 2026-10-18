"""
Unit Tests: Genetics Calculation Engine
Verifies Monohybrid, Dihybrid, Test Crosses, and General Combinatorial Algorithms
"""
import pytest
from genetics_engine.allele import TALL_ALLELE, DWARF_ALLELE, LOCUS_A_DOM, LOCUS_A_REC, LOCUS_B_DOM, LOCUS_B_REC
from genetics_engine.genotype import MultiLocusGenotype
from genetics_engine.models import MENDELIAN_COMPLETE_DOMINANCE, DIHYBRID_INDEPENDENT_ASSORTMENT
from genetics_engine.crosses import execute_cross

MONO_MAP = {'T': TALL_ALLELE, 't': DWARF_ALLELE}
DI_MAP = {'A': LOCUS_A_DOM, 'a': LOCUS_A_REC, 'B': LOCUS_B_DOM, 'b': LOCUS_B_REC}


def test_monohybrid_true_breeding_tt_x_tt():
    """TT × tt → 100% Tt (100% Tall phenotype)"""
    p1 = MultiLocusGenotype.from_str("TT", MONO_MAP)
    p2 = MultiLocusGenotype.from_str("tt", MONO_MAP)
    result = execute_cross(p1, p2, MENDELIAN_COMPLETE_DOMINANCE, MONO_MAP)

    assert result.genotype_frequencies.get("Tt") == 1.0
    assert result.phenotype_frequencies.get("Tall") == 1.0
    assert result.punnett_square.num_rows == 1
    assert result.punnett_square.num_cols == 1


def test_monohybrid_heterozygous_tt_x_tt():
    """Tt × Tt → 1 TT : 2 Tt : 1 tt genotypic, 3 Tall : 1 Dwarf phenotypic"""
    p1 = MultiLocusGenotype.from_str("Tt", MONO_MAP)
    p2 = MultiLocusGenotype.from_str("Tt", MONO_MAP)
    result = execute_cross(p1, p2, MENDELIAN_COMPLETE_DOMINANCE, MONO_MAP)

    assert abs(result.genotype_frequencies["Tt"] - 0.50) < 1e-5
    assert abs(result.genotype_frequencies["TT"] - 0.25) < 1e-5
    assert abs(result.genotype_frequencies["tt"] - 0.25) < 1e-5

    assert abs(result.phenotype_frequencies["Tall"] - 0.75) < 1e-5
    assert abs(result.phenotype_frequencies["Dwarf"] - 0.25) < 1e-5

    assert result.genotype_ratios == "1 : 2 : 1" or result.genotype_ratios == "2 : 1 : 1"
    assert result.phenotype_ratios == "3 : 1"


def test_monohybrid_test_cross_tt_x_tt():
    """Tt × tt → 50% Tt, 50% tt (1:1 phenotypic ratio)"""
    p1 = MultiLocusGenotype.from_str("Tt", MONO_MAP)
    p2 = MultiLocusGenotype.from_str("tt", MONO_MAP)
    result = execute_cross(p1, p2, MENDELIAN_COMPLETE_DOMINANCE, MONO_MAP)

    assert abs(result.phenotype_frequencies["Tall"] - 0.50) < 1e-5
    assert abs(result.phenotype_frequencies["Dwarf"] - 0.50) < 1e-5
    assert result.phenotype_ratios == "1 : 1"


def test_monohybrid_recessive_cross_tt_x_tt():
    """tt × tt → 100% tt (100% Dwarf phenotype)"""
    p1 = MultiLocusGenotype.from_str("tt", MONO_MAP)
    p2 = MultiLocusGenotype.from_str("tt", MONO_MAP)
    result = execute_cross(p1, p2, MENDELIAN_COMPLETE_DOMINANCE, MONO_MAP)

    assert result.genotype_frequencies.get("tt") == 1.0
    assert result.phenotype_frequencies.get("Dwarf") == 1.0


def test_dihybrid_heterozygous_cross_aabb_x_aabb():
    """AaBb × AaBb → 9:3:3:1 phenotypic distribution under independent assortment"""
    p1 = MultiLocusGenotype.from_str("AaBb", DI_MAP)
    p2 = MultiLocusGenotype.from_str("AaBb", DI_MAP)
    result = execute_cross(p1, p2, DIHYBRID_INDEPENDENT_ASSORTMENT, DI_MAP)

    assert result.punnett_square.num_rows == 4
    assert result.punnett_square.num_cols == 4
    assert len(result.punnett_square.grid) == 4
    assert len(result.punnett_square.grid[0]) == 4

    # 9/16, 3/16, 3/16, 1/16
    phenos = list(result.phenotype_frequencies.values())
    assert len(phenos) == 4
    assert abs(phenos[0] - 9.0/16.0) < 1e-5
    assert abs(phenos[1] - 3.0/16.0) < 1e-5
    assert abs(phenos[2] - 3.0/16.0) < 1e-5
    assert abs(phenos[3] - 1.0/16.0) < 1e-5
    assert result.phenotype_ratios == "9 : 3 : 3 : 1"


def test_dihybrid_true_breeding_aabb_x_aabb():
    """AABB × aabb → 100% AaBb"""
    p1 = MultiLocusGenotype.from_str("AABB", DI_MAP)
    p2 = MultiLocusGenotype.from_str("aabb", DI_MAP)
    result = execute_cross(p1, p2, DIHYBRID_INDEPENDENT_ASSORTMENT, DI_MAP)

    assert result.genotype_frequencies.get("AaBb") == 1.0
    assert len(result.phenotype_frequencies) == 1
