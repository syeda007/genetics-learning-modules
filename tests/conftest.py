"""
Pytest configuration and environment fixtures
"""
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
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

