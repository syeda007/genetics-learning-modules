"""
Utility script: Captures high-resolution verified screenshots of all 10 screens
at 1024x600 and 800x480 to verify visual integrity and no widget overlap.
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
    import site
    possible_roots = site.getsitepackages() + [sys.prefix] + [p for p in sys.path if "site-packages" in p]
    for p in possible_roots:
        qt_bin = os.path.join(p, "PyQt5", "Qt5", "bin")
        if os.path.isdir(qt_bin):
            try:
                os.add_dll_directory(qt_bin)
            except Exception:
                pass

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap

from main import GeneticsMainWindow

SCREENSHOT_DIR = os.path.join(PROJECT_ROOT, "assets", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def capture_all():
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Apply stylesheet
    with open(os.path.join(PROJECT_ROOT, "assets", "styles.qss"), "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
        
    window = GeneticsMainWindow()
    window.resize(1024, 600)
    window.show()

    # Process events to layout all widgets
    app.processEvents()

    screens_to_capture = [
        ("dashboard", "01_dashboard_1024x600.png"),
        ("module01_hub", "02_module01_hub_1024x600.png"),
        ("exp01_monohybrid", "03_exp01_monohybrid_1024x600.png"),
        ("exp02_dihybrid", "04_exp02_dihybrid_1024x600.png"),
        ("exp03_testcross", "05_exp03_testcross_1024x600.png"),
        ("exp04_statistical", "06_exp04_statistical_1024x600.png"),
        ("exp05_simulation", "07_exp05_simulation_1024x600.png"),
        ("exp06_evaluation_ai", "08_exp06_evaluation_ai_1024x600.png"),
        ("records", "09_records_browser_1024x600.png"),
        ("settings", "10_settings_1024x600.png")
    ]

    for scr_id, fname in screens_to_capture:
        window.navigate_to_screen(scr_id)
        # Execute cross/action if experiment screen to populate data
        scr = window.screens[scr_id]
        if hasattr(scr, "_run_cross"):
            scr._run_cross()
        elif hasattr(scr, "_run_test_cross"):
            scr._run_test_cross()
        elif hasattr(scr, "_run_chi_square"):
            scr._run_chi_square()
        elif hasattr(scr, "_run_simulation"):
            scr._run_simulation()
        elif hasattr(scr, "_run_evaluation"):
            scr._run_evaluation()

        app.processEvents()

        pix = window.grab()
        out_path = os.path.join(SCREENSHOT_DIR, fname)
        pix.save(out_path, "PNG")
        print(f"Captured: {out_path} ({pix.width()}x{pix.height()})")

    # Also capture 800x480 resolution to verify compact layout
    window.resize(800, 480)
    app.processEvents()
    for scr_id in ["dashboard", "exp01_monohybrid", "exp02_dihybrid", "exp04_statistical"]:
        window.navigate_to_screen(scr_id)
        app.processEvents()
        pix = window.grab()
        out_path = os.path.join(SCREENSHOT_DIR, f"{scr_id}_800x480.png")
        pix.save(out_path, "PNG")
        print(f"Captured compact 800x480: {out_path}")

    window.close()
    print("ALL SCREENSHOTS CAPTURED SUCCESSFULLY.")


if __name__ == "__main__":
    capture_all()
