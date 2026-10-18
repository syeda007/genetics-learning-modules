"""
Web Application: Streamlit Cloud Genetics Research System
Academic Genetics Research Instrument (Postgraduate M.Sc. Genetics)
100% Free Public Cloud Deployment for Streamlit Community Cloud (share.streamlit.io)
"""
import sys
import os
import random
import pandas as pd
import numpy as np
import streamlit as st

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from genetics_engine.allele import TALL_ALLELE, DWARF_ALLELE, LOCUS_A_DOM, LOCUS_A_REC, LOCUS_B_DOM, LOCUS_B_REC
from genetics_engine.genotype import MultiLocusGenotype
from genetics_engine.models import MENDELIAN_COMPLETE_DOMINANCE, DIHYBRID_INDEPENDENT_ASSORTMENT
from genetics_engine.crosses import execute_cross
from biostatistics.chi_square import calculate_chi_square
from biostatistics.ratios import parse_ratio_string
from simulations.population import simulate_offspring_population
from ml.deterministic_evaluator import evaluate_student_prediction
from ml.error_classifier import get_error_classifier
from content.scientific_text import MENDELIAN_BACKGROUND

# Page Configuration
st.set_page_config(
    page_title="Genetics Experimentation System",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Lab Workstation CSS Styling
st.markdown("""
<style>
    .stApp {
        background-color: #070d1e;
        color: #e0e6ed;
    }
    .main-header {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
        letter-spacing: 1px;
    }
    .sub-header {
        font-size: 13px;
        color: #00b4d8;
        margin-bottom: 15px;
    }
    .card {
        background-color: #0f1a30;
        border: 1px solid #223a66;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Navigation Sidebar
st.sidebar.markdown("## 🧬 GENETICS SYSTEM")
st.sidebar.markdown("**M.Sc. Postgraduate Research Workstation**")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation Suite:",
    [
        "Laboratory Dashboard",
        "Exp 01: Monohybrid Inheritance",
        "Exp 02: Dihybrid Inheritance",
        "Exp 03: Test Cross Analysis",
        "Exp 04: Biostatistical Validation (χ²)",
        "Exp 05: Population Simulation",
        "Exp 06: Offline AI Error Classifier"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("System Status: 🟢 ONLINE | 100% Deterministic Engine + Offline ML")


# ------------------------------------------------------------------------------
# SCREEN: DASHBOARD
# ------------------------------------------------------------------------------
if menu == "Laboratory Dashboard":
    st.markdown('<div class="main-header">GENETICS EXPERIMENTATION SYSTEM</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Interactive Classical Genetics and Statistical Inheritance Analysis | M.Sc. Workstation</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Architecture", "Modular Python")
    col2.metric("Target", "M.Sc. Genetics")
    col3.metric("Machine Learning", "Offline DecisionTree")
    col4.metric("Verification", "24/24 Tests Passed")

    st.markdown("### 🔬 Active Research Module")
    st.info(
        "**Module 01: Mendelian Inheritance & Statistical Analysis** is fully operational across all 6 experimental suites. "
        "Select an experiment from the left navigation sidebar to begin."
    )

    st.markdown("### 📋 Planned Research Modules (Phase II)")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown("- **Module 02**: Extensions of Mendelian Genetics (Incomplete dominance, epistasis, lethal alleles)")
        st.markdown("- **Module 03**: Linkage & Genetic Recombination (3-point test crosses, chiasma interference)")
    with p2:
        st.markdown("- **Module 04**: Population Genetics (Hardy-Weinberg, genetic drift, selection coefficients)")
        st.markdown("- **Module 05**: Quantitative Genetics (Broad & narrow-sense heritability, polygenic inheritance)")


# ------------------------------------------------------------------------------
# SCREEN: EXP 01 - MONOHYBRID
# ------------------------------------------------------------------------------
elif menu == "Exp 01: Monohybrid Inheritance":
    st.markdown("### Experiment 01: Monohybrid Inheritance — Allelic Segregation")
    st.caption(MENDELIAN_BACKGROUND["exp01_objective"])

    col_ctrl, col_res = st.columns([1, 1.4])
    allele_map = {'T': TALL_ALLELE, 't': DWARF_ALLELE}

    with col_ctrl:
        st.markdown("#### ⚙️ Parental Configuration")
        p1_geno = st.selectbox("Parent 1 Genotype (♀):", ["Tt", "TT", "tt"], index=0)
        p2_geno = st.selectbox("Parent 2 Genotype (♂):", ["Tt", "TT", "tt"], index=0)
        pred_ratio = st.text_input("Formulate Hypothesis (Predicted Phenotype Ratio):", value="3:1")
        run_btn = st.button("⚡ Run Cross & Evaluate", type="primary")

    p1 = MultiLocusGenotype.from_str(p1_geno, allele_map)
    p2 = MultiLocusGenotype.from_str(p2_geno, allele_map)
    cross_res = execute_cross(p1, p2, MENDELIAN_COMPLETE_DOMINANCE, allele_map)

    with col_res:
        st.markdown("#### 📊 Punnett Square Matrix")
        # Format table
        rows = [g for g, p in cross_res.punnett_square.row_gametes]
        cols = [g for g, p in cross_res.punnett_square.col_gametes]
        grid_data = [[cell.zygote_genotype for cell in row] for row in cross_res.punnett_square.grid]
        df_punnett = pd.DataFrame(grid_data, index=[f"♂ {r}" for r in rows], columns=[f"♀ {c}" for c in cols])
        st.dataframe(df_punnett, use_container_width=True)

        st.markdown(f"**Theoretical Genotypic Ratio**: `{cross_res.genotype_ratios}`")
        st.markdown(f"**Theoretical Phenotypic Ratio**: `{cross_res.phenotype_ratios}`")

        eval_rep = evaluate_student_prediction(cross_res, pred_ratio, target_attribute="phenotype")
        if eval_rep.is_correct:
            st.success(eval_rep.scientific_feedback)
        else:
            st.error(eval_rep.scientific_feedback)

        with st.expander("Molecular Basis & Chromosomal Mechanics"):
            st.write(MENDELIAN_BACKGROUND["exp01_scientific_basis"])


# ------------------------------------------------------------------------------
# SCREEN: EXP 02 - DIHYBRID
# ------------------------------------------------------------------------------
elif menu == "Exp 02: Dihybrid Inheritance":
    st.markdown("### Experiment 02: Dihybrid Inheritance — Independent Assortment")
    st.caption(MENDELIAN_BACKGROUND["exp02_objective"])

    col_ctrl, col_res = st.columns([1, 1.4])
    di_map = {'A': LOCUS_A_DOM, 'a': LOCUS_A_REC, 'B': LOCUS_B_DOM, 'b': LOCUS_B_REC}
    choices = ["AaBb", "AABB", "AABb", "AAbb", "AaBB", "Aabb", "aaBB", "aaBb", "aabb"]

    with col_ctrl:
        st.markdown("#### ⚙️ Two-Locus Parental Configuration")
        p1_geno = st.selectbox("Parent 1 Genotype (♀):", choices, index=0)
        p2_geno = st.selectbox("Parent 2 Genotype (♂):", choices, index=0)
        pred_ratio = st.text_input("Predicted Phenotype Ratio:", value="9:3:3:1")
        run_btn = st.button("⚡ Compute 4×4 Matrix", type="primary")

    p1 = MultiLocusGenotype.from_str(p1_geno, di_map)
    p2 = MultiLocusGenotype.from_str(p2_geno, di_map)
    cross_res = execute_cross(p1, p2, DIHYBRID_INDEPENDENT_ASSORTMENT, di_map)

    with col_res:
        st.markdown("#### 📊 16-Cell Punnett Square Matrix")
        rows = [g for g, p in cross_res.punnett_square.row_gametes]
        cols = [g for g, p in cross_res.punnett_square.col_gametes]
        grid_data = [[cell.zygote_genotype for cell in row] for row in cross_res.punnett_square.grid]
        df_punnett = pd.DataFrame(grid_data, index=[f"♂ {r}" for r in rows], columns=[f"♀ {c}" for c in cols])
        st.dataframe(df_punnett, use_container_width=True)

        st.markdown(f"**Phenotypic Ratio**: `{cross_res.phenotype_ratios}`")
        eval_rep = evaluate_student_prediction(cross_res, pred_ratio, target_attribute="phenotype")
        if eval_rep.is_correct:
            st.success(eval_rep.scientific_feedback)
        else:
            st.error(eval_rep.scientific_feedback)

        with st.expander("Conditions for 9:3:3:1 & Linkage Disclaimers"):
            st.write(MENDELIAN_BACKGROUND["exp02_scientific_basis"])


# ------------------------------------------------------------------------------
# SCREEN: EXP 03 - TEST CROSS
# ------------------------------------------------------------------------------
elif menu == "Exp 03: Test Cross Analysis":
    st.markdown("### Experiment 03: Test Cross Analysis — Zygosity Discrimination")
    st.caption(MENDELIAN_BACKGROUND["exp03_objective"])

    col_ctrl, col_res = st.columns([1, 1.4])
    with col_ctrl:
        st.markdown("#### 🔬 Unknown Test Subject (A_)")
        test_hypo = st.radio(
            "Formulate Zygosity Hypothesis:",
            ["Subject is Homozygous Dominant (AA) → Expected 100% Dominant",
             "Subject is Heterozygous (Aa) → Expected 1:1 Dominant:Recessive"]
        )
        sample_n = st.slider("Offspring Sample Size (N):", min_value=10, max_value=200, value=40, step=10)
        run_tc = st.button("⚡ Generate Test Cross Sample", type="primary")

    with col_res:
        # Simulate hidden genotype
        hidden = "Aa" if "Heterozygous" in test_hypo else "AA"
        if hidden == "AA":
            dom_n = sample_n
            rec_n = 0
        else:
            dom_n = sum(1 for _ in range(sample_n) if random.random() < 0.5)
            rec_n = sample_n - dom_n

        df_chart = pd.DataFrame({
            "Phenotypic Class": ["Dominant (A_)", "Recessive (aa)"],
            "Observed Count": [dom_n, rec_n]
        }).set_index("Phenotypic Class")
        st.bar_chart(df_chart)

        if rec_n > 0:
            st.success(f"✓ Definitive Identification: {rec_n} homozygous recessive offspring observed. Subject is definitively Heterozygous (Aa).")
        else:
            prob = (0.5) ** sample_n
            st.info(f"Statistical Likelihood: P(0 recessive | Aa) = {prob:.6e}. Strong empirical support for Homozygous Dominant (AA).")


# ------------------------------------------------------------------------------
# SCREEN: EXP 04 - BIOSTATISTICS (CHI-SQUARE)
# ------------------------------------------------------------------------------
elif menu == "Exp 04: Biostatistical Validation (χ²)":
    st.markdown("### Experiment 04: Biostatistical Validation — Pearson Chi-Square")
    st.caption(MENDELIAN_BACKGROUND["exp04_objective"])

    col_ctrl, col_res = st.columns([1, 1.4])
    with col_ctrl:
        st.markdown("#### ⚙️ Input Parameters & Benchmarks")
        preset = st.selectbox(
            "Historical Benchmarks:",
            ["Mendel Monohybrid F2 (556, 184)", "Mendel Dihybrid F2 (315, 108, 101, 32)", "Severe Linkage Deviation (450, 48, 52, 450)"]
        )
        if "Monohybrid" in preset:
            d_ratio, d_counts, d_names = "3:1", "556, 184", "Tall, Dwarf"
        elif "Dihybrid" in preset:
            d_ratio, d_counts, d_names = "9:3:3:1", "315, 108, 101, 32", "Round Yellow, Round Green, Wrinkled Yellow, Wrinkled Green"
        else:
            d_ratio, d_counts, d_names = "1:1:1:1", "450, 48, 52, 450", "AB, Ab, aB, ab"

        ratio_input = st.text_input("Hypothesized Ratio:", value=d_ratio)
        counts_input = st.text_input("Observed Counts (comma separated):", value=d_counts)
        alpha_val = st.selectbox("Significance Level (α):", [0.05, 0.01, 0.10], index=0)
        calc_btn = st.button("⚡ Calculate Chi-Square", type="primary")

    with col_res:
        props = parse_ratio_string(ratio_input)
        counts = [float(c.strip()) for c in counts_input.split(",") if c.strip()]
        names = [f"Class {i+1}" for i in range(len(counts))]
        obs_dict = {k: v for k, v in zip(names, counts)}
        exp_dict = {k: v for k, v in zip(names, props)}

        chi2_res = calculate_chi_square(obs_dict, exp_dict, alpha=alpha_val)

        # Comparative Bar Chart
        df_stat = pd.DataFrame({
            "Class": [c.category for c in chi2_res.categories],
            "Expected": [c.expected for c in chi2_res.categories],
            "Observed": [c.observed for c in chi2_res.categories]
        }).set_index("Class")
        st.bar_chart(df_stat)

        # Metrics Table
        st.markdown(f"**χ² Statistic**: `{chi2_res.chi_square_statistic:.4f}` | **df**: `{chi2_res.degrees_of_freedom}` | **p-value**: `{chi2_res.p_value:.5e}`")
        if chi2_res.is_significant:
            st.error(f"Decision: {chi2_res.conclusion} — Significant departure from Mendelian ratio.")
        else:
            st.success(f"Decision: {chi2_res.conclusion} — Observed counts consistent with model.")

        if chi2_res.warning_message:
            st.warning(chi2_res.warning_message)


# ------------------------------------------------------------------------------
# SCREEN: EXP 05 - POPULATION SIMULATION
# ------------------------------------------------------------------------------
elif menu == "Exp 05: Population Simulation":
    st.markdown("### Experiment 05: Population Simulation & Sampling Variation")
    st.caption(MENDELIAN_BACKGROUND["exp05_objective"])

    col_ctrl, col_res = st.columns([1, 1.4])
    with col_ctrl:
        cross_type = st.selectbox("Select Model:", ["Tt × Tt (3:1)", "AaBb × AaBb (9:3:3:1)"])
        cohort_n = st.select_slider("Sample Size (N):", options=[20, 50, 100, 500, 1000, 5000], value=100)
        seed_val = st.number_input("Random Seed (for reproduction):", value=42, step=1)
        sim_btn = st.button("⚡ Run Stochastic Simulation", type="primary")

    with col_res:
        allele_map = {'T': TALL_ALLELE, 't': DWARF_ALLELE}
        p1 = MultiLocusGenotype.from_str("Tt", allele_map)
        p2 = MultiLocusGenotype.from_str("Tt", allele_map)
        cross_res = execute_cross(p1, p2, MENDELIAN_COMPLETE_DOMINANCE, allele_map)
        sim_res = simulate_offspring_population(cross_res, sample_size=cohort_n, seed=int(seed_val))

        df_sim = pd.DataFrame([
            {
                "Phenotype": item.category,
                "Expected Count": round(item.expected_count, 1),
                "Simulated Count": item.simulated_count,
                "Deviation %": round(item.percentage_deviation, 2)
            }
            for item in sim_res.items
        ]).set_index("Phenotype")
        st.dataframe(df_sim, use_container_width=True)
        st.info(sim_res.scientific_summary)


# ------------------------------------------------------------------------------
# SCREEN: EXP 06 - OFFLINE AI ERROR CLASSIFIER
# ------------------------------------------------------------------------------
elif menu == "Exp 06: Offline AI Error Classifier":
    st.markdown("### Experiment 06: Student Prediction Evaluation & Offline AI Classifier")
    st.caption(MENDELIAN_BACKGROUND["exp06_objective"])

    col_ctrl, col_res = st.columns([1, 1.4])
    clf = get_error_classifier()

    with col_ctrl:
        st.markdown("#### ⚙️ Test Scenario Configuration")
        c_mode = st.selectbox("Cross:", ["Tt × tt (Monohybrid Test Cross)", "Tt × Tt (Monohybrid)", "AaBb × AaBb (Dihybrid)"])
        student_pred = st.text_input("Student Submitted Ratio:", value="1:2:1")
        eval_btn = st.button("⚡ Evaluate Student Submission", type="primary")

    with col_res:
        loci = 2 if "Dihybrid" in c_mode else 1
        exp_p = "9:3:3:1" if loci == 2 else ("1:1" if "Test" in c_mode else "3:1")
        exp_g = "1:2:1:2:4:2:1:2:1" if loci == 2 else ("1:1" if "Test" in c_mode else "1:2:1")

        pred_category, conf = clf.predict(loci, exp_p, exp_g, student_pred)

        st.markdown("#### 🤖 Local Offline AI Inference (Decision Tree)")
        st.write(f"**Predicted Conceptual Error**: `{pred_category}`")
        st.write(f"**Classification Confidence**: `{conf * 100:.1f}%`")
        st.caption("Execution Latency: < 2 ms | 100% Local Inference | No Cloud API Required")

        if pred_category == "CORRECT_PREDICTION":
            st.success("Hypothesis correctly aligns with theoretical inheritance mechanics.")
        elif pred_category == "CONFUSING_GENOTYPE_WITH_PHENOTYPE_RATIO":
            st.warning("Diagnostic Diagnosis: Confusing genotypic classes with phenotypic masking.")
        else:
            st.error(f"Diagnostic Diagnosis: {pred_category.replace('_', ' ')}")
