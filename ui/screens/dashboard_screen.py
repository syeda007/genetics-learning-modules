"""
UI Screen: Genetics Laboratory Dashboard (Home Screen)
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal


class DashboardScreen(QWidget):
    """
    Main Research Workstation Dashboard.
    Provides academic navigation to Module 01, Planned Modules, Records, and Settings.
    """
    navigate_to = pyqtSignal(str)  # Target screen identifier

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(10)

        # Header Section
        header_frame = QFrame(self)
        header_frame.setObjectName("lab-panel")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_layout.setSpacing(2)

        title = QLabel("GENETICS EXPERIMENTATION SYSTEM", header_frame)
        title.setObjectName("heading-primary")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff; letter-spacing: 1px;")
        
        subtitle = QLabel("Interactive Classical Genetics and Statistical Inheritance Analysis | M.Sc. Research Instrument", header_frame)
        subtitle.setStyleSheet("color: #00b4d8; font-size: 11px; font-weight: 500;")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addWidget(header_frame)

        # System Telemetry Bar
        telemetry_frame = QFrame(self)
        telemetry_frame.setStyleSheet("background-color: #0c1527; border: 1px solid #1a2c4e; border-radius: 4px; padding: 4px;")
        telemetry_layout = QHBoxLayout(telemetry_frame)
        telemetry_layout.setContentsMargins(8, 2, 8, 2)
        
        telemetry_layout.addWidget(QLabel("● SYSTEM: ONLINE (100% OFFLINE CAPABLE)", self))
        telemetry_layout.addWidget(QLabel("● TARGET: M.Sc. GENETICS", self))
        telemetry_layout.addWidget(QLabel("● HARDWARE: GPIO-READY / SIMULATION", self))
        telemetry_layout.addWidget(QLabel("● VER: 1.0.0-ACADEMIC", self))
        telemetry_layout.addStretch()
        main_layout.addWidget(telemetry_frame)

        # Scroll area for modules
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        grid = QGridLayout(scroll_content)
        grid.setSpacing(10)

        # MODULE 01: Fully Functional Primary Module
        mod1_card = QFrame(scroll_content)
        mod1_card.setObjectName("lab-card")
        mod1_card.setStyleSheet("background-color: #122244; border: 2px solid #00b4d8; border-radius: 6px; padding: 10px;")
        mod1_layout = QVBoxLayout(mod1_card)
        mod1_layout.setSpacing(6)

        m1_top = QHBoxLayout()
        m1_badge = QLabel("ACTIVE RESEARCH MODULE", mod1_card)
        m1_badge.setStyleSheet("background-color: #1b4d3e; color: #2ec4b6; border: 1px solid #2ec4b6; border-radius: 3px; padding: 2px 6px; font-size: 9px; font-weight: bold;")
        m1_top.addWidget(QLabel("MODULE 01", mod1_card))
        m1_top.addStretch()
        m1_top.addWidget(m1_badge)
        mod1_layout.addLayout(m1_top)

        m1_title = QLabel("Mendelian Inheritance & Statistical Analysis", mod1_card)
        m1_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffffff;")
        mod1_layout.addWidget(m1_title)

        m1_desc = QLabel("Complete 6-experiment suite: Monohybrid, Dihybrid, Test Cross, Chi-Square Goodness-of-Fit, Offspring Population Simulation, and Offline AI Prediction Evaluation.", mod1_card)
        m1_desc.setWordWrap(True)
        m1_desc.setStyleSheet("color: #a0b2c6; font-size: 10px;")
        mod1_layout.addWidget(m1_desc)

        btn_launch_m1 = QPushButton("ENTER MODULE 01 EXPERIMENTS →", mod1_card)
        btn_launch_m1.setObjectName("btn-primary")
        btn_launch_m1.clicked.connect(lambda: self.navigate_to.emit("module01_hub"))
        mod1_layout.addWidget(btn_launch_m1)
        grid.addWidget(mod1_card, 0, 0, 1, 2)

        # PLANNED MODULES 2 to 6
        planned_modules = [
            ("MODULE 02", "Extensions of Mendelian Genetics", "Incomplete dominance, codominance, multiple alleles, lethal genes, and inter-locus epistasis."),
            ("MODULE 03", "Linkage and Genetic Recombination", "Synteny mapping, 2-point and 3-point test crosses, chiasma interference, and centimorgan calculation."),
            ("MODULE 04", "Population Genetics", "Hardy-Weinberg equilibrium, genetic drift, bottleneck simulations, and selection coefficients."),
            ("MODULE 05", "Quantitative Genetics", "Polygenic inheritance, broad-sense and narrow-sense heritability, additive genetic variance."),
            ("MODULE 06", "Molecular Genetics", "Central dogma mechanics, transcription, translation kinetics, and point mutation consequences.")
        ]

        row = 1
        col = 0
        for tag, name, desc in planned_modules:
            card = QFrame(scroll_content)
            card.setObjectName("lab-card")
            card.setStyleSheet("background-color: #0d172a; border: 1px dashed #243552; border-radius: 6px; padding: 8px;")
            c_layout = QVBoxLayout(card)
            
            top_h = QHBoxLayout()
            lbl_tag = QLabel(tag, card)
            lbl_tag.setStyleSheet("color: #60738a; font-weight: bold; font-size: 9px;")
            badge = QLabel("PLANNED MODULE", card)
            badge.setStyleSheet("background-color: #1a2233; color: #8da0b8; border-radius: 3px; padding: 2px 4px; font-size: 8px;")
            top_h.addWidget(lbl_tag)
            top_h.addStretch()
            top_h.addWidget(badge)
            c_layout.addLayout(top_h)

            c_title = QLabel(name, card)
            c_title.setStyleSheet("font-weight: bold; color: #c4d1e0; font-size: 11px;")
            c_layout.addWidget(c_title)

            c_desc = QLabel(desc, card)
            c_desc.setWordWrap(True)
            c_desc.setStyleSheet("color: #70849d; font-size: 9px;")
            c_layout.addWidget(c_desc)

            btn_disabled = QPushButton("Planned for Phase II", card)
            btn_disabled.setEnabled(False)
            btn_disabled.setStyleSheet("background-color: #121c2e; color: #4f637e; border: 1px solid #1f2c42;")
            c_layout.addWidget(btn_disabled)

            grid.addWidget(card, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        # SYSTEM & RECORDS BUTTONS
        sys_h = QHBoxLayout()
        btn_records = QPushButton("📋 EXPERIMENTAL RECORDS BROWSER", self)
        btn_records.clicked.connect(lambda: self.navigate_to.emit("records"))
        sys_h.addWidget(btn_records)

        btn_settings = QPushButton("⚙️ SYSTEM SETTINGS & HARDWARE", self)
        btn_settings.clicked.connect(lambda: self.navigate_to.emit("settings"))
        sys_h.addWidget(btn_settings)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        main_layout.addLayout(sys_h)
