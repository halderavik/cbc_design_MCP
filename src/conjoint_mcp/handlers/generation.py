from __future__ import annotations

from typing import List

from pydantic import BaseModel

from conjoint_mcp.algorithms.random import generate_random_design
from conjoint_mcp.algorithms.balanced import generate_balanced_overlap_design
from conjoint_mcp.algorithms.orthogonal import generate_orthogonal_array_design
from conjoint_mcp.algorithms.doptimal import generate_doptimal_design, calculate_d_efficiency
from conjoint_mcp.models.requests import GenerateDesignRequest
from conjoint_mcp.models.responses import GenerateDesignResponse, GeneratedChoiceTask
from conjoint_mcp.utils.metrics import naive_level_balance_score
from conjoint_mcp.utils.validation import validate_grid
from conjoint_mcp.utils.respondent_optimization import suggest_optimal_respondents, calculate_expected_power
from conjoint_mcp.utils.performance import monitor_memory_usage, get_performance_limiter


class GenerateDesignPayload(BaseModel):
    """
    Payload wrapper to align with JSON-RPC params structure if needed later.
    """

    request: GenerateDesignRequest


@monitor_memory_usage
def handle_generate_design(req: GenerateDesignRequest) -> GenerateDesignResponse:
    """
    Dispatch design generation based on method.
    """

    validate_grid(req.grid)
    
    # Performance validation
    performance_limiter = get_performance_limiter()
    num_attributes = len(req.grid.attributes)
    total_levels = sum(len(attr.levels) for attr in req.grid.attributes)
    
    # Determine number of respondents first for validation
    if req.num_respondents is None:
        suggested_respondents = suggest_optimal_respondents(
            req.grid, req.num_screens, req.options_per_screen, default_commercial=True
        )
        num_respondents = suggested_respondents
    else:
        num_respondents = req.num_respondents
    
    # Validate performance constraints
    validation = performance_limiter.validate_design_parameters(
        num_respondents, req.num_screens, req.options_per_screen, num_attributes, total_levels
    )
    
    if not validation["is_valid"]:
        # Log warnings but continue with reduced parameters
        import logging
        logger = logging.getLogger(__name__)
        for issue in validation["issues"]:
            logger.warning(f"Performance issue: {issue}")
        for recommendation in validation["recommendations"]:
            logger.info(f"Recommendation: {recommendation}")

    # Set notes based on whether we suggested respondents
    if req.num_respondents is None:
        notes = f"Using {num_respondents} respondents (default commercial target). For segment analysis, consider specifying segments or custom sample size."
        suggested_respondents = num_respondents
    else:
        suggested_respondents = None
        notes = None

    method = req.method.lower()
    if method == "random":
        tasks = generate_random_design(req.grid, req.options_per_screen, req.num_screens)
        score = naive_level_balance_score(tasks)
    elif method in ("balanced", "balanced_overlap"):
        tasks = generate_balanced_overlap_design(
            req.grid, req.options_per_screen, req.num_screens
        )
        score = naive_level_balance_score(tasks)
    elif method in ("orthogonal", "orthogonal_array"):
        tasks = generate_orthogonal_array_design(
            req.grid, req.options_per_screen, req.num_screens
        )
        score = naive_level_balance_score(tasks)
    elif method in ("doptimal", "d-optimal"):
        tasks = generate_doptimal_design(req.grid, req.num_screens, req.options_per_screen)
        score = calculate_d_efficiency(tasks, req.grid)
    else:
        raise ValueError(f"Unsupported design method: {req.method}")

    converted: List[GeneratedChoiceTask] = [
        GeneratedChoiceTask(task_index=t["task_index"], options=t["options"]) for t in tasks
    ]
    
    return GenerateDesignResponse(
        tasks=converted, 
        efficiency=score,
        num_respondents=num_respondents,
        suggested_respondents=suggested_respondents,
        notes=notes
    )


