# Genetics Experimentation System v2.0
**University-Level Interactive Genetics Research Workstation**
*M.Sc. Genetics | Raspberry Pi 3 + 7-inch HDMI | Desktop Simulation Mode*

---

## Overview

A professional, scientifically rigorous, fully offline PyQt5 application for postgraduate M.Sc. Genetics students. Provides interactive Mendelian inheritance experiments, chromosomal segregation visualizations, statistical analysis, population simulation, and an offline ML diagnostic classifier. Designed to run on a Raspberry Pi 3 with physical genotype selector switches and a 7-inch HDMI display, with full laptop simulation support.

> **Scientific Principle:** The deterministic genetics engine is always the primary source of truth. The ML classifier is a supplementary, clearly labelled heuristic trained exclusively on synthetic educational simulation data.

---

## v2.0 New Features

### Cytogenetics Laboratory — Interactive Meiosis Visualization
- Animated vector chromosome segregation with Q‑Painter rendering (~30 fps, capped for Pi 3)
- Depicts Prophase I pairing, Metaphase I alignment, Anaphase I reductional division, Meiosis II equational division, and 4 haploid gamete products
- Dihybrid independent assortment with switchable Metaphase I orientation (Orientation 1: AB/ab vs Orientation 2: Ab/aB)
- Play/Pause/Next Stage/Prev Stage/Reset/Speed controls — fully keyboard-navigable
- Biological annotation distinguishing chromosome segregation from recombination (chiasma)
- F3 keyboard shortcut for direct access

### Upgraded Dynamic Punnett Square Laboratory
- Animated gamete fusion (`⚡ Animate Fusion` button)
- Interactive cell inspection: click or keyboard-navigate any cell to inspect maternal/paternal allele origin
- Zygosity highlighting filter: All / Homozygous Dominant / Heterozygous / Homozygous Recessive
- Step-by-step mathematical derivation (gametogenesis → Cartesian product → genotypic distribution)
- 2×2 monohybrid and 4×4 dihybrid full support

### Improved ML Diagnostic Laboratory (Experiment 06)
- **Model training never runs on UI open.** Pre-trained artifacts are loaded from `ml/model_artifacts.joblib`
- Reports actual trained depth (not configured depth) — both are verified to be 6
- Actual per-sample inference latency measured at runtime via `time.perf_counter_ns()`
- Held-out evaluation on previously unseen cross configurations: **75.8% accuracy, Macro F1 = 0.64**
- Validation set accuracy: **82.6%** (used for model selection, not test set leakage)
- Ambiguity warnings when multiple error categories produce indistinguishable submitted ratios
- Candidate model comparison table: Decision Tree vs Random Forest vs Logistic Regression
- Feature importance bar chart with Gini impurity reduction
- Colour-coded confusion matrix from held-out unseen cross configurations

### Premium Scientific Stylesheet v2.0
- QTabBar, QSlider, QRadioButton, QProgressBar, QToolTip, QSplitter all styled
- Consistent deep-navy/teal/cyan scientific laboratory instrument aesthetic

---

## Navigation

| Key | Screen |
|-----|--------|
| F1 | Dashboard (Home) |
| F2 | Module 01 Experiment Hub |
| **F3** | **Cytogenetics: Meiosis Laboratory** |
| F5 | Experimental Records Browser |
| F12 | System Settings & Hardware |
| Esc | Exit |

---

## Installation

### Requirements
- Python 3.10+ (tested on 3.12)
- PyQt5 ≥ 5.15.2
- scikit-learn ≥ 1.3.0
- pandas, numpy, scipy, joblib, pytest

### Windows / Laptop (Simulation Mode)

```powershell
cd genetic-module
python -m pip install PyQt5 scikit-learn pandas numpy scipy joblib pytest
python ml/train_models.py      # Build ML artifacts (one-time)
python main.py
```

### Raspberry Pi 3 (Production Mode)

