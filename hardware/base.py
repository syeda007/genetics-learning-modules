"""
Hardware Abstraction Layer: Base Adapter Interface
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
from PyQt5.QtCore import QObject, pyqtSignal
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class HardwareAdapter(QObject):
    """
    Abstract Hardware Adapter establishing an architectural boundary between
    Raspberry Pi GPIO physical switch inputs and the Qt UI/Genetics engine.
    
    All hardware events MUST be dispatched via Qt signals to guarantee thread-safe GUI updates.
    """
    # Signals emitted to UI thread
    genotype_selected = pyqtSignal(int, str)  # (parent_index: 1 or 2, genotype_str: 'TT', 'Tt', 'tt', etc.)
    navigation_action = pyqtSignal(str)       # 'confirm', 'next', 'prev', 'toggle_locus'
    hardware_latency = pyqtSignal(float)      # latency in ms
    status_message = pyqtSignal(str)          # hardware diagnostic notifications
    led_state_changed = pyqtSignal(str, bool) # (indicator_name, is_on)

    def __init__(self, config: Dict[str, Any], parent: Optional[QObject] = None):
        super().__init__(parent)
        self.config = config
        self.is_connected = False
        self.hardware_mode = "unknown"

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize hardware lines, switch event listeners, or mock bindings."""
        pass

    @abstractmethod
    def shutdown(self):
        """Safely release all GPIO lines, timers, and turn off LED indicators."""
        pass

    @abstractmethod
    def set_led(self, indicator_name: str, state: bool):
        """Control physical or virtual LED state."""
        pass

    @abstractmethod
    def get_switch_states(self) -> Dict[str, Any]:
        """Returns snapshot of active switch positions."""
        pass
