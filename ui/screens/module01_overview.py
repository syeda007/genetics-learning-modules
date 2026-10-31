"""
UI Screen: Module 01 Experiment Hub — Visual-First v3.0
Bold card grid with color-coded experiment tiles.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QLinearGradient, QColor


class Module01OverviewScreen(QWidget):
    navigate_to = pyqtSignal(str)

    EXPERIMENTS = [
        ("exp01_monohybrid", "01", "Monohybrid Inheritance", "🌱",
         "Single locus · TT × tt · Punnett square · 3:1 ratio",
         "#4f46e5", "#eef2ff"),
        ("exp02_dihybrid", "02", "Dihybrid Inheritance", "🌿",
         "Two loci · AaBb × AaBb · 4×4 matrix · 9:3:3:1",
         "#7c3aed", "#fdf4ff"),
        ("exp03_testcross", "03", "Test Cross & Zygosity", "🔍",
         "AA vs Aa · Backcross with aa · Sample offspring",
         "#0ea5e9", "#f0f9ff"),
        ("exp04_statistical", "04", "Chi-Square Validation", "📐",
         "χ² goodness-of-fit · Mendel's actual seed data · p-value",
         "#059669", "#f0fdf4"),
        ("exp05_simulation", "05", "Population Simulation", "🧬",
         "Stochastic sampling · N = 20 → 5000 · Drift",
         "#f59e0b", "#fffbeb"),
        ("exp06_evaluation_ai", "06", "Offline AI Evaluator", "🤖",
         "Student error diagnosis · Decision Tree · ≤2ms",
         "#e11d48", "#fff1f2"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(14)

        # ── Header ─────────────────────────────────────────────────────────
        header_h = QHBoxLayout()
        btn_back = QPushButton("← Dashboard", self)
        btn_back.setObjectName("btn-back")
        btn_back.setFixedWidth(100)
        btn_back.clicked.connect(lambda: self.navigate_to.emit("dashboard"))
        header_h.addWidget(btn_back)

        header_content = QVBoxLayout()
        header_content.setSpacing(2)
        t = QLabel("MODULE 01 · Mendelian Inheritance Lab Suite", self)
        t.setStyleSheet("font-size: 16px; font-weight: 900; color: #1e1b4b;")
        header_content.addWidget(t)
        s = QLabel("Select an experiment to begin. Each lab includes theory, visual Punnett matrix & real-time evaluation.", self)
        s.setStyleSheet("font-size: 10px; color: #6b7280; font-weight: 500;")
        header_content.addWidget(s)

        header_h.addLayout(header_content)
        header_h.addStretch()

        badge = QLabel("● 6 / 6 READY", self)
        badge.setStyleSheet(
            "background: #dcfce7; color: #166534; border-radius: 8px;"
            "padding: 5px 14px; font-size: 10px; font-weight: 800;"
        )
        header_h.addWidget(badge)
        main_layout.addLayout(header_h)

        # ── Separator ──────────────────────────────────────────────────────
        sep = QFrame(self)
        sep.setFixedHeight(2)
        sep.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4f46e5, stop:1 #10b981); border:none;")
        main_layout.addWidget(sep)

        # ── Scrollable Grid ────────────────────────────────────────────────
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        grid = QGridLayout(content)
        grid.setSpacing(12)
        grid.setContentsMargins(0, 4, 0, 4)

        for i, (screen_id, num, title, icon, desc, accent, bg) in enumerate(self.EXPERIMENTS):
            card = self._make_exp_card(screen_id, num, title, icon, desc, accent, bg, content)
            grid.addWidget(card, i // 2, i % 2)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _make_exp_card(self, screen_id, num, title, icon, desc, accent, bg, parent):
        card = QFrame(parent)
        card.setStyleSheet(
            f"QFrame {{ background-color: {bg}; border: 2px solid {accent}33;"
            f"border-left: 5px solid {accent}; border-radius: 14px; }}"
        )
        card.setMinimumHeight(130)
        card.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(14)

        # Left: big icon
        icon_frame = QFrame(card)
        icon_frame.setFixedSize(60, 60)
        icon_frame.setStyleSheet(
            f"background-color: {accent}; border-radius: 14px; border: none;"
        )
        icon_inner = QVBoxLayout(icon_frame)
        icon_inner.setContentsMargins(0, 0, 0, 0)
        il = QLabel(icon, icon_frame)
        il.setAlignment(Qt.AlignCenter)
        il.setStyleSheet("font-size: 28px; background: transparent;")
        icon_inner.addWidget(il)
        layout.addWidget(icon_frame)

        # Right: content
        right = QVBoxLayout()
        right.setSpacing(4)

        num_title = QHBoxLayout()
        num_lbl = QLabel(f"EXP {num}", card)
        num_lbl.setStyleSheet(
            f"background-color: {accent}; color: #ffffff; border-radius: 5px;"
            f"padding: 2px 8px; font-size: 9px; font-weight: 900; letter-spacing: 0.8px;"
        )
        num_title.addWidget(num_lbl)
        num_title.addSpacing(6)
        t_lbl = QLabel(title, card)
        t_lbl.setStyleSheet(
            f"font-size: 14px; font-weight: 800; color: #1e1b4b; background: transparent;"
        )
        num_title.addWidget(t_lbl)
        num_title.addStretch()
        right.addLayout(num_title)

        d_lbl = QLabel(desc, card)
        d_lbl.setWordWrap(True)
        d_lbl.setStyleSheet("color: #374151; font-size: 10px; font-weight: 500; background: transparent;")
        right.addWidget(d_lbl)

        btn = QPushButton("LAUNCH EXPERIMENT →", card)
        btn.setStyleSheet(
            f"background: {accent}; color: #ffffff; border: none; border-radius: 8px;"
            f"padding: 8px 18px; font-weight: 800; font-size: 10px; letter-spacing: 0.5px;"
        )
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda checked, s=screen_id: self.navigate_to.emit(s))
        btn.setFixedWidth(180)
        right.addWidget(btn)

        layout.addLayout(right)
        return card
