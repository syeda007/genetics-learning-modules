"""
UI Screen: System Settings & Hardware Diagnostics
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QTextEdit, QScrollArea, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal

from hardware.base import HardwareAdapter
from hardware.led_controller import LedController

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "config.json")


class SettingsScreen(QWidget):
    navigate_to = pyqtSignal(str)
    resolution_changed = pyqtSignal(int, int, bool) # (width, height, is_fullscreen)

    def __init__(self, hardware_adapter: HardwareAdapter, led_controller: LedController, parent=None):
        super().__init__(parent)
        self.adapter = hardware_adapter
        self.led_controller = led_controller
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(8)

        # Header bar
        header_h = QHBoxLayout()
        btn_back = QPushButton("← BACK TO DASHBOARD", self)
        btn_back.clicked.connect(lambda: self.navigate_to.emit("dashboard"))
        header_h.addWidget(btn_back)
        
        title = QLabel("SYSTEM SETTINGS & HARDWARE DIAGNOSTICS", self)
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffffff;")
        header_h.addWidget(title)
        header_h.addStretch()
        main_layout.addLayout(header_h)

        splitter = QSplitter(Qt.Horizontal, self)

        # LEFT PANEL: Controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(6)

        # Display Resolution Card
        disp_card = QFrame(left_widget)
        disp_card.setObjectName("lab-card")
        d_layout = QVBoxLayout(disp_card)
        d_layout.setSpacing(4)
        d_title = QLabel("DISPLAY RESOLUTION & KIOSK GEOMETRY", disp_card)
        d_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        d_layout.addWidget(d_title)

        d_layout.addWidget(QLabel("Target Display Resolution:", disp_card))
        self.res_combo = QComboBox(disp_card)
        self.res_combo.addItems([
            "1024 × 600 (7-inch Landscape High-Res)",
            "800 × 480 (7-inch Standard HDMI)",
            "Fullscreen (Kiosk Research Mode)"
        ])
        d_layout.addWidget(self.res_combo)

        btn_apply_res = QPushButton("Apply Display Geometry", disp_card)
        btn_apply_res.setObjectName("btn-primary")
        btn_apply_res.clicked.connect(self._apply_resolution)
        d_layout.addWidget(btn_apply_res)
        left_layout.addWidget(disp_card)

        # Hardware Mode Card
        hw_card = QFrame(left_widget)
        hw_card.setObjectName("lab-card")
        h_layout = QVBoxLayout(hw_card)
        h_layout.setSpacing(4)
        h_title = QLabel("HARDWARE SUBSYSTEM & OPERATING MODE", hw_card)
        h_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        h_layout.addWidget(h_title)

        self.mode_status_lbl = QLabel(f"Active Mode: {self.adapter.hardware_mode.upper()}", hw_card)
        self.mode_status_lbl.setStyleSheet("font-weight: bold; color: #2ec4b6; font-size: 10px;")
        h_layout.addWidget(self.mode_status_lbl)

        btn_reconnect = QPushButton("Re-probe Hardware Subsystem", hw_card)
        btn_reconnect.clicked.connect(self._reprobe_hardware)
        h_layout.addWidget(btn_reconnect)
        left_layout.addWidget(hw_card)

        # LED Indicator Test Bench
        led_card = QFrame(left_widget)
        led_card.setObjectName("lab-card")
        l_layout = QVBoxLayout(led_card)
        l_layout.setSpacing(4)
        l_title = QLabel("LED OPTICAL FEEDBACK TEST BENCH", led_card)
        l_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        l_layout.addWidget(l_title)

        led_grid = QHBoxLayout()
        btn_t_conf = QPushButton("Confirm", led_card)
        btn_t_conf.clicked.connect(lambda: self.led_controller.trigger_input_confirmed())
        led_grid.addWidget(btn_t_conf)

        btn_t_corr = QPushButton("Correct", led_card)
        btn_t_corr.clicked.connect(lambda: self.led_controller.trigger_prediction_result(True))
        led_grid.addWidget(btn_t_corr)

        btn_t_alert = QPushButton("Discrepancy", led_card)
        btn_t_alert.clicked.connect(lambda: self.led_controller.trigger_prediction_result(False))
        led_grid.addWidget(btn_t_alert)

        btn_t_comp = QPushButton("Complete", led_card)
        btn_t_comp.clicked.connect(lambda: self.led_controller.trigger_experiment_complete())
        led_grid.addWidget(btn_t_comp)
        l_layout.addLayout(led_grid)
        left_layout.addWidget(led_card)
        left_layout.addStretch()

        splitter.addWidget(left_widget)

        # RIGHT PANEL: Config File Viewer
        right_frame = QFrame(self)
        right_frame.setObjectName("lab-card")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setSpacing(4)

        conf_title = QLabel("HARDWARE PIN CONFIGURATION MAP (config.json)", right_frame)
        conf_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 10px;")
        right_layout.addWidget(conf_title)

        self.conf_text = QTextEdit(right_frame)
        self.conf_text.setReadOnly(True)
        self.conf_text.setStyleSheet("background-color: #0b1325; border: 1px solid #1a2c4e; color: #e0e6ed; font-family: monospace; font-size: 9px;")
        right_layout.addWidget(self.conf_text)

        splitter.addWidget(right_frame)
        splitter.setSizes([350, 450])
        main_layout.addWidget(splitter)
        self._load_config_display()

    def _load_config_display(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                self.conf_text.setText(f.read())

    def _apply_resolution(self):
        idx = self.res_combo.currentIndex()
        if idx == 0:
            self.resolution_changed.emit(1024, 600, False)
        elif idx == 1:
            self.resolution_changed.emit(800, 480, False)
        else:
            self.resolution_changed.emit(1024, 600, True)

    def _reprobe_hardware(self):
        success = self.adapter.initialize()
        self.mode_status_lbl.setText(f"Active Mode: {self.adapter.hardware_mode.upper()} ({'CONNECTED' if success else 'STANDBY'})")
