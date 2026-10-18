"""
Genetics Engine: Gametogenesis and Independent Assortment Module
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from typing import Dict, List, Tuple
from collections import defaultdict
from genetics_engine.genotype import MultiLocusGenotype, LocusGenotype


def calculate_gametes(parent: MultiLocusGenotype) -> Dict[str, float]:
    """
    Computes gamete genotypes and their theoretical probabilities according to:
    1. Mendel's Law of Segregation (each locus allele pair segregates with p = 0.5 for heterozygotes, p = 1.0 for homozygotes)
    2. Mendel's Law of Independent Assortment (metaphase I orientation of non-homologous chromosomes is independent)
    3. Product Rule of Probability: P(Gamete) = ∏ P(Allele_i)
    
    Returns:
        Dict mapping gamete string (e.g., 'AB', 'Ab', 'aB', 'ab') to probability float.
    """
    gametes: Dict[str, float] = {"": 1.0}
    
    for locus_geno in parent.loci:
        locus_gametes = locus_geno.get_gamete_distribution()
        new_gametes: Dict[str, float] = defaultdict(float)
        
        for partial_gamete, partial_prob in gametes.items():
            for allele_char, allele_prob in locus_gametes.items():
                combo = partial_gamete + allele_char
                new_gametes[combo] += partial_prob * allele_prob
                
        gametes = dict(new_gametes)
        
    return gametes


def get_gamete_list_ordered(gamete_dict: Dict[str, float]) -> List[Tuple[str, float]]:
    """
    Returns gametes in canonical order (all-dominant first, e.g. AB, Ab, aB, ab).
    """
    # Sort keys: uppercase letters precede lowercase
    sorted_keys = sorted(gamete_dict.keys(), key=lambda g: (-sum(1 for c in g if c.isupper()), g))
    return [(k, gamete_dict[k]) for k in sorted_keys]
