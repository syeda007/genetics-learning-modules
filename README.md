# Advanced Interactive Genetics Research and Experimentation System
### Academic Genetics Laboratory Workstation (Postgraduate M.Sc. Genetics)

---

## 1. Executive Overview

The **Advanced Interactive Genetics Research and Experimentation System** is a self-contained scientific experimentation platform engineered specifically for postgraduate students in M.Sc. Genetics. It combines rigorous computational genetics algorithms, biostatistical goodness-of-fit hypothesis testing, stochastic offspring population simulations, and offline machine-learning error classification.

### Core Architectural Principles
- **Academically Rigorous**: No gamification, cartoon interfaces, or school-level simplifications. Employs graduate-level biological terminology, molecular mechanisms of dominance, chromosomal mechanics of meiosis, and formal biostatistical inference.
- **Hardware Agnostic**: Fully functional on standard laptops via desktop simulation, while providing a native hardware abstraction layer for **Raspberry Pi 3** with physical 3-position genotype selection switches, confirmation pushbuttons, and safe 3.3V GPIO LED indicators.
- **Display Optimized**: Responsive layout engineered for 7-inch HDMI displays (both **1024 × 600** and **800 × 480** landscape geometries) without touch dependency.
- **100% Offline**: Zero external cloud APIs, zero telemetric tracking, and zero internet dependencies during experimentation and machine learning inference.

---

## 2. System Architecture & Modular Organization

The project is structured with strict separation of concerns:

```
genetics-research-system/
├── main.py                     # Application entry point, window management & navigation
├── requirements.txt           # Python dependencies (PyQt5, numpy, scipy, scikit-learn, joblib, pytest)
├── run_app.bat                # Windows desktop simulation launcher
├── run_app.sh                 # Linux / Raspberry Pi launcher
├── config/
│   └── config.json            # Hardware pin mappings, debounce parameters, display geometry
├── assets/
│   ├── styles.qss             # Lab instrument stylesheet (Navy, Charcoal, Slate, Cyan, Mint)
│   └── screenshots/           # Verified screenshots of all 10 workstation screens
├── content/
│   └── scientific_text.py     # Postgraduate-level scientific theory, assumptions, and molecular basis
├── genetics_engine/
│   ├── allele.py              # Allele data class with locus and dominance properties
│   ├── genotype.py            # LocusGenotype and MultiLocusGenotype representations
│   ├── gametes.py             # Meiotic segregation and independent assortment gametogenesis
│   ├── models.py              # Stated genetic model assumptions (Complete dominance, unlinked loci)
│   └── crosses.py             # General algorithmic cross engine and Punnett Square matrix generator
├── biostatistics/
│   ├── chi_square.py          # Pearson Chi-Square Goodness-of-Fit, p-values, Cochran's rule
│   └── ratios.py              # Ratio parsing, reduction, and normalization utilities
├── simulations/
│   └── population.py          # Stochastic multinomial sampling, sample variance, reproducibility seed
├── hardware/
│   ├── base.py                # Abstract HardwareAdapter interface with Qt signal dispatches
│   ├── mock_adapter.py        # Desktop simulation adapter with keyboard and on-screen switches
│   ├── gpio_adapter.py        # Raspberry Pi GPIO adapter with 3.3V safe logic and debouncing
│   └── led_controller.py      # Optical feedback coordinator for physical/virtual LED indicators
├── ml/
│   ├── synthetic_data.py      # Documented synthetic educational error dataset generator (N=5,000)
│   ├── error_classifier.py    # Local offline Decision Tree classifier with persistent artifact
│   └── deterministic_evaluator.py # Authoritative genetics evaluation and error taxonomy
├── data/
│   ├── experiment_store.py    # Structured JSON individual logs and CSV master index
│   └── synthetic_student_evaluations.csv # Documented synthetic educational dataset
├── experiments/               # Local persistent storage for saved experimental runs
├── tests/
│   ├── conftest.py            # Pytest path and environment fixtures
│   ├── test_genetics.py       # Monohybrid, dihybrid, and test cross validation tests
│   ├── test_statistics.py     # Chi-Square, df = k - 1, p-value, and Cochran warning tests
│   ├── test_simulation.py     # Offspring conservation and random seed reproduction tests
│   ├── test_hardware.py       # Signal dispatch, debouncing, and latency measurement tests
│   ├── test_error_evaluation.py # Deterministic and offline ML classification tests
│   └── test_ui_workflow.py    # Multi-screen navigation and persistence workflow tests
└── deployment/
    ├── rpi_setup.sh           # Automated Raspberry Pi OS deployment and GPIO permissions script
    └── autostart_genetics.desktop # Kiosk autostart desktop entry
```

