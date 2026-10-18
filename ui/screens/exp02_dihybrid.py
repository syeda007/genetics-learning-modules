"""
UI Screen: Experiment 02 — Dihybrid Inheritance
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QLineEdit, QTextEdit, QScrollArea, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal

from genetics_engine.allele import LOCUS_A_DOM, LOCUS_A_REC, LOCUS_B_DOM, LOCUS_B_REC
from genetics_engine.genotype import MultiLocusGenotype
from genetics_engine.models import DIHYBRID_INDEPENDENT_ASSORTMENT
from genetics_engine.crosses import execute_cross
from ml.deterministic_evaluator import evaluate_student_prediction
from data.experiment_store import ExperimentRecord, ExperimentStore
from ui.components.punnett_widget import PunnettSquareWidget
from hardware.base import HardwareAdapter
from hardware.led_controller import LedController
from content.scientific_text import MENDELIAN_BACKGROUND

DIHYBRID_ALLELE_MAP = {
    'A': LOCUS_A_DOM, 'a': LOCUS_A_REC,
    'B': LOCUS_B_DOM, 'b': LOCUS_B_REC
}

DIHYBRID_CHOICES = ["AaBb", "AABB", "AABb", "AAbb", "AaBB", "Aabb", "aaBB", "aaBb", "aabb"]


class DihybridExperimentScreen(QWidget):
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
        
        title = QLabel("EXPERIMENT 02: DIHYBRID INHERITANCE (INDEPENDENT ASSORTMENT)", self)
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffffff;")
        header_h.addWidget(title)
        header_h.addStretch()
        main_layout.addLayout(header_h)

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
        obj_title = QLabel("EXPERIMENTAL OBJECTIVE & CONDITIONS FOR 9:3:3:1", obj_frame)
        obj_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        obj_desc = QLabel(MENDELIAN_BACKGROUND["exp02_objective"], obj_frame)
        obj_desc.setWordWrap(True)
        obj_desc.setStyleSheet("color: #a0b2c6; font-size: 9px;")
        obj_layout.addWidget(obj_title)
        obj_layout.addWidget(obj_desc)
        left_layout.addWidget(obj_frame)

        # Parents Selection
        parents_frame = QFrame(left_widget)
        parents_frame.setObjectName("lab-card")
        p_layout = QVBoxLayout(parents_frame)
        p_layout.setSpacing(4)
        p_title = QLabel("TWO-LOCUS PARENTAL CONFIGURATION", parents_frame)
        p_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        p_layout.addWidget(p_title)

        p1_h = QHBoxLayout()
        p1_h.addWidget(QLabel("Parent 1 (♀):", parents_frame))
        self.p1_combo = QComboBox(parents_frame)
        self.p1_combo.addItems(DIHYBRID_CHOICES)
        self.p1_combo.setCurrentIndex(0) # AaBb
        p1_h.addWidget(self.p1_combo)
        p_layout.addLayout(p1_h)

        p2_h = QHBoxLayout()
        p2_h.addWidget(QLabel("Parent 2 (♂):", parents_frame))
        self.p2_combo = QComboBox(parents_frame)
        self.p2_combo.addItems(DIHYBRID_CHOICES)
        self.p2_combo.setCurrentIndex(0) # AaBb
        p2_h.addWidget(self.p2_combo)
        p_layout.addLayout(p2_h)
        left_layout.addWidget(parents_frame)

        # Student Prediction
        hypo_frame = QFrame(left_widget)
        hypo_frame.setObjectName("lab-card")
        hypo_layout = QVBoxLayout(hypo_frame)
        hypo_layout.setSpacing(4)
        hypo_title = QLabel("HYPOTHESIS: EXPECTED PHENOTYPIC RATIO", hypo_frame)
        hypo_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        hypo_layout.addWidget(hypo_title)
        
        hypo_input_h = QHBoxLayout()
        hypo_input_h.addWidget(QLabel("Predicted Ratio:", hypo_frame))
        self.pred_input = QLineEdit(hypo_frame)
        self.pred_input.setPlaceholderText("e.g. 9:3:3:1 or 1:1:1:1")
        self.pred_input.setText("9:3:3:1")
        hypo_input_h.addWidget(self.pred_input)
        hypo_layout.addLayout(hypo_input_h)
        left_layout.addWidget(hypo_frame)

        # Buttons
        btn_cross = QPushButton("⚡ COMPUTE 4×4 CROSS & DERIVATION", left_widget)
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

        # RIGHT PANEL: Punnett Square & Explanation
        right_scroll = QScrollArea(self)
        right_scroll.setWidgetResizable(True)
        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)
        right_layout.setContentsMargins(6, 4, 6, 4)
        right_layout.setSpacing(8)

        self.punnett_widget = PunnettSquareWidget(right_content)
        right_layout.addWidget(self.punnett_widget)

        self.results_card = QFrame(right_content)
        self.results_card.setObjectName("lab-card")
        self.res_layout = QVBoxLayout(self.results_card)
        self.res_title = QLabel("THEORETICAL DIHYBRID RATIOS", self.results_card)
        self.res_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        self.res_text = QLabel("Execute cross to construct 4×4 matrix and determine gamete probabilities.", self.results_card)
        self.res_text.setWordWrap(True)
        self.res_layout.addWidget(self.res_title)
        self.res_layout.addWidget(self.res_text)
        right_layout.addWidget(self.results_card)

        self.feedback_card = QFrame(right_content)
        self.feedback_card.setObjectName("lab-card")
        self.fb_layout = QVBoxLayout(self.feedback_card)
        self.fb_title = QLabel("INDEPENDENT ASSORTMENT DERIVATION & LINKAGE CAVEAT", self.feedback_card)
        self.fb_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        self.fb_text = QTextEdit(self.feedback_card)
        self.fb_text.setReadOnly(True)
        self.fb_text.setStyleSheet("background-color: #0b1325; border: 1px solid #1a2c4e; color: #e0e6ed; font-size: 10px;")
        self.fb_text.setFixedHeight(115)
        self.fb_layout.addWidget(self.fb_title)
        self.fb_layout.addWidget(self.fb_text)
        right_layout.addWidget(self.feedback_card)

        right_scroll.setWidget(right_content)
        splitter.addWidget(right_scroll)
        splitter.setSizes([340, 460])

        main_layout.addWidget(splitter)

    def _run_cross(self):
        p1_str = self.p1_combo.currentText()
        p2_str = self.p2_combo.currentText()

        p1 = MultiLocusGenotype.from_str(p1_str, DIHYBRID_ALLELE_MAP)
        p2 = MultiLocusGenotype.from_str(p2_str, DIHYBRID_ALLELE_MAP)

        self.last_cross_result = execute_cross(p1, p2, DIHYBRID_INDEPENDENT_ASSORTMENT, DIHYBRID_ALLELE_MAP)
        self.punnett_widget.display_punnett_square(self.last_cross_result.punnett_square)

        self.res_text.setText(
            f"Cross: {p1_str} × {p2_str}\n"
            f"Phenotypic Ratio: {self.last_cross_result.phenotype_ratios}\n"
            f"Expected Classes: {', '.join(f'{k}: {v*100:.1f}%' for k, v in self.last_cross_result.phenotype_frequencies.items())}"
        )

        pred_text = self.pred_input.text().strip()
        eval_report = evaluate_student_prediction(self.last_cross_result, pred_text, target_attribute="phenotype")
        self.led_controller.trigger_prediction_result(eval_report.is_correct)

        self.fb_text.setText(
            f"{eval_report.scientific_feedback}\n\n"
            f"--- MATHEMATICAL DERIVATION ---\n{eval_report.derivation_proof}\n\n"
            f"--- CHROMOSOMAL MECHANISM & LINKAGE WARNING ---\n{MENDELIAN_BACKGROUND['exp02_scientific_basis']}"
        )
        self.btn_save.setEnabled(True)
        self.save_status_label.setText("")

    def _save_record(self):
        if not self.last_cross_result:
            return
        p1_str = self.p1_combo.currentText()
        p2_str = self.p2_combo.currentText()
        pred_text = self.pred_input.text().strip()

        eval_report = evaluate_student_prediction(self.last_cross_result, pred_text)

        rec = ExperimentRecord(
            experiment_id=f"EXP02-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            experiment_type="Dihybrid Inheritance (Independent Assortment)",
            parent1_genotype=p1_str,
            parent2_genotype=p2_str,
            model_name=DIHYBRID_INDEPENDENT_ASSORTMENT.model_name,
            model_assumptions=DIHYBRID_INDEPENDENT_ASSORTMENT.scientific_assumptions,
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
        self.exp_store.save_experiment(rec)
        self.led_controller.trigger_experiment_complete()
        self.save_status_label.setText(f"✓ Experiment record logged: {rec.experiment_id}")
