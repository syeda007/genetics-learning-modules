"""
UI Screen: Experiment 03 — Test Cross Analysis
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from datetime import datetime
import random
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QSpinBox, QTextEdit, QScrollArea, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal

from genetics_engine.allele import LOCUS_A_DOM, LOCUS_A_REC
from genetics_engine.genotype import MultiLocusGenotype
from genetics_engine.models import MENDELIAN_COMPLETE_DOMINANCE
from genetics_engine.crosses import execute_cross
from data.experiment_store import ExperimentRecord, ExperimentStore
from ui.components.chart_widget import ScientificBarChartWidget
from hardware.base import HardwareAdapter
from hardware.led_controller import LedController
from content.scientific_text import MENDELIAN_BACKGROUND

TEST_ALLELE_MAP = {'A': LOCUS_A_DOM, 'a': LOCUS_A_REC}


class TestCrossExperimentScreen(QWidget):
    navigate_to = pyqtSignal(str)

    def __init__(self, hardware_adapter: HardwareAdapter, led_controller: LedController, exp_store: ExperimentStore, parent=None):
        super().__init__(parent)
        self.adapter = hardware_adapter
        self.led_controller = led_controller
        self.exp_store = exp_store
        self.hidden_genotype = "Aa"
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(8)

        # Header bar
        header_h = QHBoxLayout()
        btn_back = QPushButton("← HUB", self)
        btn_back.setFixedWidth(80)
        btn_back.clicked.connect(lambda: self.navigate_to.emit("module01_hub"))
        header_h.addWidget(btn_back)
        title = QLabel("EXP 03 · Test Cross & Zygosity", self)
        title.setStyleSheet("font-size: 14px; font-weight: 800; color: #0f172a;")
        header_h.addWidget(title)
        badge = QLabel("Discriminates TT vs Tt · aa Tester", self)
        badge.setStyleSheet(
            "background:#dcfce7; color:#15803d; font-size:9px; font-weight:700;"
            "border-radius:8px; padding:3px 8px;"
        )
        header_h.addWidget(badge)
        header_h.addStretch()
        main_layout.addLayout(header_h)

        splitter = QSplitter(Qt.Horizontal, self)

        # LEFT PANEL
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(6)


        # Subject Setup
        subj_frame = QFrame(left_widget)
        subj_frame.setObjectName("lab-card")
        s_layout = QVBoxLayout(subj_frame)
        s_layout.setSpacing(4)
        s_title = QLabel("TEST SUBJECT SELECTION", subj_frame)
        s_title.setStyleSheet("color: #2563eb; font-weight: 700; font-size: 10px;")
        s_layout.addWidget(s_title)

        s_h = QHBoxLayout()
        s_h.addWidget(QLabel("Phenotype: Dominant Trait (A_)", subj_frame))
        btn_gen_unknown = QPushButton("🎲 Generate New Unknown Subject", subj_frame)
        btn_gen_unknown.clicked.connect(self._generate_new_unknown)
        s_h.addWidget(btn_gen_unknown)
        s_layout.addLayout(s_h)

        s_layout.addWidget(QLabel("Tester: Homozygous Recessive (aa) — Transparent Genetic Background", subj_frame))
        left_layout.addWidget(subj_frame)

        # Student Hypothesis
        hypo_frame = QFrame(left_widget)
        hypo_frame.setObjectName("lab-card")
        h_layout = QVBoxLayout(hypo_frame)
        h_layout.setSpacing(4)
        h_title = QLabel("FORMULATE STUDENT HYPOTHESIS", hypo_frame)
        h_title.setStyleSheet("color: #2563eb; font-weight: 700; font-size: 10px;")
        h_layout.addWidget(h_title)

        self.hypo_combo = QComboBox(hypo_frame)
        self.hypo_combo.addItems([
            "Hypothesis A: Subject is Homozygous Dominant (AA) → Expected 100% Dominant",
            "Hypothesis B: Subject is Heterozygous (Aa) → Expected 1:1 Dominant:Recessive"
        ])
        h_layout.addWidget(self.hypo_combo)

        sample_h = QHBoxLayout()
        sample_h.addWidget(QLabel("Offspring Sample Size (N):", hypo_frame))
        self.sample_spin = QSpinBox(hypo_frame)
        self.sample_spin.setRange(10, 500)
        self.sample_spin.setValue(40)
        sample_h.addWidget(self.sample_spin)
        h_layout.addLayout(sample_h)
        left_layout.addWidget(hypo_frame)

        # Buttons
        btn_test = QPushButton("⚡ PERFORM TEST CROSS & SAMPLE OFFSPRING", left_widget)
        btn_test.setObjectName("btn-primary")
        btn_test.clicked.connect(self._run_test_cross)
        left_layout.addWidget(btn_test)

        self.btn_save = QPushButton("💾 SAVE EXPERIMENT RECORD", left_widget)
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._save_record)
        left_layout.addWidget(self.btn_save)

        self.save_status = QLabel("", left_widget)
        self.save_status.setStyleSheet("color: #2ec4b6; font-size: 9px; font-weight: bold;")
        left_layout.addWidget(self.save_status)
        left_layout.addStretch()

        splitter.addWidget(left_widget)

        # RIGHT PANEL: Chart & Likelihood Analysis
        right_scroll = QScrollArea(self)
        right_scroll.setWidgetResizable(True)
        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)
        right_layout.setContentsMargins(6, 4, 6, 4)
        right_layout.setSpacing(8)

        self.chart_widget = ScientificBarChartWidget(right_content)
        right_layout.addWidget(self.chart_widget)

        self.analysis_card = QFrame(right_content)
        self.analysis_card.setObjectName("lab-card")
        self.a_layout = QVBoxLayout(self.analysis_card)
        self.a_title = QLabel("STATISTICAL INFERENCE & LIKELIHOOD ANALYSIS", self.analysis_card)
        self.a_title.setStyleSheet("color: #2563eb; font-weight: 700; font-size: 10px;")
        self.a_text = QTextEdit(self.analysis_card)
        self.a_text.setReadOnly(True)
        self.a_text.setStyleSheet("background-color: #ffffff; border: 1.5px solid #cbd5e1; color: #0f172a; font-size: 10px;")
        self.a_text.setFixedHeight(150)
        self.a_layout.addWidget(self.a_title)
        self.a_layout.addWidget(self.a_text)
        right_layout.addWidget(self.analysis_card)

        right_scroll.setWidget(right_content)
        splitter.addWidget(right_scroll)
        splitter.setSizes([340, 460])

        main_layout.addWidget(splitter)
        self._generate_new_unknown()

    def _generate_new_unknown(self):
        self.hidden_genotype = random.choice(["AA", "Aa"])
        self.a_text.setText(
            "New unknown test individual initialized with dominant phenotype (A_).\n"
            "Formulate your hypothesis and generate test cross offspring with tester (aa)."
        )
        self.chart_widget.set_data([], [], [])
        self.btn_save.setEnabled(False)
        self.save_status.setText("")

    def _run_test_cross(self):
        n = self.sample_spin.value()
        selected_hypo_idx = self.hypo_combo.currentIndex()  # 0 for AA, 1 for Aa

        # Simulate offspring from hidden genotype x aa
        if self.hidden_genotype == "AA":
            dom_count = n
            rec_count = 0
        else: # Aa
            # Binomial draw p = 0.5
            dom_count = sum(1 for _ in range(n) if random.random() < 0.5)
            rec_count = n - dom_count

        # Expected counts under selected student hypothesis
        if selected_hypo_idx == 0:  # Student predicted AA
            exp_dom = n
            exp_rec = 0
            hypo_name = "Subject is Homozygous Dominant (AA)"
        else:  # Student predicted Aa
            exp_dom = n / 2.0
            exp_rec = n / 2.0
            hypo_name = "Subject is Heterozygous (Aa)"

        # Update Chart
        categories = ["Dominant Phenotype (A_)", "Recessive Phenotype (aa)"]
        self.chart_widget.set_data(categories, [float(exp_dom), float(exp_rec)], [float(dom_count), float(rec_count)])

        # Scientific inference
        is_consistent = False
        if rec_count > 0:
            # Definite identification of heterozygote
            is_consistent = (selected_hypo_idx == 1)
            verdict = (
                f"DEFINITIVE GENETIC PROOF: {rec_count} homozygous recessive offspring (aa) observed.\n"
                f"Because the tester contributes an 'a' allele, the presence of recessive offspring proves with 100% certainty "
                f"that the test individual contributed an 'a' allele and is HETEROZYGOUS (Aa).\n"
                f"Student Hypothesis: {hypo_name} → {'CONSISTENT ✓' if is_consistent else 'REFUTED ✗'}."
            )
        else:
            # All dominant offspring
            # Likelihood of observing n dominant if actually Aa is (0.5)^n
            prob_if_hetero = (0.5) ** n
            is_consistent = (selected_hypo_idx == 0)
            verdict = (
                f"ALL {n} OFFSPRING DISPLAY DOMINANT PHENOTYPE (0 recessive).\n"
                f"Statistical Likelihood Analysis:\n"
                f"Under H₀: Heterozygous (Aa), the probability of observing 0 recessive offspring in {n} trials is "
                f"(1/2)^{n} = {prob_if_hetero:.6e}.\n"
                f"Scientific Epistemic Caveat: While the data provide strong empirical support for Homozygous Dominance (AA), "
                f"finite biological sampling cannot rule out heterozygosity with metaphysical certainty, only with confidence (1 - p) = {1 - prob_if_hetero:.6f}."
            )

        self.led_controller.trigger_prediction_result(is_consistent)
        self.a_text.setText(verdict)
        self.btn_save.setEnabled(True)

    def _save_record(self):
        n = self.sample_spin.value()
        hypo_text = self.hypo_combo.currentText()
        rec = ExperimentRecord(
            experiment_id=f"EXP03-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            experiment_type="Test Cross Analysis (Zygosity Discrimination)",
            parent1_genotype=f"Unknown ({self.hidden_genotype})",
            parent2_genotype="aa (Tester)",
            model_name=MENDELIAN_COMPLETE_DOMINANCE.model_name,
            model_assumptions=MENDELIAN_COMPLETE_DOMINANCE.scientific_assumptions,
            student_prediction=hypo_text,
            expected_genotypic_ratio="100% Aa or 1:1",
            expected_phenotypic_ratio="100% Dom or 1:1",
            theoretical_frequencies={"Dominant": 0.5, "Recessive": 0.5},
            simulated_or_observed_counts={},
            is_simulation=True,
            simulation_seed=None,
            sample_size=n,
            chi_square_statistic=None,
            degrees_of_freedom=1,
            p_value=None,
            statistical_conclusion="Hypothesis Tested",
            error_classification="TEST_CROSS_EVALUATION",
            scientific_interpretation=self.a_text.toPlainText()
        )
        self.exp_store.save_experiment(rec)
        self.led_controller.trigger_experiment_complete()
        self.save_status.setText(f"✓ Experiment record logged: {rec.experiment_id}")
