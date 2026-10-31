"""
UI Screen: Dashboard — Premium Visual-First Light Theme v4.0
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient, QBrush, QPainterPath


class ChromosomeBannerWidget(QWidget):
    """Elegant light-theme hero banner with chromosome illustration."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Soft gradient background
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor("#f0f4ff"))
        grad.setColorAt(1.0, QColor("#f5f3ff"))
        p.fillRect(self.rect(), grad)

        # Decorative chromosome shapes (simplified)
        pen = QPen(QColor("#c7d2fe"), 2)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)

        for x_off in range(0, self.width(), 90):
            cx = x_off + 20
            # Chromosome body
            p.setBrush(QBrush(QColor("#e0e7ff")))
            p.drawRoundedRect(cx, 20, 12, 60, 6, 6)
            # Centromere
            p.setBrush(QBrush(QColor("#6366f1")))
            p.drawEllipse(cx + 2, 47, 8, 8)

        # Title text
        p.setPen(QColor("#1a1d2e"))
        f = QFont("Segoe UI Variable", 16, QFont.Bold)
        p.setFont(f)
        p.drawText(self.rect().adjusted(24, 0, 0, -10), Qt.AlignVCenter | Qt.AlignLeft,
                   "Genetics Learning System")
        p.setPen(QColor("#6366f1"))
        f2 = QFont("Segoe UI Variable", 9)
        p.setFont(f2)
        p.drawText(self.rect().adjusted(24, 36, 0, 0), Qt.AlignVCenter | Qt.AlignLeft,
                   "Interactive Classical Genetics & Statistical Inheritance  |  M.Sc. Research Instrument")
        p.end()


class ModuleCard(QFrame):
    """Clickable visual module card."""
    clicked = pyqtSignal(str)

    def __init__(self, screen_id, number, title, desc, tag, accent, parent=None):
        super().__init__(parent)
        self.screen_id = screen_id
        self.setObjectName("card")
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumHeight(130)
        self.setStyleSheet(
            f"QFrame#card {{ background: #ffffff; border: 1.5px solid #e8eaf2; "
            f"border-top: 4px solid {accent}; border-radius: 12px; }}"
            f"QFrame#card:hover {{ border-color: {accent}; background: #fafafe; }}"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(6)

        top = QHBoxLayout()
        num_lbl = QLabel(number, self)
        num_lbl.setStyleSheet(
            f"background: {accent}; color: #ffffff; border-radius: 6px;"
            f"padding: 2px 10px; font-size: 9px; font-weight: 800; letter-spacing: 1px;"
        )
        top.addWidget(num_lbl)
        top.addStretch()
        if tag:
            tag_lbl = QLabel(tag, self)
            tag_lbl.setStyleSheet(
                "background: #f1f5f9; color: #64748b; border-radius: 4px;"
                "padding: 2px 8px; font-size: 8px; font-weight: 700;"
            )
            top.addWidget(tag_lbl)
        lay.addLayout(top)

        title_lbl = QLabel(title, self)
        title_lbl.setWordWrap(True)
        title_lbl.setStyleSheet("font-size: 12px; font-weight: 800; color: #1a1d2e;")
        lay.addWidget(title_lbl)

        desc_lbl = QLabel(desc, self)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("font-size: 9px; color: #64748b;")
        lay.addWidget(desc_lbl)
        lay.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.screen_id)


class QuickLinkButton(QPushButton):
    """Compact quick-link at bottom of dashboard."""
    def __init__(self, label, parent=None):
        super().__init__(label, parent)
        self.setObjectName("btn-secondary")
        self.setFixedHeight(38)


class DashboardScreen(QWidget):
    navigate_to = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Banner
        banner = ChromosomeBannerWidget(self)
        root.addWidget(banner)

        # ── Scrollable content
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        clayout = QVBoxLayout(content)
        clayout.setContentsMargins(20, 16, 20, 20)
        clayout.setSpacing(16)

        # ── Section header
        section_h = QHBoxLayout()
        section_lbl = QLabel("EXPERIMENT MODULES", content)
        section_lbl.setStyleSheet(
            "font-size: 9px; font-weight: 800; color: #6366f1; letter-spacing: 1.5px;"
        )
        section_h.addWidget(section_lbl)
        section_h.addStretch()
        clayout.addLayout(section_h)

        # ── Module grid
        grid = QGridLayout()
        grid.setSpacing(12)

        modules = [
            ("module01_hub", "MODULE 01", "Mendelian Inheritance & Statistics",
             "Mono/Dihybrid crosses, Test cross, Chi-square, Population simulation",
             "ACTIVE", "#6366f1"),
            ("", "MODULE 02", "Extensions of Mendelian Genetics",
             "Incomplete dominance, codominance, epistasis, multiple alleles",
             "PLANNED", "#94a3b8"),
            ("", "MODULE 03", "Linkage & Recombination",
             "Synteny mapping, 2-point & 3-point test crosses, centimorgans",
             "PLANNED", "#94a3b8"),
            ("", "MODULE 04", "Molecular & Population Genetics",
             "Hardy-Weinberg, genetic drift, selection, allele frequency dynamics",
             "PLANNED", "#94a3b8"),
        ]

        for i, (sid, num, title, desc, tag, accent) in enumerate(modules):
            card = ModuleCard(sid or "dashboard", num, title, desc, tag, accent, content)
            if sid:
                card.clicked.connect(self.navigate_to.emit)
            grid.addWidget(card, i // 2, i % 2)

        clayout.addLayout(grid)

        # ── Quick links
        ql_lbl = QLabel("QUICK ACCESS", content)
        ql_lbl.setStyleSheet(
            "font-size: 9px; font-weight: 800; color: #6366f1; letter-spacing: 1.5px;"
        )
        clayout.addWidget(ql_lbl)

        ql_row = QHBoxLayout()
        ql_row.setSpacing(10)
        for label, sid in [
            ("Records Browser", "records"),
            ("System Settings", "settings"),
            ("EXP 01 — Monohybrid", "exp01_monohybrid"),
            ("EXP 04 — Statistics", "exp04_statistical"),
            ("EXP 05 — Simulation", "exp05_simulation"),
        ]:
            btn = QuickLinkButton(label, content)
            btn.clicked.connect(lambda _, s=sid: self.navigate_to.emit(s))
            ql_row.addWidget(btn)
        clayout.addLayout(ql_row)
        clayout.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll)
