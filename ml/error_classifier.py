"""
Machine Learning Module: Offline Student Error Classifier (Decision Tree Baseline)
Academic Genetics Research System (Postgraduate M.Sc. Genetics)

SCIENTIFIC & ARCHITECTURAL PRINCIPLE:
1. Operates 100% offline with zero cloud/API dependencies.
2. The deterministic genetics engine is always the primary truth authority.
3. This ML classifier predicts the conceptual root-cause category of the student error.
4. Model architecture: Interpretable scikit-learn DecisionTreeClassifier with max_depth=6.
"""
import os
import csv
import joblib
import numpy as np
from typing import Dict, Any, Tuple, Optional, List
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from ml.synthetic_data import generate_synthetic_dataset

MODEL_FILE = os.path.join(os.path.dirname(__file__), "model_decision_tree.joblib")
DATASET_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_student_evaluations.csv")


class OfflineErrorClassifier:
    """
    Offline Decision Tree classifier for categorizing student genetic errors.
    """
    def __init__(self):
        self.model: Optional[DecisionTreeClassifier] = None
        self.classes_: Optional[np.ndarray] = None
        self.feature_names: List[str] = [
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

    def _extract_features(self, row: Dict[str, Any]) -> List[float]:
        locus_count = float(row.get("locus_count", 1))
        exp_p = str(row.get("expected_pheno_ratio", "")).strip().replace(" ", "")
        exp_g = str(row.get("expected_geno_ratio", "")).strip().replace(" ", "")
        sub = str(row.get("student_submitted_ratio", "")).strip().replace(" ", "")
        
        matches_p = 1.0 if sub == exp_p else 0.0
        matches_g = 1.0 if sub == exp_g else 0.0
        matches_perm = 1.0 if sorted(sub.split(":")) == sorted(exp_g.split(":")) else 0.0
        is_single = 1.0 if sub in ["3:1", "1:2:1", "1:1", "100%"] else 0.0
        is_dihybrid = 1.0 if sub in ["9:3:3:1", "1:1:1:1"] else 0.0
        
        comps = len(sub.split(":"))
        is_1_1 = 1.0 if "1:1" in sub else 0.0
        is_3_1 = 1.0 if "3:1" in sub else 0.0
        exp_dihybrid = 1.0 if "9:3:3:1" in exp_p else 0.0
        
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

    def train(self, dataset_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Trains the Decision Tree on synthetic educational data and saves the artifact locally.
        """
        if dataset_path is None:
            dataset_path = DATASET_FILE
            
        if not os.path.exists(dataset_path):
            generate_synthetic_dataset(dataset_path, num_samples=5000, seed=42)
            
        X, y = [], []
        with open(dataset_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                X.append(self._extract_features(row))
                y.append(row["target_error_category"])
                
        X = np.array(X)
        y = np.array(y)
        
        # 80/20 train/test split with stratified sampling
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42, stratify=y
        )
        
        self.model = DecisionTreeClassifier(
            max_depth=8,
            criterion="entropy",
            random_state=42
        )
        self.model.fit(X_train, y_train)
        self.classes_ = self.model.classes_
        
        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        conf_matrix = confusion_matrix(y_test, y_pred, labels=self.classes_)
        
        # Save model artifact
        artifact = {
            "model": self.model,
            "classes": self.classes_,
            "feature_names": self.feature_names,
            "accuracy": acc
        }
        joblib.dump(artifact, MODEL_FILE)
        
        return {
            "accuracy": acc,
            "test_samples": len(y_test),
            "train_samples": len(y_train),
            "classes": list(self.classes_),
            "confusion_matrix": conf_matrix.tolist()
        }

    def load(self) -> bool:
        """Loads pre-trained model from disk."""
        if os.path.exists(MODEL_FILE):
            artifact = joblib.load(MODEL_FILE)
            self.model = artifact["model"]
            self.classes_ = artifact["classes"]
            self.feature_names = artifact["feature_names"]
            return True
        return False

    def predict(self, locus_count: int, expected_pheno: str, expected_geno: str, student_sub: str) -> Tuple[str, float]:
        """
        Fast local offline inference (< 2ms) on student submission.
        Returns predicted category and classification confidence.
        """
        if self.model is None:
            if not self.load():
                self.train()
                
        sample_dict = {
            "locus_count": locus_count,
            "expected_pheno_ratio": expected_pheno,
            "expected_geno_ratio": expected_geno,
            "student_submitted_ratio": student_sub
        }
        features = np.array([self._extract_features(sample_dict)])
        pred_idx = self.model.predict(features)[0]
        probs = self.model.predict_proba(features)[0]
        confidence = float(np.max(probs))
        return pred_idx, confidence


# Singleton offline classifier instance
_CLASSIFIER_INSTANCE = None

def get_error_classifier() -> OfflineErrorClassifier:
    global _CLASSIFIER_INSTANCE
    if _CLASSIFIER_INSTANCE is None:
        _CLASSIFIER_INSTANCE = OfflineErrorClassifier()
        if not _CLASSIFIER_INSTANCE.load():
            _CLASSIFIER_INSTANCE.train()
    return _CLASSIFIER_INSTANCE
