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
    alpha: float = 0.05,
    include_interactions: bool = False,
    quality_buffer: float = 0.15,
    default_commercial: bool = True
) -> int:
    """
    Suggest optimal number of respondents using the Johnson-Orme rule-of-thumb for CBC designs.
    
    This implements the academically validated approach:
    n ≥ 500c / (t × a)
    
    Where:
    - n = respondents
    - t = choice tasks per respondent  
    - a = alternatives per task (exclude None option)
    - c = largest number of levels for any attribute (main effects)
    - c = largest product of levels for any attribute pair (interactions)
    
    Args:
        grid: Design grid with attributes and levels
        num_screens: Number of choice tasks per respondent
        options_per_screen: Number of options per choice task
        target_power: Target statistical power (default 0.8)
        effect_size: Expected effect size (default 0.2)
        alpha: Significance level (default 0.05)
        include_interactions: Whether to plan for two-way interactions (default False)
        quality_buffer: Buffer for quality loss/dropouts (default 0.15 = 15%)
        default_commercial: If True, defaults to 300 respondents for commercial studies (default True)
    
    Returns:
        int: Suggested number of respondents
    """
    # Get attribute levels
    attribute_levels = [len(attr.levels) for attr in grid.attributes]
    
    if include_interactions:
        # For two-way interactions: find largest product of levels for any attribute pair
        max_product = 0
        for i in range(len(attribute_levels)):
            for j in range(i + 1, len(attribute_levels)):
                product = attribute_levels[i] * attribute_levels[j]
                max_product = max(max_product, product)
        c = max_product
    else:
        # For main effects: largest number of levels for any attribute
        c = max(attribute_levels) if attribute_levels else 1
    
    # Johnson-Orme rule: n ≥ 500c / (t × a)
    # Using 500 as baseline (can be increased to 1000 for extra precision)
    baseline_multiplier = 500
    
    t = num_screens  # choice tasks per respondent
    a = options_per_screen  # alternatives per task
    
    # Calculate base sample size
    base_respondents = math.ceil((baseline_multiplier * c) / (t * a))
    
    # Apply quality buffer for dropouts/quality loss
    buffered_respondents = math.ceil(base_respondents * (1 + quality_buffer))
    
    # Apply practical constraints
    min_respondents = 30  # Minimum for any meaningful analysis
    max_respondents = 2000  # Upper limit for most studies
    
    # For very simple designs, allow smaller minimums
    if c <= 2 and t * a >= 10:
        min_respondents = 20
    
    # Default to commercial standard if requested
    if default_commercial:
        # Use 300 as the default commercial target, but ensure it meets minimum requirements
        suggested_respondents = max(buffered_respondents, 300)
    else:
        suggested_respondents = max(min_respondents, min(buffered_respondents, max_respondents))
    
    return suggested_respondents


