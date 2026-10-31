"""
UI Screen: Experiment 05 — Offspring Population Simulation
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QSpinBox, QLineEdit, QTextEdit, QScrollArea, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal

from genetics_engine.allele import TALL_ALLELE, DWARF_ALLELE, LOCUS_A_DOM, LOCUS_A_REC, LOCUS_B_DOM, LOCUS_B_REC
from genetics_engine.genotype import MultiLocusGenotype
from genetics_engine.models import MENDELIAN_COMPLETE_DOMINANCE, DIHYBRID_INDEPENDENT_ASSORTMENT
from genetics_engine.crosses import execute_cross
from simulations.population import simulate_offspring_population, PopulationSimulationResult
from data.experiment_store import ExperimentRecord, ExperimentStore
from ui.components.chart_widget import ScientificBarChartWidget
from hardware.base import HardwareAdapter
from hardware.led_controller import LedController
from content.scientific_text import MENDELIAN_BACKGROUND

ALL_ALLELES = {
    'T': TALL_ALLELE, 't': DWARF_ALLELE,
    'A': LOCUS_A_DOM, 'a': LOCUS_A_REC,
    'B': LOCUS_B_DOM, 'b': LOCUS_B_REC
}


class PopulationSimulationScreen(QWidget):
    navigate_to = pyqtSignal(str)

    def __init__(self, hardware_adapter: HardwareAdapter, led_controller: LedController, exp_store: ExperimentStore, parent=None):
        super().__init__(parent)
        self.adapter = hardware_adapter
        self.led_controller = led_controller
        self.exp_store = exp_store
        self.last_sim_result: Optional[PopulationSimulationResult] = None
        self.last_cross = None
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
        
        title = QLabel("EXPERIMENT 05: OFFSPRING POPULATION SIMULATION & SAMPLING VARIATION", self)
        title.setStyleSheet("font-size: 13px; font-weight: 800; color: #0f172a;")
        header_h.addWidget(title)
        header_h.addStretch()
        main_layout.addLayout(header_h)

        splitter = QSplitter(Qt.Horizontal, self)

        # LEFT PANEL: Parameters & Controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(6)

        # Cross Configuration
        c_frame = QFrame(left_widget)
        c_frame.setObjectName("lab-card")
        c_layout = QVBoxLayout(c_frame)
        c_layout.setSpacing(4)
        c_title = QLabel("PARENTAL GENETIC MODEL", c_frame)
        c_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        c_layout.addWidget(c_title)

        c_layout.addWidget(QLabel("Select Cross:", c_frame))
        self.cross_combo = QComboBox(c_frame)
        self.cross_combo.addItems([
            "Tt × Tt (Monohybrid F2, Expected 3:1)",
            "Tt × tt (Monohybrid Test Cross, Expected 1:1)",
            "TT × tt (Monohybrid True-Breeding, Expected 100%)",
            "AaBb × AaBb (Dihybrid F2, Expected 9:3:3:1)",
            "AaBb × aabb (Dihybrid Test Cross, Expected 1:1:1:1)"
        ])
        c_layout.addWidget(self.cross_combo)
        left_layout.addWidget(c_frame)

        # Population Parameters
        p_frame = QFrame(left_widget)
        p_frame.setObjectName("lab-card")
        p_layout = QVBoxLayout(p_frame)
        p_layout.setSpacing(4)
        p_title = QLabel("STOCHASTIC SAMPLING PARAMETERS", p_frame)
        p_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        p_layout.addWidget(p_title)

        p_layout.addWidget(QLabel("Sample Cohort Size (N):", p_frame))
        size_h = QHBoxLayout()
        self.size_combo = QComboBox(p_frame)
        self.size_combo.addItems(["20 (Small - High Variance)", "50", "100", "500", "1,000 (Large - Low Variance)", "Custom"])
        self.size_combo.setCurrentIndex(2) # 100
        self.size_combo.currentIndexChanged.connect(self._on_size_preset_changed)
        size_h.addWidget(self.size_combo)
        
        self.custom_size_spin = QSpinBox(p_frame)
        self.custom_size_spin.setRange(5, 50000)
        self.custom_size_spin.setValue(100)
        self.custom_size_spin.setEnabled(False)
        size_h.addWidget(self.custom_size_spin)
        p_layout.addLayout(size_h)

        seed_h = QHBoxLayout()
        seed_h.addWidget(QLabel("Random Seed (for reproduction):", p_frame))
        self.seed_input = QLineEdit(p_frame)
        self.seed_input.setPlaceholderText("Optional (e.g. 42)")
        self.seed_input.setText("42")
        seed_h.addWidget(self.seed_input)
        p_layout.addLayout(seed_h)
        left_layout.addWidget(p_frame)

        # Action Buttons
        btn_sim = QPushButton("⚡ RUN STOCHASTIC POPULATION SIMULATION", left_widget)
        btn_sim.setObjectName("btn-primary")
        btn_sim.clicked.connect(self._run_simulation)
        left_layout.addWidget(btn_sim)

        self.btn_save = QPushButton("💾 SAVE EXPERIMENT & REPRODUCIBILITY SEED", left_widget)
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._save_record)
        left_layout.addWidget(self.btn_save)

        self.save_status = QLabel("", left_widget)
        self.save_status.setStyleSheet("color: #2ec4b6; font-size: 9px; font-weight: bold;")
        left_layout.addWidget(self.save_status)
        left_layout.addStretch()

        splitter.addWidget(left_widget)

        # RIGHT PANEL: Chart, Table & Sampling Analysis
        right_scroll = QScrollArea(self)
        right_scroll.setWidgetResizable(True)
        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)
        right_layout.setContentsMargins(6, 4, 6, 4)
        right_layout.setSpacing(6)

        self.chart_widget = ScientificBarChartWidget(right_content)
        right_layout.addWidget(self.chart_widget)

        self.table = QTableWidget(right_content)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Phenotype", "Theory Prob", "Exp Count", "Obs Count", "Obs %", "Dev %"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setFixedHeight(120)
        right_layout.addWidget(self.table)

        self.summary_card = QFrame(right_content)
        self.summary_card.setObjectName("lab-card")
        self.s_layout = QVBoxLayout(self.summary_card)
        self.s_title = QLabel("LAW OF LARGE NUMBERS & SAMPLING VARIATION ANALYSIS", self.summary_card)
        self.s_title.setStyleSheet("color: #2563eb; font-weight: 700; font-size: 10px;")
        self.s_text = QTextEdit(self.summary_card)
        self.s_text.setReadOnly(True)
        self.s_text.setStyleSheet("background-color: #ffffff; border: 1.5px solid #cbd5e1; color: #0f172a; font-size: 10px;")
        self.s_text.setFixedHeight(130)
        self.s_layout.addWidget(self.s_title)
        self.s_layout.addWidget(self.s_text)
        right_layout.addWidget(self.summary_card)

        right_scroll.setWidget(right_content)
        splitter.addWidget(right_scroll)
        splitter.setSizes([340, 460])

        main_layout.addWidget(splitter)
        self._run_simulation()

    def _on_size_preset_changed(self):
        txt = self.size_combo.currentText()
        if "Custom" in txt:
            self.custom_size_spin.setEnabled(True)
        else:
            self.custom_size_spin.setEnabled(False)
            val = int(txt.split()[0].replace(",", ""))
            self.custom_size_spin.setValue(val)

    def _run_simulation(self):
        cross_idx = self.cross_combo.currentIndex()
        if cross_idx == 0:
            p1 = MultiLocusGenotype.from_str("Tt", ALL_ALLELES)
            p2 = MultiLocusGenotype.from_str("Tt", ALL_ALLELES)
            model = MENDELIAN_COMPLETE_DOMINANCE
        elif cross_idx == 1:
            p1 = MultiLocusGenotype.from_str("Tt", ALL_ALLELES)
            p2 = MultiLocusGenotype.from_str("tt", ALL_ALLELES)
            model = MENDELIAN_COMPLETE_DOMINANCE
        elif cross_idx == 2:
            p1 = MultiLocusGenotype.from_str("TT", ALL_ALLELES)
            p2 = MultiLocusGenotype.from_str("tt", ALL_ALLELES)
            model = MENDELIAN_COMPLETE_DOMINANCE
        elif cross_idx == 3:
            p1 = MultiLocusGenotype.from_str("AaBb", ALL_ALLELES)
            p2 = MultiLocusGenotype.from_str("AaBb", ALL_ALLELES)
            model = DIHYBRID_INDEPENDENT_ASSORTMENT
        else:
            p1 = MultiLocusGenotype.from_str("AaBb", ALL_ALLELES)
            p2 = MultiLocusGenotype.from_str("aabb", ALL_ALLELES)
            model = DIHYBRID_INDEPENDENT_ASSORTMENT

        self.last_cross = execute_cross(p1, p2, model, ALL_ALLELES)

        n = self.custom_size_spin.value()
        seed_str = self.seed_input.text().strip()
        seed_val = int(seed_str) if seed_str.isdigit() else None

        self.last_sim_result = simulate_offspring_population(self.last_cross, sample_size=n, seed=seed_val)

        # Update Chart
        cats = [item.category for item in self.last_sim_result.items]
        exp_vals = [item.expected_count for item in self.last_sim_result.items]
        obs_vals = [float(item.simulated_count) for item in self.last_sim_result.items]
        self.chart_widget.set_data(cats, exp_vals, obs_vals)

        # Update Table
        self.table.setRowCount(len(self.last_sim_result.items))
        for r, item in enumerate(self.last_sim_result.items):
            self.table.setItem(r, 0, QTableWidgetItem(item.category))
            self.table.setItem(r, 1, QTableWidgetItem(f"{item.theoretical_prob:.4f}"))
            self.table.setItem(r, 2, QTableWidgetItem(f"{item.expected_count:.1f}"))
            self.table.setItem(r, 3, QTableWidgetItem(f"{item.simulated_count}"))
            self.table.setItem(r, 4, QTableWidgetItem(f"{item.simulated_percentage:.2f}%"))
            self.table.setItem(r, 5, QTableWidgetItem(f"{item.percentage_deviation:.2f}%"))

        # Update Summary Text
        self.s_text.setText(
            f"{self.last_sim_result.scientific_summary}\n\n"
            f"--- STATISTICAL VALIDATION OF SIMULATED COHORT ---\n"
            f"Chi-Square: χ² = {self.last_sim_result.chi_square_result.chi_square_statistic:.4f}, "
            f"df = {self.last_sim_result.chi_square_result.degrees_of_freedom}, "
            f"p = {self.last_sim_result.chi_square_result.p_value:.4f}\n"
            f"Result: {self.last_sim_result.chi_square_result.conclusion}\n\n"
            f"--- SAMPLING THEORY ---\n{MENDELIAN_BACKGROUND['exp05_scientific_basis']}"
        )

        self.led_controller.trigger_prediction_result(not self.last_sim_result.chi_square_result.is_significant)
        self.btn_save.setEnabled(True)
        self.save_status.setText("")

    def _save_record(self):
        if not self.last_sim_result:
            return
        rec = ExperimentRecord(
            experiment_id=f"EXP05-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            experiment_type="Offspring Population Simulation",
            parent1_genotype=self.last_cross.parent1.string_rep,
            parent2_genotype=self.last_cross.parent2.string_rep,
            model_name=self.last_cross.model.model_name,
            model_assumptions=self.last_cross.model.scientific_assumptions,
            student_prediction=f"Simulated N={self.last_sim_result.sample_size}",
            expected_genotypic_ratio=self.last_cross.genotype_ratios,
            expected_phenotypic_ratio=self.last_cross.phenotype_ratios,
            theoretical_frequencies={item.category: item.theoretical_prob for item in self.last_sim_result.items},
            simulated_or_observed_counts={item.category: item.simulated_count for item in self.last_sim_result.items},
            is_simulation=True,
            simulation_seed=self.last_sim_result.random_seed,
            sample_size=self.last_sim_result.sample_size,
            chi_square_statistic=self.last_sim_result.chi_square_result.chi_square_statistic,
            degrees_of_freedom=self.last_sim_result.chi_square_result.degrees_of_freedom,
            p_value=self.last_sim_result.chi_square_result.p_value,
            statistical_conclusion=self.last_sim_result.chi_square_result.conclusion,
            error_classification="SIMULATION_SAMPLING",
            scientific_interpretation=self.s_text.toPlainText()
        )
        self.exp_store.save_experiment(rec)
        self.led_controller.trigger_experiment_complete()
        self.save_status.setText(f"✓ Experiment record logged: {rec.experiment_id} (Seed: {self.last_sim_result.random_seed})")
