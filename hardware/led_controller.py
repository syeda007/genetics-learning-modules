"""
Hardware Abstraction Layer: LED Indicator Controller
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from typing import Optional
from PyQt5.QtCore import QObject, QTimer
from hardware.base import HardwareAdapter


class LedController(QObject):
    """
    Coordinates scientifically meaningful optical feedback to students via LEDs.
    States:
        - input_confirmed: Parent genotype selection latched.
        - prediction_correct: Student hypothesis verified by genetics engine.
        - prediction_inconsistent: Mathematical/biological discrepancy detected.
        - experiment_complete: Dataset saved and exported.
        - hardware_error: Invalid switch combination or communication fault.
    """
    def __init__(self, adapter: HardwareAdapter, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.adapter = adapter

    def trigger_input_confirmed(self, pulse_ms: int = 400):
        self.adapter.set_led("input_confirmed", True)
        QTimer.singleShot(pulse_ms, lambda: self.adapter.set_led("input_confirmed", False))

    def trigger_prediction_result(self, is_correct: bool, pulse_ms: int = 1200):
        if is_correct:
            self.adapter.set_led("prediction_correct", True)
            self.adapter.set_led("prediction_inconsistent", False)
            QTimer.singleShot(pulse_ms, lambda: self.adapter.set_led("prediction_correct", False))
        else:
            self.adapter.set_led("prediction_inconsistent", True)
            self.adapter.set_led("prediction_correct", False)
            QTimer.singleShot(pulse_ms, lambda: self.adapter.set_led("prediction_inconsistent", False))

    def trigger_experiment_complete(self, pulse_ms: int = 800):
        self.adapter.set_led("experiment_complete", True)
        QTimer.singleShot(pulse_ms, lambda: self.adapter.set_led("experiment_complete", False))

    def trigger_error(self, pulse_ms: int = 1500):
        self.adapter.set_led("hardware_error", True)
        QTimer.singleShot(pulse_ms, lambda: self.adapter.set_led("hardware_error", False))

    def reset_all(self):
        for name in ["input_confirmed", "prediction_correct", "prediction_inconsistent", "experiment_complete", "hardware_error"]:
            self.adapter.set_led(name, False)
