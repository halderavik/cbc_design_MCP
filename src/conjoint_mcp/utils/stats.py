from __future__ import annotations

import math
from typing import List

from conjoint_mcp.models.requests import Attribute, DesignGrid


def calculate_design_complexity(grid: DesignGrid) -> int:
    """
    Calculate total number of possible combinations in the design space.

    Args:
        grid (DesignGrid): Design grid specification.

    Returns:
        int: Total number of possible combinations.
    """

    total_combinations = 1
    for attr in grid.attributes:
        total_combinations *= len(attr.levels)
    return total_combinations


def estimate_parameters_count(grid: DesignGrid) -> int:
    """
    Estimate number of parameters to be estimated in the model.

    Args:
        grid (DesignGrid): Design grid specification.

    Returns:
        int: Estimated parameter count.
    """

    # Main effects: sum of (levels - 1) for each attribute
    main_effects = sum(len(attr.levels) - 1 for attr in grid.attributes)
    
    # Interaction effects: for now, assume no interactions
    # TODO: Add interaction parameter counting when interactions are specified
    interaction_effects = 0
    
    return main_effects + interaction_effects


def calculate_statistical_power(
    num_respondents: int,
    num_screens: int,
    options_per_screen: int,
    parameter_count: int,
    effect_size: float = 0.2,
    alpha: float = 0.05,
) -> float:
    """
    Calculate statistical power for the design.

    Args:
        num_respondents (int): Number of respondents.
        num_screens (int): Number of choice tasks per respondent.
        options_per_screen (int): Number of options per choice task.
        parameter_count (int): Number of parameters to estimate.
        effect_size (float): Expected effect size (Cohen's d).
        alpha (float): Significance level.

    Returns:
        float: Statistical power (0-1).
    """

    # Total observations = respondents * screens * (options_per_screen - 1)
    # Subtract 1 because one option is reference in choice modeling
    total_observations = num_respondents * num_screens * (options_per_screen - 1)
    
    # Degrees of freedom
    df = total_observations - parameter_count
    
    if df <= 0:
        return 0.0
    
    # Simplified power calculation based on t-test approximation
    # This is a rough approximation for choice modeling
    ncp = effect_size * math.sqrt(total_observations)  # Non-centrality parameter
    
    # Approximate power using normal distribution
    # For more accuracy, would need t-distribution with non-centrality
    z_alpha = 1.96 if alpha == 0.05 else 2.576 if alpha == 0.01 else 1.645
    z_beta = ncp - z_alpha
    
    # Convert to power (probability)
    power = 0.5 * (1 + math.erf(z_beta / math.sqrt(2)))
    
    return min(1.0, max(0.0, power))


def optimize_respondent_size(
    grid: DesignGrid,
    num_screens: int,
    options_per_screen: int,
    target_power: float = 0.8,
    effect_size: float = 0.2,
    alpha: float = 0.05,
    max_respondents: int = 1000,
) -> int:
    """
    Find minimum number of respondents needed for target statistical power.

    Args:
        grid (DesignGrid): Design grid specification.
        num_screens (int): Number of choice tasks per respondent.
        options_per_screen (int): Number of options per choice task.
        target_power (float): Target statistical power.
        effect_size (float): Expected effect size.
        alpha (float): Significance level.
        max_respondents (int): Maximum respondents to consider.

    Returns:
        int: Recommended number of respondents.
    """

    parameter_count = estimate_parameters_count(grid)
    
    # Binary search for minimum respondents
    low, high = 1, max_respondents
    best_respondents = max_respondents
    
    while low <= high:
        mid = (low + high) // 2
        power = calculate_statistical_power(
            mid, num_screens, options_per_screen, parameter_count, effect_size, alpha
        )
        
        if power >= target_power:
            best_respondents = mid
            high = mid - 1
        else:
            low = mid + 1
    
    return best_respondents


def optimize_screen_count(
    grid: DesignGrid,
    num_respondents: int,
    options_per_screen: int,
    target_power: float = 0.8,
    effect_size: float = 0.2,
    alpha: float = 0.05,
    max_screens: int = 20,
) -> int:
    """
    Find minimum number of screens needed for target statistical power.

    Args:
        grid (DesignGrid): Design grid specification.
        num_respondents (int): Number of respondents.
        options_per_screen (int): Number of options per choice task.
        target_power (float): Target statistical power.
        effect_size (float): Expected effect size.
        alpha (float): Significance level.
        max_screens (int): Maximum screens to consider.

    Returns:
        int: Recommended number of screens.
    """

    parameter_count = estimate_parameters_count(grid)
    
    # Binary search for minimum screens
    low, high = 1, max_screens
    best_screens = max_screens
    
    while low <= high:
        mid = (low + high) // 2
        power = calculate_statistical_power(
            num_respondents, mid, options_per_screen, parameter_count, effect_size, alpha
        )
        
        if power >= target_power:
            best_screens = mid
            high = mid - 1
        else:
            low = mid + 1
    
    return best_screens


def optimize_options_per_screen(
    grid: DesignGrid,
    num_respondents: int,
    num_screens: int,
    target_power: float = 0.8,
    effect_size: float = 0.2,
    alpha: float = 0.05,
    max_options: int = 5,
) -> int:
    """
    Find optimal number of options per screen for target statistical power.

    Args:
        grid (DesignGrid): Design grid specification.
        num_respondents (int): Number of respondents.
        num_screens (int): Number of choice tasks per respondent.
        target_power (float): Target statistical power.
        effect_size (float): Expected effect size.
        alpha (float): Significance level.
        max_options (int): Maximum options per screen.

    Returns:
        int: Recommended number of options per screen.
    """

    parameter_count = estimate_parameters_count(grid)
    
    # Binary search for optimal options
    low, high = 2, max_options
    best_options = max_options
    
    while low <= high:
        mid = (low + high) // 2
        power = calculate_statistical_power(
            num_respondents, num_screens, mid, parameter_count, effect_size, alpha
        )
        
        if power >= target_power:
            best_options = mid
            high = mid - 1
        else:
            low = mid + 1
    
    return best_options
