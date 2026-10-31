import sys
import os

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
os.environ["QT_QPA_PLATFORM"] = "offscreen"
