"""
amdahl.py — Amdahl's Law Speedup Calculator

Amdahl's Law gives the theoretical maximum speedup of a system when
only a fraction of the workload can be improved (parallelised).

    Speedup = 1 / ((1 - P) + (P / S))

Where:
    P — Fraction of execution time that can be enhanced  (0 ≤ P ≤ 1).
    S — Speedup factor of the enhanced (parallel) portion (S ≥ 1).

Special cases:
    • P = 0  → Speedup = 1  (nothing is parallelised).
    • S → ∞  → Speedup = 1 / (1 - P)  (maximum possible speedup).

This module also provides a helper that sweeps over a range of S values
so the results can be plotted.
"""

import numpy as np


def compute_speedup(parallel_fraction: float, speedup_enhanced: float) -> float:
    """
    Compute the overall system speedup using Amdahl's Law.

    Parameters
    ----------
    parallel_fraction : float
        Fraction of the workload that benefits from enhancement (0–1).
    speedup_enhanced : float
        Speedup factor applied to the enhanced portion (≥ 1).

    Returns
    -------
    float
        Overall speedup, rounded to 4 decimal places.
    """
    if speedup_enhanced == 0:
        return 0.0

    serial_fraction = 1.0 - parallel_fraction
    overall = 1.0 / (serial_fraction + (parallel_fraction / speedup_enhanced))
    return round(overall, 4)


def speedup_vs_processors(parallel_fraction: float, max_processors: int = 64) -> dict:
    """
    Compute Amdahl's-law speedup for 1 … max_processors cores/speedup factors.

    Useful for generating a speedup-curve chart.

    Parameters
    ----------
    parallel_fraction : float
        Fraction of the workload that can be parallelised.
    max_processors : int
        Maximum number of processors (used as the enhanced-part speedup).

    Returns
    -------
    dict
        processors : list[int]
        speedups   : list[float]
        max_speedup: float   (theoretical limit as S → ∞)
    """
    processors = list(range(1, max_processors + 1))
    speedups = [compute_speedup(parallel_fraction, s) for s in processors]
    max_speedup = round(1.0 / (1.0 - parallel_fraction), 4) if parallel_fraction < 1.0 else float("inf")

    return {
        "processors": processors,
        "speedups": speedups,
        "max_speedup": max_speedup,
    }
