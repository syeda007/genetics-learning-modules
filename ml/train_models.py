"""
Machine Learning Module: Model Training, Cross-Template Validation & Model Selection
Academic Genetics Research System (Postgraduate M.Sc. Genetics)

SCIENTIFIC PROVENANCE & CAVEAT:
All training and evaluation datasets are SYNTHETIC educational simulation data.
They model common student misconceptions (such as confusing phenotypic and
genotypic ratios, or failing to apply Mendel's second law of independent assortment).
These models are NOT clinically or educationally validated on human student cohorts
and must not be presented as cognitive certainty.
"""
import os
import csv
import time
import random
import joblib
import numpy as np
from typing import Dict, Any, List, Tuple

from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
ARTIFACTS_FILE = os.path.join(BASE_DIR, "model_artifacts.joblib")
LEGACY_MODEL_FILE = os.path.join(BASE_DIR, "model_decision_tree.joblib")
DATASET_FILE = os.path.join(DATA_DIR, "synthetic_student_evaluations.csv")

FEATURE_NAMES = [
    "locus_count",
    "matches_expected_pheno",
    "matches_expected_geno",
    "matches_geno_perm",
    "is_single_locus_ratio",
    "is_dihybrid_ratio",
    "ratio_component_count",
    "student_is_1_to_1",
    "student_is_3_to_1",
    "exp_is_dihybrid"
]

ERROR_CATEGORIES = [
    "CORRECT_PREDICTION",
    "CONFUSING_GENOTYPE_WITH_PHENOTYPE_RATIO",
    "INCORRECT_DOMINANCE_ASSUMPTION",
    "INDEPENDENT_ASSORTMENT_FAILURE",
    "GENERAL_ARITHMETIC_DISCREPANCY"
]


def extract_features(row: Dict[str, Any]) -> List[float]:
    locus_count = float(row.get("locus_count", 1))
    exp_p = str(row.get("expected_pheno_ratio", "")).strip().replace(" ", "")
    exp_g = str(row.get("expected_geno_ratio", "")).strip().replace(" ", "")
    sub = str(row.get("student_submitted_ratio", "")).strip().replace(" ", "")
    
    matches_p = 1.0 if sub == exp_p else 0.0
    matches_g = 1.0 if sub == exp_g else 0.0
    matches_perm = 1.0 if sorted(sub.split(":")) == sorted(exp_g.split(":")) else 0.0
    is_single = 1.0 if sub in ["3:1", "1:2:1", "1:1", "100%", "100%Tall", "100%Dwarf"] else 0.0
    is_dihybrid = 1.0 if sub in ["9:3:3:1", "1:1:1:1", "100%Dominant"] else 0.0
    
    comps = len(sub.split(":"))
    is_1_1 = 1.0 if "1:1" in sub else 0.0
    is_3_1 = 1.0 if "3:1" in sub else 0.0
    exp_dihybrid = 1.0 if ("9:3:3:1" in exp_p or "1:1:1:1" in exp_p) else 0.0
    
    return [
        locus_count,
        matches_p,
        matches_g,
        matches_perm,
        is_single,
        is_dihybrid,
        float(comps),
        is_1_1,
        is_3_1,
        exp_dihybrid
    ]


