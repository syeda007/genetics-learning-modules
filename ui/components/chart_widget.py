"""
UI Component: Lightweight Scientific 2D Bar Chart (Expected vs. Observed)
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF
from typing import Dict, List, Optional


class ScientificBarChartWidget(QWidget):
    """
    Ultra-lightweight QPainter 2D comparative bar chart.
    Renders Expected vs Observed distributions with zero third-party rendering overhead.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.categories: List[str] = []
        self.expected_values: List[float] = []
        self.observed_values: List[float] = []
        self.setMinimumHeight(150)

    def set_data(self, categories: List[str], expected: List[float], observed: List[float]):
        self.categories = categories
        self.expected_values = expected
        self.observed_values = observed
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        w = rect.width()
        h = rect.height()
        
        # Fill background
        painter.fillRect(rect, QColor(11, 19, 37))
        
        if not self.categories or not self.expected_values or not self.observed_values:
            painter.setPen(QColor(141, 160, 184))
            painter.drawText(rect, Qt.AlignCenter, "No experimental data loaded for graphical comparison.")
            return

        # Margins
        left = 50
        right = 20
        top = 35
        bottom = 40
        plot_w = w - left - right
        plot_h = h - top - bottom
        
        if plot_w <= 0 or plot_h <= 0:
            return
            
        max_val = max(max(self.expected_values), max(self.observed_values), 1.0) * 1.15
        
        # Draw Axes
        axis_pen = QPen(QColor(42, 61, 102), 1)
        painter.setPen(axis_pen)
        painter.drawLine(left, top, left, top + plot_h)
        painter.drawLine(left, top + plot_h, left + plot_w, top + plot_h)
        
        # Gridlines (3 lines)
        grid_pen = QPen(QColor(24, 38, 66), 1, Qt.DashLine)
        font_axis = QFont("Segoe UI", 8)
        painter.setFont(font_axis)
        for i in range(1, 4):
            val = max_val * (i / 4.0)
            y = top + plot_h - (val / max_val * plot_h)
            painter.setPen(grid_pen)
            painter.drawLine(left, int(y), left + plot_w, int(y))
            painter.setPen(QColor(141, 160, 184))
            painter.drawText(QRectF(5, y - 8, left - 10, 16), Qt.AlignRight | Qt.AlignVCenter, f"{val:.0f}")

        # Legend at top
        font_legend = QFont("Segoe UI", 9, QFont.Bold)
        painter.setFont(font_legend)
        # Expected Box
        painter.fillRect(left, 10, 12, 12, QColor(0, 180, 216))
        painter.setPen(QColor(224, 230, 237))
        painter.drawText(left + 16, 21, "Theoretical Expected")
        
        # Observed Box
        painter.fillRect(left + 150, 10, 12, 12, QColor(46, 196, 182))
        painter.drawText(left + 166, 21, "Observed Sample")

        # Draw Bars
        k = len(self.categories)
        group_width = plot_w / k
        bar_width = min(28.0, group_width * 0.35)
        
        for idx, cat in enumerate(self.categories):
            center_x = left + idx * group_width + group_width / 2.0
            
            exp_val = self.expected_values[idx]
            obs_val = self.observed_values[idx]
            
            exp_bar_h = (exp_val / max_val) * plot_h
            obs_bar_h = (obs_val / max_val) * plot_h
            
            # Expected bar (Cyan)
            x_exp = center_x - bar_width - 2
            y_exp = top + plot_h - exp_bar_h
            painter.fillRect(QRectF(x_exp, y_exp, bar_width, exp_bar_h), QColor(0, 180, 216))
            
            # Observed bar (Mint)
            x_obs = center_x + 2
            y_obs = top + plot_h - obs_bar_h
            painter.fillRect(QRectF(x_obs, y_obs, bar_width, obs_bar_h), QColor(46, 196, 182))
            
            # Category label below
            painter.setPen(QColor(224, 230, 237))
            font_cat = QFont("Segoe UI", 8)
            painter.setFont(font_cat)
            label_rect = QRectF(left + idx * group_width, top + plot_h + 4, group_width, bottom - 4)
            painter.drawText(label_rect, Qt.AlignHCenter | Qt.AlignTop, cat)
            
            # Values above bars
            font_val = QFont("Segoe UI", 7)
            painter.setFont(font_val)
            painter.setPen(QColor(0, 180, 216))
            painter.drawText(QRectF(x_exp - 5, y_exp - 14, bar_width + 10, 12), Qt.AlignCenter, f"{exp_val:.0f}")
            painter.setPen(QColor(46, 196, 182))
            painter.drawText(QRectF(x_obs - 5, y_obs - 14, bar_width + 10, 12), Qt.AlignCenter, f"{obs_val:.0f}")
