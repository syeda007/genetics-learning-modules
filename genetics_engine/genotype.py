"""
Genetics Engine: Genotype and Zygosity Representation Module
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from typing import Tuple, List, Dict
from genetics_engine.allele import Allele, TALL_ALLELE, DWARF_ALLELE, LOCUS_A_DOM, LOCUS_A_REC, LOCUS_B_DOM, LOCUS_B_REC


class LocusGenotype:
    """
    Represents a diploid pair of alleles at a single locus.
    """
    def __init__(self, allele1: Allele, allele2: Allele):
        if allele1.locus != allele2.locus:
            raise ValueError(f"Alleles must belong to the same locus. Got {allele1.locus} and {allele2.locus}")
        
        # Enforce canonical sorting: dominant first, or alphabetical if same dominance
        if not allele1.is_dominant and allele2.is_dominant:
            self.allele1, self.allele2 = allele2, allele1
        elif allele1.symbol > allele2.symbol and allele1.is_dominant == allele2.is_dominant:
            self.allele1, self.allele2 = allele2, allele1
        else:
            self.allele1, self.allele2 = allele1, allele2
            
        self.locus = self.allele1.locus

    @classmethod
    def from_str(cls, genotype_str: str, allele_map: Dict[str, Allele]) -> 'LocusGenotype':
        """Construct LocusGenotype from 2-letter string representation."""
        if len(genotype_str) != 2:
            raise ValueError(f"Single-locus genotype string must have length 2, got '{genotype_str}'")
        a1 = allele_map[genotype_str[0]]
        a2 = allele_map[genotype_str[1]]
        return cls(a1, a2)

    @property
    def is_homozygous(self) -> bool:
        return self.allele1.symbol == self.allele2.symbol

    @property
    def is_heterozygous(self) -> bool:
        return self.allele1.symbol != self.allele2.symbol

    @property
    def is_homozygous_dominant(self) -> bool:
        return self.is_homozygous and self.allele1.is_dominant

    @property
    def is_homozygous_recessive(self) -> bool:
        return self.is_homozygous and not self.allele1.is_dominant

    @property
    def zygosity_description(self) -> str:
        if self.is_homozygous_dominant:
            return "Homozygous Dominant"
        elif self.is_heterozygous:
            return "Heterozygous"
        elif self.is_homozygous_recessive:
            return "Homozygous Recessive"
        return "Unknown Zygosity"

    def get_phenotype(self) -> str:
        """
        Determines the phenotype under the assumption of complete dominance.
        If at least one dominant allele is present, the dominant phenotype is expressed.
        Otherwise, the homozygous recessive phenotype is expressed.
        """
        if self.allele1.is_dominant or self.allele2.is_dominant:
            dom = self.allele1 if self.allele1.is_dominant else self.allele2
            return dom.phenotypic_effect
        return self.allele1.phenotypic_effect

    def get_gamete_distribution(self) -> Dict[str, float]:
        """
        Calculates gametes formed according to Mendel's Law of Segregation.
        Under normal meiosis without meiotic drive, each allele segregates with equal probability (0.5).
        """
        if self.is_homozygous:
            return {self.allele1.symbol: 1.0}
        else:
            return {self.allele1.symbol: 0.5, self.allele2.symbol: 0.5}

    @property
    def string_rep(self) -> str:
        return f"{self.allele1.symbol}{self.allele2.symbol}"

    def __str__(self) -> str:
        return self.string_rep

    def __repr__(self) -> str:
        return f"LocusGenotype({self.string_rep}, {self.zygosity_description})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, LocusGenotype):
            return False
        return self.string_rep == other.string_rep

    def __hash__(self) -> int:
        return hash(self.string_rep)


class MultiLocusGenotype:
    """
    Represents an organism's genotype across multiple independently assorting loci.
    """
    def __init__(self, loci: List[LocusGenotype]):
        if not loci:
            raise ValueError("MultiLocusGenotype requires at least one locus.")
        self.loci = loci

    @classmethod
    def from_str(cls, genotype_str: str, allele_map: Dict[str, Allele]) -> 'MultiLocusGenotype':
        """
        Construct MultiLocusGenotype from string like 'AaBb' or 'TT'.
        """
        if len(genotype_str) % 2 != 0:
            raise ValueError(f"Genotype string must have an even number of characters, got '{genotype_str}'")
        
        loci = []
        for i in range(0, len(genotype_str), 2):
            sub = genotype_str[i:i+2]
            loci.append(LocusGenotype.from_str(sub, allele_map))
        return cls(loci)

    @property
    def string_rep(self) -> str:
        return "".join(loc.string_rep for loc in self.loci)

    def get_phenotype(self) -> str:
        """Composite phenotype across all loci under complete dominance."""
        return " / ".join(loc.get_phenotype() for loc in self.loci)

    def __str__(self) -> str:
        return self.string_rep

    def __repr__(self) -> str:
        return f"MultiLocusGenotype({self.string_rep})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, MultiLocusGenotype):
            return False
        return self.string_rep == other.string_rep

    def __hash__(self) -> int:
        return hash(self.string_rep)
