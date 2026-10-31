"""
UI Component: Hardware Status Bar and Desktop Simulation Panel
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
Light Theme Edition (v2.5)
"""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QComboBox, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from hardware.base import HardwareAdapter


class HardwareStatusWidget(QFrame):
    """
    Displays real-time hardware status, switch configurations, and input latency.
    Provides on-screen switch selectors for desktop simulation mode.
    """
    switch_changed_signal = pyqtSignal(int, str, str)  # (parent_idx, locus_char, genotype)

    def __init__(self, hardware_adapter: HardwareAdapter, parent=None):
        super().__init__(parent)
        self.adapter = hardware_adapter
        self.setObjectName("lab-card-telemetry")
        self.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px;")
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 5, 10, 5)
        self.main_layout.setSpacing(12)
        
        # Mode & Status Indicator Badge
        self.mode_label = QLabel(f"MODE: {self.adapter.hardware_mode.upper()}", self)
        self.mode_label.setStyleSheet(
            "background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; "
            "border-radius: 4px; padding: 2px 8px; font-weight: 700; font-size: 10px;"
        )
        self.main_layout.addWidget(self.mode_label)
        
        # Latency Display Badge
        self.latency_label = QLabel("LATENCY: < 1.0 ms", self)
        self.latency_label.setStyleSheet(
            "background-color: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; "
            "border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: 700;"
        )
        self.main_layout.addWidget(self.latency_label)
        
        # P1 Genotype Switch simulator
        p1_lbl = QLabel("P1 Switch (♀):", self)
        p1_lbl.setStyleSheet("font-weight: 600; color: #475569; font-size: 10px;")
        self.main_layout.addWidget(p1_lbl)
        
        self.p1_combo = QComboBox(self)
        self.p1_combo.addItems(["TT", "Tt", "tt"])
        self.p1_combo.currentIndexChanged.connect(self._on_p1_changed)
        self.main_layout.addWidget(self.p1_combo)

        # P2 Genotype Switch simulator
        p2_lbl = QLabel("P2 Switch (♂):", self)
        p2_lbl.setStyleSheet("font-weight: 600; color: #475569; font-size: 10px;")
        self.main_layout.addWidget(p2_lbl)
        
        self.p2_combo = QComboBox(self)
        self.p2_combo.addItems(["tt", "Tt", "TT"])
        self.p2_combo.currentIndexChanged.connect(self._on_p2_changed)
        self.main_layout.addWidget(self.p2_combo)
        
        self.main_layout.addStretch()

        # LED state pills
        self.led_pill_confirm = QLabel("CONFIRM", self)
        self.led_pill_confirm.setStyleSheet(
            "background-color: #f1f5f9; color: #64748b; border: 1px solid #cbd5e1; "
            "border-radius: 4px; padding: 2px 6px; font-size: 9px; font-weight: 600;"
        )
        self.main_layout.addWidget(self.led_pill_confirm)

        self.led_pill_correct = QLabel("CORRECT", self)
        self.led_pill_correct.setStyleSheet(
            "background-color: #f1f5f9; color: #64748b; border: 1px solid #cbd5e1; "
            "border-radius: 4px; padding: 2px 6px; font-size: 9px; font-weight: 600;"
        )
        self.main_layout.addWidget(self.led_pill_correct)

        self.led_pill_alert = QLabel("DISCREPANCY", self)
        self.led_pill_alert.setStyleSheet(
            "background-color: #f1f5f9; color: #64748b; border: 1px solid #cbd5e1; "
            "border-radius: 4px; padding: 2px 6px; font-size: 9px; font-weight: 600;"
        )
        self.main_layout.addWidget(self.led_pill_alert)

        # Connect adapter signals
        self.adapter.hardware_latency.connect(self._update_latency)
        self.adapter.led_state_changed.connect(self._update_led)

    def _on_p1_changed(self):
        geno = self.p1_combo.currentText()
        self.switch_changed_signal.emit(1, 'T', geno)

    def _on_p2_changed(self):
        geno = self.p2_combo.currentText()
        self.switch_changed_signal.emit(2, 'T', geno)

    def set_switch_choices(self, locus_choices: list):
        self.p1_combo.blockSignals(True)
        self.p2_combo.blockSignals(True)
        self.p1_combo.clear()
        self.p2_combo.clear()
        self.p1_combo.addItems(locus_choices)
        self.p2_combo.addItems(locus_choices)
        self.p1_combo.blockSignals(False)
        self.p2_combo.blockSignals(False)

    def _update_latency(self, latency_ms: float):
        if latency_ms < 15.0:
            bg, text, border = "#f0fdf4", "#15803d", "#bbf7d0"
        elif latency_ms < 50.0:
            bg, text, border = "#fffbeb", "#b45309", "#fde68a"
        else:
            bg, text, border = "#fef2f2", "#b91c1c", "#fecaca"
        self.latency_label.setText(f"LATENCY: {latency_ms:.1f} ms")
        self.latency_label.setStyleSheet(
            f"background-color: {bg}; color: {text}; border: 1px solid {border}; "
            f"border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: 700;"
        )

    def _update_led(self, name: str, state: bool):
        inactive_style = (
            "background-color: #f1f5f9; color: #64748b; border: 1px solid #cbd5e1; "
            "border-radius: 4px; padding: 2px 6px; font-size: 9px; font-weight: 600;"
        )
        if name == "input_confirmed":
            self.led_pill_confirm.setStyleSheet(
                "background-color: #2563eb; color: #ffffff; border-radius: 4px; padding: 2px 6px; font-size: 9px; font-weight: 700;"
                if state else inactive_style
            )
        elif name == "prediction_correct":
            self.led_pill_correct.setStyleSheet(
                "background-color: #10b981; color: #ffffff; border-radius: 4px; padding: 2px 6px; font-size: 9px; font-weight: 700;"
                if state else inactive_style
            )
        elif name == "prediction_inconsistent":
            self.led_pill_alert.setStyleSheet(
                "background-color: #ef4444; color: #ffffff; border-radius: 4px; padding: 2px 6px; font-size: 9px; font-weight: 700;"
                if state else inactive_style
            )
