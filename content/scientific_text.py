"""
Scientific Educational Content Module
Academic Genetics Research System (Postgraduate M.Sc. Genetics)

Academically rigorous, reference-grade curriculum text for postgraduate students.
"""

MENDELIAN_BACKGROUND = {
    "exp01_title": "Experiment 01: Monohybrid Inheritance — Allelic Segregation and Complete Dominance",
    "exp01_objective": (
        "Investigate the transmission of a single autosomal gene locus with two alleles under a strictly defined "
        "complete-dominance model. Calculate theoretical gametic segregation probabilities during meiosis I, "
        "construct Punnett squares, and derive genotypic (1:2:1) and phenotypic (3:1) distributions."
    ),
    "exp01_scientific_basis": (
        "Mendel's First Law (Law of Segregation):\n"
        "During gametogenesis, the two alleles at any locus segregate from each other into separate gametes during Anaphase I "
        "of meiosis, such that each gamete carries exactly one allele with equal probability (p = 0.5 for a heterozygote).\n\n"
        "Molecular Basis of Complete Dominance:\n"
        "Dominance is an allelic interaction, not an inherent physical power. In pea height (Le/le locus, GA 3-beta-hydroxylase), "
        "the dominant 'T' (or 'Le') allele encodes a functional enzyme catalyzing active gibberellin synthesis. The recessive 't' (or 'le') "
        "allele contains an alanine-to-threonine missense mutation causing severe catalytic loss. Because a single functional copy in a "
        "heterozygote (Tt) produces sufficient gibberellin to attain normal internode elongation (haplosufficiency), the phenotype of Tt "
        "is indistinguishable from TT. Dominance is thus a physiological threshold effect, NOT a universal law of genetics."
    ),

    "exp02_title": "Experiment 02: Dihybrid Inheritance — Independent Assortment and Two-Locus Combinatorics",
    "exp02_objective": (
        "Investigate the simultaneous inheritance of two distinct autosomal gene loci. Test whether alleles at separate "
        "loci segregate independently during gamete formation, construct a 4 × 4 Punnett square, and evaluate the conditions "
        "governing the classic 9:3:3:1 F2 phenotypic distribution."
    ),
    "exp02_scientific_basis": (
        "Mendel's Second Law (Law of Independent Assortment):\n"
        "Alleles at separate, non-homologous gene loci assort independently during gamete formation. "
        "The chromosomal basis is the random, independent alignment of non-homologous bivalents on the equatorial plate during Metaphase I of meiosis.\n\n"
        "Product Rule of Probability:\n"
        "P(A_ ∩ B_) = P(A_) × P(B_) = (3/4) × (3/4) = 9/16\n"
        "P(A_ ∩ bb) = P(A_) × P(bb) = (3/4) × (1/4) = 3/16\n"
        "P(aa ∩ B_) = P(aa) × P(B_) = (1/4) × (3/4) = 3/16\n"
        "P(aa ∩ bb) = P(aa) × P(bb) = (1/4) × (1/4) = 1/16\n\n"
        "Critical Limitation & Qualifications:\n"
        "Independent assortment holds strictly when loci reside on separate chromosomes or are separated by ≥ 50 cM on the same chromosome "
        "(genetic synteny with complete cross-over equilibrium). Syntenic genes with recombination frequency r < 0.50 exhibit genetic linkage "
        "and deviate markedly from the 9:3:3:1 ratio."
    ),

    "exp03_title": "Experiment 03: Test Cross Analysis — Zygosity Discrimination in Dominant Phenotypes",
    "exp03_objective": (
        "Discriminate between homozygous dominant (TT / AA) and heterozygous (Tt / Aa) individuals displaying identical "
        "dominant phenotypes by crossing the test subject with a homozygous recessive tester (tt / aa). Formulate competing hypotheses "
        "and evaluate observed offspring distributions against expected outcomes."
    ),
    "exp03_scientific_basis": (
        "Rationale of the Test Cross:\n"
        "Because the homozygous recessive parent contributes only recessive alleles (t or a) in 100% of its gametes, the tester gametes "
        "act as a transparent genetic background. The phenotypic distribution of the resulting offspring directly reflects the gametic "
        "output of the unknown test individual.\n\n"
        "Statistical Interpretation Caveat:\n"
        "If a test cross produces even a single recessive offspring (tt), the unknown parent is definitively identified as heterozygous (Tt) "
        "(excluding de novo mutation). However, if an experiment yields 10 tall offspring and 0 dwarf offspring, this does NOT prove with "
        "absolute certainty that the parent is TT; under H₀: Aa × aa, the probability of obtaining 10 tall offspring purely by chance is "
        "(0.5)¹⁰ = 0.000976 (p < 0.001). We state hypotheses in terms of statistical likelihood rather than dogmatic certainty."
    ),

    "exp04_title": "Experiment 04: Biostatistical Validation — Pearson Chi-Square Goodness-of-Fit",
    "exp04_objective": (
        "Formulate null (H₀) and alternative (H₁) hypotheses for genetic inheritance ratios. Compute the Pearson Chi-Square test statistic, "
        "determine degrees of freedom, derive p-values, verify Cochran's rule for minimum expected frequencies, and render academically sound "
        "statistical conclusions without committing common epistemic fallacies."
    ),
    "exp04_scientific_basis": (
        "Chi-Square Goodness-of-Fit Statistic:\n"
        "χ² = Σ [ (Oᵢ - Eᵢ)² / Eᵢ ]\n"
        "Degrees of freedom: df = k - 1 (where k is the number of mutually exclusive categorical phenotypic classes).\n\n"
        "Cochran's Rule & Small-Sample Warnings:\n"
        "The continuous chi-square distribution is an asymptotic approximation to the discrete multinomial distribution. If any expected "
        "cell frequency Eᵢ < 5 (or if N < 20), the approximation degrades, inflating Type I error rates. In such cases, exact multinomial "
        "probabilities or Yates' correction for continuity (for df = 1) must be consulted.\n\n"
        "Academic Epistemic Standard:\n"
        "A non-significant result (p ≥ 0.05) indicates failure to reject the null hypothesis; it NEVER proves that H₀ is objectively true. "
        "Conversely, rejecting H₀ indicates significant departure from Mendelian proportions, requiring investigation into biological phenomena "
        "such as linkage, epistatic lethality, or meiotic drive."
    ),

    "exp05_title": "Experiment 05: Population Simulation — Stochasticity, Sampling Variance, and Law of Large Numbers",
    "exp05_objective": (
        "Demonstrate the impact of finite population sampling on observed genetic ratios. Compare empirical cohorts (N = 20, 50, 100, 500, 1000) "
        "against theoretical Mendelian probabilities using stochastic multinomial sampling with reproducible random seeds."
    ),
    "exp05_scientific_basis": (
        "Sampling Variance in Genetics:\n"
        "Individual fertilization events are independent stochastic Bernoulli trials. In a monohybrid cross (Tt × Tt), the variance of the sample "
        "proportion is given by Var(p̂) = p(1 - p) / N. Consequently, as population size N increases, the standard error SE = sqrt(p(1 - p) / N) "
        "decreases as 1 / sqrt(N). Small student cohorts (e.g., N = 20) routinely deviate from 3:1 by 15-25% without violating Mendelian mechanics."
    ),

    "exp06_title": "Experiment 06: Student Diagnostic Assessment — Deterministic Genetics Authority & Offline ML",
    "exp06_objective": (
        "Evaluate student predictions across monohybrid, dihybrid, and test crosses using a deterministic genetics calculation engine, "
        "coupled with an offline Decision Tree machine-learning classifier to categorize conceptual root-cause errors."
    ),
    "exp06_scientific_basis": (
        "Genetics Error Taxonomy:\n"
        "1. Confusing Genotype with Phenotype Ratio: Failing to account for phenotypic masking by dominant alleles in heterozygotes.\n"
        "2. Incorrect Dominance Assumption: Assuming incomplete dominance, codominance, or equal phenotypic splits in complete-dominance crosses.\n"
        "3. Segregation Failure: Violation of equal meiotic disjunction during anaphase I.\n"
        "4. Independent Assortment Failure: Applying single-gene ratios (3:1) to multi-locus dihybrid crosses.\n"
        "5. Sampling Variance Misinterpretation: Attributing normal binomial sampling fluctuations to theoretical model failure."
    )
}