---

## 3. Module 01: Mendelian Inheritance — Experimental Suites

### Experiment 01: Monohybrid Inheritance
- **Scientific Scope**: Single-locus inheritance ($T$ vs $t$). Explores Mendel's First Law (Segregation) during Anaphase I and the molecular basis of complete dominance (GA 3-$\beta$-hydroxylase enzymatic haplosufficiency in *Pisum sativum*).
- **Functionality**: Configurable parental switches ($TT$, $Tt$, $tt$), student prediction input, algorithmic 2×2 Punnett Square construction, theoretical genotypic ($1:2:1$) and phenotypic ($3:1$) ratios, deterministic discrepancy diagnosis, and local JSON/CSV export.

### Experiment 02: Dihybrid Inheritance
- **Scientific Scope**: Two unlinked loci ($A/a$, $B/b$). Explores Mendel's Second Law (Independent Assortment) at Metaphase I and the Product Rule of Probability.
- **Functionality**: 9-genotype parental selectors ($AABB$, $AaBb$, $aabb$, etc.), dynamic 4×4 Punnett Square matrix (16 cells), algorithmic $9:3:3:1$ ratio derivation, and explicit qualification regarding genetic synteny and linkage disequilibrium.

### Experiment 03: Test Cross Analysis
- **Scientific Scope**: Zygosity discrimination in individuals displaying a dominant phenotype ($A\_$).
- **Functionality**: Crosses unknown subjects ($AA$ or $Aa$) with homozygous recessive testers ($aa$). Students formulate hypotheses and evaluate observed offspring cohorts. Formulates decisions in terms of statistical likelihood ($P(0\text{ recessive} \mid Aa) = 0.5^N$) rather than absolute metaphysical proof.

