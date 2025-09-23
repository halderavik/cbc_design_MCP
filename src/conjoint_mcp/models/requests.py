from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class AttributeLevel(BaseModel):
    """
    Represents a single attribute level in the design grid.

    Args:
        name (str): Level name.
        code (Optional[str]): Optional machine code/id.
    """

    name: str
    code: Optional[str] = None


class Attribute(BaseModel):
    """
    Represents an attribute containing multiple levels.

    Args:
        name (str): Attribute name.
        levels (List[AttributeLevel]): Attribute levels.
    """

    name: str
    levels: List[AttributeLevel]


class DesignGrid(BaseModel):
    """
    Design grid describing attributes and levels, optionally interactions.
    """

    attributes: List[Attribute] = Field(default_factory=list)
    interactions: List[str] = Field(default_factory=list)


class GenerateDesignRequest(BaseModel):
    """
    Request for generating a CBC design.

    Args:
        method (str): Algorithm name (e.g., "random", "balanced", "doptimal").
        grid (DesignGrid): Design grid specification.
        options_per_screen (int): Alternatives per choice task.
        num_screens (int): Number of choice tasks per respondent.
        num_respondents (Optional[int]): Number of respondents. If not provided, will suggest optimal number.
        constraints (Optional[dict]): Constraint specification payload.
    """

    method: str
    grid: DesignGrid
    options_per_screen: int = 3
    num_screens: int = 10
    num_respondents: Optional[int] = None
    constraints: Optional[dict] = None


class OptimizeParametersRequest(BaseModel):
    """
    Request to optimize respondent/sample and task parameters.
    """

    grid: DesignGrid
    max_budget: Optional[float] = None
    max_time_minutes: Optional[int] = None


