"""
Performance optimization utilities for Heroku deployment.
"""

import gc
import logging
import psutil
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


def monitor_memory_usage(func: Callable) -> Callable:
    """
    Decorator to monitor memory usage of functions.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            # Get final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            execution_time = time.time() - start_time
            
            logger.info(
                f"Function {func.__name__} completed: "
                f"Memory: {initial_memory:.1f}MB -> {final_memory:.1f}MB "
                f"(+{final_memory - initial_memory:.1f}MB), "
                f"Time: {execution_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Function {func.__name__} failed: {e}")
            raise
            
    return wrapper


def optimize_memory():
    """
    Force garbage collection to optimize memory usage.
    """
    collected = gc.collect()
    logger.debug(f"Garbage collection freed {collected} objects")


def check_memory_limits(max_memory_mb: int = 512) -> bool:
    """
    Check if memory usage is within limits.
    
    Args:
        max_memory_mb: Maximum allowed memory in MB
        
    Returns:
        bool: True if within limits, False otherwise
    """
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    if memory_mb > max_memory_mb:
        logger.warning(f"Memory usage ({memory_mb:.1f}MB) exceeds limit ({max_memory_mb}MB)")
        return False
    
    return True


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for monitoring.
    
    Returns:
        Dict containing system information
    """
    process = psutil.Process()
    
    return {
        "memory": {
            "rss_mb": process.memory_info().rss / 1024 / 1024,
            "vms_mb": process.memory_info().vms / 1024 / 1024,
            "percent": process.memory_percent()
        },
        "cpu": {
            "percent": process.cpu_percent(),
            "count": psutil.cpu_count()
        },
        "disk": {
            "free_gb": psutil.disk_usage('/').free / 1024 / 1024 / 1024,
            "used_percent": psutil.disk_usage('/').percent
        }
    }


class PerformanceLimiter:
    """
    Performance limiter to ensure operations stay within Heroku constraints.
    """
    
    def __init__(
        self,
        max_memory_mb: int = 512,
        max_execution_time: float = 30.0,
        max_respondents: int = 2000,
        max_tasks_per_respondent: int = 20,
        max_options_per_task: int = 5
    ):
        self.max_memory_mb = max_memory_mb
        self.max_execution_time = max_execution_time
        self.max_respondents = max_respondents
        self.max_tasks_per_respondent = max_tasks_per_respondent
        self.max_options_per_task = max_options_per_task
    
    def validate_design_parameters(
        self,
        num_respondents: int,
        num_screens: int,
        options_per_screen: int,
        num_attributes: int,
        total_levels: int
    ) -> Dict[str, Any]:
        """
        Validate design parameters against performance limits.
        
        Returns:
            Dict with validation results and recommendations
        """
        issues = []
        recommendations = []
        
        # Check respondent count
        if num_respondents > self.max_respondents:
            issues.append(f"Too many respondents ({num_respondents} > {self.max_respondents})")
            recommendations.append(f"Reduce to {self.max_respondents} or fewer respondents")
        
        # Check tasks per respondent
        if num_screens > self.max_tasks_per_respondent:
            issues.append(f"Too many tasks per respondent ({num_screens} > {self.max_tasks_per_respondent})")
            recommendations.append(f"Reduce to {self.max_tasks_per_respondent} or fewer tasks per respondent")
        
        # Check options per task
        if options_per_screen > self.max_options_per_task:
            issues.append(f"Too many options per task ({options_per_screen} > {self.max_options_per_task})")
            recommendations.append(f"Reduce to {self.max_options_per_task} or fewer options per task")
        
        # Estimate memory usage
        estimated_memory = self._estimate_memory_usage(
            num_respondents, num_screens, options_per_screen, num_attributes, total_levels
        )
        
        if estimated_memory > self.max_memory_mb:
            issues.append(f"Estimated memory usage too high ({estimated_memory:.1f}MB > {self.max_memory_mb}MB)")
            recommendations.append("Reduce design complexity or sample size")
        
        # Estimate execution time
        estimated_time = self._estimate_execution_time(
            num_respondents, num_screens, options_per_screen, num_attributes, total_levels
        )
        
        if estimated_time > self.max_execution_time:
            issues.append(f"Estimated execution time too long ({estimated_time:.1f}s > {self.max_execution_time}s)")
            recommendations.append("Reduce design complexity or sample size")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations,
            "estimates": {
                "memory_mb": estimated_memory,
                "execution_time_s": estimated_time
            }
        }
    
    def _estimate_memory_usage(
        self,
        num_respondents: int,
        num_screens: int,
        options_per_screen: int,
        num_attributes: int,
        total_levels: int
    ) -> float:
        """
        Estimate memory usage for a design.
        
        Returns:
            Estimated memory usage in MB
        """
        # Base memory for Python objects
        base_memory = 50  # MB
        
        # Memory for design data
        total_observations = num_respondents * num_screens * options_per_screen
        data_memory = total_observations * num_attributes * 0.001  # Rough estimate
        
        # Memory for algorithm processing
        algorithm_memory = total_levels * num_attributes * 0.01  # Rough estimate
        
        return base_memory + data_memory + algorithm_memory
    
    def _estimate_execution_time(
        self,
        num_respondents: int,
        num_screens: int,
        options_per_screen: int,
        num_attributes: int,
        total_levels: int
    ) -> float:
        """
        Estimate execution time for a design.
        
        Returns:
            Estimated execution time in seconds
        """
        # Base time
        base_time = 1.0  # seconds
        
        # Time scales with complexity
        complexity_factor = (num_respondents * num_screens * options_per_screen * total_levels) / 10000
        
        return base_time + complexity_factor


# Global performance limiter instance
performance_limiter = PerformanceLimiter()


def get_performance_limiter() -> PerformanceLimiter:
    """
    Get the global performance limiter instance.
    
    Returns:
        PerformanceLimiter instance
    """
    return performance_limiter
