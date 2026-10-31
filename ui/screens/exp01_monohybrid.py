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
from ui.components.dna_visualizer import DnaHelixWidget
from ui.components.cross_diagram import CrossDiagramWidget
from hardware.base import HardwareAdapter
from hardware.led_controller import LedController
from content.scientific_text import MENDELIAN_BACKGROUND

ALLELE_MAP = {'T': TALL_ALLELE, 't': DWARF_ALLELE}


class MonohybridExperimentScreen(QWidget):
    navigate_to = pyqtSignal(str)

    def __init__(self, hardware_adapter: HardwareAdapter, led_controller: LedController,
                 exp_store: ExperimentStore, parent=None):
        super().__init__(parent)
        self.adapter = hardware_adapter
        self.led_controller = led_controller
        self.exp_store = exp_store
        self.last_cross_result = None
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 6, 10, 6)
        main_layout.setSpacing(6)

        # ── Header ──────────────────────────────────────────────
        header_h = QHBoxLayout()
        btn_back = QPushButton("← HUB", self)
        btn_back.setFixedWidth(80)
        btn_back.clicked.connect(lambda: self.navigate_to.emit("module01_hub"))
        header_h.addWidget(btn_back)

        title = QLabel("EXP 01 · Monohybrid Inheritance", self)
        title.setStyleSheet("font-size: 14px; font-weight: 800; color: #0f172a; letter-spacing: 0.5px;")
        header_h.addWidget(title)

        badge = QLabel("Single Locus · Complete Dominance", self)
        badge.setStyleSheet(
            "background:#dbeafe; color:#1d4ed8; font-size:9px; font-weight:700;"
            "border-radius:8px; padding:3px 8px;"
        )
        header_h.addWidget(badge)
        header_h.addStretch()
        main_layout.addLayout(header_h)

        # ── 3-panel splitter ──────────────────────────────────────
        splitter = QSplitter(Qt.Horizontal, self)

        # ── LEFT: DNA helix + cross diagram ──────────────────────
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(2, 2, 2, 2)
        left_layout.setSpacing(4)

        # DNA helix
        self.dna_widget = DnaHelixWidget(left_widget)
        self.dna_widget.setFixedHeight(200)
        self.dna_widget.set_loci_info("Locus T (Height)", "ACTIVE")
        left_layout.addWidget(self.dna_widget)

        # Cross diagram
        self.cross_diagram = CrossDiagramWidget(left_widget)
        self.cross_diagram.setFixedHeight(185)
        left_layout.addWidget(self.cross_diagram)

        left_layout.addStretch()
        splitter.addWidget(left_widget)

        # ── MIDDLE: Controls ──────────────────────────────────────
        mid_widget = QWidget()
        mid_layout = QVBoxLayout(mid_widget)
        mid_layout.setContentsMargins(4, 4, 4, 4)
        mid_layout.setSpacing(6)

        # Parents card
        parents_frame = QFrame(mid_widget)
        parents_frame.setObjectName("lab-card")
        p_layout = QVBoxLayout(parents_frame)
        p_layout.setSpacing(6)

        p_lbl = QLabel("⚗ PARENTAL GENOTYPES", parents_frame)
        p_lbl.setStyleSheet("color: #2563eb; font-weight: 700; font-size: 10px;")
        p_layout.addWidget(p_lbl)

        for label_txt, attr in [("♀ Parent 1:", "p1_combo"), ("♂ Parent 2:", "p2_combo")]:
            row = QHBoxLayout()
            lbl = QLabel(label_txt, parents_frame)
            lbl.setFixedWidth(72)
            combo = QComboBox(parents_frame)
            combo.addItems(["TT — Homozygous Dom.", "Tt — Heterozygous", "tt — Homozygous Rec."])
            combo.setCurrentIndex(1)
            row.addWidget(lbl)
            row.addWidget(combo)
            p_layout.addLayout(row)
            setattr(self, attr, combo)

        mid_layout.addWidget(parents_frame)

        # Hypothesis card
        hypo_frame = QFrame(mid_widget)
        hypo_frame.setObjectName("lab-card")
        hypo_layout = QVBoxLayout(hypo_frame)
        hypo_layout.setSpacing(4)
        hypo_lbl = QLabel("🎯 PREDICTED PHENOTYPIC RATIO", hypo_frame)
        hypo_lbl.setStyleSheet("color: #2563eb; font-weight: 700; font-size: 10px;")
        hypo_layout.addWidget(hypo_lbl)

        pred_row = QHBoxLayout()
        pred_row.addWidget(QLabel("Ratio:", hypo_frame))
        self.pred_input = QLineEdit(hypo_frame)
        self.pred_input.setPlaceholderText("e.g. 3:1")
        self.pred_input.setText("3:1")
        pred_row.addWidget(self.pred_input)
        hypo_layout.addLayout(pred_row)
        mid_layout.addWidget(hypo_frame)

        # Buttons
        btn_cross = QPushButton("⚡ RUN CROSS", mid_widget)
        btn_cross.setObjectName("btn-primary")
        btn_cross.clicked.connect(self._run_cross)
        mid_layout.addWidget(btn_cross)

        self.btn_save = QPushButton("💾 SAVE RECORD", mid_widget)
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._save_record)
        mid_layout.addWidget(self.btn_save)

        self.save_status_label = QLabel("", mid_widget)
        self.save_status_label.setStyleSheet("color: #10b981; font-size: 9px; font-weight: bold;")
        mid_layout.addWidget(self.save_status_label)

        # Results card
        self.results_card = QFrame(mid_widget)
        self.results_card.setObjectName("lab-card")
        res_layout = QVBoxLayout(self.results_card)
        res_lbl = QLabel("📊 CALCULATED RATIOS", self.results_card)
        res_lbl.setStyleSheet("color: #2563eb; font-weight: 700; font-size: 10px;")
        self.res_text = QLabel("Run a cross to see results.", self.results_card)
        self.res_text.setWordWrap(True)
        self.res_text.setStyleSheet("color: #334155; font-size: 10px; font-family: 'Consolas', monospace;")
        res_layout.addWidget(res_lbl)
        res_layout.addWidget(self.res_text)
        mid_layout.addWidget(self.results_card)

        mid_layout.addStretch()
        splitter.addWidget(mid_widget)

        # ── RIGHT: Punnett + feedback ─────────────────────────────
        right_scroll = QScrollArea(self)
        right_scroll.setWidgetResizable(True)
        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right_layout.setSpacing(6)

        punnett_lbl = QLabel("PUNNETT SQUARE", right_content)
        punnett_lbl.setStyleSheet("color: #2563eb; font-weight: 700; font-size: 10px;")
        right_layout.addWidget(punnett_lbl)

        self.punnett_widget = PunnettSquareWidget(right_content)
        right_layout.addWidget(self.punnett_widget)

        # Feedback card (Verdict Panel)
        self.feedback_card = QFrame(right_content)
        # objectName will be set dynamically to 'verdict-correct' or 'verdict-incorrect'
        fb_layout = QVBoxLayout(self.feedback_card)
        self.fb_label = QLabel(self.feedback_card)
        self.fb_label.setWordWrap(True)
        self.fb_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # default neutral style
        self.feedback_card.setObjectName("verdict-neutral")
        fb_layout.addWidget(self.fb_label)
        right_layout.addWidget(self.feedback_card)

        right_layout.addStretch()
        right_scroll.setWidget(right_content)
        splitter.addWidget(right_scroll)

        splitter.setSizes([230, 280, 290])
        main_layout.addWidget(splitter)

        self.adapter.genotype_selected.connect(self._on_hardware_genotype_selected)

    def _get_selected_geno(self, combo: QComboBox) -> str:
        return combo.currentText()[:2]

    def _on_hardware_genotype_selected(self, parent_idx: int, geno: str):
        if len(geno) == 2 and geno in ["TT", "Tt", "tt"]:
            combo = self.p1_combo if parent_idx == 1 else self.p2_combo
            combo.setCurrentIndex(["TT", "Tt", "tt"].index(geno))
            self.led_controller.trigger_input_confirmed()

    def _run_cross(self):
        p1_str = self._get_selected_geno(self.p1_combo)
        p2_str = self._get_selected_geno(self.p2_combo)

        p1 = MultiLocusGenotype.from_str(p1_str, ALLELE_MAP)
        p2 = MultiLocusGenotype.from_str(p2_str, ALLELE_MAP)
        self.last_cross_result = execute_cross(p1, p2, MENDELIAN_COMPLETE_DOMINANCE, ALLELE_MAP)

        self.punnett_widget.display_punnett_square(self.last_cross_result.punnett_square)

        # Update cross diagram
        ps = self.last_cross_result.punnett_square
        row_gametes = [g[0] for g in ps.row_gametes]
        col_gametes = [g[0] for g in ps.col_gametes]
        offspring = list(dict.fromkeys(cell.zygote_genotype for row in ps.grid for cell in row))[:4]
        ratios = self.last_cross_result.phenotype_ratios
        self.cross_diagram.set_cross(
            p1_str, p2_str,
            row_gametes, col_gametes,
            offspring,
            ratios if isinstance(ratios, dict) else {}
        )

        # Update loci
        self.dna_widget.set_loci_info(f"T-locus ({p1_str[0]}/{p2_str[0]})", "ACTIVE")

        # Results text — concise
        gf = self.last_cross_result.genotype_frequencies
        pf = self.last_cross_result.phenotype_frequencies
        geno_str = "  ".join(f"{k} {v*100:.0f}%" for k, v in gf.items())
        pheno_str = "  ".join(f"{k} {v*100:.0f}%" for k, v in pf.items())
        self.res_text.setText(
            f"Cross: {p1_str} × {p2_str}\n"
            f"Geno: {self.last_cross_result.genotype_ratios} → {geno_str}\n"
            f"Pheno: {self.last_cross_result.phenotype_ratios} → {pheno_str}"
        )

        # Evaluate
        pred_text = self.pred_input.text().strip()
        eval_report = evaluate_student_prediction(self.last_cross_result, pred_text,
                                                   target_attribute="phenotype")
        self.led_controller.trigger_prediction_result(eval_report.is_correct)

        # Set verdict panel styling based on correctness
        if eval_report.is_correct:
            self.feedback_card.setObjectName("verdict-correct")
            verdict_msg = "✓ CORRECT"
        else:
            self.feedback_card.setObjectName("verdict-incorrect")
            verdict_msg = "✗ INCORRECT"
        # Compose feedback text
        feedback_html = f"{verdict_msg}<br><br>{eval_report.scientific_feedback}<br><br>Derivation: {eval_report.derivation_proof}"
        self.fb_label.setText(feedback_html)

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
        self.exp_store.save_experiment(rec)
        self.led_controller.trigger_experiment_complete()
        self.save_status_label.setText(f"✓ Saved: {rec.experiment_id}")
