"""
UI Screen: Module 01 Overview — Experiment Hub v4.0
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal


def _make_exp_card(screen_id, num, title, desc, tag, accent, navigate_fn, parent):
    card = QFrame(parent)
    card.setObjectName("card")
    card.setStyleSheet(
        f"QFrame#card {{ background:#ffffff; border:1.5px solid #e8eaf2;"
        f"border-top:4px solid {accent}; border-radius:12px; }}"
    )
    card.setMinimumHeight(110)
    lay = QVBoxLayout(card)
    lay.setContentsMargins(14, 12, 14, 12)
    lay.setSpacing(5)

    top = QHBoxLayout()
    num_lbl = QLabel(num, card)
    num_lbl.setStyleSheet(
        f"background:{accent}; color:#ffffff; border-radius:5px;"
        f"padding:2px 8px; font-size:9px; font-weight:800;"
    )
    top.addWidget(num_lbl)
    top.addStretch()
    tag_lbl = QLabel(tag, card)
    tag_lbl.setStyleSheet(
        "background:#f1f5f9; color:#64748b; border-radius:4px; padding:2px 7px; font-size:8px; font-weight:700;"
    )
    top.addWidget(tag_lbl)
    lay.addLayout(top)

    t = QLabel(title, card)
    t.setStyleSheet("font-size: 11px; font-weight: 800; color: #1a1d2e;")
    lay.addWidget(t)
    d = QLabel(desc, card)
    d.setWordWrap(True)
    d.setStyleSheet("font-size: 9px; color: #64748b;")
    lay.addWidget(d)

    btn = QPushButton("Open Experiment", card)
    btn.setObjectName("btn-primary" if accent != "#94a3b8" else "btn-secondary")
    btn.setFixedHeight(30)
    if screen_id:
        btn.clicked.connect(lambda: navigate_fn(screen_id))
    else:
        btn.setEnabled(False)
        btn.setText("Coming Soon")
    lay.addWidget(btn)
    return card


class Module01OverviewScreen(QWidget):
    navigate_to = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        hdr = QFrame(self)
        hdr.setStyleSheet("background:#ffffff; border-bottom:1px solid #e8eaf2;")
        hdr.setFixedHeight(44)
        h = QHBoxLayout(hdr)
        h.setContentsMargins(14, 6, 14, 6)

        back = QPushButton("← Dashboard", hdr)
        back.setObjectName("btn-back")
        back.setFixedWidth(100)
        back.clicked.connect(lambda: self.navigate_to.emit("dashboard"))
        h.addWidget(back)

        t = QLabel("MODULE 01 — Mendelian Inheritance & Statistics", hdr)
        t.setStyleSheet("font-size: 13px; font-weight: 800; color: #1a1d2e;")
        h.addWidget(t)
        h.addStretch()
        root.addWidget(hdr)

        # Scroll
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(12)

        sub = QLabel("Select an experiment to begin:", content)
        sub.setStyleSheet("font-size: 9px; color: #64748b; font-weight: 600;")
        cl.addWidget(sub)

        grid = QGridLayout()
        grid.setSpacing(12)

        experiments = [
            ("exp01_monohybrid", "EXP 01", "Monohybrid Inheritance",
             "Single locus, complete dominance. Construct Punnett squares and derive 3:1 ratios.",
             "GENETICS", "#6366f1"),
            ("exp02_dihybrid", "EXP 02", "Dihybrid Inheritance",
             "Two-locus independent assortment. Derive 9:3:3:1 phenotypic ratios.",
             "GENETICS", "#0d9488"),
            ("exp03_testcross", "EXP 03", "Test Cross Analysis",
             "Determine unknown genotypes using recessive homozygous parents.",
             "GENETICS", "#8b5cf6"),
            ("exp04_statistical", "EXP 04", "Chi-Square Validation",
             "Test observed vs. expected ratios. Degrees of freedom and significance.",
             "STATISTICS", "#f59e0b"),
            ("exp05_simulation", "EXP 05", "Population Simulation",
             "Hardy-Weinberg equilibrium and genetic drift over generations.",
             "SIMULATION", "#059669"),
            ("exp06_evaluation_ai", "EXP 06", "AI Prediction Evaluator",
             "Offline ML classifier to evaluate student predictions scientifically.",
             "AI/ML", "#6366f1"),
        ]

        for i, args in enumerate(experiments):
            card = _make_exp_card(*args, self.navigate_to.emit, content)
            grid.addWidget(card, i // 2, i % 2)

        cl.addLayout(grid)
        cl.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll)
