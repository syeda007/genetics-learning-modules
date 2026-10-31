"""
UI Component: Cross Diagram Visualizer
Shows a live animated P × P → F1 genetic cross diagram with gamete bubbles.
"""
import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF


class CrossDiagramWidget(QWidget):
    """
    Animated cross diagram: draws two parent nodes, gamete clouds, and offspring row.
    Visually communicates the genetic cross without walls of text.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 180)
        self.p1_label = "Tt"
        self.p2_label = "Tt"
        self.gametes_p1 = ["T", "t"]
        self.gametes_p2 = ["T", "t"]
        self.offspring = ["TT", "Tt", "Tt", "tt"]
        self.ratios = {"Tall": "3", "Dwarf": "1"}
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def set_cross(self, p1: str, p2: str, gametes_p1: list, gametes_p2: list,
                  offspring: list, ratios: dict):
        self.p1_label = p1
        self.p2_label = p2
        self.gametes_p1 = gametes_p1
        self.gametes_p2 = gametes_p2
        self.offspring = offspring
        self.ratios = ratios
        self.update()

    def _tick(self):
        self._phase = (self._phase + 0.05) % (2 * math.pi)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = float(self.width()), float(self.height())

        # Background
        p.fillRect(self.rect(), QColor(248, 250, 252))

        # ── Layout constants ──────────────────────────────────────
        node_r = 28.0
        p1_cx, p1_cy = w * 0.22, h * 0.22
        p2_cx, p2_cy = w * 0.78, h * 0.22
        mid_x, mid_y = w * 0.50, h * 0.22
        gamete_y = h * 0.52
        off_y = h * 0.80

        # ── Parent nodes ─────────────────────────────────────────
        for cx, cy, label, col in [
            (p1_cx, p1_cy, self.p1_label, QColor(37, 99, 235)),
            (p2_cx, p2_cy, self.p2_label, QColor(124, 58, 237)),
        ]:
            grad = QLinearGradient(cx - node_r, cy - node_r, cx + node_r, cy + node_r)
            grad.setColorAt(0, col.lighter(140))
            grad.setColorAt(1, col)
            p.setPen(QPen(col.darker(130), 1.5))
            p.setBrush(QBrush(grad))
            p.drawEllipse(QPointF(cx, cy), node_r, node_r)
            p.setPen(QColor(255, 255, 255))
            p.setFont(QFont("Segoe UI", 10, QFont.Bold))
            p.drawText(QRectF(cx - node_r, cy - node_r, node_r * 2, node_r * 2),
                       Qt.AlignCenter, label)

        # × symbol in middle
        p.setPen(QPen(QColor(100, 116, 139), 1))
        p.setFont(QFont("Segoe UI", 14, QFont.Bold))
        p.drawText(QRectF(mid_x - 12, p1_cy - 14, 24, 28), Qt.AlignCenter, "×")

        # ── Animated connector lines (parent → gametes) ───────────
        dash_pen = QPen(QColor(148, 163, 184), 1.2, Qt.DashLine)
        dash_pen.setDashOffset(self._phase * 6)
        p.setPen(dash_pen)
        # Draw lines from parent to each gamete
        num_g = max(len(self.gametes_p1), len(self.gametes_p2))
        spacing = min(40.0, w * 0.15)
        g_centers = []
        for gi, (g1, g2) in enumerate(zip(self.gametes_p1, self.gametes_p2)):
            offset = (gi - (len(self.gametes_p1) - 1) / 2.0) * spacing
            gx1 = p1_cx + offset
            gx2 = p2_cx + offset
            p.drawLine(QPointF(p1_cx, p1_cy + node_r), QPointF(gx1, gamete_y - 12))
            p.drawLine(QPointF(p2_cx, p2_cy + node_r), QPointF(gx2, gamete_y - 12))
            g_centers.append(((gx1, gamete_y), g1, QColor(37, 99, 235)))
            g_centers.append(((gx2, gamete_y), g2, QColor(124, 58, 237)))

        # ── Gamete bubbles ────────────────────────────────────────
        gamete_r = 14.0
        for (gx, gy), label, col in g_centers:
            # Pulse animation
            pulse = math.sin(self._phase + gx) * 1.5
            r = gamete_r + pulse
            p.setPen(QPen(col, 1.2))
            p.setBrush(QBrush(QColor(col.red(), col.green(), col.blue(), 50)))
            p.drawEllipse(QPointF(gx, gy), r, r)
            p.setPen(col)
            p.setFont(QFont("Segoe UI", 8, QFont.Bold))
            p.drawText(QRectF(gx - r, gy - r, r * 2, r * 2), Qt.AlignCenter, label)

        # ── Offspring row ─────────────────────────────────────────
        n_off = len(self.offspring)
        if n_off:
            off_spacing = min(38.0, (w - 20) / max(n_off, 1))
            off_start = w / 2 - (n_off - 1) * off_spacing / 2

            # Arrow from gamete row to offspring
            arrow_pen = QPen(QColor(100, 116, 139), 1.5)
            p.setPen(arrow_pen)
            p.drawLine(QPointF(w / 2, gamete_y + gamete_r + 4), QPointF(w / 2, off_y - 15))
            # arrowhead
            p.drawLine(QPointF(w / 2, off_y - 15), QPointF(w / 2 - 5, off_y - 22))
            p.drawLine(QPointF(w / 2, off_y - 15), QPointF(w / 2 + 5, off_y - 22))

            off_colors = [
                QColor(16, 185, 129),  # green dominant
                QColor(16, 185, 129),
                QColor(16, 185, 129),
                QColor(239, 68, 68),   # red recessive
            ]
            for oi, geno in enumerate(self.offspring):
                ox = off_start + oi * off_spacing
                col = off_colors[min(oi, len(off_colors) - 1)]
                p.setPen(QPen(col, 1.2))
                p.setBrush(QBrush(QColor(col.red(), col.green(), col.blue(), 40)))
                p.drawRoundedRect(QRectF(ox - 16, off_y - 12, 32, 22), 5, 5)
                p.setPen(col.darker(120))
                p.setFont(QFont("Segoe UI", 8, QFont.Bold))
                p.drawText(QRectF(ox - 16, off_y - 12, 32, 22), Qt.AlignCenter, geno)

        # ── Ratio legend (bottom strip) ───────────────────────────
        if self.ratios:
            ratio_str = " : ".join(f"{v} {k}" for k, v in self.ratios.items())
            p.setPen(QColor(71, 85, 105))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(QRectF(0, h - 18, w, 16), Qt.AlignCenter, ratio_str)

        p.end()
