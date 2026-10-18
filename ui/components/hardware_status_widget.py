"""
UI Component: Hardware Status Bar and Desktop Simulation Panel
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
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
        self.setObjectName("lab-card")
        self.setStyleSheet("background-color: #0f1a30; border: 1px solid #223a66; border-radius: 4px;")
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(8, 4, 8, 4)
        self.main_layout.setSpacing(12)
        
        # Mode & Status Indicator
        self.mode_label = QLabel(f"MODE: {self.adapter.hardware_mode.upper()}", self)
        self.mode_label.setStyleSheet("font-weight: bold; color: #00b4d8; font-size: 10px;")
        self.main_layout.addWidget(self.mode_label)
        
        # Latency Display
        self.latency_label = QLabel("LATENCY: < 1.0 ms", self)
        self.latency_label.setStyleSheet("color: #2ec4b6; font-size: 10px; font-weight: bold;")
        self.main_layout.addWidget(self.latency_label)
        
        # P1 Genotype Switch simulator
        self.main_layout.addWidget(QLabel("P1 Switch:", self))
        self.p1_combo = QComboBox(self)
        self.p1_combo.addItems(["TT", "Tt", "tt"])
        self.p1_combo.currentIndexChanged.connect(self._on_p1_changed)
        self.main_layout.addWidget(self.p1_combo)

        # P2 Genotype Switch simulator
        self.main_layout.addWidget(QLabel("P2 Switch:", self))
        self.p2_combo = QComboBox(self)
        self.p2_combo.addItems(["tt", "Tt", "TT"])
        self.p2_combo.currentIndexChanged.connect(self._on_p2_changed)
        self.main_layout.addWidget(self.p2_combo)
        
        # LED state pills
        self.led_pill_confirm = QLabel("CONFIRM", self)
        self.led_pill_confirm.setStyleSheet("background-color: #1a2a44; color: #8da0b8; border-radius: 3px; padding: 2px 4px; font-size: 8px;")
        self.main_layout.addWidget(self.led_pill_confirm)

        self.led_pill_correct = QLabel("CORRECT", self)
        self.led_pill_correct.setStyleSheet("background-color: #1a2a44; color: #8da0b8; border-radius: 3px; padding: 2px 4px; font-size: 8px;")
        self.main_layout.addWidget(self.led_pill_correct)

        self.led_pill_alert = QLabel("DISCREPANCY", self)
        self.led_pill_alert.setStyleSheet("background-color: #1a2a44; color: #8da0b8; border-radius: 3px; padding: 2px 4px; font-size: 8px;")
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
        color = "#2ec4b6" if latency_ms < 15.0 else ("#f4a261" if latency_ms < 50.0 else "#e76f51")
        self.latency_label.setText(f"LATENCY: {latency_ms:.1f} ms")
        self.latency_label.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: bold;")

    def _update_led(self, name: str, state: bool):
        if name == "input_confirmed":
            self.led_pill_confirm.setStyleSheet(
                "background-color: #0077b6; color: #ffffff; border-radius: 3px; padding: 2px 4px; font-size: 8px; font-weight: bold;"
                if state else "background-color: #1a2a44; color: #8da0b8; border-radius: 3px; padding: 2px 4px; font-size: 8px;"
            )
        elif name == "prediction_correct":
            self.led_pill_correct.setStyleSheet(
                "background-color: #1b4d3e; color: #2ec4b6; border-radius: 3px; padding: 2px 4px; font-size: 8px; font-weight: bold;"
                if state else "background-color: #1a2a44; color: #8da0b8; border-radius: 3px; padding: 2px 4px; font-size: 8px;"
            )
        elif name == "prediction_inconsistent":
            self.led_pill_alert.setStyleSheet(
                "background-color: #5c1d24; color: #ff6b6b; border-radius: 3px; padding: 2px 4px; font-size: 8px; font-weight: bold;"
                if state else "background-color: #1a2a44; color: #8da0b8; border-radius: 3px; padding: 2px 4px; font-size: 8px;"
            )
