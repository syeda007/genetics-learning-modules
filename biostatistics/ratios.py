"""
Statistical Analysis: Ratio Parsing and Normalization Module
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
import re
from typing import Dict, List, Optional, Tuple


def parse_ratio_string(ratio_str: str) -> Optional[List[float]]:
    """
    Parses a ratio string such as "3:1", "1 : 2 : 1", "9:3:3:1", or "50 : 50" into normalized proportions.
    Returns normalized float list that sums to 1.0, or None if invalid.
    """
    cleaned = ratio_str.strip().replace(" ", "").replace("%", "")
    parts = cleaned.split(":")
    if len(parts) < 2:
        parts = cleaned.split(",")
    if len(parts) < 2:
        return None
    
    try:
        nums = [float(p) for p in parts]
        if any(n < 0 for n in nums):
            return None
        total = sum(nums)
        if total <= 0:
            return None
        return [n / total for n in nums]
    except ValueError:
        return None


def format_proportions_as_ratio(proportions: List[float], tolerance: float = 0.05) -> str:
    """
    Converts list of proportions to the nearest small integer ratio.
    """
    if not proportions:
        return ""
    min_p = min(p for p in proportions if p > 0)
    scaled = [round(p / min_p) for p in proportions]
    return " : ".join(str(s) for s in scaled)
