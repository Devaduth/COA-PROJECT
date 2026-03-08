"""
performance.py — Processor Performance Calculator Module

This module computes key CPU performance metrics based on instruction mix,
CPI (Cycles Per Instruction) values, and clock cycle time.

Metrics computed:
    - Total Instruction Count
    - Average CPI (weighted by instruction mix)
    - Total Execution Cycles
    - Execution Time (seconds)
    - MIPS (Million Instructions Per Second)

Formulas:
    Total Instructions = ALU_count + Load_count + Branch_count
    Avg CPI = Σ(Instruction_count_i × CPI_i) / Total Instructions
    Total Cycles = Σ(Instruction_count_i × CPI_i)
    Execution Time = Total Cycles × Clock Cycle Time
    MIPS = Total Instructions / (Execution Time × 10^6)
"""


def compute_performance(
    alu_count: int,
    load_count: int,
    branch_count: int,
    cpi_alu: float,
    cpi_load: float,
    cpi_branch: float,
    clock_cycle_ns: float,
) -> dict:
    """
    Calculate processor performance metrics.

    Parameters
    ----------
    alu_count : int
        Number of ALU (arithmetic/logic) instructions.
    load_count : int
        Number of Load/Store instructions.
    branch_count : int
        Number of Branch instructions.
    cpi_alu : float
        Cycles per instruction for ALU operations.
    cpi_load : float
        Cycles per instruction for Load/Store operations.
    cpi_branch : float
        Cycles per instruction for Branch operations.
    clock_cycle_ns : float
        Duration of one clock cycle in nanoseconds.

    Returns
    -------
    dict
        Dictionary containing:
            total_instructions, avg_cpi, total_cycles,
            execution_time_sec, mips
    """
    # --- Total instruction count ---
    total_instructions = alu_count + load_count + branch_count

    if total_instructions == 0:
        return {
            "total_instructions": 0,
            "avg_cpi": 0.0,
            "total_cycles": 0.0,
            "execution_time_sec": 0.0,
            "mips": 0.0,
        }

    # --- Weighted total cycles ---
    total_cycles = (alu_count * cpi_alu) + (load_count * cpi_load) + (branch_count * cpi_branch)

    # --- Average CPI (weighted) ---
    avg_cpi = total_cycles / total_instructions

    # --- Execution time in seconds ---
    clock_cycle_sec = clock_cycle_ns * 1e-9          # convert ns → s
    execution_time_sec = total_cycles * clock_cycle_sec

    # --- MIPS (Million Instructions Per Second) ---
    mips = total_instructions / (execution_time_sec * 1e6) if execution_time_sec > 0 else 0.0

    return {
        "total_instructions": total_instructions,
        "avg_cpi": round(avg_cpi, 4),
        "total_cycles": round(total_cycles, 4),
        "execution_time_sec": round(execution_time_sec, 10),
        "mips": round(mips, 4),
    }
