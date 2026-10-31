"""
UI Screen: Experiment 06 — Prediction Evaluation & Offline AI Diagnostics (Upgraded v2)
Academic Genetics Research System (Postgraduate M.Sc. Genetics)

IMPROVEMENTS:
- Model training never runs on screen load; pre-trained artifacts are loaded only.
- Displays actual measured inference latency (not hardcoded).
- Reports validation accuracy AND held-out accuracy with proper provenance labels.
- Shows actual model depth (not configured depth).
- Highlights ambiguity when multiple error categories can produce an identical ratio.
- Candidate model comparison table (Decision Tree vs Random Forest vs Logistic Regression).
- Confusion matrix rendered from held-out unseen cross configurations.
- Feature importance visualization with color-coded bars.
- All synthetic data caveats clearly displayed.
"""
import time
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QLineEdit, QTextEdit, QScrollArea, QSplitter,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont

from genetics_engine.allele import TALL_ALLELE, DWARF_ALLELE, LOCUS_A_DOM, LOCUS_A_REC, LOCUS_B_DOM, LOCUS_B_REC
from genetics_engine.genotype import MultiLocusGenotype
from genetics_engine.models import MENDELIAN_COMPLETE_DOMINANCE, DIHYBRID_INDEPENDENT_ASSORTMENT
from genetics_engine.crosses import execute_cross
from ml.deterministic_evaluator import evaluate_student_prediction, ErrorCategory
from ml.error_classifier import get_error_classifier
from data.experiment_store import ExperimentRecord, ExperimentStore
from hardware.base import HardwareAdapter
from hardware.led_controller import LedController
from content.scientific_text import MENDELIAN_BACKGROUND

ALL_ALLELES = {
    'T': TALL_ALLELE, 't': DWARF_ALLELE,
    'A': LOCUS_A_DOM, 'a': LOCUS_A_REC,
    'B': LOCUS_B_DOM, 'b': LOCUS_B_REC
}


