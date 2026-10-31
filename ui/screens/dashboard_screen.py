"""
UI Screen: Central Dashboard — Visual-First Lab Hub v3.0
Bold, engaging, visual-forward design with vibrant indigo/emerald palette.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QGridLayout, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPainter, QLinearGradient, QPen, QBrush


class GradientBannerWidget(QWidget):
    """Full-width hero banner with indigo gradient and big title."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(110)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor("#4f46e5"))
        grad.setColorAt(0.5, QColor("#6366f1"))
        grad.setColorAt(1.0, QColor("#10b981"))
        p.fillRect(self.rect(), grad)

        # DNA strand dots accent
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(255, 255, 255, 18)))
        for i in range(0, self.width(), 60):
            p.drawEllipse(i, 10, 40, 40)
            p.drawEllipse(i + 20, 55, 30, 30)

        p.end()


class StatBadge(QFrame):
    """A vivid stat metric badge card."""
    def __init__(self, icon, value, label, bg_color, text_color, parent=None):
        super().__init__(parent)
        self.setObjectName("lab-card")
        self.setStyleSheet(
            f"background-color: {bg_color}; border: none; border-radius: 14px; padding: 10px;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(2)

        icon_lbl = QLabel(icon, self)
        icon_lbl.setStyleSheet("font-size: 22px; background: transparent;")
        layout.addWidget(icon_lbl)

        val_lbl = QLabel(value, self)
        val_lbl.setStyleSheet(
            f"font-size: 18px; font-weight: 900; color: {text_color}; background: transparent;"
        )
        layout.addWidget(val_lbl)

        lbl = QLabel(label, self)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(
            f"font-size: 9px; font-weight: 700; color: {text_color}; "
            f"opacity: 0.8; background: transparent; letter-spacing: 0.5px;"
        )
        layout.addWidget(lbl)


class ExperimentCard(QFrame):
    """Visual experiment launch card with color-coded top accent."""
    def __init__(self, screen_id, num, title, icon, desc, accent, parent=None):
        super().__init__(parent)
        self.setObjectName("lab-card")
        self.setStyleSheet(
            f"background-color: #ffffff; border: 1.5px solid #e0e7ff;"
            f"border-top: 4px solid {accent}; border-radius: 14px; padding: 0;"
        )
        self.setCursor(Qt.PointingHandCursor)
        self.screen_id = screen_id

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        # Top: number badge + icon
        top_row = QHBoxLayout()
        num_badge = QLabel(num, self)
        num_badge.setStyleSheet(
            f"background-color: {accent}; color: #ffffff; border-radius: 8px;"
            f"padding: 3px 10px; font-size: 9px; font-weight: 900; letter-spacing: 1px;"
        )
        num_badge.setFixedHeight(20)
        top_row.addWidget(num_badge)
        top_row.addStretch()
        icon_lbl = QLabel(icon, self)
        icon_lbl.setStyleSheet("font-size: 26px; background: transparent;")
        top_row.addWidget(icon_lbl)
        layout.addLayout(top_row)

        # Title
        title_lbl = QLabel(title, self)
        title_lbl.setStyleSheet(
            "font-size: 13px; font-weight: 800; color: #1e1b4b; background: transparent;"
        )
        title_lbl.setWordWrap(True)
        layout.addWidget(title_lbl)

        # Desc — very short
        desc_lbl = QLabel(desc, self)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(
            "color: #6b7280; font-size: 10px; font-weight: 500; background: transparent;"
        )
        layout.addWidget(desc_lbl)
        layout.addStretch()


class DashboardScreen(QWidget):
    navigate_to = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Hero Banner ───────────────────────────────────────────────────────
        banner = GradientBannerWidget(self)
        banner_content = QWidget(banner)
        banner_content.setGeometry(0, 0, 2000, 110)
        b_layout = QVBoxLayout(banner_content)
        b_layout.setContentsMargins(20, 12, 20, 12)
        b_layout.setSpacing(3)

        title_lbl = QLabel("🧬 GENETICS EXPERIMENTATION SYSTEM", banner_content)
        title_lbl.setStyleSheet(
            "font-size: 22px; font-weight: 900; color: #ffffff; letter-spacing: 1px;"
            "background: transparent;"
        )
        b_layout.addWidget(title_lbl)

        sub_lbl = QLabel(
            "Interactive Mendelian Genetics · Biostatistics · Offline AI Evaluation  ·  M.Sc. Research Workstation",
            banner_content
        )
        sub_lbl.setStyleSheet(
            "font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.80);"
            "background: transparent;"
        )
        b_layout.addWidget(sub_lbl)

        status_row = QHBoxLayout()
        for dot, txt, col in [
            ("●", "SYSTEM ONLINE", "#86efac"),
            ("●", "MODULE 01 ACTIVE", "#67e8f9"),
            ("●", "24/24 TESTS PASSED", "#fde68a"),
        ]:
            lbl = QLabel(f"{dot}  {txt}", banner_content)
            lbl.setStyleSheet(
                f"font-size: 9px; font-weight: 800; color: {col}; "
                f"background: transparent; letter-spacing: 0.8px;"
            )
            status_row.addWidget(lbl)
            status_row.addSpacing(18)
        status_row.addStretch()
        b_layout.addLayout(status_row)

        main_layout.addWidget(banner)

        # ── Inner scroll content ──────────────────────────────────────────────
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: #f0f4ff;")
        inner = QVBoxLayout(scroll_widget)
        inner.setContentsMargins(18, 16, 18, 16)
        inner.setSpacing(16)

        # ── Stats Row ─────────────────────────────────────────────────────────
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        stats = [
            ("🔬", "6", "ACTIVE EXPERIMENTS", "#eef2ff", "#4f46e5"),
            ("🧪", "100%", "DETERMINISTIC ENGINE", "#f0fdf4", "#059669"),
            ("🤖", "Offline ML", "DECISION TREE AI", "#fdf4ff", "#7c3aed"),
            ("📊", "χ²", "BIOSTATISTICAL TESTS", "#fff7ed", "#c2410c"),
        ]
        for icon, val, lbl, bg, col in stats:
            badge = StatBadge(icon, val, lbl, bg, col, scroll_widget)
            badge.setFixedHeight(100)
            stats_row.addWidget(badge)
        inner.addLayout(stats_row)

        # ── Section: Module 01 ────────────────────────────────────────────────
        mod_header = QHBoxLayout()
        sec_lbl = QLabel("MODULE 01  ·  Mendelian Inheritance & Statistical Analysis", scroll_widget)
        sec_lbl.setStyleSheet(
            "font-size: 13px; font-weight: 900; color: #1e1b4b; letter-spacing: 0.5px;"
        )
        mod_header.addWidget(sec_lbl)
        mod_header.addStretch()

        active_badge = QLabel("● ACTIVE MODULE", scroll_widget)
        active_badge.setStyleSheet(
            "background-color: #dcfce7; color: #166534; border-radius: 8px;"
            "padding: 4px 12px; font-size: 9px; font-weight: 800; letter-spacing: 0.5px;"
        )
        mod_header.addWidget(active_badge)
        inner.addLayout(mod_header)

        # ── Experiment Cards Grid ─────────────────────────────────────────────
        experiments = [
            ("exp01_monohybrid", "EXP 01", "Monohybrid Inheritance", "🌱",
             "Allele segregation · Single locus · 3:1 phenotypic ratio", "#4f46e5"),
            ("exp02_dihybrid", "EXP 02", "Dihybrid Inheritance", "🌿",
             "Two loci · Independent assortment · 9:3:3:1 ratio", "#7c3aed"),
            ("exp03_testcross", "EXP 03", "Test Cross & Zygosity", "🔍",
             "AA vs Aa identification · Backcross with aa", "#0ea5e9"),
            ("exp04_statistical", "EXP 04", "Chi-Square Validation", "📐",
             "Pearson χ² goodness-of-fit · p-value · Mendel's data", "#059669"),
            ("exp05_simulation", "EXP 05", "Population Simulation", "🧬",
             "Stochastic sampling · N = 20 to 5000 · Drift visualization", "#f59e0b"),
            ("exp06_evaluation_ai", "EXP 06", "Offline AI Evaluator", "🤖",
             "Student error diagnosis · Decision Tree · Instant feedback", "#e11d48"),
        ]

        grid = QGridLayout()
        grid.setSpacing(12)
        row, col = 0, 0
        for screen_id, num, title, icon, desc, accent in experiments:
            card = ExperimentCard(screen_id, num, title, icon, desc, accent, scroll_widget)
            card.setMinimumHeight(155)

            # Launch button inside card
            btn = QPushButton("LAUNCH →", card)
            btn.setObjectName("btn-primary")
            btn.setStyleSheet(
                f"background: {accent}; color: #ffffff; border: none; "
                f"border-radius: 8px; padding: 7px 16px; font-weight: 800; font-size: 10px;"
            )
            btn.clicked.connect(lambda checked, s=screen_id: self.navigate_to.emit(s))
            card.layout().addWidget(btn)

            grid.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        inner.addLayout(grid)

        # ── Coming Soon ───────────────────────────────────────────────────────
        coming_lbl = QLabel("PHASE II MODULES  ·  Coming Soon", scroll_widget)
        coming_lbl.setStyleSheet(
            "font-size: 11px; font-weight: 800; color: #9ca3af; letter-spacing: 0.5px; margin-top: 4px;"
        )
        inner.addWidget(coming_lbl)

        planned_row = QHBoxLayout()
        planned_row.setSpacing(10)
        planned = [
            ("📗", "MOD 02", "Extensions of Mendelian Genetics", "#f3f4f6", "#9ca3af"),
            ("🔗", "MOD 03", "Linkage & Recombination", "#f3f4f6", "#9ca3af"),
            ("🌍", "MOD 04", "Population Genetics", "#f3f4f6", "#9ca3af"),
            ("📈", "MOD 05", "Quantitative Genetics", "#f3f4f6", "#9ca3af"),
        ]
        for icon, tag, title, bg, col in planned:
            f = QFrame(scroll_widget)
            f.setStyleSheet(
                f"background: {bg}; border: 1.5px dashed #d1d5db; border-radius: 12px; padding: 10px;"
            )
            fl = QVBoxLayout(f)
            fl.setContentsMargins(10, 8, 10, 8)
            fl.setSpacing(3)
            fl.addWidget(QLabel(icon + "  " + tag, f))
            tl = QLabel(title, f)
            tl.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {col};")
            tl.setWordWrap(True)
            fl.addWidget(tl)
            bl = QLabel("PLANNED", f)
            bl.setStyleSheet(
                "background: #e5e7eb; color: #6b7280; border-radius: 4px;"
                "padding: 2px 8px; font-size: 8px; font-weight: 800;"
            )
            fl.addWidget(bl)
            planned_row.addWidget(f)
        inner.addLayout(planned_row)

        # ── Bottom nav buttons ────────────────────────────────────────────────
        nav_row = QHBoxLayout()
        nav_row.setSpacing(10)

        btn_module = QPushButton("📋  Module 01 Hub  →", scroll_widget)
        btn_module.setObjectName("btn-primary")
        btn_module.clicked.connect(lambda: self.navigate_to.emit("module01_hub"))
        nav_row.addWidget(btn_module)

        btn_records = QPushButton("🗂  Experiment Records", scroll_widget)
        btn_records.setObjectName("btn-secondary")
        btn_records.clicked.connect(lambda: self.navigate_to.emit("records"))
        nav_row.addWidget(btn_records)

        btn_settings = QPushButton("⚙  Settings & Hardware", scroll_widget)
        btn_settings.setObjectName("btn-secondary")
        btn_settings.clicked.connect(lambda: self.navigate_to.emit("settings"))
        nav_row.addWidget(btn_settings)

        nav_row.addStretch()
        inner.addLayout(nav_row)

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
