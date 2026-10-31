"""
UI Component: Interactive Biotech DNA Helix & Locus Map Widget
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
Inspired by high-tech genome analysis workstations.

SCIENTIFIC & VISUAL CAPABILITIES:
- Smooth vector QPainter rendering of the DNA double helix.
- Highlights target genetic loci (Locus A, Locus B, alleles) with glowing chromatic rungs.
- HUD bracket callouts displaying locus name, dominance state, and chromosomal coordinates.
- Fully offline, vector-rendered at 30+ FPS on Raspberry Pi 3 and desktop.
"""
import math
from typing import Dict, List, Optional
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath, QLinearGradient
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF


class DnaHelixWidget(QWidget):
    """
    Renders an animated, luminous DNA double helix with labeled genetic loci
    and futuristic HUD callouts.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220, 260)
        self.phase = 0.0
        self.loci = [
            {"id": "LOC-A", "name": "Locus A (T/t)", "state": "ACTIVE", "color": QColor(0, 229, 255), "y_pct": 0.28},
            {"id": "LOC-B", "name": "Locus B (R/r)", "state": "UNLINKED", "color": QColor(255, 183, 3), "y_pct": 0.65},
        ]
        
        # 35 fps animation
        self.timer = QTimer(self)
        self.timer.setInterval(28)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start()

    def set_loci_info(self, locus_a_name: str, locus_a_state: str,
                      locus_b_name: Optional[str] = None, locus_b_state: Optional[str] = None):
        self.loci[0]["name"] = locus_a_name
        self.loci[0]["state"] = locus_a_state
        if locus_b_name:
            if len(self.loci) < 2:
                self.loci.append({"id": "LOC-B", "name": locus_b_name, "state": locus_b_state or "UNLINKED", "color": QColor(255, 183, 3), "y_pct": 0.65})
            else:
                self.loci[1]["name"] = locus_b_name
                self.loci[1]["state"] = locus_b_state or "UNLINKED"
        elif len(self.loci) > 1:
            self.loci = [self.loci[0]]
        self.update()

    def _on_tick(self):
        self.phase += 0.04
        if self.phase > 2 * math.pi:
            self.phase -= 2 * math.pi
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = float(self.width())
        h = float(self.height())

        # Dark biotech viewport background with subtle grid
        painter.fillRect(self.rect(), QColor(8, 14, 26))

        # Tech grid lines
        grid_pen = QPen(QColor(20, 32, 54), 1)
        painter.setPen(grid_pen)
        for y in range(0, int(h), 32):
            painter.drawLine(0, y, int(w), y)
        for x in range(0, int(w), 32):
            painter.drawLine(x, 0, x, int(h))

        # Center axis of helix
        center_x = w * 0.38
        amplitude = min(w * 0.18, 45.0)
        num_rungs = 24
        step_y = h / float(num_rungs)

        # 1. Draw base-pair rungs and strands
        for i in range(num_rungs):
            y = (i + 0.5) * step_y
            theta = self.phase + i * 0.35
            
            x1 = center_x + amplitude * math.sin(theta)
            x2 = center_x - amplitude * math.sin(theta)
            
            # Depth cueing using cosine
            depth = math.cos(theta) # -1.0 (back) to +1.0 (front)
            alpha = int(120 + 135 * (depth + 1.0) / 2.0)
            rung_thick = 1.5 + 1.5 * (depth + 1.0) / 2.0

            # Check if this rung is near a labeled locus
            is_locus_a = abs(y / h - 0.28) < 0.08
            is_locus_b = len(self.loci) > 1 and abs(y / h - 0.65) < 0.08

            if is_locus_a:
                rung_color = QColor(0, 229, 255, alpha) # Glowing Cyan
                rung_thick += 1.5
            elif is_locus_b:
                rung_color = QColor(255, 183, 3, alpha) # Glowing Amber
                rung_thick += 1.5
            else:
                # Alternating base pairs: Adenine-Thymine (Green) / Guanine-Cytosine (Indigo)
                if i % 2 == 0:
                    rung_color = QColor(0, 255, 157, int(alpha * 0.75))
                else:
                    rung_color = QColor(138, 92, 246, int(alpha * 0.75))

            # Draw rung
            painter.setPen(QPen(rung_color, rung_thick))
            painter.drawLine(QPointF(x1, y), QPointF(x2, y))

            # Draw phosphodiester backbone node
            node_r = 2.5 + 1.5 * (depth + 1.0) / 2.0
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(220, 240, 255, alpha)))
            painter.drawEllipse(QPointF(x1, y), node_r, node_r)
            
            painter.setBrush(QBrush(QColor(220, 240, 255, int(100 + 100 * (-depth + 1.0) / 2.0))))
            painter.drawEllipse(QPointF(x2, y), node_r * 0.8, node_r * 0.8)

        # 2. Draw HUD Callout Brackets on loci
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        for locus in self.loci:
            target_y = h * locus["y_pct"]
            callout_x = center_x + amplitude + 16
            
            # HUD Leader line
            leader_pen = QPen(locus["color"], 1.5, Qt.SolidLine)
            painter.setPen(leader_pen)
            
            # Bracket lines
            p1 = QPointF(center_x + amplitude * 0.7, target_y)
            p2 = QPointF(callout_x, target_y)
            p3 = QPointF(callout_x + 8, target_y - 8)
            p4 = QPointF(w - 12, target_y - 8)
            
            painter.drawPolyline([p1, p2, p3, p4])
            
            # Reticle dot on chromosome
            painter.setBrush(QBrush(locus["color"]))
            painter.drawEllipse(p1, 3.5, 3.5)

            # HUD text card
            painter.setPen(QPen(locus["color"]))
            painter.drawText(int(callout_x + 10), int(target_y - 12), locus["name"])
            
            # State Pill
            state_bg = QColor(locus["color"].red(), locus["color"].green(), locus["color"].blue(), 45)
            pill_rect = QRectF(callout_x + 10, target_y - 2, 72, 14)
            painter.setPen(QPen(locus["color"], 1))
            painter.setBrush(QBrush(state_bg))
            painter.drawRoundedRect(pill_rect, 3, 3)
            
            painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
            painter.drawText(pill_rect, Qt.AlignCenter, locus["state"])
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))

        # Frame border
        painter.setPen(QPen(QColor(30, 48, 80), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(0, 0, int(w) - 1, int(h) - 1)
        
        # Corner brackets
        bracket_pen = QPen(QColor(0, 229, 255), 2)
        painter.setPen(bracket_pen)
        bracket_len = 8
        # Top-left
        painter.drawLine(2, 2, 2 + bracket_len, 2)
        painter.drawLine(2, 2, 2, 2 + bracket_len)
        # Top-right
        painter.drawLine(int(w) - 3, 2, int(w) - 3 - bracket_len, 2)
        painter.drawLine(int(w) - 3, 2, int(w) - 3, 2 + bracket_len)
        # Bottom-left
        painter.drawLine(2, int(h) - 3, 2 + bracket_len, int(h) - 3)
        painter.drawLine(2, int(h) - 3, 2, int(h) - 3 - bracket_len)
        # Bottom-right
        painter.drawLine(int(w) - 3, int(h) - 3, int(w) - 3 - bracket_len, int(h) - 3)
        painter.drawLine(int(w) - 3, int(h) - 3, int(w) - 3, int(h) - 3 - bracket_len)
