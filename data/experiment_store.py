"""
Experiment Storage and Reproducibility Module
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
import os
import json
import csv
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ExperimentRecord:
    experiment_id: str
    timestamp: str
    experiment_type: str
    parent1_genotype: str
    parent2_genotype: str
    model_name: str
    model_assumptions: List[str]
    student_prediction: str
    expected_genotypic_ratio: str
    expected_phenotypic_ratio: str
    theoretical_frequencies: Dict[str, float]
    simulated_or_observed_counts: Dict[str, int]
    is_simulation: bool
    simulation_seed: Optional[int]
    sample_size: int
    chi_square_statistic: Optional[float]
    degrees_of_freedom: Optional[int]
    p_value: Optional[float]
    statistical_conclusion: Optional[str]
    error_classification: Optional[str]
    scientific_interpretation: str


class ExperimentStore:
    """
    Manages structured local experiment logs in JSON and CSV formats.
    Enables postgraduates to review experimental history and reproduce simulations via seed.
    """
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.experiments_dir = os.path.join(base_dir, "experiments")
        self.index_file = os.path.join(self.experiments_dir, "experiments_index.csv")
        os.makedirs(self.experiments_dir, exist_ok=True)
        self._ensure_index_file()

    def _ensure_index_file(self):
        if not os.path.exists(self.index_file):
            with open(self.index_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "experiment_id", "timestamp", "experiment_type",
                    "parent1", "parent2", "sample_size", "chi2_stat", "p_value", "seed"
                ])

    def save_experiment(self, record: ExperimentRecord) -> str:
        """
        Saves full experiment record to an individual JSON file and appends summary to CSV index.
        """
        filename = f"{record.experiment_id}.json"
        json_path = os.path.join(self.experiments_dir, filename)
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(asdict(record), f, indent=2)
            
        # Append to CSV index
        with open(self.index_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                record.experiment_id,
                record.timestamp,
                record.experiment_type,
                record.parent1_genotype,
                record.parent2_genotype,
                record.sample_size,
                f"{record.chi_square_statistic:.4f}" if record.chi_square_statistic is not None else "N/A",
                f"{record.p_value:.4f}" if record.p_value is not None else "N/A",
                record.simulation_seed if record.simulation_seed is not None else "N/A"
            ])
            
        return json_path

    def load_experiment(self, experiment_id: str) -> Optional[ExperimentRecord]:
        """Loads a specific record by experiment ID."""
        json_path = os.path.join(self.experiments_dir, f"{experiment_id}.json")
        if not os.path.exists(json_path):
            return None
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return ExperimentRecord(**data)

    def list_recent_experiments(self, limit: int = 50) -> List[Dict[str, str]]:
        """Returns recent experiment summaries from the CSV index."""
        if not os.path.exists(self.index_file):
            return []
        rows = []
        with open(self.index_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return list(reversed(rows))[:limit]
