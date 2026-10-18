"""
UI Component: Punnett Square Visualizer
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from genetics_engine.crosses import PunnettSquare


class PunnettSquareWidget(QWidget):
    """
    Renders an interactive, clearly formatted Punnett Square matrix.
    Supports 2x2 monohybrid and 4x4 dihybrid grids with responsive scaling for 800x480 / 1024x600 displays.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        
        self.title_label = QLabel("PUNNETT SQUARE COMBINATORIAL MATRIX", self)
        self.title_label.setObjectName("heading-secondary")
        self.title_label.setStyleSheet("font-weight: bold; color: #00b4d8; font-size: 11px;")
        self.layout.addWidget(self.title_label)
        
        self.table = QTableWidget(self)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

    def display_punnett_square(self, punnett_sq: PunnettSquare):
        rows = punnett_sq.num_rows
        cols = punnett_sq.num_cols
        
        self.table.clear()
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)
        
        # Headers: parent gametes
        col_headers = [f"♀ {gam} ({p:.2f})" for gam, p in punnett_sq.col_gametes]
        row_headers = [f"♂ {gam} ({p:.2f})" for gam, p in punnett_sq.row_gametes]
        
        self.table.setHorizontalHeaderLabels(col_headers)
        self.table.setVerticalHeaderLabels(row_headers)
        
        font_bold = QFont("Segoe UI", 10, QFont.Bold)
        
        for r in range(rows):
            for c in range(cols):
                cell = punnett_sq.grid[r][c]
                # Format cell text: Genotype on top, phenotype snippet on bottom
                text = f"{cell.zygote_genotype}\n({cell.probability * 100:.1f}%)"
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                item.setFont(font_bold)
                
                # Alternate soft background coloring to distinguish zygotes
                if "t" in cell.zygote_genotype or "a" in cell.zygote_genotype:
                    item.setBackground(QColor(22, 36, 68))
                else:
                    item.setBackground(QColor(18, 48, 76))
                
                item.setToolTip(f"Genotype: {cell.zygote_genotype}\nPhenotype: {cell.zygote_phenotype}\nProbability: {cell.probability:.4f}")
                self.table.setItem(r, c, item)
