"""
Unit Tests: Error Evaluation and Offline Machine Learning Module
Verifies Deterministic Genetics Authority and Local Decision Tree Inference
"""
import pytest
from genetics_engine.allele import TALL_ALLELE, DWARF_ALLELE, LOCUS_A_DOM, LOCUS_A_REC, LOCUS_B_DOM, LOCUS_B_REC
from genetics_engine.genotype import MultiLocusGenotype
from genetics_engine.models import MENDELIAN_COMPLETE_DOMINANCE, DIHYBRID_INDEPENDENT_ASSORTMENT
from genetics_engine.crosses import execute_cross
from ml.deterministic_evaluator import evaluate_student_prediction, ErrorCategory
from ml.error_classifier import OfflineErrorClassifier

MONO_MAP = {'T': TALL_ALLELE, 't': DWARF_ALLELE}
DI_MAP = {'A': LOCUS_A_DOM, 'a': LOCUS_A_REC, 'B': LOCUS_B_DOM, 'b': LOCUS_B_REC}


def test_deterministic_correct_prediction():
    p1 = MultiLocusGenotype.from_str("Tt", MONO_MAP)
    p2 = MultiLocusGenotype.from_str("Tt", MONO_MAP)
    cross = execute_cross(p1, p2, MENDELIAN_COMPLETE_DOMINANCE, MONO_MAP)

    rep = evaluate_student_prediction(cross, "3:1")
    assert rep.is_correct is True
    assert rep.error_category == ErrorCategory.CORRECT


def test_deterministic_genotype_phenotype_confusion():
    p1 = MultiLocusGenotype.from_str("Tt", MONO_MAP)
    p2 = MultiLocusGenotype.from_str("Tt", MONO_MAP)
    cross = execute_cross(p1, p2, MENDELIAN_COMPLETE_DOMINANCE, MONO_MAP)

    # Submitting 1:2:1 when phenotype requested (3:1 expected)
    rep = evaluate_student_prediction(cross, "1:2:1")
    assert rep.is_correct is False
    assert rep.error_category == ErrorCategory.CONFUSING_GENOTYPE_WITH_PHENOTYPE
    assert "GENOTYPIC" in rep.scientific_feedback


def test_deterministic_independent_assortment_failure():
    p1 = MultiLocusGenotype.from_str("AaBb", DI_MAP)
    p2 = MultiLocusGenotype.from_str("AaBb", DI_MAP)
    cross = execute_cross(p1, p2, DIHYBRID_INDEPENDENT_ASSORTMENT, DI_MAP)

    # Submitting 3:1 on a dihybrid cross
    rep = evaluate_student_prediction(cross, "3:1")
    assert rep.is_correct is False
    assert rep.error_category == ErrorCategory.INDEPENDENT_ASSORTMENT_FAILURE


def test_offline_ml_training_and_inference():
    """Verify local Decision Tree trains, persists, and performs offline inference"""
    clf = OfflineErrorClassifier()
    metrics = clf.train()

    assert metrics["accuracy"] >= 0.80
    assert metrics["test_samples"] > 0
    assert len(metrics["classes"]) >= 4

    # Test inference: locus_count=1, exp_pheno="3:1", exp_geno="1:2:1", student="1:2:1"
    pred_cat, conf = clf.predict(1, "3:1", "1:2:1", "1:2:1")
    assert pred_cat == "CONFUSING_GENOTYPE_WITH_PHENOTYPE_RATIO"
    assert conf > 0.50

    # Test inference: correct prediction
    pred_corr, conf_corr = clf.predict(1, "3:1", "1:2:1", "3:1")
    assert pred_corr == "CORRECT_PREDICTION"
