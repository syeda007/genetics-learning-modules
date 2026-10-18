"""
Genetics Error Analysis: Deterministic Evaluation and Genetics Authority Module
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

from genetics_engine.crosses import CrossResult
from biostatistics.ratios import parse_ratio_string


class ErrorCategory(str, Enum):
    CORRECT = "CORRECT_PREDICTION"
    CONFUSING_GENOTYPE_WITH_PHENOTYPE = "CONFUSING_GENOTYPE_WITH_PHENOTYPE_RATIO"
    INCORRECT_DOMINANCE_ASSUMPTION = "INCORRECT_DOMINANCE_ASSUMPTION"
    SEGREGATION_FAILURE = "SEGREGATION_FAILURE"
    INDEPENDENT_ASSORTMENT_FAILURE = "INDEPENDENT_ASSORTMENT_FAILURE"
    PRODUCT_RULE_ERROR = "PRODUCT_RULE_ERROR"
    SAMPLING_VARIANCE_MISINTERPRETATION = "SAMPLING_VARIANCE_MISINTERPRETATION"
    STATISTICAL_INCORRECT_CONCLUSION = "STATISTICAL_INCORRECT_CONCLUSION"
    GENERAL_ARITHMETIC_DISCREPANCY = "GENERAL_ARITHMETIC_DISCREPANCY"


@dataclass
class EvaluationReport:
    is_correct: bool
    error_category: ErrorCategory
    student_prediction: str
    expected_ratio: str
    cross_representation: str
    scientific_feedback: str
    derivation_proof: str
    confidence: float = 1.0


def evaluate_student_prediction(cross_result: CrossResult,
                                student_ratio_input: str,
                                target_attribute: str = "phenotype") -> EvaluationReport:
    """
    Deterministic genetics authority evaluating student hypothesis/prediction against calculated inheritance outcomes.
    
    Identifies exact error taxonomy and generates academically rigorous feedback.
    """
    expected_ratio = cross_result.phenotype_ratios if target_attribute == "phenotype" else cross_result.genotype_ratios
    alt_ratio = cross_result.genotype_ratios if target_attribute == "phenotype" else cross_result.phenotype_ratios
    
    clean_student = student_ratio_input.strip().replace(" ", "")
    clean_expected = expected_ratio.strip().replace(" ", "")
    clean_alt = alt_ratio.strip().replace(" ", "")
    
    parsed_student = parse_ratio_string(clean_student)
    parsed_expected = parse_ratio_string(clean_expected)
    parsed_alt = parse_ratio_string(clean_alt)
    
    cross_str = f"{cross_result.parent1.string_rep} × {cross_result.parent2.string_rep}"
    
    # Check exact string or numerical equivalence
    if clean_student == clean_expected or (parsed_student and parsed_expected and len(parsed_student) == len(parsed_expected) and all(abs(a - b) < 0.05 for a, b in zip(parsed_student, parsed_expected))):
        return EvaluationReport(
            is_correct=True,
            error_category=ErrorCategory.CORRECT,
            student_prediction=student_ratio_input,
            expected_ratio=expected_ratio,
            cross_representation=cross_str,
            scientific_feedback=(
                f"CORRECT: Your predicted {target_attribute} ratio ({student_ratio_input}) is completely consistent with the "
                f"theoretical outcome under {cross_result.model.model_name}. Meiotic segregation and gametic union produce this exact distribution."
            ),
            derivation_proof="\n".join(cross_result.derivation_steps),
            confidence=1.0
        )
        
    # Check if student confused genotype ratio with phenotype ratio
    is_geno_confusion = False
    if clean_student == clean_alt:
        is_geno_confusion = True
    elif parsed_student and parsed_alt and len(parsed_student) == len(parsed_alt):
        if all(abs(a - b) < 0.05 for a, b in zip(parsed_student, parsed_alt)) or \
           all(abs(a - b) < 0.05 for a, b in zip(sorted(parsed_student), sorted(parsed_alt))):
            is_geno_confusion = True

    if is_geno_confusion:
        feedback = (
            f"DISCREPANCY: Confusing Genotypic with Phenotypic Distribution.\n"
            f"You submitted '{student_ratio_input}', which matches the theoretical GENOTYPIC ratio ({alt_ratio}), "
            f"rather than the requested PHENOTYPIC ratio ({expected_ratio}).\n"
            "Under complete dominance, heterozygous individuals (e.g., Tt or Aa) manifest the dominant phenotype, "
            "coalescing the homozygous dominant and heterozygous genotypic classes into a single phenotypic class."
        )
        return EvaluationReport(
            is_correct=False,
            error_category=ErrorCategory.CONFUSING_GENOTYPE_WITH_PHENOTYPE,
            student_prediction=student_ratio_input,
            expected_ratio=expected_ratio,
            cross_representation=cross_str,
            scientific_feedback=feedback,
            derivation_proof="\n".join(cross_result.derivation_steps),
            confidence=1.0
        )

    # Check for monohybrid vs dihybrid confusion
    num_loci = len(cross_result.parent1.loci)
    if num_loci == 2 and ("3:1" in clean_student or "1:2:1" in clean_student):
        feedback = (
            f"DISCREPANCY: Independent Assortment Misapplication.\n"
            f"For a dihybrid cross involving two unlinked loci ({cross_str}), four distinct gamete types are produced per parent. "
            f"Predicting a single-locus ratio (such as {student_ratio_input}) fails to account for simultaneous independent assortment across both loci. "
            f"The classic dihybrid F2 phenotypic ratio under independent assortment and complete dominance is 9:3:3:1."
        )
        return EvaluationReport(
            is_correct=False,
            error_category=ErrorCategory.INDEPENDENT_ASSORTMENT_FAILURE,
            student_prediction=student_ratio_input,
            expected_ratio=expected_ratio,
            cross_representation=cross_str,
            scientific_feedback=feedback,
            derivation_proof="\n".join(cross_result.derivation_steps),
            confidence=1.0
        )

    # Check dominance assumption error
    if "1:1" in clean_student and clean_expected in ["3:1", "100%"]:
        feedback = (
            f"DISCREPANCY: Incorrect Dominance or Segregation Assumption.\n"
            f"A 1:1 ratio arises specifically in a monohybrid test cross (heterozygote × homozygous recessive, Tt × tt). "
            f"In the cross {cross_str}, the expected phenotypic ratio is {expected_ratio}. "
            "Verify the parental zygosity and gametic combinations in the Punnett square."
        )
        return EvaluationReport(
            is_correct=False,
            error_category=ErrorCategory.INCORRECT_DOMINANCE_ASSUMPTION,
            student_prediction=student_ratio_input,
            expected_ratio=expected_ratio,
            cross_representation=cross_str,
            scientific_feedback=feedback,
            derivation_proof="\n".join(cross_result.derivation_steps),
            confidence=0.95
        )

    # General discrepancy
    feedback = (
        f"DISCREPANCY: Prediction Inconsistent with Stated Mendelian Model.\n"
        f"Submitted: '{student_ratio_input}', Expected: '{expected_ratio}'.\n"
        "Please review the Punnett square grid below: examine the gametes generated during meiotic disjunction, "
        "and calculate the resulting zygote frequencies using the product and sum rules of probability."
    )
    return EvaluationReport(
        is_correct=False,
        error_category=ErrorCategory.GENERAL_ARITHMETIC_DISCREPANCY,
        student_prediction=student_ratio_input,
        expected_ratio=expected_ratio,
        cross_representation=cross_str,
        scientific_feedback=feedback,
        derivation_proof="\n".join(cross_result.derivation_steps),
        confidence=0.90
    )
