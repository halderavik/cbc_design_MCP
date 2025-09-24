from __future__ import annotations

import math
from typing import Optional

from conjoint_mcp.models.requests import DesignGrid


def suggest_optimal_respondents(
    grid: DesignGrid,
    num_screens: int,
    options_per_screen: int,
    target_power: float = 0.8,
    effect_size: float = 0.2,
    alpha: float = 0.05
) -> int:
    """
    Suggest optimal number of respondents based on CBC design best practices.
    Uses the standard rule: 5-10 observations per parameter (including intercept).
    
    Args:
        grid: Design grid with attributes and levels
        num_screens: Number of choice tasks per respondent
        options_per_screen: Number of options per choice task
        target_power: Target statistical power (default 0.8)
        effect_size: Expected effect size (default 0.2)
        alpha: Significance level (default 0.05)
    
    Returns:
        int: Suggested number of respondents
    """
    # Calculate total number of parameters to estimate (including intercept)
    total_levels = sum(len(attr.levels) for attr in grid.attributes)
    num_parameters = total_levels - len(grid.attributes) + 1  # +1 for intercept
    
    # Calculate total observations per respondent
    observations_per_respondent = num_screens * options_per_screen
    
    # CBC Design Rule: 5-10 observations per parameter
    # Use 7.5 as the optimal middle ground (between 5 and 10)
    optimal_obs_per_param = 7.5
    
    # Calculate suggested respondents based on parameter count
    suggested_respondents = math.ceil(num_parameters * optimal_obs_per_param)
    
    # Apply practical constraints
    min_respondents = 30  # Minimum for any meaningful analysis
    max_respondents = 1000  # Upper limit for most studies
    
    # For very simple designs, allow smaller minimums
    if num_parameters <= 3 and observations_per_respondent >= 10:
        min_respondents = 20
    
    suggested_respondents = max(min_respondents, min(suggested_respondents, max_respondents))
    
    return suggested_respondents


def calculate_expected_power(
    grid: DesignGrid,
    num_respondents: int,
    num_screens: int,
    options_per_screen: int,
    effect_size: float = 0.2,
    alpha: float = 0.05
) -> float:
    """
    Calculate expected statistical power for given parameters.
    
    Args:
        grid: Design grid with attributes and levels
        num_respondents: Number of respondents
        num_screens: Number of choice tasks per respondent
        options_per_screen: Number of options per choice task
        effect_size: Expected effect size
        alpha: Significance level
    
    Returns:
        float: Expected statistical power (0-1)
    """
    # Calculate total observations
    total_observations = num_respondents * num_screens * options_per_screen
    
    # Calculate number of parameters
    total_levels = sum(len(attr.levels) for attr in grid.attributes)
    num_parameters = total_levels - len(grid.attributes)
    
    # Simplified power calculation
    # This is a rough approximation - real power calculations are more complex
    z_alpha = 1.96  # For alpha = 0.05
    
    # Calculate effect size in terms of observations
    effect_size_squared = effect_size ** 2
    power_term = math.sqrt(total_observations * effect_size_squared) - z_alpha
    
    # Convert to power (simplified)
    expected_power = min(0.99, max(0.01, 0.5 + 0.5 * math.tanh(power_term / 2)))
    
    return expected_power
