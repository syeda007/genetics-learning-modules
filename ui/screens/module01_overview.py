"""
UI Screen: Module 01 Experiment Hub
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal


class Module01OverviewScreen(QWidget):
    """
    Experiment Selection Hub for Module 01: Mendelian Inheritance.
    All 6 experiments are independently accessible and fully implemented.
    """
    navigate_to = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(10)

        # Header with Back button
        header_h = QHBoxLayout()
        btn_back = QPushButton("← BACK TO DASHBOARD", self)
        btn_back.setStyleSheet("max-width: 160px;")
        btn_back.clicked.connect(lambda: self.navigate_to.emit("dashboard"))
        header_h.addWidget(btn_back)

        title = QLabel("MODULE 01: MENDELIAN INHERITANCE — RESEARCH LAB SUITE", self)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffffff;")
        header_h.addWidget(title)
        header_h.addStretch()
        main_layout.addLayout(header_h)

        # Description
        desc_lbl = QLabel(
            "Select an experimental investigation below. Each experiment provides full theoretical modeling, "
            "physical/simulated genotype selection, Punnett square construction, and statistical analysis.",
            self
        )
        desc_lbl.setStyleSheet("color: #8da0b8; font-size: 10px;")
        main_layout.addWidget(desc_lbl)

        # Scroll Area for 6 Experiments
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        grid = QGridLayout(scroll_content)
        grid.setSpacing(10)

        experiments = [
            ("exp01_monohybrid", "EXPERIMENT 01", "Monohybrid Inheritance",
             "Single locus (T/t). Complete dominance model, allele segregation, Punnett square, 3:1 phenotypic & 1:2:1 genotypic ratios.",
             "● Complete Dominance  ● Pisum sativum model"),
            ("exp02_dihybrid", "EXPERIMENT 02", "Dihybrid Inheritance",
             "Two unlinked loci (A/a, B/b). Independent assortment, 4×4 Punnett square, product rule of probability, 9:3:3:1 ratio derivation.",
             "● Independent Assortment  ● 16-Cell Matrix"),
            ("exp03_testcross", "EXPERIMENT 03", "Test Cross Analysis",
             "Zygosity determination of dominant phenotypes (AA vs Aa crossed with aa). Formulate hypotheses and calculate statistical likelihoods.",
             "● Zygosity Discrimination  ● Likelihood Ratio"),
            ("exp04_statistical", "EXPERIMENT 04", "Biostatistical Validation",
             "Pearson Chi-Square goodness-of-fit testing. Calculate χ², degrees of freedom, p-value, Cochran's small count rule, and academic decision.",
             "● Pearson χ² Test  ● Cochran Minimum Count"),
            ("exp05_simulation", "EXPERIMENT 05", "Population Simulation",
             "Stochastic multinomial sampling across population cohorts (N=20 to 1,000+). Demonstrate sampling variation and the Law of Large Numbers.",
             "● Stochastic Sampling  ● Law of Large Numbers"),
            ("exp06_evaluation_ai", "EXPERIMENT 06", "Diagnostic Error AI",
             "Student prediction evaluation combining deterministic genetics calculation authority with an offline Decision Tree classifier.",
             "● Error Taxonomy  ● Offline ML Inference")
        ]

        row = 0
        col = 0
        for screen_id, tag, title_text, desc, tags in experiments:
            card = QFrame(scroll_content)
            card.setObjectName("lab-card")
            card.setStyleSheet("background-color: #0f1a30; border: 1px solid #223a66; border-radius: 6px; padding: 10px;")
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(6)

            top_h = QHBoxLayout()
            tag_lbl = QLabel(tag, card)
            tag_lbl.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
            status_lbl = QLabel("READY", card)
            status_lbl.setStyleSheet("background-color: #103b42; color: #2ec4b6; border-radius: 2px; padding: 1px 4px; font-size: 8px; font-weight: bold;")
            top_h.addWidget(tag_lbl)
            top_h.addStretch()
            top_h.addWidget(status_lbl)
            card_layout.addLayout(top_h)

            t_lbl = QLabel(title_text, card)
            t_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #ffffff;")
            card_layout.addWidget(t_lbl)

            d_lbl = QLabel(desc, card)
            d_lbl.setWordWrap(True)
            d_lbl.setStyleSheet("color: #8da0b8; font-size: 9px;")
            card_layout.addWidget(d_lbl)

            tag_footer = QLabel(tags, card)
            tag_footer.setStyleSheet("color: #5c7494; font-size: 8px; font-style: italic;")
            card_layout.addWidget(tag_footer)

            btn = QPushButton("LAUNCH EXPERIMENT →", card)
            btn.setObjectName("btn-primary")
            btn.clicked.connect(lambda checked, s=screen_id: self.navigate_to.emit(s))
            card_layout.addWidget(btn)

            grid.addWidget(card, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
