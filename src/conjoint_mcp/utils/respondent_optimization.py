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
    Uses a more intelligent approach that balances statistical rigor with practicality.
    
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
    
    # More intelligent power analysis approach
    z_alpha = 1.96  # For alpha = 0.05
    z_beta = 0.84   # For power = 0.8
    
    # Calculate required sample size for target power
    effect_size_squared = effect_size ** 2
    required_respondents_by_power = math.ceil(
        ((z_alpha + z_beta) ** 2) / (effect_size_squared * observations_per_respondent)
    )
    
    # Adaptive parameter-based calculation
    # Use fewer observations per parameter for simpler designs, more for complex ones
    if num_parameters <= 3:
        obs_per_param = 5  # Simple designs need fewer observations
    elif num_parameters <= 6:
        obs_per_param = 7  # Medium complexity
    elif num_parameters <= 10:
        obs_per_param = 8  # Complex designs
    else:
        obs_per_param = 10  # Very complex designs
    
    min_respondents_by_parameters = math.ceil(num_parameters * obs_per_param)
    
    # Use the more appropriate calculation based on design complexity
    if num_parameters <= 5:
        # For simple designs, prioritize power analysis
        suggested_respondents = max(required_respondents_by_power, min_respondents_by_parameters)
    else:
        # For complex designs, use a weighted average to avoid extreme values
        power_weight = 0.6
        param_weight = 0.4
        suggested_respondents = math.ceil(
            power_weight * required_respondents_by_power + 
            param_weight * min_respondents_by_parameters
        )
    
    # Apply practical constraints with more reasonable bounds
    min_respondents = 30  # Minimum for any meaningful analysis
    max_respondents = 500  # More reasonable upper limit for most studies
    
    # For very simple designs, allow smaller minimums
    if num_parameters <= 2 and observations_per_respondent >= 10:
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
