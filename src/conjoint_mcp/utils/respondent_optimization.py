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
    Suggest optimal number of respondents based on statistical power calculations.
    
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
    # Calculate total number of parameters to estimate
    total_levels = sum(len(attr.levels) for attr in grid.attributes)
    num_parameters = total_levels - len(grid.attributes)  # Subtract one for each attribute (reference level)
    
    # Calculate total observations per respondent
    observations_per_respondent = num_screens * options_per_screen
    
    # Use Cohen's power analysis for logistic regression
    # This is a simplified calculation - in practice, you'd use more sophisticated methods
    
    # Minimum sample size based on rule of thumb: 10-15 observations per parameter
    min_respondents_by_parameters = math.ceil(num_parameters * 10)
    
    # Minimum sample size based on power analysis (simplified)
    # For binary choice, we need sufficient observations to detect effects
    z_alpha = 1.96  # For alpha = 0.05
    z_beta = 0.84   # For power = 0.8
    
    # Simplified power calculation
    effect_size_squared = effect_size ** 2
    min_respondents_by_power = math.ceil(
        ((z_alpha + z_beta) ** 2) / (effect_size_squared * observations_per_respondent)
    )
    
    # Take the maximum of both calculations
    suggested_respondents = max(min_respondents_by_parameters, min_respondents_by_power)
    
    # Apply some practical constraints
    min_respondents = 30  # Minimum for any meaningful analysis
    max_respondents = 2000  # Practical upper limit
    
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
