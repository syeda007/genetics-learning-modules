"""
Machine Learning Module: Documented Synthetic Educational Dataset Generator
Academic Genetics Research System (Postgraduate M.Sc. Genetics)

SCIENTIFIC NOTICE:
This module generates SYNTHETIC EDUCATIONAL SIMULATION DATA for the purpose of training
and evaluating an offline student error classification model.
These data points DO NOT constitute genuine biological observations from living organisms.
They represent modeled student interaction patterns and theoretical genetic cross configurations.
"""
import csv
import os
import random
from typing import List, Dict

MONOHYBRID_CROSSES = [
    ("TT", "tt", "100% Tall", "100% Tt", 1),
    ("Tt", "Tt", "3:1", "1:2:1", 1),
    ("Tt", "tt", "1:1", "1:1", 1),
    ("TT", "Tt", "100% Tall", "1:1", 1),
    ("tt", "tt", "100% Dwarf", "100% tt", 1),
    ("TT", "TT", "100% Tall", "100% TT", 1)
]

DIHYBRID_CROSSES = [
    ("AaBb", "AaBb", "9:3:3:1", "1:2:1:2:4:2:1:2:1", 2),
    ("AABB", "aabb", "100% Dominant", "100% AaBb", 2),
    ("AaBb", "aabb", "1:1:1:1", "1:1:1:1", 2),
    ("AABb", "AaBb", "3:1", "1:2:1:1:2:1", 2),
    ("AaBB", "AaBb", "3:1", "1:1:2:2:1:1", 2)
]

ERROR_PROFILES = [
    ("CORRECT_PREDICTION", lambda exp_p, exp_g: exp_p),
    ("CONFUSING_GENOTYPE_WITH_PHENOTYPE_RATIO", lambda exp_p, exp_g: exp_g),
    ("INCORRECT_DOMINANCE_ASSUMPTION", lambda exp_p, exp_g: "1:1" if exp_p != "1:1" else "3:1"),
    ("INDEPENDENT_ASSORTMENT_FAILURE", lambda exp_p, exp_g: "3:1" if "9:3:3:1" in exp_p else "1:1"),
    ("GENERAL_ARITHMETIC_DISCREPANCY", lambda exp_p, exp_g: "2:1" if "3:1" in exp_p else "4:1")
]


def generate_synthetic_dataset(output_path: str, num_samples: int = 5000, seed: int = 42) -> str:
    """
    Generates synthetic student submission records with realistic error frequencies.
    """
    random.seed(seed)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    headers = [
        "sample_id",
        "data_type",
        "parent1_geno",
        "parent2_geno",
        "locus_count",
        "expected_pheno_ratio",
        "expected_geno_ratio",
        "student_submitted_ratio",
        "is_correct",
        "target_error_category"
    ]
    
    rows = []
    for i in range(num_samples):
        # 60% monohybrid, 40% dihybrid
        if random.random() < 0.6:
            cross = random.choice(MONOHYBRID_CROSSES)
        else:
            cross = random.choice(DIHYBRID_CROSSES)
            
        p1, p2, exp_pheno, exp_geno, loci = cross
        
        # Error choice: 45% correct, 55% various mistakes
        err_cat, gen_fn = random.choices(
            ERROR_PROFILES,
            weights=[0.45, 0.20, 0.15, 0.12, 0.08],
            k=1
        )[0]
        
        # If dihybrid error was selected for monohybrid, fallback gracefully
        if loci == 1 and err_cat == "INDEPENDENT_ASSORTMENT_FAILURE":
            err_cat = "GENERAL_ARITHMETIC_DISCREPANCY"
            
        student_ratio = gen_fn(exp_pheno, exp_geno)
        is_corr = 1 if err_cat == "CORRECT_PREDICTION" else 0
        
        rows.append({
            "sample_id": f"SYN-{i+1:05d}",
            "data_type": "SYNTHETIC_EDUCATIONAL_DATA_NOT_BIOLOGICAL",
            "parent1_geno": p1,
            "parent2_geno": p2,
            "locus_count": loci,
            "expected_pheno_ratio": exp_pheno,
            "expected_geno_ratio": exp_geno,
            "student_submitted_ratio": student_ratio,
            "is_correct": is_corr,
            "target_error_category": err_cat
        })
        
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
        
    return output_path


if __name__ == "__main__":
    out = generate_synthetic_dataset("d:/ai-projectscd/genetics-research-system/data/synthetic_student_evaluations.csv")
    print(f"Generated synthetic training dataset: {out}")
