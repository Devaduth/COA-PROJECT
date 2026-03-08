"""
pipeline.py — 5-Stage CPU Pipeline Simulator  (improved)

Simulates a classic RISC 5-stage pipeline:
    IF  → Instruction Fetch
    ID  → Instruction Decode / Register Read
    EX  → Execute / ALU Operation
    MEM → Memory Access
    WB  → Write Back

Features
--------
* Cycle-by-cycle execution table as a coloured pandas DataFrame.
* Three hazard / stall modes:
    1.  **No stalls** — ideal pipeline.
    2.  **Manual stalls** — user picks which instructions cause a stall.
    3.  **Random stalls** — stalls are inserted at random positions to
        model unpredictable data hazards (seed-controlled for
        reproducibility in a classroom demo).
* Stall rows appear explicitly in the table as "⬤ STALL" so students
  can see exactly where bubbles are injected.
* Rich summary statistics: total cycles, ideal cycles, stall count,
  CPI, pipeline speedup, and efficiency percentage.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

import pandas as pd

# ──────────────────────────────────────────────
#  Constants
# ──────────────────────────────────────────────
STAGES: list[str] = ["IF", "ID", "EX", "MEM", "WB"]

STAGE_DESCRIPTIONS: dict[str, str] = {
    "IF":  "Instruction Fetch — read instruction from memory",
    "ID":  "Instruction Decode — decode opcode & read registers",
    "EX":  "Execute — ALU operation / address calculation",
    "MEM": "Memory Access — load / store to data memory",
    "WB":  "Write Back — write result into the register file",
}

# Label used inside stall-bubble cells
STALL_MARKER = "⬤ STALL"


# ──────────────────────────────────────────────
#  Data class returned by the simulator
# ──────────────────────────────────────────────
@dataclass
class PipelineResult:
    """Bundles every output of a single simulation run."""

    table: pd.DataFrame                    # cycle-by-cycle table (rows = instr/stall, cols = cycles)
    start_cycles: list[int]                # 0-based start cycle per *real* instruction
    stall_after: list[int]                 # 0-based instruction indices that caused stalls
    stall_cycles_per_hazard: int           # bubble width per stall event
    num_instructions: int
    total_stalls: int = 0                  # total bubble rows inserted
    summary: dict = field(default_factory=dict)


# ──────────────────────────────────────────────
#  Random-stall generator
# ──────────────────────────────────────────────
def generate_random_stalls(
    num_instructions: int,
    probability: float = 0.30,
    seed: int | None = None,
) -> list[int]:
    """
    Return a sorted list of 0-based instruction indices after which a
    stall will be inserted.

    Parameters
    ----------
    num_instructions : int
        Total instruction count (stalls can appear after I0 … I(n-2)).
    probability : float
        Per-instruction probability of a data hazard (0–1).
    seed : int | None
        Random seed for reproducibility.  ``None`` → non-deterministic.

    Returns
    -------
    list[int]
        Sorted 0-based indices.
    """
    rng = random.Random(seed)
    # A stall after the *last* instruction has no visible effect, so skip it.
    candidates = range(num_instructions - 1) if num_instructions > 1 else range(0)
    return sorted(i for i in candidates if rng.random() < probability)


# ──────────────────────────────────────────────
#  Core simulator
# ──────────────────────────────────────────────
def simulate_pipeline(
    num_instructions: int,
    stall_after: list[int] | None = None,
    stall_cycles: int = 1,
    *,
    random_stalls: bool = False,
    random_probability: float = 0.30,
    random_seed: int | None = None,
) -> PipelineResult:
    """
    Simulate a 5-stage pipeline and return a full ``PipelineResult``.

    Parameters
    ----------
    num_instructions : int
        Number of instructions to push through the pipeline (≥ 1).
    stall_after : list[int] | None
        Zero-based indices of instructions after which a stall occurs.
        Ignored when *random_stalls* is True.
    stall_cycles : int
        Number of bubble cycles inserted per stall event (1–5).
    random_stalls : bool
        If True, stalls are generated randomly instead of using
        *stall_after*.
    random_probability : float
        Per-instruction hazard probability (used only when
        *random_stalls* is True).
    random_seed : int | None
        Seed for the random generator (classroom reproducibility).

    Returns
    -------
    PipelineResult
        Dataclass containing the table, start_cycles, summary dict, etc.
    """
    if num_instructions < 1:
        empty = PipelineResult(
            table=pd.DataFrame(),
            start_cycles=[],
            stall_after=[],
            stall_cycles_per_hazard=stall_cycles,
            num_instructions=0,
        )
        return empty

    # ---- Resolve stall positions --------------------------------
    if random_stalls:
        stall_positions = generate_random_stalls(
            num_instructions, random_probability, random_seed,
        )
    else:
        stall_positions = sorted(set(stall_after)) if stall_after else []

    num_stages = len(STAGES)

    # ---- Compute start cycles for each instruction ---------------
    inst_start: list[int] = []          # 0-indexed start cycle per instruction
    cumulative_delay = 0

    for i in range(num_instructions):
        inst_start.append(i + cumulative_delay)
        if i in stall_positions:
            cumulative_delay += stall_cycles

    total_cycles = inst_start[-1] + num_stages

    # ---- Build the table (instructions + stall rows) ------------
    # Each row is either an instruction (I1, I2, …) or a stall bubble.
    row_labels: list[str] = []
    # row_data[row_index][cycle_index] = cell text
    row_data: list[list[str]] = []

    stall_set = set(stall_positions)
    stall_row_count = 0

    for i in range(num_instructions):
        # --- Instruction row ---
        row = [""] * total_cycles
        for s_idx, stage_name in enumerate(STAGES):
            cycle = inst_start[i] + s_idx
            if cycle < total_cycles:
                row[cycle] = stage_name
        row_labels.append(f"I{i + 1}")
        row_data.append(row)

        # --- Stall bubble row(s) right after this instruction ---
        if i in stall_set:
            for b in range(stall_cycles):
                bubble_row = [""] * total_cycles
                # Place the stall marker in the cycle where the bubble lives
                bubble_cycle = inst_start[i] + num_stages + b  # after the instr's WB? No.
                # Actually: the stall sits in the cycle right after the
                # producing instruction's ID stage (classic load-use).
                # For visual clarity we mark the bubble in the ID column of
                # the *next* instruction's would-be start.
                bubble_cycle = inst_start[i] + 1 + b  # cycle after IF of producer
                if bubble_cycle < total_cycles:
                    bubble_row[bubble_cycle] = STALL_MARKER
                stall_row_count += 1
                row_labels.append(f"  ↳ stall")
                row_data.append(bubble_row)

    # ---- Assemble DataFrame ---
    col_labels = [f"C{c + 1}" for c in range(total_cycles)]
    df = pd.DataFrame(row_data, index=row_labels, columns=col_labels)

    # ---- Summary statistics ---
    total_stalls = len(stall_positions) * stall_cycles
    ideal_cycles = num_instructions + num_stages - 1
    no_pipe_cycles = num_instructions * num_stages

    summary = _compute_summary(
        num_instructions=num_instructions,
        total_cycles=total_cycles,
        ideal_cycles=ideal_cycles,
        no_pipe_cycles=no_pipe_cycles,
        total_stalls=total_stalls,
    )

    return PipelineResult(
        table=df,
        start_cycles=inst_start,
        stall_after=stall_positions,
        stall_cycles_per_hazard=stall_cycles,
        num_instructions=num_instructions,
        total_stalls=total_stalls,
        summary=summary,
    )


# ──────────────────────────────────────────────
#  Summary helper
# ──────────────────────────────────────────────
def _compute_summary(
    *,
    num_instructions: int,
    total_cycles: int,
    ideal_cycles: int,
    no_pipe_cycles: int,
    total_stalls: int,
) -> dict:
    """Return a dict of human-friendly performance numbers."""
    cpi = total_cycles / num_instructions if num_instructions else 0
    speedup = no_pipe_cycles / total_cycles if total_cycles else 0
    efficiency = (ideal_cycles / total_cycles * 100) if total_cycles else 0

    return {
        "total_cycles":      total_cycles,
        "ideal_cycles":      ideal_cycles,
        "no_pipe_cycles":    no_pipe_cycles,
        "total_stalls":      total_stalls,
        "cpi":               round(cpi, 4),
        "pipeline_speedup":  round(speedup, 4),
        "efficiency_pct":    round(efficiency, 2),
    }


# ──────────────────────────────────────────────
#  Backward-compatible wrapper
# ──────────────────────────────────────────────
def pipeline_summary(df: pd.DataFrame, num_instructions: int) -> dict:
    """
    Quick summary from a raw DataFrame (kept for backward compat).

    Prefer using ``PipelineResult.summary`` from ``simulate_pipeline()``.
    """
    total_cycles = len(df.columns)
    ideal_cycles = num_instructions + len(STAGES) - 1
    no_pipe_cycles = num_instructions * len(STAGES)
    # Count stall rows
    stall_rows = sum(1 for idx in df.index if "stall" in str(idx).lower())

    return _compute_summary(
        num_instructions=num_instructions,
        total_cycles=total_cycles,
        ideal_cycles=ideal_cycles,
        no_pipe_cycles=no_pipe_cycles,
        total_stalls=stall_rows,
    )
