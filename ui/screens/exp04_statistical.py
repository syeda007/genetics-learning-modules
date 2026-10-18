"""
UI Screen: Experiment 04 — Biostatistical Validation (Chi-Square)
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QLineEdit, QTextEdit, QScrollArea, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal

from biostatistics.chi_square import calculate_chi_square, ChiSquareResult
from biostatistics.ratios import parse_ratio_string
from data.experiment_store import ExperimentRecord, ExperimentStore
from ui.components.chart_widget import ScientificBarChartWidget
from hardware.base import HardwareAdapter
from hardware.led_controller import LedController
from content.scientific_text import MENDELIAN_BACKGROUND


class StatisticalValidationScreen(QWidget):
    navigate_to = pyqtSignal(str)

    def __init__(self, hardware_adapter: HardwareAdapter, led_controller: LedController, exp_store: ExperimentStore, parent=None):
        super().__init__(parent)
        self.adapter = hardware_adapter
        self.led_controller = led_controller
        self.exp_store = exp_store
        self.last_chi2_result = None
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
        
        title = QLabel("EXPERIMENT 04: STATISTICAL VALIDATION (PEARSON χ² GOODNESS-OF-FIT)", self)
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffffff;")
        header_h.addWidget(title)
        header_h.addStretch()
        main_layout.addLayout(header_h)

        splitter = QSplitter(Qt.Horizontal, self)

        # LEFT PANEL: Parameters & Quick Presets
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(6)

        # Presets Card
        preset_frame = QFrame(left_widget)
        preset_frame.setObjectName("lab-card")
        p_layout = QVBoxLayout(preset_frame)
        p_layout.setSpacing(4)
        p_title = QLabel("HISTORICAL & EXPERIMENTAL BENCHMARKS", preset_frame)
        p_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        p_layout.addWidget(p_title)

        btn_mendel_mono = QPushButton("Mendel F2 Monohybrid (556 Tall, 184 Dwarf)", preset_frame)
        btn_mendel_mono.clicked.connect(self._load_mendel_mono)
        p_layout.addWidget(btn_mendel_mono)

        btn_mendel_di = QPushButton("Mendel F2 Dihybrid (315, 108, 101, 32)", preset_frame)
        btn_mendel_di.clicked.connect(self._load_mendel_di)
        p_layout.addWidget(btn_mendel_di)

        btn_departure = QPushButton("Significant Deviation / Linkage Example", preset_frame)
        btn_departure.clicked.connect(self._load_departure_example)
        p_layout.addWidget(btn_departure)
        left_layout.addWidget(preset_frame)

        # Input Parameters
        param_frame = QFrame(left_widget)
        param_frame.setObjectName("lab-card")
        param_layout = QVBoxLayout(param_frame)
        param_layout.setSpacing(4)
        
        param_layout.addWidget(QLabel("Hypothesized Mendelian Ratio:", param_frame))
        self.ratio_input = QLineEdit(param_frame)
        self.ratio_input.setText("3:1")
        param_layout.addWidget(self.ratio_input)

        param_layout.addWidget(QLabel("Observed Class Counts (comma separated):", param_frame))
        self.counts_input = QLineEdit(param_frame)
        self.counts_input.setText("556, 184")
        param_layout.addWidget(self.counts_input)

        param_layout.addWidget(QLabel("Category Names (optional comma separated):", param_frame))
        self.names_input = QLineEdit(param_frame)
        self.names_input.setText("Tall, Dwarf")
        param_layout.addWidget(self.names_input)

        alpha_h = QHBoxLayout()
        alpha_h.addWidget(QLabel("Significance Level (α):", param_frame))
        self.alpha_combo = QComboBox(param_frame)
        self.alpha_combo.addItems(["0.05 (Standard)", "0.01 (Stringent)", "0.10 (Exploratory)"])
        alpha_h.addWidget(self.alpha_combo)
        param_layout.addLayout(alpha_h)
        left_layout.addWidget(param_frame)

        # Action Buttons
        btn_calc = QPushButton("⚡ COMPUTE CHI-SQUARE GOODNESS-OF-FIT", left_widget)
        btn_calc.setObjectName("btn-primary")
        btn_calc.clicked.connect(self._run_chi_square)
        left_layout.addWidget(btn_calc)

        self.btn_save = QPushButton("💾 SAVE EXPERIMENT RECORD", left_widget)
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._save_record)
        left_layout.addWidget(self.btn_save)

        self.save_status = QLabel("", left_widget)
        self.save_status.setStyleSheet("color: #2ec4b6; font-size: 9px; font-weight: bold;")
        left_layout.addWidget(self.save_status)
        left_layout.addStretch()

        splitter.addWidget(left_widget)

        # RIGHT PANEL: Chart, Table & Rigorous Interpretation
        right_scroll = QScrollArea(self)
        right_scroll.setWidgetResizable(True)
        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)
        right_layout.setContentsMargins(6, 4, 6, 4)
        right_layout.setSpacing(6)

        # Chart
        self.chart_widget = ScientificBarChartWidget(right_content)
        right_layout.addWidget(self.chart_widget)

        # Table
        self.table = QTableWidget(right_content)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Class", "Observed (O)", "Expected (E)", "(O - E)", "(O - E)²", "(O - E)² / E"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setFixedHeight(120)
        right_layout.addWidget(self.table)

        # Statistical Summary Card
        self.summary_card = QFrame(right_content)
        self.summary_card.setObjectName("lab-card")
        self.s_layout = QVBoxLayout(self.summary_card)
        self.s_title = QLabel("STATISTICAL METRICS & ACADEMIC INTERPRETATION", self.summary_card)
        self.s_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        self.s_text = QTextEdit(self.summary_card)
        self.s_text.setReadOnly(True)
        self.s_text.setStyleSheet("background-color: #0b1325; border: 1px solid #1a2c4e; color: #e0e6ed; font-size: 10px;")
        self.s_text.setFixedHeight(130)
        self.s_layout.addWidget(self.s_title)
        self.s_layout.addWidget(self.s_text)
        right_layout.addWidget(self.summary_card)

        right_scroll.setWidget(right_content)
        splitter.addWidget(right_scroll)
        splitter.setSizes([340, 460])

        main_layout.addWidget(splitter)
        self._load_mendel_mono()

    def _load_mendel_mono(self):
        self.ratio_input.setText("3:1")
        self.counts_input.setText("556, 184")
        self.names_input.setText("Tall, Dwarf")
        self._run_chi_square()

    def _load_mendel_di(self):
        self.ratio_input.setText("9:3:3:1")
        self.counts_input.setText("315, 108, 101, 32")
        self.names_input.setText("Round Yellow, Round Green, Wrinkled Yellow, Wrinkled Green")
        self._run_chi_square()

    def _load_departure_example(self):
        self.ratio_input.setText("1:1:1:1")
        self.counts_input.setText("450, 48, 52, 450")
        self.names_input.setText("AB Parental, Ab Recombinant, aB Recombinant, ab Parental")
        self._run_chi_square()

    def _run_chi_square(self):
        ratio_str = self.ratio_input.text().strip()
        counts_str = self.counts_input.text().strip()
        names_str = self.names_input.text().strip()

        parsed_ratio = parse_ratio_string(ratio_str)
        if not parsed_ratio:
            self.s_text.setText("Error: Invalid ratio format. Use colon-separated numbers like '3:1' or '9:3:3:1'.")
            return

        try:
            obs_counts = [float(c.strip()) for c in counts_str.split(",") if c.strip()]
        except ValueError:
            self.s_text.setText("Error: Counts must be numeric values separated by commas.")
            return

        if len(obs_counts) != len(parsed_ratio):
            self.s_text.setText(f"Error: Number of observed counts ({len(obs_counts)}) does not match ratio categories ({len(parsed_ratio)}).")
            return

        cat_names = [n.strip() for n in names_str.split(",") if n.strip()] if names_str else []
        while len(cat_names) < len(obs_counts):
            cat_names.append(f"Class {len(cat_names)+1}")

        # Build dictionaries
        obs_dict = {cat: count for cat, count in zip(cat_names, obs_counts)}
        exp_props = {cat: prop for cat, prop in zip(cat_names, parsed_ratio)}

        alpha_val = 0.05 if "0.05" in self.alpha_combo.currentText() else (0.01 if "0.01" in self.alpha_combo.currentText() else 0.10)

        # Calculate Chi-Square
        self.last_chi2_result = calculate_chi_square(obs_dict, exp_props, alpha=alpha_val)

        # Update Chart
        exp_counts = [item.expected for item in self.last_chi2_result.categories]
        self.chart_widget.set_data(cat_names, exp_counts, obs_counts)

        # Update Table
        self.table.setRowCount(len(self.last_chi2_result.categories))
        for r, item in enumerate(self.last_chi2_result.categories):
            self.table.setItem(r, 0, QTableWidgetItem(item.category))
            self.table.setItem(r, 1, QTableWidgetItem(f"{item.observed:.0f}"))
            self.table.setItem(r, 2, QTableWidgetItem(f"{item.expected:.2f}"))
            self.table.setItem(r, 3, QTableWidgetItem(f"{item.difference:+.2f}"))
            self.table.setItem(r, 4, QTableWidgetItem(f"{item.squared_diff:.2f}"))
            self.table.setItem(r, 5, QTableWidgetItem(f"{item.chi_square_contribution:.4f}"))

        # Update Summary Text
        warning_str = f"\n{self.last_chi2_result.warning_message}\n" if self.last_chi2_result.warning_message else ""
        self.s_text.setText(
            f"CHI-SQUARE STATISTIC (χ²): {self.last_chi2_result.chi_square_statistic:.4f}\n"
            f"DEGREES OF FREEDOM (df): {self.last_chi2_result.degrees_of_freedom} (k - 1, fully prespecified)\n"
            f"p-VALUE: {self.last_chi2_result.p_value:.5e} | α: {self.last_chi2_result.alpha}\n"
            f"STATISTICAL DECISION: {self.last_chi2_result.conclusion}\n"
            f"{warning_str}\n"
            f"INTERPRETATION:\n{self.last_chi2_result.interpretation}\n\n"
            f"--- BIOSTATISTICAL THEORY ---\n{MENDELIAN_BACKGROUND['exp04_scientific_basis']}"
        )

        self.led_controller.trigger_prediction_result(not self.last_chi2_result.is_significant)
        self.btn_save.setEnabled(True)
        self.save_status.setText("")

    def _save_record(self):
        if not self.last_chi2_result:
            return
        rec = ExperimentRecord(
            experiment_id=f"EXP04-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            experiment_type="Statistical Validation of Mendelian Ratios",
            parent1_genotype="Cross Sample Data",
            parent2_genotype="Mendelian Prespecified",
            model_name="Pearson Chi-Square Goodness-of-Fit",
            model_assumptions=[
                "df = k - 1 for fully prespecified expected proportions.",
                "Cochran's minimum expected frequency requirement verified.",
                "Failure to reject H0 does not constitute absolute proof."
            ],
            student_prediction=self.ratio_input.text().strip(),
            expected_genotypic_ratio=self.ratio_input.text().strip(),
            expected_phenotypic_ratio=self.ratio_input.text().strip(),
            theoretical_frequencies={item.category: item.expected / self.last_chi2_result.total_expected for item in self.last_chi2_result.categories},
            simulated_or_observed_counts={item.category: int(item.observed) for item in self.last_chi2_result.categories},
            is_simulation=False,
            simulation_seed=None,
            sample_size=int(self.last_chi2_result.total_observed),
            chi_square_statistic=self.last_chi2_result.chi_square_statistic,
            degrees_of_freedom=self.last_chi2_result.degrees_of_freedom,
            p_value=self.last_chi2_result.p_value,
            statistical_conclusion=self.last_chi2_result.conclusion,
            error_classification=None,
            scientific_interpretation=self.last_chi2_result.interpretation
        )
        self.exp_store.save_experiment(rec)
        self.led_controller.trigger_experiment_complete()
        self.save_status.setText(f"✓ Experiment record logged: {rec.experiment_id}")