```bash
sudo apt-get install python3-pyqt5 python3-sklearn python3-pandas python3-numpy python3-scipy python3-joblib
cd genetic-module
python3 ml/train_models.py     # Build ML artifacts offline
python3 main.py
```

Edit `config/config.json` to set `"mode": "raspberry_pi"` for GPIO activation.

### Quick Run (Windows)
```powershell
.\run_app.bat
```

---

## ML Classifier — Scientific Provenance

```
Model:            scikit-learn DecisionTreeClassifier
Configured Depth: 6 | Actual Trained Depth: 6
Training Set:     3,000 synthetic educational records
Validation Set:   1,000 synthetic records (model selection)
Held-out Set:     1,000 records with UNSEEN cross templates
Val Accuracy:     82.6%  (used for candidate model selection)
Held-out Acc:     75.8%  (generalization on unseen configurations)
Held-out Macro F1: 0.64

⚠ NOTICE: All data is SYNTHETIC educational simulation data.
   This classifier has NOT been validated on real human student cohorts.
   Class predictions indicate plausible error patterns,
   NOT confirmed cognitive states.
```

---

## Running Tests

```powershell
python -m pytest tests/ -v
```

Expected: **24/24 tests passing.**

| Test Suite | Tests | Status |
|---|---|---|
| test_genetics.py | Monohybrid & Dihybrid cross probabilities | ✅ 6/6 |
| test_statistics.py | Chi-square GoF, df, Cochran warning | ✅ 4/4 |
| test_simulation.py | Reproducibility, seed, LLN convergence | ✅ 4/4 |
| test_hardware.py | Mock adapter, LED states, latency | ✅ 4/4 |
| test_error_evaluation.py | Deterministic evaluator + ML inference | ✅ 4/4 |
| test_ui_workflow.py | Screen navigation (11 screens), EXP01 workflow | ✅ 2/2 |

---

## Raspberry Pi 3 Performance Notes

- Animation frame rate capped at 30 fps via `QTimer` (33 ms interval)
- All QPainter rendering uses native Qt vector graphics — no OpenGL/3D engine
- ML inference: Decision Tree sub-millisecond on Pi 3 CPU (no cloud calls ever)
- GPIO assignments preserved from v1.0 in `hardware/gpio_adapter.py` — not changed
- Laptop simulation mode: `MockHardwareAdapter` emulates all switch and LED I/O

---

## Repository Structure

```
genetic-module/
├── main.py                          # Application entry point
├── assets/styles.qss                # Premium scientific QSS v2.0
├── genetics_engine/                 # Deterministic Mendelian cross engine
├── biostatistics/                   # Chi-square GoF with Cochran validation
├── simulations/                     # Stochastic population sampling
├── ml/
│   ├── error_classifier.py          # Offline classifier (load-only on UI)
│   ├── train_models.py              # Explicit training pipeline (run once)
│   ├── model_artifacts.joblib       # Pre-trained artifacts with diagnostics
│   ├── model_decision_tree.joblib   # Legacy artifact (backward compat)
│   ├── synthetic_data.py            # Synthetic data generator
│   └── deterministic_evaluator.py  # Rule-based correctness engine
├── hardware/                        # GPIO adapter + mock simulation adapter
├── ui/
│   ├── components/
│   │   ├── meiosis_widget.py        # NEW: Animated meiosis canvas
│   │   ├── punnett_widget.py        # UPGRADED: Interactive Punnett square
│   │   ├── chart_widget.py          # Scientific bar chart
│   │   └── hardware_status_widget.py
│   └── screens/
│       ├── dashboard_screen.py      # Updated: Meiosis Lab shortcut
│       ├── meiosis_screen.py        # NEW: Cytogenetics laboratory
│       ├── exp06_evaluation_ai.py   # UPGRADED: Full ML diagnostics
│       └── exp01-05_*.py            # Existing experiment screens
├── data/                            # Experiment records & synthetic CSV
├── tests/                           # 24 automated tests
└── config/                          # System configuration JSON
```
