"""
Genetics Experimentation System: Main Application Entry Point
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
Compatible with Raspberry Pi 3 (7-inch HDMI 800x480 / 1024x600) and Desktop Simulation
"""
import sys
import os
import json

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QStackedWidget,
    QStatusBar, QShortcut
)
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtCore import Qt

# Ensure root package is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from hardware.mock_adapter import MockHardwareAdapter
from hardware.gpio_adapter import RaspberryPiGPIOAdapter, RPI_GPIO_AVAILABLE
from hardware.led_controller import LedController
from data.experiment_store import ExperimentStore
from ui.components.hardware_status_widget import HardwareStatusWidget

from ui.screens.dashboard_screen import DashboardScreen
from ui.screens.module01_overview import Module01OverviewScreen
from ui.screens.exp01_monohybrid import MonohybridExperimentScreen
from ui.screens.exp02_dihybrid import DihybridExperimentScreen
from ui.screens.exp03_testcross import TestCrossExperimentScreen
from ui.screens.exp04_statistical import StatisticalValidationScreen
from ui.screens.exp05_simulation import PopulationSimulationScreen
from ui.screens.exp06_evaluation_ai import PredictionEvaluationAIScreen
from ui.screens.records_screen import RecordsBrowserScreen
from ui.screens.settings_screen import SettingsScreen


class GeneticsMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Genetics Experimentation System — M.Sc. Research Workstation")
        
        # Load Configuration
        config_path = os.path.join(BASE_DIR, "config", "config.json")
        self.config = {}
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
                
        # Set Geometry: Default 1024x600 (fits 7-inch Raspberry Pi display)
        self.setMinimumSize(800, 480)
        self.resize(1024, 600)

        # Initialize Hardware Layer
        mode_setting = self.config.get("system", {}).get("mode", "desktop_simulation")
        if mode_setting == "raspberry_pi" and RPI_GPIO_AVAILABLE:
            self.hardware_adapter = RaspberryPiGPIOAdapter(self.config, self)
        else:
            self.hardware_adapter = MockHardwareAdapter(self.config, self)
            
        self.hardware_adapter.initialize()
        self.led_controller = LedController(self.hardware_adapter, self)
        self.exp_store = ExperimentStore(BASE_DIR)

        self._init_ui()
        self._init_shortcuts()

    def _init_ui(self):
        # Central Container
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Top Hardware Telemetry Bar
        self.hw_widget = HardwareStatusWidget(self.hardware_adapter, self)
        self.hw_widget.switch_changed_signal.connect(self._on_switch_changed)
        main_layout.addWidget(self.hw_widget)

        # Screen Stack
        self.stack = QStackedWidget(self)
        self.screens = {}

        # Instantiate Screens
        self.dashboard_screen = DashboardScreen(self)
        self.module01_screen = Module01OverviewScreen(self)
        self.exp01_screen = MonohybridExperimentScreen(self.hardware_adapter, self.led_controller, self.exp_store, self)
        self.exp02_screen = DihybridExperimentScreen(self.hardware_adapter, self.led_controller, self.exp_store, self)
        self.exp03_screen = TestCrossExperimentScreen(self.hardware_adapter, self.led_controller, self.exp_store, self)
        self.exp04_screen = StatisticalValidationScreen(self.hardware_adapter, self.led_controller, self.exp_store, self)
        self.exp05_screen = PopulationSimulationScreen(self.hardware_adapter, self.led_controller, self.exp_store, self)
        self.exp06_screen = PredictionEvaluationAIScreen(self.hardware_adapter, self.led_controller, self.exp_store, self)
        self.records_screen = RecordsBrowserScreen(self.exp_store, self)
        self.settings_screen = SettingsScreen(self.hardware_adapter, self.led_controller, self)

        # Map screens
        screen_map = {
            "dashboard": self.dashboard_screen,
            "module01_hub": self.module01_screen,
            "exp01_monohybrid": self.exp01_screen,
            "exp02_dihybrid": self.exp02_screen,
            "exp03_testcross": self.exp03_screen,
            "exp04_statistical": self.exp04_screen,
            "exp05_simulation": self.exp05_screen,
            "exp06_evaluation_ai": self.exp06_screen,
            "records": self.records_screen,
            "settings": self.settings_screen
        }

        for name, scr in screen_map.items():
            self.screens[name] = scr
            self.stack.addWidget(scr)
            if hasattr(scr, "navigate_to"):
                scr.navigate_to.connect(self.navigate_to_screen)

        self.settings_screen.resolution_changed.connect(self._handle_resolution_change)

        main_layout.addWidget(self.stack)

        # Status Bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Academic Genetics Workstation Initialized. Ready for research cross.")
        self.hardware_adapter.status_message.connect(self.status_bar.showMessage)

    def _init_shortcuts(self):
        # Keyboard Navigation for Non-Touchscreen Kiosk Operation
        QShortcut(QKeySequence("F1"), self, lambda: self.navigate_to_screen("dashboard"))
        QShortcut(QKeySequence("F2"), self, lambda: self.navigate_to_screen("module01_hub"))
        QShortcut(QKeySequence("F3"), self, lambda: self.navigate_to_screen("exp01_monohybrid"))
        QShortcut(QKeySequence("F5"), self, lambda: self.navigate_to_screen("records"))
        QShortcut(QKeySequence("F12"), self, lambda: self.navigate_to_screen("settings"))
        QShortcut(QKeySequence("Escape"), self, self.close)

    def navigate_to_screen(self, screen_id: str):
        if screen_id in self.screens:
            self.stack.setCurrentWidget(self.screens[screen_id])
            if screen_id == "records":
                self.records_screen.reload_records()
            self.status_bar.showMessage(f"Active Screen: {screen_id.upper()}")

    def _on_switch_changed(self, parent_idx: int, locus_char: str, geno: str):
        if isinstance(self.hardware_adapter, MockHardwareAdapter):
            self.hardware_adapter.set_switch_position(parent_idx, locus_char, geno)

    def _handle_resolution_change(self, width: int, height: int, is_fullscreen: bool):
        if is_fullscreen:
            self.showFullScreen()
        else:
            self.showNormal()
            self.resize(width, height)

    def closeEvent(self, event):
        self.hardware_adapter.shutdown()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # Load stylesheet
    style_path = os.path.join(BASE_DIR, "assets", "styles.qss")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    window = GeneticsMainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
