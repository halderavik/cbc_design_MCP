from __future__ import annotations

from typing import Dict, List


def naive_level_balance_score(tasks: List[dict]) -> float:
    """
    A placeholder metric: returns a normalized score based on the number of tasks.
    This is a stub for future efficiency metrics.
    """

    if not tasks:
        return 0.0
    # Count occurrences of each attribute-level
    counts: Dict[str, int] = {}
    total = 0
    for t in tasks:
        for option in t.get("options", []):
            for attr, level in option.items():
                key = f"{attr}::{level}"
                counts[key] = counts.get(key, 0) + 1
                total += 1
    if total == 0:
        return 0.0
    avg = total / max(1, len(counts))
    # Compute simple deviation-based score in [0,1]
    deviation = sum(abs(c - avg) for c in counts.values()) / (total)
    score = max(0.0, 1.0 - deviation)
    return round(score, 4)


