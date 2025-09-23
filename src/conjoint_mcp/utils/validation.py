from __future__ import annotations

from conjoint_mcp.models.requests import DesignGrid


def validate_grid(grid: DesignGrid) -> None:
    """
    Minimal validation for attributes/levels.
    Raises ValueError on invalid input.
    """

    if not grid.attributes:
        raise ValueError("Design grid must include at least one attribute")
    for attr in grid.attributes:
        if not attr.levels:
            raise ValueError(f"Attribute '{attr.name}' must include at least one level")
        names = [lvl.name for lvl in attr.levels]
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicate level names in attribute '{attr.name}'")


