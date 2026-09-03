"""
=========================================================
STL OPTIMIZER

Shared timing utilities for STL Optimizer.

Compatible with:
    Windows
    Linux
    SteamOS

Author:
    Jose María Beltrán Díaz
=========================================================
"""

def format_elapsed_time(seconds):
    """Formats elapsed seconds as HH:MM:SS.mmm."""
    if seconds is None:
        return "NOT AVAILABLE"
    try:
        total_seconds = max(0.0, float(seconds))
    except (TypeError, ValueError):
        return "NOT AVAILABLE"

    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    remaining = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{remaining:06.3f}"