def get_sample_size_recommendations(
    grid: DesignGrid,
    num_screens: int,
    options_per_screen: int,
    quality_buffer: float = 0.15
) -> dict:
    """
    Get comprehensive sample size recommendations using Johnson-Orme rule.
    
    Args:
        grid: Design grid with attributes and levels
        num_screens: Number of choice tasks per respondent
        options_per_screen: Number of options per choice task
        quality_buffer: Buffer for quality loss/dropouts (default 0.15 = 15%)
    
    Returns:
        dict: Comprehensive sample size recommendations
    """
    # Get attribute levels
    attribute_levels = [len(attr.levels) for attr in grid.attributes]
    c_main = max(attribute_levels) if attribute_levels else 1
    
    # Calculate largest product for interactions
    max_product = 0
    for i in range(len(attribute_levels)):
        for j in range(i + 1, len(attribute_levels)):
            product = attribute_levels[i] * attribute_levels[j]
            max_product = max(max_product, product)
    c_interactions = max_product
    
    t = num_screens
    a = options_per_screen
    
    # Base calculations
    base_main_500 = math.ceil((500 * c_main) / (t * a))
    base_main_1000 = math.ceil((1000 * c_main) / (t * a))
    base_interactions_500 = math.ceil((500 * c_interactions) / (t * a))
    base_interactions_1000 = math.ceil((1000 * c_interactions) / (t * a))
    
    # With quality buffer
    main_500_buffered = math.ceil(base_main_500 * (1 + quality_buffer))
    main_1000_buffered = math.ceil(base_main_1000 * (1 + quality_buffer))
    interactions_500_buffered = math.ceil(base_interactions_500 * (1 + quality_buffer))
    interactions_1000_buffered = math.ceil(base_interactions_1000 * (1 + quality_buffer))
    
    return {
        "design_info": {
            "attribute_levels": attribute_levels,
            "c_main_effects": c_main,
            "c_interactions": c_interactions,
            "tasks_per_respondent": t,
            "alternatives_per_task": a,
            "total_observations_per_respondent": t * a
        },
        "johnson_orme_base": {
            "main_effects_500": base_main_500,
            "main_effects_1000": base_main_1000,
            "interactions_500": base_interactions_500,
            "interactions_1000": base_interactions_1000
        },
        "with_quality_buffer": {
            "main_effects_500": main_500_buffered,
            "main_effects_1000": main_1000_buffered,
            "interactions_500": interactions_500_buffered,
            "interactions_1000": interactions_1000_buffered
        },
        "pragmatic_targets": {
            "minimum_credible": max(250, main_500_buffered),
            "typical_commercial": max(300, main_500_buffered),
            "subgroup_analysis": max(400, main_500_buffered * 2),  # For 2+ subgroups
            "high_precision": main_1000_buffered
        },
        "recommendations": {
            "main_effects_only": main_500_buffered,
            "with_interactions": interactions_500_buffered,
            "conservative": main_1000_buffered,
            "subgroups_200_each": max(400, main_500_buffered * 2)
        }
    }


def get_segment_aware_recommendations(
    grid: DesignGrid,
    num_screens: int,
    options_per_screen: int,
    segments: list = None,
    min_per_segment: int = 200
) -> dict:
    """
    Get sample size recommendations considering segment analysis requirements.
    
    Args:
        grid: Design grid with attributes and levels
        num_screens: Number of choice tasks per respondent
        options_per_screen: Number of options per choice task
        segments: List of segment names (e.g., ["Young", "Middle-aged", "Senior"])
        min_per_segment: Minimum respondents per segment (default 200)
    
    Returns:
        dict: Segment-aware sample size recommendations
    """
    # Get base recommendations
    base_recommendations = get_sample_size_recommendations(grid, num_screens, options_per_screen)
    
    # Calculate segment requirements
    if segments:
        num_segments = len(segments)
        total_for_segments = num_segments * min_per_segment
        
        # Ensure we meet both base requirements and segment requirements
        recommended_total = max(
            base_recommendations["recommendations"]["main_effects_only"],
            total_for_segments
        )
        
        segment_analysis = {
            "segments": segments,
            "num_segments": num_segments,
            "min_per_segment": min_per_segment,
            "total_for_segments": total_for_segments,
            "recommended_total": recommended_total,
            "per_segment": recommended_total // num_segments if num_segments > 0 else 0
        }
    else:
        # No segments specified - use base recommendation
        recommended_total = base_recommendations["recommendations"]["main_effects_only"]
        segment_analysis = {
            "segments": None,
            "num_segments": 0,
            "min_per_segment": min_per_segment,
            "total_for_segments": 0,
            "recommended_total": recommended_total,
            "per_segment": 0
        }
    
    return {
        "base_recommendations": base_recommendations,
        "segment_analysis": segment_analysis,
        "final_recommendation": {
            "total_respondents": recommended_total,
            "reasoning": _get_recommendation_reasoning(base_recommendations, segment_analysis)
        }
    }


def _get_recommendation_reasoning(base_recs: dict, segment_analysis: dict) -> str:
    """Generate human-readable reasoning for the recommendation."""
    base_main = base_recs["recommendations"]["main_effects_only"]
    total_recommended = segment_analysis["recommended_total"]
    
    if segment_analysis["num_segments"] == 0:
        return f"Using base Johnson-Orme calculation: {base_main} respondents for main effects analysis."
    
    total_for_segments = segment_analysis["total_for_segments"]
    
    if total_recommended == base_main:
        return f"Base calculation ({base_main}) meets segment requirements ({total_for_segments})."
    else:
        return f"Segment analysis requires {total_for_segments} respondents ({segment_analysis['num_segments']} segments × {segment_analysis['min_per_segment']} each), which exceeds base calculation ({base_main})."


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
