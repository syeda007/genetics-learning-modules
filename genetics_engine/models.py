"""
Genetics Engine: Model Assumptions and Qualifications
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from dataclasses import dataclass
from typing import List


@dataclass
class GeneticModel:
    """
    Defines the biological parameters and theoretical assumptions governing the cross.
    """
    model_name: str
    dominance_type: str = "Complete Dominance"
    linkage_status: str = "Unlinked (Synteny Absent, r = 0.50)"
    viability_assumption: bool = True
    penetrance: float = 1.0
    expressivity: str = "Uniform"
    
    @property
    def scientific_assumptions(self) -> List[str]:
        return [
            f"Dominance Model: {self.dominance_type}. Heterozygotes exhibit the exact phenotype of the dominant homozygote.",
            f"Chromosomal Linkage: {self.linkage_status}. Loci segregate independently according to Mendel's Second Law.",
            "Meiotic Segregation: Normal chromosome disjunction occurs at anaphase I with no meiotic drive.",
            "Fertilization: Random union of gametes with equal gamete and zygote viability (no lethal alleles).",
            f"Expressivity & Penetrance: Complete penetrance ({int(self.penetrance * 100)}%) with {self.expressivity} phenotypic manifestation.",
            "Gene Interaction: No inter-locus epistasis, duplicate gene action, or modifying gene effects."
        ]

    def get_summary_text(self) -> str:
        lines = [f"=== {self.model_name.upper()} ASSUMPTIONS ==="]
        for idx, asm in enumerate(self.scientific_assumptions, 1):
            lines.append(f"{idx}. {asm}")
        lines.append("Note: Complete dominance is a model-specific physiological relationship between alleles, not a general law of biology.")
        return "\n".join(lines)


# Standard Classical Mendelian Model
MENDELIAN_COMPLETE_DOMINANCE = GeneticModel(
    model_name="Classical Mendelian Inheritance (Complete Dominance)"
)

# Dihybrid Independent Assortment Model
DIHYBRID_INDEPENDENT_ASSORTMENT = GeneticModel(
    model_name="Dihybrid Independent Assortment",
    linkage_status="Unlinked loci on separate non-homologous autosomes"
)
