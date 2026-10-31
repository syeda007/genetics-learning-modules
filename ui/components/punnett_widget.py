"""
UI Component: Dynamic Punnett Square Laboratory & Visual Phenotype Matrix
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
Inspired by classical genetics diagrams (Mendel's Peas) and high-tech biotech workstations.

CAPABILITIES:
- Custom QStyledItemDelegate rendering visual organism phenotypes (Yellow Round, Green Round, Yellow Wrinkled, Green Wrinkled, Tall, Dwarf).
- Visual phenotype icons inside every cell matching classical textbooks and university laboratory references.
- Graphical Phenotype Legend with fractional distribution (9/16, 3/16, 3/16, 1/16).
- Interactive cell inspection showing maternal (♀) and paternal (♂) allele origin.
- Highlighting filters: Homozygous Dominant, Heterozygous, Homozygous Recessive.
- Step-by-step mathematical & biological inheritance derivation.
"""
import math
from typing import Optional, Dict, List, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QFrame, QPushButton, QComboBox, QSplitter,
    QAbstractItemView, QStyledItemDelegate, QStyle
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRectF, QPointF
from PyQt5.QtGui import QColor, QFont, QBrush, QPainter, QPainterPath, QPen, QRadialGradient, QLinearGradient

from genetics_engine.crosses import PunnettSquare, PunnettCell


