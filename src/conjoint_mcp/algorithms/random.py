from __future__ import annotations

import random
from typing import Dict, List

from conjoint_mcp.models.requests import Attribute, DesignGrid


def _enumerate_attribute_levels(attributes: List[Attribute]) -> List[List[Dict[str, str]]]:
    """
    For each attribute, return a list of level dicts to be used for option creation.
    """

    enumerated: List[List[Dict[str, str]]] = []
    for attribute in attributes:
        enumerated.append(
            [{"attribute": attribute.name, "level": level.name} for level in attribute.levels]
        )
    return enumerated


def generate_random_design(grid: DesignGrid, options_per_screen: int, num_screens: int) -> List[dict]:
    """
    Generate a naive random design: for each screen, create options by sampling a level for
    each attribute independently.

    Args:
        grid (DesignGrid): Attributes and levels specification.
        options_per_screen (int): Number of options per choice task.
        num_screens (int): Number of choice tasks.

    Returns:
        List[dict]: List of tasks, each containing an options list.
    """

    attributes = grid.attributes
    level_space = _enumerate_attribute_levels(attributes)

    tasks: List[dict] = []
    for task_idx in range(num_screens):
        options: List[dict] = []
        for _ in range(options_per_screen):
            option = {}
            for per_attribute_levels in level_space:
                chosen = random.choice(per_attribute_levels)
                option[chosen["attribute"]] = chosen["level"]
            options.append(option)
        tasks.append({"task_index": task_idx + 1, "options": options})
    return tasks


