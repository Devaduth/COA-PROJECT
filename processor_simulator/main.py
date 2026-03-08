"""
main.py — Streamlit GUI for the Processor Performance Analysis & Simulation Tool

Run with:
    cd processor_simulator
    streamlit run main.py

Sidebar navigation drives four pages:
    1. Processor Performance Calculator
    2. Pipeline Simulation
    3. Cache Performance Analyzer
    4. Amdahl's Law Speedup
"""

# ─────────────────────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from performance import compute_performance
from pipeline import (
    simulate_pipeline,
    pipeline_summary,
    generate_random_stalls,
    PipelineResult,
    STAGES,
    STAGE_DESCRIPTIONS,
    STALL_MARKER,
)
from cache import compute_amat, compute_amat_multilevel
from amdahl import compute_speedup, speedup_vs_processors
from visualization import (
    plot_cpi_vs_exec_time,
    plot_instruction_mix,
    plot_amdahl_curve,
    plot_amat_comparison,
    plot_pipeline_gantt,
    plot_performance_comparison,
)

# ─────────────────────────────────────────────────────────────
# Page config & custom CSS
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Processor Performance Simulator",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject lightweight academic styling
st.markdown(
    """
    <style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #6c757d !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }

    /* Page header accent bar */
    .block-container { padding-top: 1.5rem; }
    h1 { border-bottom: 3px solid #4C72B0; padding-bottom: 0.3rem; }
    h2 { color: #16213e; }
    h3 { color: #1a1a2e; }

    /* Table polish */
    table { font-size: 0.92rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# Sidebar — Navigation Menu
# ─────────────────────────────────────────────────────────────
st.sidebar.image(
    "https://img.icons8.com/fluency/96/processor.png",
    width=72,
)
st.sidebar.title("COA Simulation Tool")
st.sidebar.caption("Computer Organization & Architecture — Mini Project")

PAGES = [
    "🏠  Home",
    "⚡  Processor Performance Calculator",
    "🔁  Pipeline Simulation",
    "💾  Cache Performance Analyzer",
    "📈  Amdahl's Law Speedup",
]

selection = st.sidebar.radio("Navigate", PAGES, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Tech Stack**\n"
    "- Python 3\n"
    "- Streamlit\n"
    "- Matplotlib\n"
    "- Pandas / NumPy"
)
st.sidebar.markdown("---")
st.sidebar.caption("© 2026 COA Mini Project")


# ═══════════════════════════════════════════════════════════════
# PAGE: Home / Landing
# ═══════════════════════════════════════════════════════════════
if selection == PAGES[0]:
    st.title("🖥️ Processor Performance Analysis & Simulation Tool")
    st.markdown(
        """
        Welcome to the **Processor Performance Simulation Tool** — an interactive
        application built for academic demonstration of core **Computer
        Organisation & Architecture** concepts.

        Use the **sidebar** on the left to navigate between modules.
        """
    )

    st.markdown("---")

    # Feature cards in a 2×2 grid
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⚡ Performance Calculator")
        st.markdown(
            "Compute **execution time**, **MIPS**, and **average CPI** "
            "from an instruction mix with per-type CPI values and clock speed."
        )
        st.subheader("💾 Cache Analyzer")
        st.markdown(
            "Calculate **AMAT** (Average Memory Access Time) for single-level "
            "and two-level cache hierarchies."
        )

    with c2:
        st.subheader("🔁 Pipeline Simulation")
        st.markdown(
            "Visualise cycle-by-cycle execution of a **5-stage RISC pipeline** "
            "(IF → ID → EX → MEM → WB) with optional data-hazard stalls."
        )
        st.subheader("📈 Amdahl's Law")
        st.markdown(
            "Determine the **overall system speedup** achievable when only a "
            "fraction of the workload is enhanced, with interactive graphs."
        )

    st.markdown("---")
    st.info("👈 Select a module from the sidebar to begin.")


# ═══════════════════════════════════════════════════════════════
# PAGE 1 — Processor Performance Calculator
# ═══════════════════════════════════════════════════════════════
elif selection == PAGES[1]:
    st.title("⚡ Processor Performance Calculator")
    st.markdown(
        "Compute key CPU metrics from an **instruction mix**, per-type "
        "**CPI** values, and **clock cycle time**."
    )

    # ---------- Theory card ----------
    with st.expander("📖 Theory & Formulas", expanded=False):
        st.latex(r"\text{Total Instructions} = N_{\text{ALU}} + N_{\text{Load}} + N_{\text{Branch}}")
        st.latex(r"\text{Avg CPI} = \frac{\sum (N_i \times \text{CPI}_i)}{\text{Total Instructions}}")
        st.latex(r"\text{Exec Time} = \text{Total Cycles} \times \text{Clock Cycle Time}")
        st.latex(r"\text{MIPS} = \frac{\text{Total Instructions}}{\text{Exec Time} \times 10^6}")

    st.markdown("---")

    # ---------- Input section ----------
    st.subheader("Input Parameters")
    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown("**Instruction Counts**")
        alu_count    = st.number_input("ALU Instructions",    min_value=0, value=500, step=10, key="p_alu")
        load_count   = st.number_input("Load Instructions",   min_value=0, value=300, step=10, key="p_load")
        branch_count = st.number_input("Branch Instructions", min_value=0, value=200, step=10, key="p_branch")

    with col_b:
        st.markdown("**CPI per Type & Clock**")
        cpi_alu    = st.number_input("CPI — ALU",              min_value=0.1, value=1.0, step=0.1, key="p_cpi_alu")
        cpi_load   = st.number_input("CPI — Load",             min_value=0.1, value=3.0, step=0.1, key="p_cpi_load")
        cpi_branch = st.number_input("CPI — Branch",           min_value=0.1, value=2.0, step=0.1, key="p_cpi_br")
        clock_ns   = st.number_input("Clock Cycle Time (ns)",  min_value=0.01, value=0.5, step=0.05, key="p_clk")

    st.markdown("")
    run_perf = st.button("🚀  Calculate Performance", use_container_width=True, key="btn_perf")

    # ---------- Output section ----------
    if run_perf:
        results = compute_performance(
            alu_count, load_count, branch_count,
            cpi_alu, cpi_load, cpi_branch,
            clock_ns,
        )

        st.markdown("---")
        st.subheader("Results")

        # Metric cards row
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Instructions", f"{results['total_instructions']:,}")
        m2.metric("Average CPI",        f"{results['avg_cpi']:.4f}")
        m3.metric("Total Cycles",       f"{results['total_cycles']:,.2f}")
        m4.metric("Exec Time (s)",      f"{results['execution_time_sec']:.2e}")
        m5.metric("MIPS",               f"{results['mips']:,.2f}")

        # Detailed table
        st.markdown("")
        res_df = pd.DataFrame({
            "Metric": [
                "Total Instruction Count",
                "Average CPI (weighted)",
                "Total Execution Cycles",
                "Execution Time (seconds)",
                "MIPS (Million Instr / sec)",
            ],
            "Value": [
                f"{results['total_instructions']:,}",
                f"{results['avg_cpi']:.4f}",
                f"{results['total_cycles']:,.2f}",
                f"{results['execution_time_sec']:.10f}",
                f"{results['mips']:,.4f}",
            ],
        })
        st.table(res_df)

        # ---------- Visualizations ----------
        st.markdown("---")
        st.subheader("Visualizations")

        categories  = ["ALU", "Load", "Branch"]
        cpi_vals    = [cpi_alu, cpi_load, cpi_branch]
        counts_list = [alu_count, load_count, branch_count]
        exec_cycles = [c * cpi for c, cpi in zip(counts_list, cpi_vals)]

        viz1, viz2 = st.columns(2)
        with viz1:
            fig1 = plot_cpi_vs_exec_time(categories, cpi_vals, exec_cycles)
            st.pyplot(fig1)
        with viz2:
            fig2 = plot_instruction_mix(categories, counts_list)
            st.pyplot(fig2)

        # MIPS across clock speeds
        st.subheader("Performance Comparison — MIPS at Various Clock Speeds")
        clock_options = [0.25, 0.5, 1.0, 2.0, 4.0]
        labels_clk, mips_list = [], []
        for clk in clock_options:
            r = compute_performance(
                alu_count, load_count, branch_count,
                cpi_alu, cpi_load, cpi_branch, clk,
            )
            labels_clk.append(f"{clk} ns")
            mips_list.append(r["mips"])

        fig3 = plot_performance_comparison(labels_clk, mips_list)
        st.pyplot(fig3)


# ═══════════════════════════════════════════════════════════════
# PAGE 2 — Pipeline Simulation  (improved)
# ═══════════════════════════════════════════════════════════════
elif selection == PAGES[2]:
    st.title("🔁 5-Stage Pipeline Simulation")
    st.markdown(
        "Simulate the classic **IF → ID → EX → MEM → WB** pipeline "
        "and observe cycle-by-cycle instruction flow with hazard stalls."
    )

    # ── Theory expander ──────────────────────────────────────
    with st.expander("📖 Theory — Pipeline Stages & Hazards", expanded=False):
        theory_df = pd.DataFrame(
            [(stg, STAGE_DESCRIPTIONS[stg]) for stg in STAGES],
            columns=["Stage", "Description"],
        )
        st.table(theory_df)
        st.markdown(
            "**Ideal throughput:** CPI ≈ 1 once the pipeline is full.\n\n"
            "**Data hazards** occur when an instruction depends on the result "
            "of a preceding instruction that has not yet written back.  "
            "A *stall* (bubble) is inserted to resolve the hazard, increasing "
            "CPI above 1."
        )
        st.latex(r"\text{CPI}_{\text{actual}} = \text{CPI}_{\text{ideal}} + \text{Stall cycles per instruction}")

    st.markdown("---")

    # ── Configuration ────────────────────────────────────────
    st.subheader("⚙️ Configuration")

    num_instr = st.slider(
        "Number of Instructions",
        min_value=1, max_value=20, value=6,
        help="How many instructions to push through the pipeline.",
        key="pipe_n",
    )

    hazard_mode = st.radio(
        "Hazard / Stall Mode",
        ["No stalls (ideal)", "Manual stalls", "Random stalls"],
        horizontal=True,
        key="pipe_hazard_mode",
    )

    stall_after_list: list[int] = []
    stall_cycles = 1
    use_random = False
    rand_prob = 0.30
    rand_seed: int | None = None

    if hazard_mode == "Manual stalls":
        mc1, mc2 = st.columns(2, gap="large")
        with mc1:
            stall_input = st.text_input(
                "Stall after instruction # (comma-separated, 1-based)",
                value="2, 4",
                key="stall_input",
                help="e.g. '2, 4' → stall after I2 and I4",
            )
            try:
                stall_after_list = sorted(
                    set(
                        int(x.strip()) - 1
                        for x in stall_input.split(",")
                        if x.strip().isdigit() and 0 < int(x.strip()) < num_instr
                    )
                )
            except ValueError:
                stall_after_list = []
        with mc2:
            stall_cycles = st.number_input(
                "Bubble cycles per hazard", 1, 5, 1, key="stall_cyc",
            )

    elif hazard_mode == "Random stalls":
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            rand_prob = st.slider(
                "Hazard probability", 0.0, 1.0, 0.30, 0.05,
                help="Chance that each instruction triggers a data hazard.",
                key="rand_prob",
            )
        with rc2:
            stall_cycles = st.number_input(
                "Bubble cycles per hazard", 1, 5, 1, key="stall_cyc_r",
            )
        with rc3:
            rand_seed_input = st.number_input(
                "Random seed (for reproducibility)",
                min_value=0, value=42, step=1,
                key="rand_seed",
            )
            rand_seed = int(rand_seed_input)
        use_random = True

    st.markdown("")
    run_pipe = st.button(
        "🚀  Simulate Pipeline", use_container_width=True, key="btn_pipe",
    )

    # ── Run simulation ───────────────────────────────────────
    if run_pipe:
        result: PipelineResult = simulate_pipeline(
            num_instr,
            stall_after=stall_after_list,
            stall_cycles=stall_cycles,
            random_stalls=use_random,
            random_probability=rand_prob,
            random_seed=rand_seed,
        )

        df_pipe = result.table
        summary = result.summary

        st.markdown("---")

        # ── Stall report (if any) ────────────────────────────
        if result.stall_after:
            nice = ", ".join(f"I{i+1}" for i in result.stall_after)
            st.warning(
                f"**{result.total_stalls} stall cycle(s)** inserted after: {nice}"
            )
        else:
            st.success("No stalls — ideal pipeline execution.")

        # ── Colour-coded pipeline table ──────────────────────
        st.subheader("📋 Cycle-by-Cycle Pipeline Table")

        stage_colors = {
            "IF": "#4C72B0", "ID": "#DD8452", "EX": "#55A868",
            "MEM": "#C44E52", "WB": "#8172B3",
        }

        def _style_pipeline_cell(val):
            if val in stage_colors:
                return (
                    f"background-color: {stage_colors[val]}; color: #fff; "
                    "font-weight: 600; text-align: center; border-radius: 4px;"
                )
            if STALL_MARKER and str(val).startswith("⬤"):
                return (
                    "background-color: #e0e0e0; color: #555; "
                    "font-style: italic; text-align: center; border-radius: 4px;"
                )
            return "color: #ddd; text-align: center;"

        styled = df_pipe.style.map(_style_pipeline_cell)
        st.dataframe(
            styled,
            use_container_width=True,
            height=min(42 * len(df_pipe) + 55, 650),
        )

        # ── Stage colour legend ──────────────────────────────
        legend_cols = st.columns(len(STAGES) + 1)
        for col, stg in zip(legend_cols, STAGES):
            col.markdown(
                f"<span style='background:{stage_colors[stg]}; color:#fff; "
                f"padding:4px 14px; border-radius:5px; font-weight:700; "
                f"font-size:0.85rem;'>{stg}</span>",
                unsafe_allow_html=True,
            )
        legend_cols[-1].markdown(
            "<span style='background:#e0e0e0; color:#555; "
            "padding:4px 14px; border-radius:5px; font-style:italic; "
            "font-size:0.85rem;'>⬤ STALL</span>",
            unsafe_allow_html=True,
        )

        st.markdown("")

        # ── Summary metrics ──────────────────────────────────
        st.subheader("📊 Performance Summary")
        sm1, sm2, sm3 = st.columns(3)
        sm1.metric("Total Cycles",              summary["total_cycles"])
        sm2.metric("Ideal Cycles (no stalls)",  summary["ideal_cycles"])
        sm3.metric("Stall Cycles Inserted",     summary["total_stalls"])

        sm4, sm5, sm6 = st.columns(3)
        sm4.metric("CPI (Cycles Per Instruction)", f"{summary['cpi']:.2f}")
        sm5.metric("Pipeline Speedup vs Sequential", f"{summary['pipeline_speedup']:.2f}×")
        sm6.metric("Pipeline Efficiency",       f"{summary['efficiency_pct']:.1f}%")

        # ── Detailed breakdown table ─────────────────────────
        with st.expander("📝 Detailed Breakdown", expanded=False):
            detail = pd.DataFrame({
                "Metric": [
                    "Instructions",
                    "Pipeline Stages",
                    "Total Clock Cycles",
                    "Ideal Cycles (N + stages − 1)",
                    "Sequential Cycles (N × stages)",
                    "Stall Events",
                    "Stall Cycles (total)",
                    "CPI",
                    "Speedup over Sequential",
                    "Efficiency (ideal / actual)",
                ],
                "Value": [
                    num_instr,
                    len(STAGES),
                    summary["total_cycles"],
                    summary["ideal_cycles"],
                    summary["no_pipe_cycles"],
                    len(result.stall_after),
                    summary["total_stalls"],
                    f"{summary['cpi']:.4f}",
                    f"{summary['pipeline_speedup']:.4f}×",
                    f"{summary['efficiency_pct']:.2f}%",
                ],
            })
            st.table(detail)

        # ── Gantt chart ──────────────────────────────────────
        st.subheader("🎨 Pipeline Gantt Chart")
        fig_gantt = plot_pipeline_gantt(
            num_instr,
            result.start_cycles,
            STAGES,
            stall_positions=result.stall_after,
            stall_width=stall_cycles,
        )
        st.pyplot(fig_gantt)


# ═══════════════════════════════════════════════════════════════
# PAGE 3 — Cache Performance Analyzer
# ═══════════════════════════════════════════════════════════════
elif selection == PAGES[3]:
    st.title("💾 Cache Performance Analyzer")
    st.markdown("Evaluate memory hierarchy efficiency via **AMAT** (Average Memory Access Time).")

    with st.expander("📖 Theory & Formula", expanded=False):
        st.latex(r"\text{AMAT} = \text{Hit Time} + (\text{Miss Rate} \times \text{Miss Penalty})")
        st.markdown(
            "For a **two-level** hierarchy:\n\n"
            r"$\text{AMAT}_{\text{eff}} = \text{HT}_{L1} + \text{MR}_{L1}"
            r"\times (\text{HT}_{L2} + \text{MR}_{L2} \times \text{MP}_{L2})$"
        )

    st.markdown("---")

    mode = st.radio(
        "Analysis mode",
        ["Single Level (L1)", "Two-Level (L1 + L2)"],
        horizontal=True,
        key="cache_mode",
    )

    if mode == "Single Level (L1)":
        st.subheader("L1 Cache Parameters")
        cc1, cc2, cc3 = st.columns(3)
        hit_time  = cc1.number_input("Hit Time (cycles/ns)",     min_value=0.0, value=1.0,   step=0.1,  key="ht")
        miss_rate = cc2.number_input("Miss Rate (0 – 1)",        min_value=0.0, max_value=1.0, value=0.05, step=0.01, key="mr")
        miss_pen  = cc3.number_input("Miss Penalty (cycles/ns)", min_value=0.0, value=100.0, step=1.0,  key="mp")

        st.markdown("")
        if st.button("🚀  Compute AMAT", use_container_width=True, key="btn_amat"):
            amat = compute_amat(hit_time, miss_rate, miss_pen)

            st.markdown("---")
            st.subheader("Result")
            st.metric("AMAT", f"{amat:.4f} cycles / ns")

            # Breakdown table
            br_df = pd.DataFrame({
                "Component": ["Hit Time", "Miss Rate × Miss Penalty", "AMAT"],
                "Value": [
                    f"{hit_time:.4f}",
                    f"{miss_rate:.4f} × {miss_pen:.2f} = {miss_rate * miss_pen:.4f}",
                    f"{amat:.4f}",
                ],
            })
            st.table(br_df)

            # Sensitivity: vary miss rate
            st.subheader("Sensitivity — AMAT vs Miss Rate")
            mr_range = [r / 100 for r in range(1, 51)]
            amats = [compute_amat(hit_time, mr, miss_pen) for mr in mr_range]
            fig_s, ax_s = plt.subplots(figsize=(8, 4))
            ax_s.plot(mr_range, amats, color="#4C72B0", linewidth=2)
            ax_s.axhline(y=amat, color="#C44E52", linestyle="--", label=f"Current ({miss_rate:.0%})")
            ax_s.set_xlabel("Miss Rate", fontsize=11)
            ax_s.set_ylabel("AMAT", fontsize=11)
            ax_s.set_title("AMAT Sensitivity to Miss Rate", fontsize=13, fontweight="bold")
            ax_s.legend()
            ax_s.grid(True, linestyle=":", alpha=0.5)
            fig_s.tight_layout()
            st.pyplot(fig_s)

    else:
        st.subheader("L1 Cache Parameters")
        lc1, lc2 = st.columns(2)
        ht_l1 = lc1.number_input("L1 Hit Time",  min_value=0.0, value=1.0,  step=0.1,  key="ht_l1")
        mr_l1 = lc2.number_input("L1 Miss Rate", min_value=0.0, max_value=1.0, value=0.05, step=0.01, key="mr_l1")

        st.subheader("L2 Cache Parameters")
        lc3, lc4, lc5 = st.columns(3)
        ht_l2 = lc3.number_input("L2 Hit Time",     min_value=0.0, value=5.0,   step=0.5,  key="ht_l2")
        mr_l2 = lc4.number_input("L2 Miss Rate",    min_value=0.0, max_value=1.0, value=0.10, step=0.01, key="mr_l2")
        mp_l2 = lc5.number_input("L2 Miss Penalty", min_value=0.0, value=200.0, step=5.0,  key="mp_l2")

        st.markdown("")
        if st.button("🚀  Compute AMAT (Two-Level)", use_container_width=True, key="btn_amat2"):
            res = compute_amat_multilevel(ht_l1, mr_l1, ht_l2, mr_l2, mp_l2)

            st.markdown("---")
            st.subheader("Results")

            rm1, rm2 = st.columns(2)
            rm1.metric("L2 AMAT",        f"{res['amat_l2']:.4f}")
            rm2.metric("Effective AMAT",  f"{res['effective_amat']:.4f}")

            fig_amat = plot_amat_comparison(
                ["L2-Only AMAT", "Effective (L1 + L2) AMAT"],
                [res["amat_l2"], res["effective_amat"]],
            )
            st.pyplot(fig_amat)


# ═══════════════════════════════════════════════════════════════
# PAGE 4 — Amdahl's Law Speedup
# ═══════════════════════════════════════════════════════════════
elif selection == PAGES[4]:
    st.title("📈 Amdahl's Law Speedup Calculator")
    st.markdown("Determine the **theoretical speedup** of a system when a fraction of the workload is enhanced.")

    with st.expander("📖 Theory & Formula", expanded=False):
        st.latex(r"\text{Speedup}_{\text{overall}} = \frac{1}{(1 - P) + \dfrac{P}{S}}")
        st.markdown(
            "- **P** — fraction of execution time that can be improved  (0 ≤ P ≤ 1)\n"
            "- **S** — speedup of the enhanced (parallel) portion  (S ≥ 1)\n"
            "- As S → ∞, Speedup → 1 / (1 − P)"
        )

    st.markdown("---")

    st.subheader("Input Parameters")
    ac1, ac2 = st.columns(2, gap="large")

    with ac1:
        par_frac = st.slider(
            "Parallel / Enhanced Fraction (P)",
            0.0, 1.0, 0.75, 0.01,
            key="amd_p",
            help="Fraction of the workload that benefits from enhancement.",
        )
    with ac2:
        speedup_s = st.number_input(
            "Speedup of Enhanced Part (S)",
            min_value=1.0, value=8.0, step=0.5,
            key="amd_s",
        )

    st.markdown("")
    run_amd = st.button("🚀  Compute Speedup", use_container_width=True, key="btn_amd")

    if run_amd:
        sp = compute_speedup(par_frac, speedup_s)

        st.markdown("---")
        st.subheader("Result")

        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Parallel Fraction (P)", f"{par_frac:.2f}")
        rc2.metric("Enhanced Speedup (S)",  f"{speedup_s:.2f}×")
        rc3.metric("Overall Speedup",       f"{sp:.4f}×")

        # Speedup curve
        st.subheader("Speedup vs Number of Processors")
        curve = speedup_vs_processors(par_frac, max_processors=64)
        fig_amd = plot_amdahl_curve(
            curve["processors"], curve["speedups"],
            curve["max_speedup"], par_frac,
        )
        st.pyplot(fig_amd)

        st.info(f"**Theoretical maximum** speedup (S → ∞) = **{curve['max_speedup']:.4f}×**")

        # Multi-P comparison
        st.subheader("Comparison — Speedup at Different Parallel Fractions")
        p_values = [0.50, 0.75, 0.90, 0.95, 0.99]
        comp_data = []
        for p in p_values:
            c = speedup_vs_processors(p, max_processors=64)
            comp_data.append({"P": p, "Max Speedup (S→∞)": c["max_speedup"],
                              f"Speedup @ S={int(speedup_s)}": compute_speedup(p, speedup_s)})
        st.table(pd.DataFrame(comp_data))


# ─────────────────────────────────────────────────────────────
# Footer (always visible)
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.82rem;'>"
    "COA Mini Project — <b>Processor Performance Analysis & Simulation Tool</b><br>"
    "Built with Python · Streamlit · Matplotlib · Pandas"
    "</div>",
    unsafe_allow_html=True,
)
