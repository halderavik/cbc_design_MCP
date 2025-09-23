from __future__ import annotations

from typing import Dict, List, Set, Tuple

from conjoint_mcp.constraints.models import ConstraintSpec, ProhibitedCombination, RequiredCombination
from conjoint_mcp.models.requests import DesignGrid


class ConstraintManager:
    """
    Manages design constraints and validates designs against them.
    """
    
    def __init__(self, constraint_spec: ConstraintSpec):
        """
        Initialize constraint manager with constraint specification.
        
        Args:
            constraint_spec (ConstraintSpec): Constraint specification.
        """
        self.constraint_spec = constraint_spec
        self._prohibited_set = self._build_prohibited_set()
        self._required_set = self._build_required_set()
    
    def _build_prohibited_set(self) -> Set[Tuple[str, ...]]:
        """Build set of prohibited combinations for fast lookup."""
        prohibited_set = set()
        for combo in self.constraint_spec.prohibited_combinations:
            # Create sorted tuple for consistent comparison
            combo_tuple = tuple(sorted(combo.attributes.items()))
            prohibited_set.add(combo_tuple)
        return prohibited_set
    
    def _build_required_set(self) -> Set[Tuple[str, ...]]:
        """Build set of required combinations for fast lookup."""
        required_set = set()
        for combo in self.constraint_spec.required_combinations:
            # Create sorted tuple for consistent comparison
            combo_tuple = tuple(sorted(combo.attributes.items()))
            required_set.add(combo_tuple)
        return required_set
    
    def is_combination_valid(self, option: Dict[str, str]) -> Tuple[bool, str]:
        """
        Check if a single option combination is valid.
        
        Args:
            option (Dict[str, str]): Option to validate.
            
        Returns:
            Tuple[bool, str]: (is_valid, reason)
        """
        # Check prohibited combinations
        option_tuple = tuple(sorted(option.items()))
        if option_tuple in self._prohibited_set:
            return False, f"Prohibited combination: {dict(option_tuple)}"
        
        return True, ""
    
    def validate_design(self, design: List[dict]) -> Tuple[bool, List[str]]:
        """
        Validate entire design against constraints.
        
        Args:
            design (List[dict]): Design to validate.
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_violations)
        """
        violations = []
        
        for task in design:
            for option in task.get("options", []):
                is_valid, reason = self.is_combination_valid(option)
                if not is_valid:
                    violations.append(f"Task {task.get('task_index', '?')}: {reason}")
        
        # Check required combinations
        if self._required_set:
            violations.extend(self._check_required_combinations(design))
        
        return len(violations) == 0, violations
    
    def _check_required_combinations(self, design: List[dict]) -> List[str]:
        """Check if all required combinations are present in the design."""
        violations = []
        
        # Collect all combinations in the design
        design_combinations = set()
        for task in design:
            for option in task.get("options", []):
                option_tuple = tuple(sorted(option.items()))
                design_combinations.add(option_tuple)
        
        # Check if all required combinations are present
        for required_tuple in self._required_set:
            if required_tuple not in design_combinations:
                violations.append(f"Missing required combination: {dict(required_tuple)}")
        
        return violations
    
    def filter_valid_options(self, grid: DesignGrid, options: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Filter options to only include valid combinations.
        
        Args:
            grid (DesignGrid): Design grid specification.
            options (List[Dict[str, str]]): Options to filter.
            
        Returns:
            List[Dict[str, str]]: Filtered valid options.
        """
        valid_options = []
        for option in options:
            is_valid, _ = self.is_combination_valid(option)
            if is_valid:
                valid_options.append(option)
        return valid_options
    
    def get_constraint_summary(self) -> Dict[str, int]:
        """
        Get summary of constraint counts.
        
        Returns:
            Dict[str, int]: Summary of constraint counts.
        """
        return {
            "prohibited_combinations": len(self.constraint_spec.prohibited_combinations),
            "required_combinations": len(self.constraint_spec.required_combinations),
            "level_balance_constraints": len(self.constraint_spec.level_balance_constraints),
            "custom_rules": len(self.constraint_spec.custom_rules),
        }