def build_synthetic_corpus(seed: int = 42) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Builds training/validation corpus AND an explicit held-out test set
    with distinct, previously unseen cross configurations to test generalization
    and address cross-template leakage.
    """
    random.seed(seed)
    
    # Standard training/validation crosses
    standard_crosses = [
        ("TT", "tt", "100% Tall", "100% Tt", 1, "standard"),
        ("Tt", "Tt", "3:1", "1:2:1", 1, "standard"),
        ("Tt", "tt", "1:1", "1:1", 1, "standard"),
        ("TT", "Tt", "100% Tall", "1:1", 1, "standard"),
        ("tt", "tt", "100% Dwarf", "100% tt", 1, "standard"),
        ("AaBb", "AaBb", "9:3:3:1", "1:2:1:2:4:2:1:2:1", 2, "standard"),
        ("AABB", "aabb", "100% Dominant", "100% AaBb", 2, "standard"),
        ("AaBb", "aabb", "1:1:1:1", "1:1:1:1", 2, "standard"),
        ("AABb", "AaBb", "3:1", "1:2:1:1:2:1", 2, "standard")
    ]
    
    # Held-out cross configurations (never seen during training or validation)
    held_out_crosses = [
        ("AaBB", "AaBb", "3:1", "1:1:2:2:1:1", 2, "held_out"),
        ("AaBb", "Aabb", "3:3:1:1", "1:1:2:2:1:1", 2, "held_out"),
        ("Aabb", "aabb", "1:1", "1:1", 2, "held_out"),
        ("AAbb", "aaBB", "100% Dominant", "100% AaBb", 2, "held_out")
    ]
    
    error_generators = [
        ("CORRECT_PREDICTION", lambda exp_p, exp_g: exp_p),
        ("CONFUSING_GENOTYPE_WITH_PHENOTYPE_RATIO", lambda exp_p, exp_g: exp_g),
        ("INCORRECT_DOMINANCE_ASSUMPTION", lambda exp_p, exp_g: "1:1" if exp_p != "1:1" else "3:1"),
        ("INDEPENDENT_ASSORTMENT_FAILURE", lambda exp_p, exp_g: "3:1" if "9:3:3:1" in exp_p else "1:1"),
        ("GENERAL_ARITHMETIC_DISCREPANCY", lambda exp_p, exp_g: "2:1" if "3:1" in exp_p else "4:1")
    ]
    
    def generate_records(cross_pool, n_samples):
        records = []
        for i in range(n_samples):
            cross = random.choice(cross_pool)
            p1, p2, exp_p, exp_g, loci, split_tag = cross
            
            err_cat, gen_fn = random.choices(
                error_generators,
                weights=[0.40, 0.22, 0.16, 0.12, 0.10],
                k=1
            )[0]
            
            if loci == 1 and err_cat == "INDEPENDENT_ASSORTMENT_FAILURE":
                err_cat = "GENERAL_ARITHMETIC_DISCREPANCY"
                
            student_ratio = gen_fn(exp_p, exp_g)
            is_corr = 1 if err_cat == "CORRECT_PREDICTION" else 0
            
            records.append({
                "sample_id": f"SYN-{i+1:05d}",
                "data_type": "SYNTHETIC_SIMULATION",
                "parent1_geno": p1,
                "parent2_geno": p2,
                "locus_count": loci,
                "expected_pheno_ratio": exp_p,
                "expected_geno_ratio": exp_g,
                "student_submitted_ratio": student_ratio,
                "is_correct": is_corr,
                "target_error_category": err_cat,
                "split_pool": split_tag
            })
        return records

    train_val_samples = generate_records(standard_crosses, 4000)
    held_out_samples = generate_records(held_out_crosses, 1000)
    
    return train_val_samples, held_out_samples


def train_and_evaluate_all_models() -> Dict[str, Any]:
    """
    Executes explicit model training, validation model selection, and held-out evaluation.
    Saves serializable artifacts for offline inference.
    """
    train_val_records, held_out_records = build_synthetic_corpus(seed=42)
    
    # Save combined synthetic dataset for record-keeping
    os.makedirs(DATA_DIR, exist_ok=True)
    all_records = train_val_records + held_out_records
    fieldnames = list(all_records[0].keys())
    with open(DATASET_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)
        
    # Feature extraction
    X_train_val = np.array([extract_features(r) for r in train_val_records])
    y_train_val = np.array([r["target_error_category"] for r in train_val_records])
    
    X_held_out = np.array([extract_features(r) for r in held_out_records])
    y_held_out = np.array([r["target_error_category"] for r in held_out_records])
    
    # Split train_val into 75% Train (3,000) and 25% Validation (1,000)
    random.seed(42)
    np.random.seed(42)
    indices = np.arange(len(X_train_val))
    np.random.shuffle(indices)
    split_idx = int(0.75 * len(indices))
    
    train_idx = indices[:split_idx]
    val_idx = indices[split_idx:]
    
    X_train, y_train = X_train_val[train_idx], y_train_val[train_idx]
    X_val, y_val = X_train_val[val_idx], y_train_val[val_idx]
    
    # Define candidate model architectures
    candidates = {
        "Decision Tree (Configured max_depth=6)": DecisionTreeClassifier(
            max_depth=6,
            criterion="entropy",
            random_state=42
        ),
        "Random Forest (n=50, max_depth=6)": RandomForestClassifier(
            n_estimators=50,
            max_depth=6,
            random_state=42
        ),
        "Logistic Regression (L2 regularized)": LogisticRegression(
            max_iter=1000,
            random_state=42
        )
    }
    
    model_evaluations = {}
    best_name = None
    best_val_f1 = -1.0
    
    classes = np.array(ERROR_CATEGORIES)
    
    for name, clf in candidates.items():
        # Fit on training set
        t0 = time.perf_counter()
        clf.fit(X_train, y_train)
        fit_time_ms = (time.perf_counter() - t0) * 1000.0
        
        # Evaluate on validation set
        val_pred = clf.predict(X_val)
        val_acc = accuracy_score(y_val, val_pred)
        p, r, f1, _ = precision_recall_fscore_support(y_val, val_pred, average="macro", zero_division=0)
        
        # Measure latency on validation samples (average per-sample inference latency)
        t_inf_start = time.perf_counter_ns()
        for i in range(min(200, len(X_val))):
            _ = clf.predict(X_val[i:i+1])
        avg_latency_ms = ((time.perf_counter_ns() - t_inf_start) / min(200, len(X_val))) / 1_000_000.0
        
        model_evaluations[name] = {
            "model": clf,
            "val_accuracy": float(val_acc),
            "val_macro_precision": float(p),
            "val_macro_recall": float(r),
            "val_macro_f1": float(f1),
            "fit_time_ms": float(fit_time_ms),
            "avg_latency_ms": float(avg_latency_ms)
        }
        
        if f1 > best_val_f1:
            best_val_f1 = f1
            best_name = name

    # Primary baseline model: Decision Tree
    dt_model = candidates["Decision Tree (Configured max_depth=6)"]
    actual_tree_depth = int(dt_model.get_depth())
    tree_rules = export_text(dt_model, feature_names=FEATURE_NAMES, max_depth=4)
    feature_importances = {fn: float(imp) for fn, imp in zip(FEATURE_NAMES, dt_model.feature_importances_)}
    
    # Held-out evaluation on unseen cross configurations
    held_out_pred = dt_model.predict(X_held_out)
    held_out_acc = accuracy_score(y_held_out, held_out_pred)
    hp, hr, hf1, _ = precision_recall_fscore_support(y_held_out, held_out_pred, average="macro", zero_division=0)
    conf_matrix = confusion_matrix(y_held_out, held_out_pred, labels=classes)
    
    # Per-class metrics
    class_p, class_r, class_f1, class_supp = precision_recall_fscore_support(
        y_held_out, held_out_pred, labels=classes, zero_division=0
    )
    per_class_metrics = {}
    for i, c in enumerate(classes):
        per_class_metrics[c] = {
            "precision": float(class_p[i]),
            "recall": float(class_r[i]),
            "f1": float(class_f1[i]),
            "support": int(class_supp[i])
        }
        
    artifacts = {
        "metadata": {
            "model_version": "2.0.0-academic",
            "model_type": "DecisionTreeClassifier (Interpretable)",
            "configured_depth": 6,
            "actual_depth": actual_tree_depth,
            "criterion": "entropy",
            "feature_names": FEATURE_NAMES,
            "classes": list(classes),
            "train_samples": len(X_train),
            "val_samples": len(X_val),
            "val_accuracy": float(model_evaluations["Decision Tree (Configured max_depth=6)"]["val_accuracy"]),
            "val_macro_f1": float(model_evaluations["Decision Tree (Configured max_depth=6)"]["val_macro_f1"]),
            "held_out_samples": len(X_held_out),
            "held_out_accuracy": float(held_out_acc),
            "held_out_macro_f1": float(hf1),
            "dataset_description": (
                "5,000 synthetic educational records with held-out unseen cross configurations. "
                "NOTICE: Synthetic educational model data, not empirical student learning data."
            )
        },
        "decision_tree": dt_model,
        "best_model_name": best_name,
        "best_model": candidates[best_name],
        "candidate_comparisons": {
            k: {
                "val_accuracy": v["val_accuracy"],
                "val_macro_precision": v["val_macro_precision"],
                "val_macro_recall": v["val_macro_recall"],
                "val_macro_f1": v["val_macro_f1"],
                "fit_time_ms": v["fit_time_ms"],
                "avg_latency_ms": v["avg_latency_ms"]
            } for k, v in model_evaluations.items()
        },
        "feature_importances": feature_importances,
        "tree_rules_text": tree_rules,
        "confusion_matrix": conf_matrix.tolist(),
        "per_class_metrics": per_class_metrics
    }
    
    # Save full artifacts
    joblib.dump(artifacts, ARTIFACTS_FILE)
    
    # Save legacy file for backward compatibility
    legacy_artifact = {
        "model": dt_model,
        "classes": classes,
        "feature_names": FEATURE_NAMES,
        "accuracy": float(held_out_acc)
    }
    joblib.dump(legacy_artifact, LEGACY_MODEL_FILE)
    
    return artifacts


if __name__ == "__main__":
    res = train_and_evaluate_all_models()
    print("Model Training & Evaluation Complete.")
    print(f"Decision Tree Configured Depth: {res['metadata']['configured_depth']}, Actual Depth: {res['metadata']['actual_depth']}")
    print(f"Held-out Unseen Cross Accuracy: {res['metadata']['held_out_accuracy']*100:.2f}%")
    print(f"Held-out Macro F1: {res['metadata']['held_out_macro_f1']:.4f}")
    print(f"Best model selected on Validation: {res['best_model_name']}")
