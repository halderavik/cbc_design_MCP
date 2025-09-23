from __future__ import annotations

from typing import List

from pydantic import BaseModel


class GeneratedChoiceTask(BaseModel):
    """
    Represents a single choice task with options encoded as rows.
    """

    task_index: int
    options: List[dict]


class GenerateDesignResponse(BaseModel):
    """
    Response for generated design including quality metrics.
    """

    tasks: List[GeneratedChoiceTask]
    efficiency: float | None = None
    notes: str | None = None
    num_respondents: int = 1
    suggested_respondents: int | None = None


class OptimizeParametersResponse(BaseModel):
    """
    Response containing recommended parameters for the study.
    """

    num_respondents: int
    num_screens: int
    options_per_screen: int
    expected_power: float | None = None


