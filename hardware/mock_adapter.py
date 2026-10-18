"""
Hardware Abstraction Layer: Desktop Simulation and Mock Adapter
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
import time
from typing import Dict, Any, Optional
from PyQt5.QtCore import QObject

from hardware.base import HardwareAdapter


class MockHardwareAdapter(HardwareAdapter):
    """
    Simulated Hardware Adapter for desktop development and automated testing.
    Emulates physical 3-position selector switches and pushbuttons.
    Logs input-to-display update latency for academic performance evaluation.
    """
    def __init__(self, config: Dict[str, Any], parent: Optional[QObject] = None):
        super().__init__(config, parent)
        self.hardware_mode = "desktop_simulation"
        self._switch_state = {
            "parent1_locus_a": "TT",
            "parent1_locus_b": "BB",
            "parent2_locus_a": "tt",
            "parent2_locus_b": "bb"
        }
        self._led_states = {
            "input_confirmed": False,
            "prediction_correct": False,
            "prediction_inconsistent": False,
            "experiment_complete": False,
            "hardware_error": False
        }

    def initialize(self) -> bool:
        self.is_connected = True
        self.status_message.emit("Desktop Simulation Mode Active: GPIO emulated via virtual switches and keyboard.")
        return True

    def shutdown(self):
        self.is_connected = False
        for k in self._led_states:
            self._led_states[k] = False
            self.led_state_changed.emit(k, False)
        self.status_message.emit("Mock Hardware Adapter shut down cleanly.")

    def set_switch_position(self, parent_index: int, locus_char: str, genotype_str: str):
        """
        Simulate switching a physical 3-position switch for Parent 1 or Parent 2.
        Measures processing latency with perf_counter.
        """
        start_time = time.perf_counter()
        
        # Prevent invalid states
        valid_singles = ["TT", "Tt", "tt", "AA", "Aa", "aa", "BB", "Bb", "bb"]
        if genotype_str not in valid_singles:
            self.status_message.emit(f"Warning: Rejected invalid switch position '{genotype_str}'")
            return
            
        key = f"parent{parent_index}_locus_{locus_char.lower()}"
        self._switch_state[key] = genotype_str
        
        # Calculate full genotype for that parent
        if locus_char.upper() in ['T', 'A']:
            other_locus = 'B'
            loc_a = genotype_str
            loc_b = self._switch_state.get(f"parent{parent_index}_locus_b", "BB")
        else:
            other_locus = 'A'
            loc_a = self._switch_state.get(f"parent{parent_index}_locus_a", "AA")
            loc_b = genotype_str
            
        full_genotype = loc_a if locus_char.upper() == 'T' else f"{loc_a}{loc_b}"
        
        # Compute latency
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        
        self.genotype_selected.emit(parent_index, full_genotype)
        self.hardware_latency.emit(latency_ms)

    def trigger_button(self, action: str):
        """Simulate physical button press (confirm, next, prev)."""
        start_time = time.perf_counter()
        self.navigation_action.emit(action)
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        self.hardware_latency.emit(latency_ms)

    def set_led(self, indicator_name: str, state: bool):
        if indicator_name in self._led_states:
            self._led_states[indicator_name] = state
            self.led_state_changed.emit(indicator_name, state)

    def get_switch_states(self) -> Dict[str, Any]:
        return dict(self._switch_state)
