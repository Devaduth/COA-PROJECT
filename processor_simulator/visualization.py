"""
visualization.py — Visualization Module (Matplotlib Charts)

Provides reusable charting functions consumed by the Streamlit GUI.
All functions return a matplotlib Figure object so the caller can
embed it with st.pyplot(fig).

Charts included:
    1. CPI vs Execution Time bar chart
    2. Instruction-mix pie chart
    3. Amdahl's Law speedup curve
    4. AMAT comparison bar chart
    5. Pipeline stage Gantt-style chart
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patheffects as pe
import numpy as np


# ──────────────────────────────────────────────
# Colour palette (consistent look across charts)
# ──────────────────────────────────────────────
PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860"]

# Extended presentation-grade palette
_ACCENT   = "#2B6CB0"   # deep blue accent
_BG       = "#FAFBFC"   # off-white figure background
_GRID_CLR = "#DEE2E6"   # subtle grid
_TEXT_CLR = "#212529"   # near-black text
_SUB_CLR  = "#6C757D"   # muted subtitle


def _apply_theme(ax, *, title: str = "", subtitle: str = "",
                 xlabel: str = "", ylabel: str = "",
                 remove_spines: tuple = ("top", "right")):
    """Apply a consistent academic-presentation theme to an Axes."""
    for spine in remove_spines:
        ax.spines[spine].set_visible(False)
    for spine in ("bottom", "left"):
        if spine not in remove_spines:
            ax.spines[spine].set_color(_GRID_CLR)
    ax.tick_params(colors=_TEXT_CLR, labelsize=10)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12, color=_TEXT_CLR, labelpad=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12, color=_TEXT_CLR, labelpad=8)
    if title:
        ax.set_title(title, fontsize=15, fontweight="bold", color=_TEXT_CLR, pad=14)
    if subtitle:
        ax.text(0.5, 1.01, subtitle, transform=ax.transAxes,
                ha="center", fontsize=10, color=_SUB_CLR, style="italic")


def plot_cpi_vs_exec_time(categories: list[str], cpis: list[float], exec_times: list[float]):
    """
    Grouped bar chart — CPI (left axis) and Execution Time (right axis)
    for each instruction category.

    Parameters
    ----------
    categories : list[str]
        Instruction type labels, e.g. ["ALU", "Load", "Branch"].
    cpis : list[float]
        CPI value for each category.
    exec_times : list[float]
        Execution-time contribution (cycles) for each category.

    Returns
    -------
    matplotlib.figure.Figure
    """
    x = np.arange(len(categories))
    width = 0.32

    fig, ax1 = plt.subplots(figsize=(9, 5.5))
    fig.patch.set_facecolor(_BG)
    ax1.set_facecolor(_BG)

    # ── CPI bars (left y-axis) ──────────────────────
    cpi_color = "#3182CE"
    bars1 = ax1.bar(
        x - width / 2, cpis, width,
        label="CPI", color=cpi_color, edgecolor="white",
        linewidth=1.2, zorder=3,
    )
    ax1.set_ylabel("Cycles Per Instruction (CPI)", fontsize=12,
                    color=cpi_color, labelpad=10)
    ax1.tick_params(axis="y", labelcolor=cpi_color, labelsize=10)

    # Data labels on CPI bars
    for bar, val in zip(bars1, cpis):
        ax1.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
            f"{val:.2f}", ha="center", va="bottom", fontsize=9,
            fontweight="bold", color=cpi_color,
        )

    # ── Execution-time bars (right y-axis) ──────────
    exec_color = "#E53E3E"
    ax2 = ax1.twinx()
    bars2 = ax2.bar(
        x + width / 2, exec_times, width,
        label="Exec Cycles", color=exec_color, edgecolor="white",
        linewidth=1.2, alpha=0.85, zorder=3,
    )
    ax2.set_ylabel("Execution Cycles", fontsize=12,
                    color=exec_color, labelpad=10)
    ax2.tick_params(axis="y", labelcolor=exec_color, labelsize=10)

    # Data labels on exec-time bars
    for bar, val in zip(bars2, exec_times):
        ax2.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
            f"{val:,.0f}", ha="center", va="bottom", fontsize=9,
            fontweight="bold", color=exec_color,
        )

    # ── Axes styling ────────────────────────────────
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=11, color=_TEXT_CLR)
    ax1.set_title(
        "CPI vs Execution Cycles by Instruction Type",
        fontsize=15, fontweight="bold", color=_TEXT_CLR, pad=18,
    )
    ax1.text(
        0.5, 1.01,
        r"Exec Cycles = Instruction Count$_i$ $\times$ CPI$_i$",
        transform=ax1.transAxes, ha="center",
        fontsize=10, color=_SUB_CLR, style="italic",
    )

    # Subtle grid only on left y-axis
    ax1.yaxis.grid(True, linestyle=":", alpha=0.4, color=_GRID_CLR, zorder=0)
    ax1.set_axisbelow(True)
    for spine in ("top", "right"):
        ax1.spines[spine].set_visible(False)
    for spine in ("top", "left"):
        ax2.spines[spine].set_visible(False)
    ax1.spines["left"].set_color(_GRID_CLR)
    ax1.spines["bottom"].set_color(_GRID_CLR)
    ax2.spines["right"].set_color(_GRID_CLR)

    # Combined legend (bottom-centre)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lines1 + lines2, labels1 + labels2,
        loc="upper center", ncol=2, frameon=True,
        fancybox=True, shadow=False, fontsize=10,
        edgecolor=_GRID_CLR,
    )

    fig.tight_layout()
    return fig


def plot_instruction_mix(labels: list[str], counts: list[int]):
    """
    Modern donut chart showing the instruction-type distribution.

    Parameters
    ----------
    labels : list[str]
        Category names (e.g. ["ALU", "Load", "Branch"]).
    counts : list[int]
        Instruction counts per category.

    Returns
    -------
    matplotlib.figure.Figure
    """
    # Professional colour set (up to 8 categories)
    DONUT_COLORS = [
        "#3182CE", "#E53E3E", "#38A169", "#D69E2E",
        "#805AD5", "#DD6B20", "#319795", "#B83280",
    ]
    colors = DONUT_COLORS[: len(labels)]
    total = sum(counts)

    fig, ax = plt.subplots(figsize=(7, 6))
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_BG)

    # Donut wedges
    wedges, texts, autotexts = ax.pie(
        counts,
        labels=None,            # labels go in legend instead
        autopct="%1.1f%%",
        colors=colors,
        startangle=140,
        pctdistance=0.78,
        wedgeprops={"width": 0.45, "edgecolor": "white", "linewidth": 2.5},
        textprops={"fontsize": 10, "fontweight": "bold", "color": "white"},
    )
    # White glow on percentage text for readability
    for at in autotexts:
        at.set_path_effects([
            pe.withStroke(linewidth=2.5, foreground="white"),
        ])
        at.set_color(_TEXT_CLR)

    # Centre annotation
    ax.text(
        0, 0, f"{total:,}\nTotal",
        ha="center", va="center",
        fontsize=18, fontweight="bold", color=_TEXT_CLR,
    )

    # External legend
    legend_labels = [
        f"{lab}  ({cnt:,} — {cnt / total * 100:.1f}%)"
        for lab, cnt in zip(labels, counts)
    ]
    ax.legend(
        wedges, legend_labels,
        title="Instruction Types", title_fontsize=11,
        loc="center left", bbox_to_anchor=(0.95, 0.5),
        fontsize=10, frameon=True, fancybox=True,
        edgecolor=_GRID_CLR,
    )

    ax.set_title(
        "Instruction Mix Distribution",
        fontsize=15, fontweight="bold", color=_TEXT_CLR, pad=16,
    )
    ax.text(
        0.5, 0.97,
        "Proportion of each instruction type in the workload",
        transform=ax.transAxes, ha="center",
        fontsize=10, color=_SUB_CLR, style="italic",
    )

    fig.tight_layout()
    return fig


def plot_amdahl_curve(processors: list[int], speedups: list[float], max_speedup: float, parallel_fraction: float):
    """
    Line chart — Amdahl's Law speedup vs number of processors.

    Parameters
    ----------
    processors : list[int]
    speedups : list[float]
    max_speedup : float
        Theoretical limit (dashed horizontal line).
    parallel_fraction : float
        Used in the subtitle.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(processors, speedups, color=PALETTE[0], linewidth=2.5, label="Speedup")
    ax.axhline(y=max_speedup, color=PALETTE[3], linestyle="--", linewidth=1.5,
               label=f"Theoretical max = {max_speedup:.2f}")
    ax.set_xlabel("Number of Processors (S)", fontsize=12)
    ax.set_ylabel("Overall Speedup", fontsize=12)
    ax.set_title(f"Amdahl's Law  (P = {parallel_fraction})", fontsize=14, fontweight="bold")
    ax.legend(fontsize=11)
    ax.grid(True, linestyle=":", alpha=0.6)
    fig.tight_layout()
    return fig


