"""
UI Screen: Experiment 01 — Monohybrid Inheritance
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QLineEdit, QTextEdit, QScrollArea, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal

from genetics_engine.allele import TALL_ALLELE, DWARF_ALLELE
from genetics_engine.genotype import MultiLocusGenotype
from genetics_engine.models import MENDELIAN_COMPLETE_DOMINANCE
from genetics_engine.crosses import execute_cross, CrossResult
from ml.deterministic_evaluator import evaluate_student_prediction
from data.experiment_store import ExperimentRecord, ExperimentStore
from ui.components.punnett_widget import PunnettSquareWidget
from hardware.base import HardwareAdapter
from hardware.led_controller import LedController
from content.scientific_text import MENDELIAN_BACKGROUND

ALLELE_MAP = {'T': TALL_ALLELE, 't': DWARF_ALLELE}


class MonohybridExperimentScreen(QWidget):
    navigate_to = pyqtSignal(str)

    def __init__(self, hardware_adapter: HardwareAdapter, led_controller: LedController, exp_store: ExperimentStore, parent=None):
        super().__init__(parent)
        self.adapter = hardware_adapter
        self.led_controller = led_controller
        self.exp_store = exp_store
        self.last_cross_result = None
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(8)

        # Header bar
        header_h = QHBoxLayout()
        btn_back = QPushButton("← MODULE 01 HUB", self)
        btn_back.clicked.connect(lambda: self.navigate_to.emit("module01_hub"))
        header_h.addWidget(btn_back)
        
        title = QLabel("EXPERIMENT 01: MONOHYBRID INHERITANCE", self)
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffffff;")
        header_h.addWidget(title)
        header_h.addStretch()
        main_layout.addLayout(header_h)

        # Splitter: Left panel (Configuration & Predictions) | Right panel (Results & Proof)
        splitter = QSplitter(Qt.Horizontal, self)

        # LEFT PANEL
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(6)

        # Objectives Card
        obj_frame = QFrame(left_widget)
        obj_frame.setObjectName("lab-card")
        obj_layout = QVBoxLayout(obj_frame)
        obj_layout.setSpacing(2)
        obj_title = QLabel("EXPERIMENTAL OBJECTIVE & MODEL ASSUMPTIONS", obj_frame)
        obj_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        obj_desc = QLabel(MENDELIAN_BACKGROUND["exp01_objective"], obj_frame)
        obj_desc.setWordWrap(True)
        obj_desc.setStyleSheet("color: #a0b2c6; font-size: 9px;")
        obj_layout.addWidget(obj_title)
        obj_layout.addWidget(obj_desc)
        left_layout.addWidget(obj_frame)

        # Parental Configuration Card
        parents_frame = QFrame(left_widget)
        parents_frame.setObjectName("lab-card")
        p_layout = QVBoxLayout(parents_frame)
        p_layout.setSpacing(4)
        
        p_title = QLabel("PARENTAL GENOTYPE CONFIGURATION (GPIO / SWITCHES)", parents_frame)
        p_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        p_layout.addWidget(p_title)

        p1_h = QHBoxLayout()
        p1_h.addWidget(QLabel("Parent 1 (♀):", parents_frame))
        self.p1_combo = QComboBox(parents_frame)
        self.p1_combo.addItems(["TT (Homozygous Dominant)", "Tt (Heterozygous)", "tt (Homozygous Recessive)"])
        self.p1_combo.setCurrentIndex(1) # Default Tt
        p1_h.addWidget(self.p1_combo)
        p_layout.addLayout(p1_h)

        p2_h = QHBoxLayout()
        p2_h.addWidget(QLabel("Parent 2 (♂):", parents_frame))
        self.p2_combo = QComboBox(parents_frame)
        self.p2_combo.addItems(["TT (Homozygous Dominant)", "Tt (Heterozygous)", "tt (Homozygous Recessive)"])
        self.p2_combo.setCurrentIndex(1) # Default Tt
        p2_h.addWidget(self.p2_combo)
        p_layout.addLayout(p2_h)
        left_layout.addWidget(parents_frame)

        # Student Hypothesis Card
        hypo_frame = QFrame(left_widget)
        hypo_frame.setObjectName("lab-card")
        hypo_layout = QVBoxLayout(hypo_frame)
        hypo_layout.setSpacing(4)
        hypo_title = QLabel("HYPOTHESIS & PREDICTED PHENOTYPIC RATIO", hypo_frame)
        hypo_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        hypo_layout.addWidget(hypo_title)
        
        hypo_input_h = QHBoxLayout()
        hypo_input_h.addWidget(QLabel("Predicted Ratio:", hypo_frame))
        self.pred_input = QLineEdit(hypo_frame)
        self.pred_input.setPlaceholderText("e.g. 3:1, 1:2:1, or 1:1")
        self.pred_input.setText("3:1")
        hypo_input_h.addWidget(self.pred_input)
        hypo_layout.addLayout(hypo_input_h)
        left_layout.addWidget(hypo_frame)

        # Action Buttons
        btn_cross = QPushButton("⚡ GENERATE CROSS & EVALUATE", left_widget)
        btn_cross.setObjectName("btn-primary")
        btn_cross.clicked.connect(self._run_cross)
        left_layout.addWidget(btn_cross)

        self.btn_save = QPushButton("💾 SAVE EXPERIMENT RECORD", left_widget)
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._save_record)
        left_layout.addWidget(self.btn_save)

        self.save_status_label = QLabel("", left_widget)
        self.save_status_label.setStyleSheet("color: #2ec4b6; font-size: 9px; font-weight: bold;")
        left_layout.addWidget(self.save_status_label)
        left_layout.addStretch()

        splitter.addWidget(left_widget)

        # RIGHT PANEL: Results, Punnett Matrix & Scientific Explanations
        right_scroll = QScrollArea(self)
        right_scroll.setWidgetResizable(True)
        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)
        right_layout.setContentsMargins(6, 4, 6, 4)
        right_layout.setSpacing(8)

        # Punnett Square Widget
        self.punnett_widget = PunnettSquareWidget(right_content)
        right_layout.addWidget(self.punnett_widget)

        # Ratios Summary Card
        self.results_card = QFrame(right_content)
        self.results_card.setObjectName("lab-card")
        self.res_layout = QVBoxLayout(self.results_card)
        self.res_title = QLabel("CALCULATED THEORETICAL RATIOS", self.results_card)
        self.res_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        self.res_text = QLabel("Configure parents and execute cross to calculate theoretical inheritance ratios.", self.results_card)
        self.res_text.setWordWrap(True)
        self.res_layout.addWidget(self.res_title)
        self.res_layout.addWidget(self.res_text)
        right_layout.addWidget(self.results_card)

        # Feedback & Scientific Explanation
        self.feedback_card = QFrame(right_content)
        self.feedback_card.setObjectName("lab-card")
        self.fb_layout = QVBoxLayout(self.feedback_card)
        self.fb_title = QLabel("PREDICTION EVALUATION & SCIENTIFIC DERIVATION", self.feedback_card)
        self.fb_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        self.fb_text = QTextEdit(self.feedback_card)
        self.fb_text.setReadOnly(True)
        self.fb_text.setStyleSheet("background-color: #0b1325; border: 1px solid #1a2c4e; color: #e0e6ed; font-size: 10px;")
        self.fb_text.setFixedHeight(110)
        self.fb_layout.addWidget(self.fb_title)
        self.fb_layout.addWidget(self.fb_text)
        right_layout.addWidget(self.feedback_card)

        right_scroll.setWidget(right_content)
        splitter.addWidget(right_scroll)
        splitter.setSizes([340, 460])

        main_layout.addWidget(splitter)

        # Connect hardware switch adapter events if parent index changes
        self.adapter.genotype_selected.connect(self._on_hardware_genotype_selected)

    def _get_selected_geno(self, combo: QComboBox) -> str:
        txt = combo.currentText()
        return txt[:2]

    def _on_hardware_genotype_selected(self, parent_idx: int, geno: str):
        if len(geno) == 2 and geno in ["TT", "Tt", "tt"]:
            combo = self.p1_combo if parent_idx == 1 else self.p2_combo
            idx = ["TT", "Tt", "tt"].index(geno)
            combo.setCurrentIndex(idx)
            self.led_controller.trigger_input_confirmed()

    def _run_cross(self):
        p1_str = self._get_selected_geno(self.p1_combo)
        p2_str = self._get_selected_geno(self.p2_combo)

        p1 = MultiLocusGenotype.from_str(p1_str, ALLELE_MAP)
        p2 = MultiLocusGenotype.from_str(p2_str, ALLELE_MAP)

        # Execute algorithmic cross
        self.last_cross_result = execute_cross(p1, p2, MENDELIAN_COMPLETE_DOMINANCE, ALLELE_MAP)

        # Update Punnett square
        self.punnett_widget.display_punnett_square(self.last_cross_result.punnett_square)

        # Update ratios text
        self.res_text.setText(
            f"Cross: {p1_str} × {p2_str}\n"
            f"Genotypic Ratio: {self.last_cross_result.genotype_ratios} "
            f"({', '.join(f'{k}: {v*100:.1f}%' for k, v in self.last_cross_result.genotype_frequencies.items())})\n"
            f"Phenotypic Ratio: {self.last_cross_result.phenotype_ratios} "
            f"({', '.join(f'{k}: {v*100:.1f}%' for k, v in self.last_cross_result.phenotype_frequencies.items())})"
        )

        # Evaluate student prediction
        pred_text = self.pred_input.text().strip()
        eval_report = evaluate_student_prediction(self.last_cross_result, pred_text, target_attribute="phenotype")
        self.led_controller.trigger_prediction_result(eval_report.is_correct)

        self.fb_text.setText(
            f"{eval_report.scientific_feedback}\n\n"
            f"--- THEORETICAL DERIVATION ---\n{eval_report.derivation_proof}\n\n"
            f"--- MOLECULAR BASIS ---\n{MENDELIAN_BACKGROUND['exp01_scientific_basis']}"
        )

        self.btn_save.setEnabled(True)
        self.save_status_label.setText("")

    def _save_record(self):
        if not self.last_cross_result:
            return
        p1_str = self._get_selected_geno(self.p1_combo)
        p2_str = self._get_selected_geno(self.p2_combo)
        pred_text = self.pred_input.text().strip()

        eval_report = evaluate_student_prediction(self.last_cross_result, pred_text)

        rec = ExperimentRecord(
            experiment_id=f"EXP01-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            experiment_type="Monohybrid Inheritance (Single Locus)",
            parent1_genotype=p1_str,
            parent2_genotype=p2_str,
            model_name=MENDELIAN_COMPLETE_DOMINANCE.model_name,
            model_assumptions=MENDELIAN_COMPLETE_DOMINANCE.scientific_assumptions,
            student_prediction=pred_text,
            expected_genotypic_ratio=self.last_cross_result.genotype_ratios,
            expected_phenotypic_ratio=self.last_cross_result.phenotype_ratios,
            theoretical_frequencies=self.last_cross_result.phenotype_frequencies,
            simulated_or_observed_counts={},
            is_simulation=False,
            simulation_seed=None,
            sample_size=0,
            chi_square_statistic=None,
            degrees_of_freedom=None,
            p_value=None,
            statistical_conclusion=None,
            error_classification=eval_report.error_category.value,
            scientific_interpretation=eval_report.scientific_feedback
        )
        saved_path = self.exp_store.save_experiment(rec)
        self.led_controller.trigger_experiment_complete()
        self.save_status_label.setText(f"✓ Experiment record logged: {rec.experiment_id}")
