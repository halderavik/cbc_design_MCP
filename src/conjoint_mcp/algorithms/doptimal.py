from __future__ import annotations

import math
import random
from typing import Dict, List, Tuple

import numpy as np

from conjoint_mcp.models.requests import Attribute, DesignGrid


def _create_design_matrix(design: List[dict], grid: DesignGrid) -> np.ndarray:
    """
    Create design matrix X for the given design.
    Each row represents an option, columns represent attribute levels (dummy coded).
    
    Args:
        design: List of choice tasks with options
        grid: Design grid specification
        
    Returns:
        Design matrix X
    """
    # Count total options across all tasks
    total_options = sum(len(task["options"]) for task in design)
    
    # Calculate number of parameters (main effects only for now)
    param_count = sum(len(attr.levels) - 1 for attr in grid.attributes)
    
    # Initialize design matrix
    X = np.zeros((total_options, param_count))
    
    # Create attribute level mapping
    attr_mappings = {}
    col_idx = 0
    for attr in grid.attributes:
        attr_mappings[attr.name] = {}
        for i, level in enumerate(attr.levels[1:], 1):  # Skip first level (reference)
            attr_mappings[attr.name][level.name] = col_idx
            col_idx += 1
    
    # Fill design matrix
    row_idx = 0
    for task in design:
        for option in task["options"]:
            for attr_name, level_name in option.items():
                if attr_name in attr_mappings and level_name in attr_mappings[attr_name]:
                    X[row_idx, attr_mappings[attr_name][level_name]] = 1
            row_idx += 1
    
    return X


def _calculate_information_matrix(X: np.ndarray) -> np.ndarray:
    """
    Calculate information matrix X'X for the design matrix.
    
    Args:
        X: Design matrix
        
    Returns:
        Information matrix X'X
    """
    return X.T @ X


def _calculate_d_optimality(X: np.ndarray) -> float:
    """
    Calculate D-optimality criterion (log determinant of information matrix).
    
    Args:
        X: Design matrix
        
    Returns:
        D-optimality value (higher is better)
    """
    info_matrix = _calculate_information_matrix(X)
    
    # Check if matrix is singular
    det = np.linalg.det(info_matrix)
    if det <= 1e-10:
        return -float('inf')
    
    # Return log determinant
    return math.log(det)


def _generate_candidate_design(
    grid: DesignGrid, 
    num_screens: int, 
    options_per_screen: int,
    current_design: List[dict] = None
) -> List[dict]:
    """
    Generate a candidate design by modifying the current design.
    
    Args:
        grid: Design grid specification
        num_screens: Number of choice tasks
        options_per_screen: Number of options per task
        current_design: Current design to modify (if None, generate random)
        
    Returns:
        Candidate design
    """
    if current_design is None:
        # Generate random design
        design = []
        for task_idx in range(num_screens):
            options = []
            for _ in range(options_per_screen):
                option = {}
                for attr in grid.attributes:
                    level = random.choice(attr.levels)
                    option[attr.name] = level.name
                options.append(option)
            design.append({"task_index": task_idx + 1, "options": options})
        return design
    
    # Modify existing design by changing one option
    design = []
    for task in current_design:
        new_task = {"task_index": task["task_index"], "options": []}
        for option in task["options"]:
            new_option = option.copy()
            new_task["options"].append(new_option)
        design.append(new_task)
    
    if not design:
        return design
    
    # Select random task and option to modify
    task_idx = random.randint(0, len(design) - 1)
    option_idx = random.randint(0, len(design[task_idx]["options"]) - 1)
    
    # Select random attribute to change
    attr = random.choice(grid.attributes)
    new_level = random.choice(attr.levels)
    
    # Update the option
    design[task_idx]["options"][option_idx][attr.name] = new_level.name
    
    return design


def generate_doptimal_design(
    grid: DesignGrid,
    num_screens: int,
    options_per_screen: int,
    max_iterations: int = 100,
    convergence_threshold: float = 1e-6,
    initial_temperature: float = 1.0,
    cooling_rate: float = 0.95,
) -> List[dict]:
    """
    Generate D-optimal design using simulated annealing.
    
    Args:
        grid: Design grid specification
        num_screens: Number of choice tasks
        options_per_screen: Number of options per task
        max_iterations: Maximum number of iterations
        convergence_threshold: Convergence threshold for stopping
        initial_temperature: Initial temperature for simulated annealing
        cooling_rate: Cooling rate for temperature
        
    Returns:
        D-optimal design
    """
    # Initialize with random design
    current_design = _generate_candidate_design(grid, num_screens, options_per_screen)
    current_X = _create_design_matrix(current_design, grid)
    current_d_opt = _calculate_d_optimality(current_X)
    
    # Ensure we have the right number of tasks
    if len(current_design) != num_screens:
        # Fallback to simple random generation if D-optimal fails
        from .random import generate_random_design
        return generate_random_design(grid, options_per_screen, num_screens)
    
    
    best_design = current_design.copy()
    best_d_opt = current_d_opt
    
    temperature = initial_temperature
    no_improvement_count = 0
    max_no_improvement = 50
    
    for iteration in range(max_iterations):
        # Generate candidate design
        candidate_design = _generate_candidate_design(
            grid, num_screens, options_per_screen, current_design
        )
        candidate_X = _create_design_matrix(candidate_design, grid)
        candidate_d_opt = _calculate_d_optimality(candidate_X)
        
        # Accept or reject candidate
        if candidate_d_opt > current_d_opt:
            # Always accept improvements
            current_design = candidate_design
            current_d_opt = candidate_d_opt
            no_improvement_count = 0
            
            # Update best if necessary
            if candidate_d_opt > best_d_opt:
                best_design = candidate_design.copy()
                best_d_opt = candidate_d_opt
        else:
            # Accept with probability based on temperature
            if temperature > 0:
                prob = math.exp((candidate_d_opt - current_d_opt) / temperature)
                if random.random() < prob:
                    current_design = candidate_design
                    current_d_opt = candidate_d_opt
                else:
                    no_improvement_count += 1
            else:
                no_improvement_count += 1
        
        # Cool down temperature
        temperature *= cooling_rate
        
        # Check convergence
        if no_improvement_count >= max_no_improvement:
            break
        
        # Early stopping if temperature is very low
        if temperature < 1e-10:
            break
    
    return best_design


def calculate_d_efficiency(design: List[dict], grid: DesignGrid) -> float:
    """
    Calculate D-efficiency of the design.
    
    Args:
        design: Design to evaluate
        grid: Design grid specification
        
    Returns:
        D-efficiency value (0-1, higher is better)
    """
    X = _create_design_matrix(design, grid)
    info_matrix = _calculate_information_matrix(X)
    
    # Check if matrix is singular
    if np.linalg.det(info_matrix) <= 1e-10:
        return 0.0
    
    # Calculate D-efficiency
    p = info_matrix.shape[0]  # Number of parameters
    n = X.shape[0]  # Number of observations
    
    d_opt = np.linalg.det(info_matrix) ** (1/p)
    d_efficiency = d_opt / n
    
    return min(1.0, max(0.0, d_efficiency))
