from __future__ import annotations

from typing import Dict, List

from conjoint_mcp.models.requests import Attribute, DesignGrid


def _cycle_levels(attribute: Attribute) -> List[str]:
    return [level.name for level in attribute.levels]


def generate_balanced_overlap_design(
    grid: DesignGrid, options_per_screen: int, num_screens: int
) -> List[dict]:
    """
    Simple balanced overlap: rotate levels per attribute across options/screens
    to even out usage; allow overlaps within a screen but rotate to balance.
    """

    attributes = grid.attributes
    level_cycles: Dict[str, List[str]] = {attr.name: _cycle_levels(attr) for attr in attributes}
    cycles_index: Dict[str, int] = {attr.name: 0 for attr in attributes}

    tasks: List[dict] = []
    for task_idx in range(num_screens):
        options: List[dict] = []
        for k in range(options_per_screen):
            option: Dict[str, str] = {}
            for attr in attributes:
                levels = level_cycles[attr.name]
                idx = (cycles_index[attr.name] + k + task_idx) % len(levels)
                option[attr.name] = levels[idx]
            options.append(option)
        # advance cycle index by options_per_screen to rotate next screen
        for attr in attributes:
            levels = level_cycles[attr.name]
            cycles_index[attr.name] = (cycles_index[attr.name] + options_per_screen) % len(levels)
        tasks.append({"task_index": task_idx + 1, "options": options})
    return tasks


