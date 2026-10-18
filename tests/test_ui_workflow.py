"""
Unit Tests: UI Workflow and Navigation
Verifies Screen Instantiation, Navigation Stack, and Experiment Record Persistence
"""
import pytest
from PyQt5.QtWidgets import QApplication
from main import GeneticsMainWindow

app = QApplication.instance() or QApplication([])


def test_main_window_initialization_and_screens():
    win = GeneticsMainWindow()
    assert win is not None
    assert win.stack.count() == 10  # 10 screens registered

    expected_screens = [
        "dashboard", "module01_hub", "exp01_monohybrid", "exp02_dihybrid",
        "exp03_testcross", "exp04_statistical", "exp05_simulation",
        "exp06_evaluation_ai", "records", "settings"
    ]
    for scr_id in expected_screens:
        assert scr_id in win.screens
        win.navigate_to_screen(scr_id)
        assert win.stack.currentWidget() == win.screens[scr_id]

    win.close()


def test_exp01_workflow_execution():
    win = GeneticsMainWindow()
    win.navigate_to_screen("exp01_monohybrid")
    scr = win.exp01_screen

    # Run cross
    scr._run_cross()
    assert scr.last_cross_result is not None
    assert scr.punnett_widget.table.rowCount() > 0

    # Save record
    scr._save_record()
    recent = win.exp_store.list_recent_experiments(limit=1)
    assert len(recent) > 0
    assert "EXP01" in recent[0]["experiment_id"]

    win.close()
