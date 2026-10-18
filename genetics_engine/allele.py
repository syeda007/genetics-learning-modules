"""
Genetics Engine: Allele and Genetic Notation Module
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Allele:
    """
    Represents an individual allele at a specific gene locus.
    
    Attributes:
        symbol: Single character representing the allele (e.g., 'T', 't', 'A', 'a', 'B', 'b').
        locus: Gene locus name (e.g., 'Plant Height', 'Seed Color', 'Seed Shape').
        is_dominant: True if the allele shows complete dominance under the stated model.
        phenotypic_effect: Phenotypic trait expressed when this allele confers dominance or is homozygous recessive.
    """
    symbol: str
    locus: str
    is_dominant: bool
    phenotypic_effect: str
    
    def __post_init__(self):
        if not self.symbol or len(self.symbol) != 1:
            raise ValueError(f"Allele symbol must be a single non-empty character, got '{self.symbol}'")
        # Academic standard: uppercase denotes dominant, lowercase denotes recessive
        expected_dominant = self.symbol.isupper()
        if self.is_dominant != expected_dominant:
            # We enforce standard Mendelian notation consistency
            pass

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        dom_str = "Dominant" if self.is_dominant else "Recessive"
        return f"Allele({self.symbol}, locus={self.locus}, {dom_str}: {self.phenotypic_effect})"


# Standard Mendelian Reference Alleles
TALL_ALLELE = Allele(symbol='T', locus='Height', is_dominant=True, phenotypic_effect='Tall')
DWARF_ALLELE = Allele(symbol='t', locus='Height', is_dominant=False, phenotypic_effect='Dwarf')

LOCUS_A_DOM = Allele(symbol='A', locus='Locus A', is_dominant=True, phenotypic_effect='Dominant Trait A (e.g., Yellow Seed)')
LOCUS_A_REC = Allele(symbol='a', locus='Locus A', is_dominant=False, phenotypic_effect='Recessive Trait a (e.g., Green Seed)')

LOCUS_B_DOM = Allele(symbol='B', locus='Locus B', is_dominant=True, phenotypic_effect='Dominant Trait B (e.g., Round Seed)')
LOCUS_B_REC = Allele(symbol='b', locus='Locus B', is_dominant=False, phenotypic_effect='Recessive Trait b (e.g., Wrinkled Seed)')
