from __future__ import annotations

from typing import List

from conjoint_mcp.models.requests import DesignGrid


def generate_orthogonal_array_design(
    grid: DesignGrid, options_per_screen: int, num_screens: int
) -> List[dict]:
    """
    Construct a simple orthogonal-like design for two-level attributes by toggling levels.
    For generality, fall back to balanced approach when not 2-level across all attributes.
    """

    two_level = all(len(a.levels) == 2 for a in grid.attributes)
    if not two_level:
        # fallback to balanced for now
        from .balanced import generate_balanced_overlap_design

        return generate_balanced_overlap_design(grid, options_per_screen, num_screens)

    # For each screen and option, flip bits to cover combinations evenly.
    tasks: List[dict] = []
    for task_idx in range(num_screens):
        options: List[dict] = []
        for opt_idx in range(options_per_screen):
            option = {}
            for a_idx, attr in enumerate(grid.attributes):
                level_idx = ((task_idx + opt_idx + a_idx) % 2)
                option[attr.name] = attr.levels[level_idx].name
            options.append(option)
        tasks.append({"task_index": task_idx + 1, "options": options})
    return tasks