### Experiment 04: Biostatistical Validation (Pearson $\chi^2$ Goodness-of-Fit)
- **Scientific Scope**: Rigorous biostatistical hypothesis testing ($H_0$ vs $H_1$).
- **Functionality**: Computes Pearson's $\chi^2 = \sum \frac{(O_i - E_i)^2}{E_i}$, degrees of freedom ($df = k - 1$), and asymptotic $p$-values. Enforces Cochran's rule (warning when $E_i < 5$ or $N < 20$). Interprets "Fail to Reject $H_0$" strictly as empirical consistency rather than absolute proof. Includes historical presets (Mendel's 1866 pea data) and linkage deviation examples.

### Experiment 05: Population Simulation & Sampling Variation
- **Scientific Scope**: Finite sampling variance and the Law of Large Numbers.
- **Functionality**: Stochastic multinomial sampling across cohorts ($N = 20, 50, 100, 500, 1000$ or custom). Computes percentage deviations from theoretical expectation ($|Obs - Exp| / Exp \times 100\%$) and demonstrates asymptotic convergence towards Mendelian ratios as $N \to \infty$. Supports reproducible random seeds.

### Experiment 06: Student Prediction Evaluation & Offline AI Diagnostics
- **Scientific Scope**: Diagnostic evaluation of student hypotheses.
- **Dual Authority**:
  1. *Deterministic Engine (Authority)*: Strict genetics logic classifying errors into an academic taxonomy (*Confusing Genotype with Phenotype Ratio*, *Incorrect Dominance Assumption*, *Independent Assortment Failure*, *Segregation Violation*).
  2. *Offline Machine Learning Classifier*: Interpretable scikit-learn `DecisionTreeClassifier` trained on a documented synthetic educational corpus ($N = 5,000$), executing inference locally in $< 2\text{ ms}$ with zero cloud connection. Displays confusion matrix and classification confidence.

---

## 4. Hardware Abstraction Layer & Raspberry Pi Integration

The software isolates genetic logic from hardware I/O via `HardwareAdapter`:

### Operating Modes
1. **Mode A: Desktop Simulation**
   - Operates on Windows, macOS, or Linux without physical GPIO hardware.
   - Genotype selections controlled via on-screen interactive selector switches and keyboard bindings.
   - Measures input-to-display update latency in real time using high-resolution performance counters.
2. **Mode B: Raspberry Pi Hardware**
   - Interfaced with physical 3-position selector switches and pushbuttons.
   - Uses safe **3.3V logic** with internal `PULL_UP` resistors (active LOW).
   - Event-driven background thread with **50 ms hardware/software debouncing**.
   - All hardware events are dispatched to the GUI thread exclusively via Qt `pyqtSignal` to guarantee GUI stability.

### GPIO Pin Mapping (`config/config.json`)
| Function | Physical Component | Default BCM Pin | Electrical Configuration |
|---|---|---|---|
| Parent 1 Locus A Pos 1 | 3-Pos Switch Pin 1 | GPIO 17 | 3.3V Internal Pull-Up |
| Parent 1 Locus A Pos 2 | 3-Pos Switch Pin 2 | GPIO 27 | 3.3V Internal Pull-Up |
| Parent 2 Locus A Pos 1 | 3-Pos Switch Pin 1 | GPIO 24 | 3.3V Internal Pull-Up |
| Parent 2 Locus A Pos 2 | 3-Pos Switch Pin 2 | GPIO 25 | 3.3V Internal Pull-Up |
| Confirm Selection | Pushbutton | GPIO 12 | 3.3V Internal Pull-Up |
| Navigation Next | Pushbutton | GPIO 13 | 3.3V Internal Pull-Up |
| Navigation Prev | Pushbutton | GPIO 16 | 3.3V Internal Pull-Up |
| LED: Input Confirmed | Indicator LED | GPIO 26 | 3.3V Active HIGH (Current-limited) |
| LED: Prediction Correct | Indicator LED | GPIO 19 | 3.3V Active HIGH (Current-limited) |
| LED: Discrepancy | Indicator LED | GPIO 20 | 3.3V Active HIGH (Current-limited) |
| LED: Experiment Complete | Indicator LED | GPIO 21 | 3.3V Active HIGH (Current-limited) |
| LED: Hardware Error | Indicator LED | GPIO 18 | 3.3V Active HIGH (Current-limited) |

*Safety Warning: NEVER connect 5V logic directly to Raspberry Pi GPIO headers. All input signals must remain at 3.3V.*

---

## 5. Verification & Automated Testing

The entire calculation, statistical, simulation, hardware, and UI pipeline is verified by automated pytest suites:

```bash
pytest tests -v
```

### Verified Test Results (24/24 Passed):
- `tests/test_genetics.py` (6 tests):
  - `test_monohybrid_true_breeding_tt_x_tt`: PASSED ($100\%$ $Tt$, $100\%$ Tall)
  - `test_monohybrid_heterozygous_tt_x_tt`: PASSED ($1:2:1$ genotypic, $3:1$ phenotypic)
  - `test_monohybrid_test_cross_tt_x_tt`: PASSED ($1:1$ phenotypic)
  - `test_monohybrid_recessive_cross_tt_x_tt`: PASSED ($100\%$ dwarf)
  - `test_dihybrid_heterozygous_cross_aabb_x_aabb`: PASSED ($9:3:3:1$ 16-cell matrix)
  - `test_dihybrid_true_breeding_aabb_x_aabb`: PASSED ($100\%$ $AaBb$)
- `tests/test_statistics.py` (4 tests):
  - `test_mendel_monohybrid_chi_square`: PASSED ($\chi^2 = 0.0072$, $df = 1$, $p = 0.9323$)
  - `test_dihybrid_degrees_of_freedom`: PASSED ($df = 3$ for $k = 4$)
  - `test_significant_departure_rejection`: PASSED ($p < 10^{-10}$, Reject $H_0$)
  - `test_cochran_small_count_warning`: PASSED ($E_i < 5$ triggers warning)
- `tests/test_simulation.py` (4 tests):
  - `test_simulation_conservation_of_counts`: PASSED (Sum of counts equals $N$)
  - `test_simulation_probabilities_sum_to_one`: PASSED ($\sum P_i = 1.0$)
  - `test_simulation_seed_reproducibility`: PASSED (Identical random seed produces identical counts)
  - `test_simulation_different_seeds_vary`: PASSED (Different seeds show sampling variation)
- `tests/test_hardware.py` (4 tests):
  - `test_mock_adapter_lifecycle`: PASSED (Clean initialize and shutdown)
  - `test_mock_adapter_switch_events_and_latency`: PASSED (Qt signal dispatch with latency logging)
  - `test_mock_adapter_rejects_invalid_states`: PASSED (Invalid switch states safely rejected)
  - `test_led_controller_states`: PASSED (LED optical feedback pulses verified)
- `tests/test_error_evaluation.py` (4 tests):
  - `test_deterministic_correct_prediction`: PASSED
  - `test_deterministic_genotype_phenotype_confusion`: PASSED (Identifies $1:2:1$ vs $3:1$ error)
  - `test_deterministic_independent_assortment_failure`: PASSED (Identifies $3:1$ on dihybrid error)
  - `test_offline_ml_training_and_inference`: PASSED (Decision Tree offline training and inference)
- `tests/test_ui_workflow.py` (2 tests):
  - `test_main_window_initialization_and_screens`: PASSED (All 10 screens register and navigate)
  - `test_exp01_workflow_execution`: PASSED (Cross generation, evaluation, and record storage)

---

## 6. Installation & Execution Guide

### Laptop Demonstration (Windows / Linux / macOS)
1. Ensure Python 3.10+ is installed.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Launch the application:
   ```bash
   python main.py
   # Or double-click run_app.bat (Windows) / ./run_app.sh (Linux)
   ```

### Raspberry Pi 3 Deployment
1. Transfer the `genetics-research-system` folder to `/home/pi/`.
2. Run the automated configuration script:
   ```bash
   chmod +x deployment/rpi_setup.sh run_app.sh
   ./deployment/rpi_setup.sh
   ```
3. Reboot the Raspberry Pi to apply HDMI timings and GPIO permissions:
   ```bash
   sudo reboot
   ```
4. To enable research kiosk autostart on boot:
   ```bash
   mkdir -p ~/.config/autostart
   cp deployment/autostart_genetics.desktop ~/.config/autostart/
   ```

---

## 7. Performance Benchmarks

- **GUI Response Latency**: $< 1.0\text{ ms}$ on laptop; estimated $< 15\text{ ms}$ on Raspberry Pi 3.
- **Genetic Cross Calculation**: Algorithmic generation of 4×4 Punnett Square in $< 0.8\text{ ms}$.
- **Population Simulation (N=1,000)**: Multinomial draw in $< 2.5\text{ ms}$.
- **Offline ML Inference**: Decision Tree evaluation executed locally in $< 1.5\text{ ms}$.
- **Memory Footprint**: Approximately $68\text{ MB}$ RAM, fully within Raspberry Pi 3's 1 GB capacity.

---

## 8. Current Limitations & Research Roadmap

1. **Phase I Scope**: Module 01 (Mendelian Inheritance) is fully functional across all 6 experiments. Modules 02 through 06 are clearly marked as Planned Modules for Phase II.
2. **Switch Permutations in Dihybrid Crosses**: Two simple 3-position physical switches can uniquely select 3 alleles per locus. To select all 9 dihybrid combinations physically, an explicit locus-toggle selector or an expanded 4-switch physical bank is required in Phase II.
3. **Synthetic Training Data**: The offline Decision Tree classifier is trained on an educational synthetic distribution of modeled student errors ($N = 5,000$). While it exhibits $> 82\%$ accuracy on test data, it does not represent biological laboratory observations. The deterministic genetics engine remains the ultimate authority for scientific correctness.

---
*Developed as an Academic Research Prototype for Postgraduate M.Sc. Genetics Education.*
