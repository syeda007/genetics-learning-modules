"""
Unit Tests: Hardware Abstraction Layer
Verifies Mock Hardware Adapter, Signal Emission, Switch Validation, and Latency Logging
"""
import pytest
from PyQt5.QtWidgets import QApplication
from hardware.mock_adapter import MockHardwareAdapter
from hardware.led_controller import LedController

# Ensure QApplication exists for Qt signal testing
app = QApplication.instance() or QApplication([])


def test_mock_adapter_lifecycle():
    config = {"hardware": {"debounce_ms": 50}}
    adapter = MockHardwareAdapter(config)
    
    assert adapter.initialize() is True
    assert adapter.is_connected is True

    adapter.shutdown()
    assert adapter.is_connected is False


def test_mock_adapter_switch_events_and_latency():
    config = {"hardware": {"debounce_ms": 50}}
    adapter = MockHardwareAdapter(config)
    adapter.initialize()

    received_signals = []
    latencies = []

    adapter.genotype_selected.connect(lambda p_idx, geno: received_signals.append((p_idx, geno)))
    adapter.hardware_latency.connect(lambda lat: latencies.append(lat))

    adapter.set_switch_position(parent_index=1, locus_char='T', genotype_str="Tt")

    assert len(received_signals) == 1
    assert received_signals[0] == (1, "Tt")
    assert len(latencies) == 1
    assert latencies[0] >= 0.0


def test_mock_adapter_rejects_invalid_states():
    config = {"hardware": {"debounce_ms": 50}}
    adapter = MockHardwareAdapter(config)
    adapter.initialize()

    received_signals = []
    adapter.genotype_selected.connect(lambda p_idx, geno: received_signals.append((p_idx, geno)))

    # Ambiguous multi-position or invalid allele
    adapter.set_switch_position(parent_index=1, locus_char='T', genotype_str="XYZ")
    assert len(received_signals) == 0


def test_led_controller_states():
    config = {"hardware": {"debounce_ms": 50}}
    adapter = MockHardwareAdapter(config)
    adapter.initialize()
    led_ctrl = LedController(adapter)

    led_changes = []
    adapter.led_state_changed.connect(lambda name, state: led_changes.append((name, state)))

    led_ctrl.trigger_prediction_result(is_correct=True, pulse_ms=10)
    assert any(name == "prediction_correct" and state is True for name, state in led_changes)