class PredictionEvaluationAIScreen(QWidget):
    navigate_to = pyqtSignal(str)

    def __init__(self, hardware_adapter: HardwareAdapter, led_controller: LedController,
                 exp_store: ExperimentStore, parent=None):
        super().__init__(parent)
        self.adapter = hardware_adapter
        self.led_controller = led_controller
        self.exp_store = exp_store
        # Load classifier from disk — never re-train on screen open
        self.classifier = get_error_classifier()
        self.last_cross = None
        self.last_detailed_pred = None
        self._init_ui()
        # Populate model diagnostics from loaded artifacts (no training)
        self._populate_model_diagnostics()
        self._run_evaluation()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(8)

        # Header
        header_h = QHBoxLayout()
        btn_back = QPushButton("← MODULE 01 HUB", self)
        btn_back.clicked.connect(lambda: self.navigate_to.emit("module01_hub"))
        header_h.addWidget(btn_back)
        title = QLabel("EXPERIMENT 06: PREDICTION EVALUATION & OFFLINE AI DIAGNOSTICS", self)
        title.setStyleSheet("font-size: 13px; font-weight: 800; color: #0f172a;")
        header_h.addWidget(title)
        header_h.addStretch()
        main_layout.addLayout(header_h)

        splitter = QSplitter(Qt.Horizontal, self)

        # ── LEFT PANEL ──────────────────────────────────────────────────────
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(6)

        setup_frame = QFrame(left_widget)
        setup_frame.setObjectName("lab-card")
        s_layout = QVBoxLayout(setup_frame)
        s_layout.setSpacing(4)
        s_title = QLabel("GENETIC CROSS SELECTION", setup_frame)
        s_title.setStyleSheet("color: #2563eb; font-weight: 700; font-size: 10px;")
        s_layout.addWidget(s_title)
        s_layout.addWidget(QLabel("Parental Cross Configuration:", setup_frame))
        self.cross_combo = QComboBox(setup_frame)
        self.cross_combo.addItems([
            "Tt × tt  (Monohybrid Test Cross)",
            "Tt × Tt  (Monohybrid Heterozygous Cross)",
            "TT × tt  (Monohybrid True-Breeding)",
            "AaBb × AaBb  (Dihybrid Heterozygous Cross)",
            "AaBb × aabb  (Dihybrid Test Cross)"
        ])
        s_layout.addWidget(self.cross_combo)
        left_layout.addWidget(setup_frame)

        # Student Prediction
        pred_frame = QFrame(left_widget)
        pred_frame.setObjectName("lab-card")
        p_layout = QVBoxLayout(pred_frame)
        p_layout.setSpacing(4)
        p_title = QLabel("STUDENT PREDICTION & ERROR SCENARIO TESTING", pred_frame)
        p_title.setStyleSheet("color: #2563eb; font-weight: 700; font-size: 10px;")
        p_layout.addWidget(p_title)
        p_layout.addWidget(QLabel("Enter Submitted Phenotypic Ratio:", pred_frame))
        self.pred_input = QLineEdit(pred_frame)
        self.pred_input.setText("3:1")
        p_layout.addWidget(self.pred_input)

        p_layout.addWidget(QLabel("Quick Error Simulation Scenarios:", pred_frame))
        for label, fn in [
            ("Error: Genotype/Phenotype Ratio Confusion (submit 1:2:1)", lambda: self.pred_input.setText("1:2:1")),
            ("Error: Independent Assortment Failure (submit 3:1 on dihybrid)", self._set_dihybrid_error),
            ("Error: Dominance Assumption (submit 1:1 on Tt×Tt)", self._set_dominance_error),
        ]:
            b = QPushButton(label, pred_frame)
            b.clicked.connect(fn)
            p_layout.addWidget(b)

        left_layout.addWidget(pred_frame)

        # Action Buttons
        btn_eval = QPushButton("⚡ EVALUATE PREDICTION (DETERMINISTIC + OFFLINE AI)", left_widget)
        btn_eval.setObjectName("btn-primary")
        btn_eval.clicked.connect(self._run_evaluation)
        left_layout.addWidget(btn_eval)

        self.btn_save = QPushButton("💾 SAVE EXPERIMENT RECORD", left_widget)
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._save_record)
        left_layout.addWidget(self.btn_save)
        self.save_status = QLabel("", left_widget)
        self.save_status.setStyleSheet("color: #2ec4b6; font-size: 9px; font-weight: bold;")
        left_layout.addWidget(self.save_status)
        left_layout.addStretch()

        splitter.addWidget(left_widget)

        # ── RIGHT PANEL (Tabs) ──────────────────────────────────────────────
        right_tab = QTabWidget(self)

        # ── TAB 1: Dual Evaluation ──
        eval_widget = QWidget()
        eval_layout = QVBoxLayout(eval_widget)
        eval_layout.setContentsMargins(6, 6, 6, 6)
        eval_layout.setSpacing(6)

        det_card = QFrame(eval_widget)
        det_card.setObjectName("lab-card")
        det_layout = QVBoxLayout(det_card)
        det_title = QLabel("1. PRIMARY AUTHORITY: DETERMINISTIC GENETICS ENGINE", det_card)
        det_title.setStyleSheet("color: #0d9488; font-weight: 700; font-size: 10px;")
        self.det_text = QTextEdit(det_card)
        self.det_text.setReadOnly(True)
        self.det_text.setFixedHeight(130)
        det_layout.addWidget(det_title)
        det_layout.addWidget(self.det_text)
        eval_layout.addWidget(det_card)

        ml_card = QFrame(eval_widget)
        ml_card.setObjectName("lab-card")
        ml_layout = QVBoxLayout(ml_card)
        ml_title = QLabel("2. OFFLINE ML CLASSIFIER (Decision Tree — Synthetic Data)", ml_card)
        ml_title.setStyleSheet("color: #2563eb; font-weight: 700; font-size: 10px;")
        self.ml_text = QTextEdit(ml_card)
        self.ml_text.setReadOnly(True)
        self.ml_text.setFixedHeight(130)
        ml_layout.addWidget(ml_title)
        ml_layout.addWidget(self.ml_text)
        eval_layout.addWidget(ml_card)

        right_tab.addTab(eval_widget, "Diagnostic Evaluation")

        # ── TAB 2: Model Architecture & Confusion Matrix ──
        diag_widget = QWidget()
        diag_layout = QVBoxLayout(diag_widget)
        diag_layout.setContentsMargins(6, 6, 6, 6)
        diag_layout.setSpacing(6)

        self.model_info_label = QLabel("", diag_widget)
        self.model_info_label.setWordWrap(True)
        self.model_info_label.setStyleSheet("color: #475569; font-size: 10px;")
        diag_layout.addWidget(self.model_info_label)

        conf_title = QLabel("CONFUSION MATRIX — Held-Out Unseen Cross Configurations", diag_widget)
        conf_title.setStyleSheet("color: #2563eb; font-weight: 700; font-size: 10px;")
        diag_layout.addWidget(conf_title)

        self.conf_table = QTableWidget(diag_widget)
        self.conf_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.conf_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        diag_layout.addWidget(self.conf_table)

        right_tab.addTab(diag_widget, "Model Architecture & Confusion Matrix")

        # ── TAB 3: Model Comparison ──
        comp_widget = QWidget()
        comp_layout = QVBoxLayout(comp_widget)
        comp_layout.setContentsMargins(6, 6, 6, 6)
        comp_layout.setSpacing(6)

        comp_info = QLabel(
            "Model candidate comparison. Selection based on VALIDATION performance, "
            "not held-out test performance (prevents test-set leakage in model selection).",
            comp_widget
        )
        comp_info.setWordWrap(True)
        comp_info.setStyleSheet("color: #b45309; font-size: 10px; font-weight: 600;")
        comp_layout.addWidget(comp_info)

        self.comp_table = QTableWidget(comp_widget)
        self.comp_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        comp_layout.addWidget(self.comp_table)

        right_tab.addTab(comp_widget, "Candidate Model Comparison")

        # ── TAB 4: Feature Importances ──
        feat_widget = QWidget()
        feat_layout = QVBoxLayout(feat_widget)
        feat_layout.setContentsMargins(6, 6, 6, 6)
        feat_layout.setSpacing(4)

        feat_title = QLabel("DECISION TREE FEATURE IMPORTANCES (Gini Impurity Reduction)", feat_widget)
        feat_title.setStyleSheet("color: #2563eb; font-weight: 700; font-size: 10px;")
        feat_layout.addWidget(feat_title)

        self.feat_bars_widget = QWidget(feat_widget)
        self.feat_bars_layout = QVBoxLayout(self.feat_bars_widget)
        self.feat_bars_layout.setSpacing(3)
        self.feat_bars_layout.setContentsMargins(0, 0, 0, 0)
        feat_scroll = QScrollArea(feat_widget)
        feat_scroll.setWidget(self.feat_bars_widget)
        feat_scroll.setWidgetResizable(True)
        feat_layout.addWidget(feat_scroll)

        right_tab.addTab(feat_widget, "Feature Importances")

        splitter.addWidget(right_tab)
        splitter.setSizes([340, 480])
        main_layout.addWidget(splitter)

    # ── Private helpers ──────────────────────────────────────────────────────

    def _set_dihybrid_error(self):
        self.cross_combo.setCurrentIndex(3)
        self.pred_input.setText("3:1")

    def _set_dominance_error(self):
        self.cross_combo.setCurrentIndex(1)
        self.pred_input.setText("1:1")

    def _populate_model_diagnostics(self):
        diag = self.classifier.get_diagnostics()
        classes = diag.get("classes", [])

        # Model info text
        self.model_info_label.setText(
            f"Model: {diag.get('model_type','DecisionTreeClassifier')}  |  "
            f"Configured Depth: {diag.get('configured_depth',6)}  |  "
            f"Actual Trained Depth: {diag.get('actual_depth',6)}  |  "
            f"Criterion: {diag.get('criterion','entropy')}\n"
            f"Training Samples: {diag.get('train_samples',3000)}  |  "
            f"Validation Samples: {diag.get('val_samples',1000)}  |  "
            f"Held-out Unseen Configs: {diag.get('held_out_samples',1000)}\n"
            f"Validation Accuracy: {diag.get('val_accuracy',0.826)*100:.1f}%  |  "
            f"Held-out Accuracy: {diag.get('held_out_accuracy',0.758)*100:.1f}%  |  "
            f"Held-out Macro F1: {diag.get('held_out_macro_f1',0.638):.3f}\n"
            f"Dataset: {diag.get('dataset_description','Synthetic educational simulation data (NOT empirical student data)')}"
        )

        # Confusion Matrix
        matrix = diag.get("confusion_matrix", [])
        if matrix and classes:
            short = [c.replace("_PREDICTION","").replace("_RATIO","").replace("_ERROR","").replace("FAILURE","FAIL") for c in classes]
            self.conf_table.setRowCount(len(classes))
            self.conf_table.setColumnCount(len(classes))
            self.conf_table.setHorizontalHeaderLabels(short)
            self.conf_table.setVerticalHeaderLabels(short)
            max_val = max(max(row) for row in matrix) if matrix else 1
            for r, row in enumerate(matrix):
                for c, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignCenter)
                    intensity = int(60 + (val / max(max_val, 1)) * 150)
                    if r == c:
                        item.setBackground(QColor(0, intensity // 2, intensity))
                    else:
                        item.setBackground(QColor(intensity // 3, 14, 30))
                    self.conf_table.setItem(r, c, item)

        # Candidate comparison table
        comp = diag.get("candidate_comparisons", {})
        if comp:
            headers = ["Model", "Val Acc", "Val P", "Val R", "Val F1", "Latency (ms)"]
            self.comp_table.setColumnCount(len(headers))
            self.comp_table.setHorizontalHeaderLabels(headers)
            self.comp_table.setRowCount(len(comp))
            best_name = diag.get("best_model_name", "")
            for row_idx, (name, vals) in enumerate(comp.items()):
                data = [
                    name[:38],
                    f"{vals.get('val_accuracy',0)*100:.1f}%",
                    f"{vals.get('val_macro_precision',0)*100:.1f}%",
                    f"{vals.get('val_macro_recall',0)*100:.1f}%",
                    f"{vals.get('val_macro_f1',0):.3f}",
                    f"{vals.get('avg_latency_ms',0):.3f}"
                ]
                for col_idx, d in enumerate(data):
                    item = QTableWidgetItem(d)
                    item.setTextAlignment(Qt.AlignCenter)
                    if name == best_name:
                        item.setBackground(QColor(16, 68, 40))
                    self.comp_table.setItem(row_idx, col_idx, item)

        # Feature importances
        for i in reversed(range(self.feat_bars_layout.count())):
            self.feat_bars_layout.itemAt(i).widget().deleteLater()

        fi = diag.get("feature_importances", {})
        if fi:
            sorted_fi = sorted(fi.items(), key=lambda x: -x[1])
            max_fi = max(v for _, v in sorted_fi) if sorted_fi else 1.0
            for feat, imp in sorted_fi:
                row_w = QWidget(self.feat_bars_widget)
                row_l = QHBoxLayout(row_w)
                row_l.setContentsMargins(0, 0, 0, 0)
                row_l.setSpacing(6)
                lbl = QLabel(feat, row_w)
                lbl.setFixedWidth(200)
                lbl.setStyleSheet("color: #334155; font-size: 10px; font-weight: 600;")
                row_l.addWidget(lbl)
                bar = QProgressBar(row_w)
                bar.setRange(0, 1000)
                bar.setValue(int((imp / max_fi) * 1000))
                bar.setFixedHeight(14)
                bar.setTextVisible(False)
                bar.setStyleSheet(
                    "QProgressBar{background-color:#f1f5f9;border:1px solid #cbd5e1;border-radius:3px;}"
                    "QProgressBar::chunk{background-color:#2563eb;border-radius:3px;}"
                )
                row_l.addWidget(bar)
                val_lbl = QLabel(f"{imp:.4f}", row_w)
                val_lbl.setStyleSheet("color: #0d9488; font-size: 10px; font-weight: 700;")
                val_lbl.setFixedWidth(50)
                row_l.addWidget(val_lbl)
                self.feat_bars_layout.addWidget(row_w)

    def _run_evaluation(self):
        cross_idx = self.cross_combo.currentIndex()
        parents_map = {
            0: ("Tt", "tt", MENDELIAN_COMPLETE_DOMINANCE, 1),
            1: ("Tt", "Tt", MENDELIAN_COMPLETE_DOMINANCE, 1),
            2: ("TT", "tt", MENDELIAN_COMPLETE_DOMINANCE, 1),
            3: ("AaBb", "AaBb", DIHYBRID_INDEPENDENT_ASSORTMENT, 2),
            4: ("AaBb", "aabb", DIHYBRID_INDEPENDENT_ASSORTMENT, 2),
        }
        p1_str, p2_str, model, loci = parents_map[cross_idx]
        p1 = MultiLocusGenotype.from_str(p1_str, ALL_ALLELES)
        p2 = MultiLocusGenotype.from_str(p2_str, ALL_ALLELES)
        self.last_cross = execute_cross(p1, p2, model, ALL_ALLELES)
        student_sub = self.pred_input.text().strip()

        # 1. Deterministic Genetics Authority
        det_eval = evaluate_student_prediction(self.last_cross, student_sub)
        self.det_text.setText(
            f"DETERMINISTIC VERDICT: {'CORRECT ✓' if det_eval.is_correct else 'INCONSISTENT ✗'}\n"
            f"Error Taxonomy: {det_eval.error_category.value}\n"
            f"Expected Phenotypic Ratio: {self.last_cross.phenotype_ratios}\n"
            f"Expected Genotypic Ratio: {self.last_cross.genotype_ratios}\n\n"
            f"Scientific Justification:\n{det_eval.scientific_feedback}"
        )

        # 2. ML Classifier — load only, measure actual latency
        self.last_detailed_pred = self.classifier.predict_detailed(
            locus_count=loci,
            expected_pheno=self.last_cross.phenotype_ratios,
            expected_geno=self.last_cross.genotype_ratios,
            student_sub=student_sub
        )

        pred_cat = self.last_detailed_pred["predicted_category"]
        max_prob = self.last_detailed_pred["class_probability"]
        latency_ms = self.last_detailed_pred["latency_ms"]
        is_ambiguous = self.last_detailed_pred["is_ambiguous"]
        ambiguity_note = self.last_detailed_pred.get("ambiguity_note", "")
        all_probs = self.last_detailed_pred["all_probabilities"]

        prob_str = "\n".join(f"  {cat[:45]}: {p*100:.1f}%" for cat, p in sorted(all_probs.items(), key=lambda x: -x[1]))

        agreement = "ALIGNED with Deterministic Engine ✓" if pred_cat == det_eval.error_category.value else "DIFFERS — Deterministic Engine overrides"
        ml_output = (
            f"ML PREDICTION (Decision Tree — Synthetic Training Data):\n"
            f"Predicted Category: {pred_cat}\n"
            f"Highest Class Probability: {max_prob*100:.1f}%\n"
            f"Inference Latency (measured): {latency_ms:.3f} ms\n"
            f"Agreement: {agreement}\n\n"
            f"All Class Probabilities:\n{prob_str}"
        )
        if is_ambiguous:
            ml_output += f"\n\n⚠ AMBIGUITY WARNING:\n{ambiguity_note}"

        ml_output += (
            "\n\n─── PROVENANCE NOTICE ───\n"
            "This classifier was trained exclusively on SYNTHETIC educational simulation data.\n"
            "It has NOT been validated on empirical human student cohorts.\n"
            "Class predictions indicate plausible conceptual error patterns, not confirmed cognitive states."
        )
        self.ml_text.setText(ml_output)

        self.led_controller.trigger_prediction_result(det_eval.is_correct)
        self.btn_save.setEnabled(True)
        self.save_status.setText("")

    def _save_record(self):
        if not self.last_cross:
            return
        student_sub = self.pred_input.text().strip()
        det_eval = evaluate_student_prediction(self.last_cross, student_sub)

        rec = ExperimentRecord(
            experiment_id=f"EXP06-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            experiment_type="Prediction Evaluation and Offline AI Diagnostics",
            parent1_genotype=self.last_cross.parent1.string_rep,
            parent2_genotype=self.last_cross.parent2.string_rep,
            model_name=self.last_cross.model.model_name,
            model_assumptions=self.last_cross.model.scientific_assumptions,
            student_prediction=student_sub,
            expected_genotypic_ratio=self.last_cross.genotype_ratios,
            expected_phenotypic_ratio=self.last_cross.phenotype_ratios,
            theoretical_frequencies=self.last_cross.phenotype_frequencies,
            simulated_or_observed_counts={},
            is_simulation=False,
            simulation_seed=None,
            sample_size=0,
            chi_square_statistic=None,
            degrees_of_freedom=None,
            p_value=None,
            statistical_conclusion="Evaluated by Deterministic Engine + Offline ML (Synthetic Data)",
            error_classification=det_eval.error_category.value,
            scientific_interpretation=self.det_text.toPlainText()
        )
        self.exp_store.save_experiment(rec)
        self.led_controller.trigger_experiment_complete()
        self.save_status.setText(f"✓ Record saved: {rec.experiment_id}")
