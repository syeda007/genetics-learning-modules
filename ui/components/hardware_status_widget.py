"""
UI Component: Hardware Status Bar (Minimal Light Edition v4.0)
"""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal
from hardware.base import HardwareAdapter


class HardwareStatusWidget(QFrame):
    switch_changed_signal = pyqtSignal(int, str, str)

    def __init__(self, hardware_adapter: HardwareAdapter, parent=None):
        super().__init__(parent)
        self.adapter = hardware_adapter
        self.setObjectName("telemetry-bar")
        self.setFixedHeight(36)
        self.setStyleSheet(
            "background-color: #ffffff; border-bottom: 1px solid #e8eaf2;"
        )

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 4, 12, 4)
        lay.setSpacing(10)

        # Mode pill
        self.mode_lbl = QLabel(f"MODE: {self.adapter.hardware_mode.upper()}", self)
        self.mode_lbl.setStyleSheet(
            "background: #eef2ff; color: #4f46e5; border: 1px solid #c7d2fe;"
            "border-radius: 4px; padding: 1px 8px; font-size: 9px; font-weight: 700;"
        )
        lay.addWidget(self.mode_lbl)

        self.latency_lbl = QLabel("LATENCY: <1 ms", self)
        self.latency_lbl.setStyleSheet(
            "background: #f0fdf4; color: #059669; border: 1px solid #bbf7d0;"
            "border-radius: 4px; padding: 1px 8px; font-size: 9px; font-weight: 700;"
        )
        lay.addWidget(self.latency_lbl)

        lay.addStretch()

        # P1 switch
        p1_lbl = QLabel("P1:", self)
        p1_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 600;")
        lay.addWidget(p1_lbl)
        self.p1_combo = QComboBox(self)
        self.p1_combo.addItems(["TT", "Tt", "tt"])
        self.p1_combo.setFixedWidth(72)
        self.p1_combo.currentIndexChanged.connect(self._on_p1)
        lay.addWidget(self.p1_combo)

        p2_lbl = QLabel("P2:", self)
        p2_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 600;")
        lay.addWidget(p2_lbl)
        self.p2_combo = QComboBox(self)
        self.p2_combo.addItems(["tt", "Tt", "TT"])
        self.p2_combo.setFixedWidth(72)
        self.p2_combo.currentIndexChanged.connect(self._on_p2)
        lay.addWidget(self.p2_combo)

        lay.addStretch()

        # LED pills (minimal)
        self.pill_correct = QLabel("CORRECT", self)
        self.pill_correct.setStyleSheet(
            "background: #f1f5f9; color: #94a3b8; border-radius: 4px;"
            "padding: 1px 7px; font-size: 9px; font-weight: 700;"
        )
        lay.addWidget(self.pill_correct)

        self.pill_error = QLabel("DISCREPANCY", self)
        self.pill_error.setStyleSheet(
            "background: #f1f5f9; color: #94a3b8; border-radius: 4px;"
            "padding: 1px 7px; font-size: 9px; font-weight: 700;"
        )
        lay.addWidget(self.pill_error)

        self.adapter.hardware_latency.connect(self._update_latency)
        self.adapter.led_state_changed.connect(self._update_led)

    def _on_p1(self):
        self.switch_changed_signal.emit(1, "T", self.p1_combo.currentText())

    def _on_p2(self):
        self.switch_changed_signal.emit(2, "T", self.p2_combo.currentText())

    def set_switch_choices(self, choices: list):
        for combo in (self.p1_combo, self.p2_combo):
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(choices)
            combo.blockSignals(False)

    def _update_latency(self, ms: float):
        self.latency_lbl.setText(f"LATENCY: {ms:.1f} ms")

    def _update_led(self, led_id: str, state: bool):
        if led_id == "prediction_correct":
            if state:
                self.pill_correct.setStyleSheet(
                    "background: #f0fdf4; color: #059669; border: 1px solid #bbf7d0;"
                    "border-radius: 4px; padding: 1px 7px; font-size: 9px; font-weight: 700;"
                )
            else:
                self.pill_correct.setStyleSheet(
                    "background: #f1f5f9; color: #94a3b8; border-radius: 4px;"
                    "padding: 1px 7px; font-size: 9px; font-weight: 700;"
                )
        elif led_id in ("prediction_inconsistent",):
            if state:
                self.pill_error.setStyleSheet(
                    "background: #fef2f2; color: #dc2626; border: 1px solid #fca5a5;"
                    "border-radius: 4px; padding: 1px 7px; font-size: 9px; font-weight: 700;"
                )
            else:
                self.pill_error.setStyleSheet(
                    "background: #f1f5f9; color: #94a3b8; border-radius: 4px;"
                    "padding: 1px 7px; font-size: 9px; font-weight: 700;"
                )