def plot_amat_comparison(labels: list[str], amats: list[float]):
    """
    Horizontal bar chart comparing AMAT values across configurations.

    Parameters
    ----------
    labels : list[str]
        Configuration names.
    amats : list[float]
        Corresponding AMAT values.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(8, max(4, len(labels) * 0.8)))
    colors = PALETTE[: len(labels)]
    bars = ax.barh(labels, amats, color=colors, edgecolor="white", height=0.5)
    ax.set_xlabel("AMAT (cycles / ns)", fontsize=12)
    ax.set_title("Cache AMAT Comparison", fontsize=14, fontweight="bold")
    # Value labels on bars
    for bar, val in zip(bars, amats):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}", va="center", fontsize=11)
    fig.tight_layout()
    return fig


def plot_pipeline_gantt(
    num_instructions: int,
    start_cycles: list[int],
    stages: list[str],
    stall_positions: list[int] | None = None,
    stall_width: int = 1,
):
    """
    Gantt-style chart showing pipeline occupancy per instruction,
    with optional stall-bubble markers.

    Parameters
    ----------
    num_instructions : int
    start_cycles : list[int]
        0-based start cycle for each instruction.
    stages : list[str]
        Stage names, e.g. ["IF", "ID", "EX", "MEM", "WB"].
    stall_positions : list[int] | None
        0-based instruction indices after which stalls were inserted.
    stall_width : int
        Number of bubble cycles per stall event.

    Returns
    -------
    matplotlib.figure.Figure
    """
    if stall_positions is None:
        stall_positions = []
    stall_set = set(stall_positions)

    num_stages = len(stages)
    stage_colors = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(stages)}
    stall_color = "#AAAAAA"

    total_vis_cycles = start_cycles[-1] + num_stages if start_cycles else num_stages

    fig, ax = plt.subplots(
        figsize=(max(10, total_vis_cycles * 0.55), num_instructions * 0.6 + 1.5),
    )

    for instr in range(num_instructions):
        for s_idx, stage in enumerate(stages):
            cycle = start_cycles[instr] + s_idx
            ax.broken_barh(
                [(cycle, 1)],
                (instr * 1.4, 0.9),
                facecolors=stage_colors[stage],
                edgecolors="white",
                linewidth=1.2,
            )
            ax.text(
                cycle + 0.5, instr * 1.4 + 0.45, stage,
                ha="center", va="center", fontsize=8,
                fontweight="bold", color="white",
            )

        # Draw stall bubble(s) after this instruction
        if instr in stall_set:
            for b in range(stall_width):
                bcycle = start_cycles[instr] + 1 + b  # bubble sits after IF
                ax.broken_barh(
                    [(bcycle, 1)],
                    (instr * 1.4 + 0.95, 0.35),
                    facecolors=stall_color,
                    edgecolors="#666",
                    linewidth=0.8,
                    hatch="///",
                )
                ax.text(
                    bcycle + 0.5, instr * 1.4 + 1.12, "stall",
                    ha="center", va="center", fontsize=6,
                    color="#555", style="italic",
                )

    ax.set_yticks([i * 1.4 + 0.45 for i in range(num_instructions)])
    ax.set_yticklabels([f"I{i+1}" for i in range(num_instructions)], fontsize=10)
    ax.set_xticks(range(total_vis_cycles + 1))
    ax.set_xticklabels([str(c) for c in range(total_vis_cycles + 1)], fontsize=8)
    ax.set_xlabel("Clock Cycle", fontsize=12)
    ax.set_title("Pipeline Execution (Gantt View)", fontsize=14, fontweight="bold")
    ax.set_xlim(-0.2, total_vis_cycles + 0.2)
    ax.invert_yaxis()
    ax.grid(True, axis="x", linestyle=":", alpha=0.5)
    fig.tight_layout()
    return fig


def plot_performance_comparison(labels: list[str], mips_values: list[float]):
    """
    Horizontal bar chart comparing MIPS across configurations,
    ranked from best to worst with relative-performance labels.

    Parameters
    ----------
    labels : list[str]
        Configuration / scenario names.
    mips_values : list[float]
        MIPS for each scenario.

    Returns
    -------
    matplotlib.figure.Figure
    """
    # Sort ascending so highest MIPS is at the top visually
    order = sorted(range(len(mips_values)), key=lambda i: mips_values[i])
    sorted_labels = [labels[i] for i in order]
    sorted_vals   = [mips_values[i] for i in order]
    best_val = max(sorted_vals) if sorted_vals else 1

    # Gradient colours: light-to-dark blue proportional to value
    cmap = plt.cm.Blues
    norm_vals = [(v / best_val) * 0.65 + 0.25 for v in sorted_vals]  # range [0.25, 0.90]
    bar_colors = [cmap(n) for n in norm_vals]

    fig, ax = plt.subplots(figsize=(9, max(4.5, len(labels) * 0.85 + 1)))
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_BG)

    bars = ax.barh(
        sorted_labels, sorted_vals,
        color=bar_colors, edgecolor="white",
        height=0.55, linewidth=1.5, zorder=3,
    )

    # Value + relative-% label on each bar
    for bar, val in zip(bars, sorted_vals):
        pct = (val / best_val) * 100 if best_val else 0
        badge = "  ★ Best" if val == best_val else f"  ({pct:.0f}%)"
        ax.text(
            bar.get_width() + best_val * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{val:,.2f} MIPS{badge}",
            va="center", fontsize=10, fontweight="bold",
            color=_ACCENT if val == best_val else _TEXT_CLR,
        )

    _apply_theme(
        ax,
        title="Performance Comparison (MIPS)",
        subtitle=r"MIPS = Instruction Count / (Execution Time $\times$ 10$^6$)",
        xlabel="MIPS (Million Instructions Per Second)",
        remove_spines=("top", "right", "bottom"),
    )
    ax.xaxis.grid(True, linestyle=":", alpha=0.45, color=_GRID_CLR, zorder=0)
    ax.set_axisbelow(True)

    # Leave right margin for labels
    x_max = best_val * 1.35 if best_val else 1
    ax.set_xlim(0, x_max)

    fig.tight_layout()
    return fig
