"""
cache.py — Cache Performance Analyzer Module

Computes the Average Memory Access Time (AMAT) for a memory hierarchy
level using the standard formula:

    AMAT = Hit Time + (Miss Rate × Miss Penalty)

Where:
    Hit Time    — Time (in cycles or ns) to access data on a cache hit.
    Miss Rate   — Fraction of accesses that result in a cache miss (0–1).
    Miss Penalty — Additional time (in same units) incurred on a miss.

An optional multi-level analysis function is provided for L1 + L2
cache hierarchies:

    Effective AMAT = Hit_L1 + MissRate_L1 × (Hit_L2 + MissRate_L2 × MissPenalty_L2)
"""


def compute_amat(hit_time: float, miss_rate: float, miss_penalty: float) -> float:
    """
    Compute Average Memory Access Time for a single cache level.

    Parameters
    ----------
    hit_time : float
        Time for a cache hit (cycles or ns).
    miss_rate : float
        Probability of a cache miss (0.0 – 1.0).
    miss_penalty : float
        Extra time incurred on a miss (same units as hit_time).

    Returns
    -------
    float
        AMAT value rounded to 4 decimal places.
    """
    amat = hit_time + (miss_rate * miss_penalty)
    return round(amat, 4)


def compute_amat_multilevel(
    hit_time_l1: float,
    miss_rate_l1: float,
    hit_time_l2: float,
    miss_rate_l2: float,
    miss_penalty_l2: float,
) -> dict:
    """
    Compute AMAT for a two-level (L1 + L2) cache hierarchy.

    Parameters
    ----------
    hit_time_l1 : float
        L1 cache hit time.
    miss_rate_l1 : float
        L1 local miss rate (0–1).
    hit_time_l2 : float
        L2 cache hit time.
    miss_rate_l2 : float
        L2 local miss rate (0–1).
    miss_penalty_l2 : float
        Penalty for an L2 miss (time to access main memory).

    Returns
    -------
    dict
        amat_l1_only, amat_l2_only, effective_amat
    """
    # Individual AMATs
    amat_l2 = compute_amat(hit_time_l2, miss_rate_l2, miss_penalty_l2)
    # L1 miss penalty is the L2 AMAT
    effective_amat = hit_time_l1 + miss_rate_l1 * amat_l2

    return {
        "amat_l2": round(amat_l2, 4),
        "effective_amat": round(effective_amat, 4),
    }
