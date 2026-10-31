"""
UI Screen: Experiment 01 — Monohybrid Inheritance v4.0
Visual-first layout with inline verdict feedback and animated Punnett square.
"""
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QLineEdit, QScrollArea, QSizePolicy, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPainterPath

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

ALLELE_MAP = {"T": TALL_ALLELE, "t": DWARF_ALLELE}


def _chip(text, bg, fg, parent):
    lbl = QLabel(text, parent)
    lbl.setStyleSheet(
        f"background:{bg}; color:{fg}; border-radius:5px;"
        f"padding:2px 9px; font-size:9px; font-weight:700;"
    )
    return lbl


class VerdictPanel(QFrame):
    """Inline verdict widget that shows CORRECT / INCORRECT prominently."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("verdict-neutral")
        self.setMinimumHeight(70)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(12)

        self.icon_lbl = QLabel("—", self)
        self.icon_lbl.setFixedWidth(32)
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setStyleSheet("font-size: 22px; font-weight: 900; color: #94a3b8;")
        lay.addWidget(self.icon_lbl)

        text_col = QVBoxLayout()
        self.verdict_lbl = QLabel("Run a cross to evaluate your prediction.", self)
        self.verdict_lbl.setStyleSheet("font-size: 12px; font-weight: 700; color: #64748b;")
        self.detail_lbl = QLabel("", self)
        self.detail_lbl.setWordWrap(True)
        self.detail_lbl.setStyleSheet("font-size: 9px; color: #475569;")
        text_col.addWidget(self.verdict_lbl)
        text_col.addWidget(self.detail_lbl)
        lay.addLayout(text_col)

    def set_result(self, is_correct: bool, feedback: str, derivation: str):
        if is_correct:
            self.setObjectName("verdict-correct")
            self.icon_lbl.setText("✓")
            self.icon_lbl.setStyleSheet("font-size: 22px; font-weight: 900; color: #059669;")
            self.verdict_lbl.setText("CORRECT — Your prediction matches the expected ratio.")
            self.verdict_lbl.setStyleSheet("font-size: 12px; font-weight: 800; color: #14532d;")
        else:
            self.setObjectName("verdict-incorrect")
            self.icon_lbl.setText("✗")
            self.icon_lbl.setStyleSheet("font-size: 22px; font-weight: 900; color: #dc2626;")
            self.verdict_lbl.setText("INCORRECT — Your prediction does not match.")
            self.verdict_lbl.setStyleSheet("font-size: 12px; font-weight: 800; color: #7f1d1d;")
        self.detail_lbl.setText(feedback[:180])
        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


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
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top header bar
        header_frame = QFrame(self)
        header_frame.setStyleSheet(
            "background: #ffffff; border-bottom: 1px solid #e8eaf2;"
        )
        header_frame.setFixedHeight(44)
        h_lay = QHBoxLayout(header_frame)
        h_lay.setContentsMargins(14, 6, 14, 6)
        h_lay.setSpacing(10)

        btn_back = QPushButton("← Hub", header_frame)
        btn_back.setObjectName("btn-back")
        btn_back.setFixedWidth(70)
        btn_back.clicked.connect(lambda: self.navigate_to.emit("module01_hub"))
        h_lay.addWidget(btn_back)

        title_lbl = QLabel("EXP 01 — Monohybrid Inheritance", header_frame)
        title_lbl.setStyleSheet("font-size: 13px; font-weight: 800; color: #1a1d2e;")
        h_lay.addWidget(title_lbl)

        h_lay.addWidget(_chip("Single Locus", "#eef2ff", "#4f46e5", header_frame))
        h_lay.addWidget(_chip("Complete Dominance", "#f0fdf4", "#059669", header_frame))
        h_lay.addStretch()

        self.save_lbl = QLabel("", header_frame)
        self.save_lbl.setStyleSheet("color: #059669; font-size: 9px; font-weight: 700;")
        h_lay.addWidget(self.save_lbl)

        root.addWidget(header_frame)

        # ── Main splitter
        splitter = QSplitter(Qt.Horizontal, self)
        splitter.setHandleWidth(1)

        # ── LEFT PANEL: controls
        left = QWidget()
        left.setMinimumWidth(260)
        left.setMaximumWidth(310)
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(14, 14, 8, 14)
        left_lay.setSpacing(10)

        # Parents card
        parents_card = QFrame(left)
        parents_card.setObjectName("card-accent")
        p_lay = QVBoxLayout(parents_card)
        p_lay.setContentsMargins(14, 12, 14, 12)
        p_lay.setSpacing(8)

        p_header = QLabel("PARENTAL GENOTYPES", parents_card)
        p_header.setStyleSheet("font-size: 9px; font-weight: 800; color: #6366f1; letter-spacing: 1px;")
        p_lay.addWidget(p_header)

        for label, attr in [("Parent 1 (♀):", "p1_combo"), ("Parent 2 (♂):", "p2_combo")]:
            row = QHBoxLayout()
            lbl = QLabel(label, parents_card)
            lbl.setFixedWidth(80)
            lbl.setStyleSheet("font-size: 10px; font-weight: 600; color: #475569;")
            combo = QComboBox(parents_card)
            combo.addItems(["TT — Homozygous Dom.", "Tt — Heterozygous", "tt — Homozygous Rec."])
            combo.setCurrentIndex(1)
            row.addWidget(lbl)
            row.addWidget(combo)
            p_lay.addLayout(row)
            setattr(self, attr, combo)

        left_lay.addWidget(parents_card)

        # Prediction card
        pred_card = QFrame(left)
        pred_card.setObjectName("card")
        pred_lay = QVBoxLayout(pred_card)
        pred_lay.setContentsMargins(14, 12, 14, 12)
        pred_lay.setSpacing(8)

        pred_header = QLabel("YOUR PREDICTION", pred_card)
        pred_header.setStyleSheet("font-size: 9px; font-weight: 800; color: #6366f1; letter-spacing: 1px;")
        pred_lay.addWidget(pred_header)

        pred_row = QHBoxLayout()
        pred_lbl = QLabel("Phenotypic ratio:", pred_card)
        pred_lbl.setStyleSheet("font-size: 10px; color: #475569;")
        pred_row.addWidget(pred_lbl)
        self.pred_input = QLineEdit(pred_card)
        self.pred_input.setPlaceholderText("e.g. 3:1")
        self.pred_input.setText("3:1")
        pred_row.addWidget(self.pred_input)
        pred_lay.addLayout(pred_row)

        left_lay.addWidget(pred_card)

        # Run button
        self.btn_run = QPushButton("Run Cross & Evaluate", left)
        self.btn_run.setObjectName("btn-primary")
        self.btn_run.clicked.connect(self._run_cross)
        left_lay.addWidget(self.btn_run)

        self.btn_save = QPushButton("Save Experiment Record", left)
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._save_record)
        left_lay.addWidget(self.btn_save)

        # Ratios display
        self.ratio_card = QFrame(left)
        self.ratio_card.setObjectName("card")
        ratio_lay = QVBoxLayout(self.ratio_card)
        ratio_lay.setContentsMargins(12, 10, 12, 10)
        ratio_hdr = QLabel("CALCULATED RATIOS", self.ratio_card)
        ratio_hdr.setStyleSheet("font-size: 9px; font-weight: 800; color: #6366f1; letter-spacing: 1px;")
        ratio_lay.addWidget(ratio_hdr)
        self.ratio_lbl = QLabel("—", self.ratio_card)
        self.ratio_lbl.setWordWrap(True)
        self.ratio_lbl.setStyleSheet(
            "font-family: 'Fira Code','Consolas',monospace; font-size: 10px; color: #334155;"
        )
        ratio_lay.addWidget(self.ratio_lbl)
        left_lay.addWidget(self.ratio_card)
        left_lay.addStretch()

        splitter.addWidget(left)

        # ── MIDDLE: DNA Helix + Cross diagram
        mid = QWidget()
        mid.setMinimumWidth(200)
        mid.setMaximumWidth(250)
        mid_lay = QVBoxLayout(mid)
        mid_lay.setContentsMargins(4, 14, 4, 14)
        mid_lay.setSpacing(8)

        self.dna_widget = DnaHelixWidget(mid)
        self.dna_widget.setFixedHeight(200)
        self.dna_widget.set_loci_info("Locus T (Height)", "ACTIVE")
        mid_lay.addWidget(self.dna_widget)

        self.cross_diagram = CrossDiagramWidget(mid)
        self.cross_diagram.setFixedHeight(190)
        mid_lay.addWidget(self.cross_diagram)
        mid_lay.addStretch()
        splitter.addWidget(mid)

        # ── RIGHT: Punnett + Verdict
        right_scroll = QScrollArea(self)
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.NoFrame)
        right_content = QWidget()
        right_lay = QVBoxLayout(right_content)
        right_lay.setContentsMargins(8, 14, 14, 14)
        right_lay.setSpacing(10)

        punnett_hdr = QLabel("PUNNETT SQUARE", right_content)
        punnett_hdr.setStyleSheet(
            "font-size: 9px; font-weight: 800; color: #6366f1; letter-spacing: 1px;"
        )
        right_lay.addWidget(punnett_hdr)

        self.punnett_widget = PunnettSquareWidget(right_content)
        right_lay.addWidget(self.punnett_widget)

        # Verdict panel (inline, prominent)
        verdict_hdr = QLabel("EVALUATION", right_content)
        verdict_hdr.setStyleSheet(
            "font-size: 9px; font-weight: 800; color: #6366f1; letter-spacing: 1px;"
        )
        right_lay.addWidget(verdict_hdr)

        self.verdict_panel = VerdictPanel(right_content)
        right_lay.addWidget(self.verdict_panel)
        right_lay.addStretch()

        right_scroll.setWidget(right_content)
        splitter.addWidget(right_scroll)

        splitter.setSizes([290, 220, 300])
        root.addWidget(splitter)

        self.adapter.genotype_selected.connect(self._on_hardware_genotype)

    def _get_geno(self, combo: QComboBox) -> str:
        return combo.currentText()[:2]

    def _on_hardware_genotype(self, parent_idx: int, geno: str):
        if geno in ("TT", "Tt", "tt"):
            combo = self.p1_combo if parent_idx == 1 else self.p2_combo
            combo.setCurrentIndex(["TT", "Tt", "tt"].index(geno))
            self.led_controller.trigger_input_confirmed()

    def _run_cross(self):
        p1s = self._get_geno(self.p1_combo)
        p2s = self._get_geno(self.p2_combo)
        p1 = MultiLocusGenotype.from_str(p1s, ALLELE_MAP)
        p2 = MultiLocusGenotype.from_str(p2s, ALLELE_MAP)
        self.last_cross_result = execute_cross(p1, p2, MENDELIAN_COMPLETE_DOMINANCE, ALLELE_MAP)

        self.punnett_widget.display_punnett_square(self.last_cross_result.punnett_square)

        ps = self.last_cross_result.punnett_square
        self.cross_diagram.set_cross(
            p1s, p2s,
            [g[0] for g in ps.row_gametes],
            [g[0] for g in ps.col_gametes],
            list(dict.fromkeys(c.zygote_genotype for row in ps.grid for c in row))[:4],
            self.last_cross_result.phenotype_ratios if isinstance(self.last_cross_result.phenotype_ratios, dict) else {}
        )

        self.dna_widget.set_loci_info(f"T-locus ({p1s[0]}/{p2s[0]})", "ACTIVE")

        gf = self.last_cross_result.genotype_frequencies
        pf = self.last_cross_result.phenotype_frequencies
        self.ratio_lbl.setText(
            f"Geno: {self.last_cross_result.genotype_ratios}\n"
            + "  ".join(f"{k} {v*100:.0f}%" for k, v in gf.items()) + "\n"
            f"Pheno: {self.last_cross_result.phenotype_ratios}\n"
            + "  ".join(f"{k} {v*100:.0f}%" for k, v in pf.items())
        )

        pred = self.pred_input.text().strip()
        report = evaluate_student_prediction(self.last_cross_result, pred, target_attribute="phenotype")
        self.led_controller.trigger_prediction_result(report.is_correct)
        self.verdict_panel.set_result(report.is_correct, report.scientific_feedback, report.derivation_proof)

        self.btn_save.setEnabled(True)
        self.save_lbl.setText("")

    def _save_record(self):
        if not self.last_cross_result:
            return
        p1s = self._get_geno(self.p1_combo)
        p2s = self._get_geno(self.p2_combo)
        pred = self.pred_input.text().strip()
        report = evaluate_student_prediction(self.last_cross_result, pred)
        rec = ExperimentRecord(
            experiment_id=f"EXP01-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            experiment_type="Monohybrid Inheritance (Single Locus)",
            parent1_genotype=p1s, parent2_genotype=p2s,
            model_name=MENDELIAN_COMPLETE_DOMINANCE.model_name,
            model_assumptions=MENDELIAN_COMPLETE_DOMINANCE.scientific_assumptions,
            student_prediction=pred,
            expected_genotypic_ratio=self.last_cross_result.genotype_ratios,
            expected_phenotypic_ratio=self.last_cross_result.phenotype_ratios,
            theoretical_frequencies=self.last_cross_result.phenotype_frequencies,
            simulated_or_observed_counts={}, is_simulation=False, simulation_seed=None,
            sample_size=0, chi_square_statistic=None, degrees_of_freedom=None,
            p_value=None, statistical_conclusion=None,
            error_classification=report.error_category.value,
            scientific_interpretation=report.scientific_feedback
        )
        self.exp_store.save_experiment(rec)
        self.led_controller.trigger_experiment_complete()
        self.save_lbl.setText(f"Saved: {rec.experiment_id}")
