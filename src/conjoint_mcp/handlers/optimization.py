from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from conjoint_mcp.models.requests import DesignGrid
from conjoint_mcp.utils.stats import (
    calculate_statistical_power,
    estimate_parameters_count,
    optimize_options_per_screen,
    optimize_respondent_size,
    optimize_screen_count,
)


class OptimizationRequest(BaseModel):
    """
    Request for optimizing design parameters.
    """

    grid: DesignGrid
    target_power: float = Field(default=0.8, ge=0.1, le=1.0)
    effect_size: float = Field(default=0.2, ge=0.1, le=1.0)
    alpha: float = Field(default=0.05, ge=0.01, le=0.1)
    max_respondents: int = Field(default=1000, ge=10, le=10000)
    max_screens: int = Field(default=20, ge=1, le=50)
    max_options: int = Field(default=5, ge=2, le=10)
    # Optional constraints
    fixed_respondents: Optional[int] = Field(default=None, ge=1, le=10000)
    fixed_screens: Optional[int] = Field(default=None, ge=1, le=50)
    fixed_options: Optional[int] = Field(default=None, ge=2, le=10)


class OptimizationResponse(BaseModel):
    """
    Response containing optimized design parameters.
    """

    num_respondents: int
    num_screens: int
    options_per_screen: int
    expected_power: float
    parameter_count: int
    design_complexity: int
    notes: Optional[str] = None


def handle_optimize_parameters(req: OptimizationRequest) -> OptimizationResponse:
    """
    Optimize design parameters based on statistical requirements.
    """

    # Get parameter count for the design
    parameter_count = estimate_parameters_count(req.grid)
    
    # Start with default values
    num_respondents = req.fixed_respondents or 100
    num_screens = req.fixed_screens or 10
    options_per_screen = req.fixed_options or 3
    
    # Optimize each parameter if not fixed
    if req.fixed_respondents is None:
        num_respondents = optimize_respondent_size(
            req.grid,
            num_screens,
            options_per_screen,
            req.target_power,
            req.effect_size,
            req.alpha,
            req.max_respondents,
        )
    
    if req.fixed_screens is None:
        num_screens = optimize_screen_count(
            req.grid,
            num_respondents,
            options_per_screen,
            req.target_power,
            req.effect_size,
            req.alpha,
            req.max_screens,
        )
    
    if req.fixed_options is None:
        options_per_screen = optimize_options_per_screen(
            req.grid,
            num_respondents,
            num_screens,
            req.target_power,
            req.effect_size,
            req.alpha,
            req.max_options,
        )
    
    # Calculate final expected power
    expected_power = calculate_statistical_power(
        num_respondents,
        num_screens,
        options_per_screen,
        parameter_count,
        req.effect_size,
        req.alpha,
    )
    
    # Calculate design complexity
    design_complexity = 1
    for attr in req.grid.attributes:
        design_complexity *= len(attr.levels)
    
    # Generate notes
    notes = []
    if expected_power < req.target_power:
        notes.append(f"Warning: Expected power ({expected_power:.3f}) below target ({req.target_power})")
    if parameter_count > num_respondents * num_screens * (options_per_screen - 1):
        notes.append("Warning: Insufficient observations for parameter estimation")
    
    return OptimizationResponse(
        num_respondents=num_respondents,
        num_screens=num_screens,
        options_per_screen=options_per_screen,
        expected_power=expected_power,
        parameter_count=parameter_count,
        design_complexity=design_complexity,
        notes="; ".join(notes) if notes else None,
    )


