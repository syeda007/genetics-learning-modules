"""
Genetics Engine: Algorithmic Cross Execution and Punnett Square Engine
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict
import math

from genetics_engine.allele import Allele
from genetics_engine.genotype import LocusGenotype, MultiLocusGenotype
from genetics_engine.gametes import calculate_gametes, get_gamete_list_ordered
from genetics_engine.models import GeneticModel, MENDELIAN_COMPLETE_DOMINANCE


@dataclass
class PunnettCell:
    row_gamete: str
    col_gamete: str
    zygote_genotype: str
    zygote_phenotype: str
    probability: float


@dataclass
class PunnettSquare:
    row_gametes: List[Tuple[str, float]]
    col_gametes: List[Tuple[str, float]]
    grid: List[List[PunnettCell]]
    
    @property
    def num_rows(self) -> int:
        return len(self.row_gametes)

    @property
    def num_cols(self) -> int:
        return len(self.col_gametes)


@dataclass
class CrossResult:
    parent1: MultiLocusGenotype
    parent2: MultiLocusGenotype
    model: GeneticModel
    punnett_square: PunnettSquare
    genotype_frequencies: Dict[str, float]
    genotype_ratios: str
    phenotype_frequencies: Dict[str, float]
    phenotype_ratios: str
    derivation_steps: List[str]

    def summary_table(self) -> str:
        lines = [
            f"Cross: {self.parent1.string_rep} × {self.parent2.string_rep}",
            f"Genetic Model: {self.model.model_name}",
            "",
            "--- GENOTYPIC DISTRIBUTION ---",
            f"Ratio: {self.genotype_ratios}"
        ]
        for g, freq in self.genotype_frequencies.items():
            lines.append(f"  {g:<8} : {freq * 100:6.2f}% (prob = {freq:.4f})")
        
        lines.append("")
        lines.append("--- PHENOTYPIC DISTRIBUTION ---")
        lines.append(f"Ratio: {self.phenotype_ratios}")
        for p, freq in self.phenotype_frequencies.items():
            lines.append(f"  {p:<30} : {freq * 100:6.2f}% (prob = {freq:.4f})")
        return "\n".join(lines)


def _combine_gametes(g1: str, g2: str, allele_map: Dict[str, Allele]) -> MultiLocusGenotype:
    """
    Combines two gamete haploid strings (e.g., 'AB' and 'ab') into a diploid MultiLocusGenotype ('AaBb').
    """
    if len(g1) != len(g2):
        raise ValueError(f"Gamete lengths must match: '{g1}' vs '{g2}'")
    
    loci = []
    for char1, char2 in zip(g1, g2):
        a1 = allele_map[char1]
        a2 = allele_map[char2]
        loci.append(LocusGenotype(a1, a2))
    return MultiLocusGenotype(loci)


def _format_ratio(freq_dict: Dict[str, float]) -> str:
    """
    Computes reduced integer ratio from a frequency dictionary (e.g., 3:1, 1:2:1, 9:3:3:1).
    """
    if not freq_dict:
        return ""
    
    values = list(freq_dict.values())
    min_val = min(v for v in values if v > 0)
    
    # Check common standard Mendelian multipliers (1, 2, 4, 16, 64)
    multipliers = [1, 2, 4, 8, 16, 64]
    best_integers = None
    best_error = float('inf')
    
    for mult in multipliers:
        scaled = [v * mult for v in values]
        rounded = [round(s) for s in scaled]
        if all(r > 0 for r in rounded):
            err = sum(abs(s - r) for s, r in zip(scaled, rounded))
            if err < 1e-4:
                # Divide by gcd of rounded integers
                g = rounded[0]
                for r in rounded[1:]:
                    g = math.gcd(g, r)
                best_integers = [r // g for r in rounded]
                break
            elif err < best_error:
                best_error = err
                best_integers = rounded

    if best_integers:
        return " : ".join(str(i) for i in best_integers)
    return " : ".join(f"{v:.2f}" for v in values)


def execute_cross(parent1: MultiLocusGenotype,
                  parent2: MultiLocusGenotype,
                  model: GeneticModel,
                  allele_map: Dict[str, Allele]) -> CrossResult:
    """
    Algorithmic execution of a genetic cross between two parents.
    Generates gametes, constructs the Punnett grid, tallies genotypic and phenotypic frequencies,
    computes ratios, and details the derivation steps.
    """
    derivation = [
        f"Step 1: Identify parental genotypes: P1 = {parent1.string_rep}, P2 = {parent2.string_rep}",
        "Step 2: Apply Mendel's First Law (Segregation) during Meiosis I to determine gametic allele distribution.",
    ]
    
    p1_gametes = calculate_gametes(parent1)
    p2_gametes = calculate_gametes(parent2)
    
    derivation.append(f"  P1 Gamete Pool: {', '.join(f'{g} (p={p:.2f})' for g, p in p1_gametes.items())}")
    derivation.append(f"  P2 Gamete Pool: {', '.join(f'{g} (p={p:.2f})' for g, p in p2_gametes.items())}")
    
    if len(parent1.loci) > 1:
        derivation.append("Step 3: Apply Mendel's Second Law (Independent Assortment) across unlinked loci.")
        derivation.append("  Gamete probabilities reflect product of independent locus segregation probabilities.")
    
    ordered_p1 = get_gamete_list_ordered(p1_gametes)
    ordered_p2 = get_gamete_list_ordered(p2_gametes)
    
    grid: List[List[PunnettCell]] = []
    geno_freqs: Dict[str, float] = defaultdict(float)
    pheno_freqs: Dict[str, float] = defaultdict(float)
    
    for r_gam, r_prob in ordered_p1:
        row: List[PunnettCell] = []
        for c_gam, c_prob in ordered_p2:
            cell_prob = r_prob * c_prob
            zygote = _combine_gametes(r_gam, c_gam, allele_map)
            z_geno_str = zygote.string_rep
            z_pheno_str = zygote.get_phenotype()
            
            geno_freqs[z_geno_str] += cell_prob
            pheno_freqs[z_pheno_str] += cell_prob
            
            row.append(PunnettCell(
                row_gamete=r_gam,
                col_gamete=c_gam,
                zygote_genotype=z_geno_str,
                zygote_phenotype=z_pheno_str,
                probability=cell_prob
            ))
        grid.append(row)
        
    punnett_sq = PunnettSquare(row_gametes=ordered_p1, col_gametes=ordered_p2, grid=grid)
    
    # Sort frequencies descending for standard display
    sorted_geno = dict(sorted(geno_freqs.items(), key=lambda item: -item[1]))
    sorted_pheno = dict(sorted(pheno_freqs.items(), key=lambda item: -item[1]))
    
    geno_ratio = _format_ratio(sorted_geno)
    pheno_ratio = _format_ratio(sorted_pheno)
    
    derivation.append(f"Step 4: Construct {punnett_sq.num_rows} × {punnett_sq.num_cols} Punnett Square ({punnett_sq.num_rows * punnett_sq.num_cols} combinations).")
    derivation.append(f"Step 5: Theoretical Genotypic Ratio: {geno_ratio}")
    derivation.append(f"Step 6: Theoretical Phenotypic Ratio (under {model.dominance_type}): {pheno_ratio}")
    
    return CrossResult(
        parent1=parent1,
        parent2=parent2,
        model=model,
        punnett_square=punnett_sq,
        genotype_frequencies=sorted_geno,
        genotype_ratios=geno_ratio,
        phenotype_frequencies=sorted_pheno,
        phenotype_ratios=pheno_ratio,
        derivation_steps=derivation
    )