class VisualPunnettDelegate(QStyledItemDelegate):
    """
    Renders visual organism phenotypes (Seed color & texture, plant habit)
    directly inside each Punnett Square cell above the genotype text.
    """
    def paint(self, painter: QPainter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        rect = option.rect
        user_data = index.data(Qt.UserRole)
        
        # Draw cell background
        bg_brush = index.data(Qt.BackgroundRole)
        if bg_brush:
            painter.fillRect(rect, bg_brush)
        else:
            painter.fillRect(rect, QColor(255, 255, 255))

        # Selection or hover outline
        if option.state & QStyle.State_Selected:
            painter.setPen(QPen(QColor(37, 99, 235), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(rect.adjusted(1, 1, -1, -1))
        else:
            painter.setPen(QPen(QColor(226, 232, 240), 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(rect.adjusted(0, 0, -1, -1))

        if not user_data:
            painter.restore()
            super().paint(painter, option, index)
            return

        is_animating = user_data.get("is_animating", False)
        col_gamete = user_data.get("col_gamete", "")
        row_gamete = user_data.get("row_gamete", "")
        geno = user_data.get("genotype", "")
        pheno = user_data.get("phenotype", "")
        prob = user_data.get("prob", 0.0)

        cx = rect.center().x()
        cy = rect.top() + rect.height() * 0.36

        if is_animating:
            # Render gamete fusion text
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.setPen(QColor(37, 99, 235))
            txt = f"♀{col_gamete} × ♂{row_gamete}\nFusing..."
            painter.drawText(rect, Qt.AlignCenter, txt)
            painter.restore()
            return

        # ── Draw Visual Phenotype Glyph ──
        # Check phenotype category
        pheno_lower = pheno.lower()
        geno_lower = geno.lower()
        icon_radius = min(rect.width(), rect.height()) * 0.22
        icon_radius = max(8.0, min(icon_radius, 16.0))

        # Check Pea Seed Dihybrid (Yellow/Green, Round/Wrinkled)
        is_yellow = "yellow" in pheno_lower or ("a" not in geno_lower and "y" in geno_lower) or (geno.startswith("A") or geno.startswith("Y"))
        if "green" in pheno_lower:
            is_yellow = False
        if len(geno) >= 2 and geno[0] in ['a', 'y'] and geno[1] in ['a', 'y']:
            is_yellow = False

        is_wrinkled = "wrinkled" in pheno_lower or "constricted" in pheno_lower or (len(geno) == 4 and geno[2:].islower())
        is_monohybrid_pea = ("tall" in pheno_lower or "dwarf" in pheno_lower)

        if is_monohybrid_pea:
            # Monohybrid Stem & Leaves
            is_tall = "tall" in pheno_lower or geno.isupper() or (geno.startswith("T") and "t" in geno)
            stem_color = QColor(16, 185, 129) if is_tall else QColor(245, 158, 11)
            stem_h = icon_radius * 2.2 if is_tall else icon_radius * 1.1
            
            # Draw stem
            painter.setPen(QPen(stem_color, 2.5, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(QPointF(cx, cy + stem_h * 0.5), QPointF(cx, cy - stem_h * 0.5))
            
            # Draw leaves
            painter.setBrush(QBrush(stem_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(cx - 5, cy - stem_h * 0.2), 4, 2.5)
            painter.drawEllipse(QPointF(cx + 5, cy - stem_h * 0.3), 4, 2.5)
        else:
            # Dihybrid Seed
            # Base color: Yellow vs Green
            if is_yellow:
                c1 = QColor(254, 240, 138) # Light yellow
                c2 = QColor(234, 179, 8)   # Deep gold
                border_c = QColor(161, 98, 7)
            else:
                c1 = QColor(134, 239, 172) # Light green
                c2 = QColor(34, 197, 94)   # Emerald green
                border_c = QColor(21, 128, 61)

            if is_wrinkled:
                # Scalloped / Wrinkled seed shape (5 lobes)
                path = QPainterPath()
                points = 10
                for p in range(points):
                    angle = (p / points) * 2 * math.pi
                    r = icon_radius * (0.80 if p % 2 == 0 else 1.05)
                    px = cx + r * math.cos(angle)
                    py = cy + r * math.sin(angle)
                    if p == 0:
                        path.moveTo(px, py)
                    else:
                        path.lineTo(px, py)
                path.closeSubpath()

                grad = QRadialGradient(cx - 3, cy - 3, icon_radius * 1.2)
                grad.setColorAt(0.0, c1)
                grad.setColorAt(1.0, c2)
                painter.setBrush(QBrush(grad))
                painter.setPen(QPen(border_c, 1.2))
                painter.drawPath(path)
            else:
                # Smooth Round seed sphere with specular highlight
                grad = QRadialGradient(cx - icon_radius * 0.35, cy - icon_radius * 0.35, icon_radius * 1.3)
                grad.setColorAt(0.0, QColor(255, 255, 255, 230))
                grad.setColorAt(0.2, c1)
                grad.setColorAt(1.0, c2)
                painter.setBrush(QBrush(grad))
                painter.setPen(QPen(border_c, 1.2))
                painter.drawEllipse(QPointF(cx, cy), icon_radius, icon_radius)

        # ── Draw Genotype & Probability text below icon ──
        text_y = int(cy + icon_radius + 4)
        fg_color = index.data(Qt.ForegroundRole)
        painter.setPen(fg_color.color() if fg_color else QColor(15, 23, 42))

        # Genotype (Bold)
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        text_rect_geno = QRectF(rect.left(), text_y, rect.width(), 14)
        painter.drawText(text_rect_geno, Qt.AlignCenter, geno)

        # Percentage
        painter.setFont(QFont("Segoe UI", 7, QFont.Normal))
        painter.setPen(QColor(71, 85, 105))
        text_rect_prob = QRectF(rect.left(), text_y + 13, rect.width(), 12)
        painter.drawText(text_rect_prob, Qt.AlignCenter, f"{prob * 100:.1f}%")

        painter.restore()


class PunnettSquareWidget(QWidget):
    """
    Advanced interactive Punnett Square viewer with visual organism phenotypes,
    zygote allele origin inspection, zygosity highlighting, and graphical 9:3:3:1 legend.
    """
    cell_inspected = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_punnett: Optional[PunnettSquare] = None
        self.highlight_filter: str = "ALL"
        self.anim_progress: float = 1.0
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(25)
        self.anim_timer.timeout.connect(self._on_anim_tick)
        
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(6)

        # Top Controls Bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(6)
        
        self.title_label = QLabel("PUNNETT SQUARE COMBINATORIAL MATRIX & PHENOTYPE MAP", self)
        self.title_label.setObjectName("heading-secondary")
        self.title_label.setStyleSheet("font-weight: 800; color: #2563eb; font-size: 11px;")
        top_bar.addWidget(self.title_label)
        top_bar.addStretch()

        lbl_filter = QLabel("Highlight Filter:", self)
        lbl_filter.setStyleSheet("font-weight: 600; color: #475569; font-size: 10px;")
        top_bar.addWidget(lbl_filter)

        self.filter_combo = QComboBox(self)
        self.filter_combo.addItems([
            "All Zygotes",
            "Homozygous Dominant",
            "Heterozygous",
            "Homozygous Recessive"
        ])
        self.filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        top_bar.addWidget(self.filter_combo)

        self.btn_animate = QPushButton("⚡ Animate Fusion", self)
        self.btn_animate.setFixedHeight(26)
        self.btn_animate.setStyleSheet(
            "background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; "
            "border-radius: 4px; font-weight: 700; font-size: 10px; padding: 2px 10px;"
        )
        self.btn_animate.clicked.connect(self.start_fusion_animation)
        top_bar.addWidget(self.btn_animate)

        main_layout.addLayout(top_bar)

        # Graphical Phenotype Legend Panel (Matching Textbook Figure 2)
        self.legend_frame = QFrame(self)
        self.legend_frame.setObjectName("lab-card")
        self.legend_frame.setStyleSheet(
            "background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 4px;"
        )
        self.legend_layout = QHBoxLayout(self.legend_frame)
        self.legend_layout.setContentsMargins(8, 3, 8, 3)
        self.legend_layout.setSpacing(12)
        
        leg_title = QLabel("PHENOTYPIC RATIO BREAKDOWN:", self.legend_frame)
        leg_title.setStyleSheet("font-weight: 800; color: #0f172a; font-size: 10px;")
        self.legend_layout.addWidget(leg_title)
        
        self.legend_pills_container = QHBoxLayout()
        self.legend_pills_container.setSpacing(8)
        self.legend_layout.addLayout(self.legend_pills_container)
        self.legend_layout.addStretch()
        main_layout.addWidget(self.legend_frame)

        # Splitter: Table on top, Inspector and Step-by-Step below
        splitter = QSplitter(Qt.Vertical, self)

        # Matrix Table with Custom Visual Delegate
        self.table = QTableWidget(self)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setItemDelegate(VisualPunnettDelegate(self.table))
        self.table.itemClicked.connect(self._on_item_clicked)
        self.table.currentItemChanged.connect(self._on_current_item_changed)
        splitter.addWidget(self.table)

        # Inspector & Derivation Panel
        self.inspector_card = QFrame(self)
        self.inspector_card.setObjectName("lab-card")
        self.inspector_card.setStyleSheet(
            "background-color: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 6px; padding: 6px;"
        )
        insp_layout = QVBoxLayout(self.inspector_card)
        insp_layout.setContentsMargins(6, 4, 6, 4)
        insp_layout.setSpacing(4)

        insp_header = QLabel("ALLELE ORIGIN & ZYGOTE INSPECTOR", self.inspector_card)
        insp_header.setStyleSheet("color: #0d9488; font-weight: 800; font-size: 10px;")
        insp_layout.addWidget(insp_header)

        self.inspector_label = QLabel(
            "Click or keyboard-navigate to any cell in the Punnett Square to inspect parental gamete contributions.",
            self.inspector_card
        )
        self.inspector_label.setWordWrap(True)
        self.inspector_label.setStyleSheet("color: #334155; font-size: 10px;")
        insp_layout.addWidget(self.inspector_label)

        self.step_label = QLabel("", self.inspector_card)
        self.step_label.setWordWrap(True)
        self.step_label.setStyleSheet("color: #475569; font-size: 9px; line-height: 1.3;")
        insp_layout.addWidget(self.step_label)

        splitter.addWidget(self.inspector_card)
        splitter.setSizes([230, 90])

        main_layout.addWidget(splitter)

    def set_punnett_square(self, punnett_data: PunnettSquare):
        self.current_punnett = punnett_data
        self.anim_progress = 1.0
        self._populate_grid()
        self._update_phenotype_legend()
        self._update_step_derivation()

    display_punnett_square = set_punnett_square

    def _populate_grid(self):
        if not self.current_punnett:
            return

        ps = self.current_punnett
        rows = ps.num_rows
        cols = ps.num_cols

        self.table.clear()
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)

        # Headers
        col_headers = [f"♀ {gam} (P={p:.2f})" for gam, p in ps.col_gametes]
        row_headers = [f"♂ {gam} (P={p:.2f})" for gam, p in ps.row_gametes]
        self.table.setHorizontalHeaderLabels(col_headers)
        self.table.setVerticalHeaderLabels(row_headers)

        for r in range(rows):
            for c in range(cols):
                cell = ps.grid[r][c]
                is_match = self._cell_matches_filter(cell.zygote_genotype)

                item = QTableWidgetItem(cell.zygote_genotype)
                item.setTextAlignment(Qt.AlignCenter)

                # Cell styling
                bg_color, fg_color = self._get_cell_colors(cell.zygote_genotype, cell.zygote_phenotype, is_match)
                item.setBackground(QBrush(bg_color))
                item.setForeground(QBrush(fg_color))

                # Pass rich metadata to delegate
                user_payload = {
                    "genotype": cell.zygote_genotype,
                    "phenotype": cell.zygote_phenotype,
                    "prob": cell.probability,
                    "col_gamete": cell.col_gamete,
                    "row_gamete": cell.row_gamete,
                    "is_animating": (self.anim_progress < 1.0),
                    "is_match": is_match
                }
                item.setData(Qt.UserRole, user_payload)

                # Tooltip
                item.setToolTip(
                    f"Zygote Genotype: {cell.zygote_genotype}\n"
                    f"Phenotype: {cell.zygote_phenotype}\n"
                    f"Maternal Allele (♀): {cell.col_gamete}\n"
                    f"Paternal Allele (♂): {cell.row_gamete}\n"
                    f"Independent Probability: {cell.probability:.4f}"
                )
                self.table.setItem(r, c, item)

    def _update_phenotype_legend(self):
        """Builds the 9/16, 3/16, 3/16, 1/16 graphical legend matching textbooks."""
        # Clear existing legend pills
        while self.legend_pills_container.count():
            item = self.legend_pills_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.current_punnett:
            return

        ps = self.current_punnett
        total_cells = ps.num_rows * ps.num_cols

        # Group counts by phenotype
        pheno_counts = {}
        for r in range(ps.num_rows):
            for c in range(ps.num_cols):
                ph = ps.grid[r][c].zygote_phenotype
                pheno_counts[ph] = pheno_counts.get(ph, 0) + 1

        # Render each phenotype badge
        for ph, count in sorted(pheno_counts.items(), key=lambda x: -x[1]):
            fraction_str = f"{count}/{total_cells}"
            pct_str = f"{(count / total_cells) * 100:.1f}%"
            
            # Badge icon & color
            ph_lower = ph.lower()
            if "wrinkled" in ph_lower:
                icon_glyph = "🌼" if ("yellow" in ph_lower or "dominant" in ph_lower) else "☘️"
                bg_color = "#fefce8" if ("yellow" in ph_lower or "dominant" in ph_lower) else "#f0fdf4"
                text_color = "#854d0e" if ("yellow" in ph_lower or "dominant" in ph_lower) else "#166534"
            elif "green" in ph_lower:
                icon_glyph = "🟢"
                bg_color = "#f0fdf4"
                text_color = "#166534"
            elif "yellow" in ph_lower:
                icon_glyph = "🟡"
                bg_color = "#fefce8"
                text_color = "#854d0e"
            elif "dwarf" in ph_lower:
                icon_glyph = "🌱"
                bg_color = "#fffbeb"
                text_color = "#b45309"
            else:
                icon_glyph = "🌿"
                bg_color = "#ecfdf5"
                text_color = "#065f46"

            badge = QLabel(f"{icon_glyph} <b>{fraction_str}</b> {ph} ({pct_str})", self.legend_frame)
            badge.setStyleSheet(
                f"background-color: {bg_color}; color: {text_color}; border: 1px solid #cbd5e1; "
                f"border-radius: 4px; padding: 2px 8px; font-size: 10px;"
            )
            self.legend_pills_container.addWidget(badge)

    def _cell_matches_filter(self, geno: str) -> bool:
        if self.highlight_filter == "ALL":
            return True
        elif self.highlight_filter == "HOMO_DOM":
            return geno.isupper()
        elif self.highlight_filter == "HOMO_REC":
            return geno.islower()
        elif self.highlight_filter == "HETERO":
            return (not geno.isupper()) and (not geno.islower())
        return True

    def _get_cell_colors(self, geno: str, pheno: str, is_match: bool) -> Tuple[QColor, QColor]:
        if not is_match:
            return QColor(248, 250, 252), QColor(148, 163, 184)
            
        if geno.isupper():
            return QColor(236, 253, 245), QColor(6, 95, 70)
        elif geno.islower():
            return QColor(254, 242, 242), QColor(153, 27, 27)
        else:
            return QColor(239, 246, 255), QColor(30, 64, 175)

    def _on_filter_changed(self, idx: int):
        filters = ["ALL", "HOMO_DOM", "HETERO", "HOMO_REC"]
        self.highlight_filter = filters[idx]
        self._populate_grid()

    def start_fusion_animation(self):
        self.anim_progress = 0.0
        self.btn_animate.setEnabled(False)
        self.anim_timer.start()

    def _on_anim_tick(self):
        self.anim_progress += 0.10
        if self.anim_progress >= 1.0:
            self.anim_progress = 1.0
            self.anim_timer.stop()
            self.btn_animate.setEnabled(True)
        self._populate_grid()

    def _on_item_clicked(self, item: QTableWidgetItem):
        self._inspect_cell(item.row(), item.column())

    def _on_current_item_changed(self, current: Optional[QTableWidgetItem], previous: Optional[QTableWidgetItem]):
        if current:
            self._inspect_cell(current.row(), current.column())

    def _inspect_cell(self, row: int, col: int):
        if not self.current_punnett:
            return
        if row < 0 or row >= self.current_punnett.num_rows or col < 0 or col >= self.current_punnett.num_cols:
            return

        cell = self.current_punnett.grid[row][col]
        geno = cell.zygote_genotype
        
        if geno.isupper():
            zygosity = "Homozygous Dominant (True-Breeding)"
            tag_color = "#059669"
        elif geno.islower():
            zygosity = "Homozygous Recessive"
            tag_color = "#dc2626"
        else:
            zygosity = "Heterozygous Carrier"
            tag_color = "#2563eb"

        insp_text = (
            f"<b>Selected Cell (Row {row+1}, Col {col+1}):</b> Genotype: <b style='font-size: 11px;'>{geno}</b> | "
            f"Class: <span style='color: {tag_color}; font-weight: bold;'>{zygosity}</span><br>"
            f"• <b>Maternal Origin (♀):</b> Allele '{cell.col_gamete}' (Gamete probability: {cell.probability**0.5:.2f})<br>"
            f"• <b>Paternal Origin (♂):</b> Allele '{cell.row_gamete}' (Gamete probability: {cell.probability**0.5:.2f})<br>"
            f"• <b>Cell Fertilization Probability:</b> P = {cell.probability:.4f} ({cell.probability*100:.2f}%)<br>"
            f"• <b>Expressed Phenotype:</b> {cell.zygote_phenotype}"
        )
        self.inspector_label.setText(insp_text)

        payload = {
            "row": row, "col": col, "genotype": geno,
            "phenotype": cell.zygote_phenotype,
            "maternal_gamete": cell.col_gamete,
            "paternal_gamete": cell.row_gamete,
            "probability": cell.probability,
            "zygosity": zygosity
        }
        self.cell_inspected.emit(payload)

    def _update_step_derivation(self):
        if not self.current_punnett:
            return
        ps = self.current_punnett
        total_cells = ps.num_rows * ps.num_cols
        
        geno_counts = {}
        for r in range(ps.num_rows):
            for c in range(ps.num_cols):
                g = ps.grid[r][c].zygote_genotype
                geno_counts[g] = geno_counts.get(g, 0) + 1

        geno_str = ", ".join(f"{g}: {cnt}/{total_cells} ({(cnt/total_cells)*100:.1f}%)" for g, cnt in sorted(geno_counts.items()))

        derivation = (
            f"<b>Step-by-Step Inheritance Derivation:</b><br>"
            f"1. <i>Gametogenesis:</i> Parental diploid homologues segregated during Anaphase I, producing {ps.num_cols} ♀ and {ps.num_rows} ♂ gamete classes.<br>"
            f"2. <i>Independent Assortment:</i> Fertilization represents the Cartesian product ({ps.num_rows} × {ps.num_cols} = {total_cells} equiprobable combinations).<br>"
            f"3. <i>Genotypic Distribution:</i> {geno_str}."
        )
        self.step_label.setText(derivation)
