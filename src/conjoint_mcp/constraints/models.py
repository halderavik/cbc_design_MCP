from __future__ import annotations

from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ProhibitedCombination(BaseModel):
    """
    Represents a prohibited combination of attribute levels.
    
    Args:
        attributes (Dict[str, str]): Attribute name to level name mapping.
        reason (Optional[str]): Reason for prohibition.
    """
    
    attributes: Dict[str, str] = Field(description="Attribute name to level name mapping")
    reason: Optional[str] = Field(default=None, description="Reason for prohibition")


class RequiredCombination(BaseModel):
    """
    Represents a required combination of attribute levels.
    
    Args:
        attributes (Dict[str, str]): Attribute name to level name mapping.
        reason (Optional[str]): Reason for requirement.
    """
    
    attributes: Dict[str, str] = Field(description="Attribute name to level name mapping")
    reason: Optional[str] = Field(default=None, description="Reason for requirement")


class LevelBalanceConstraint(BaseModel):
    """
    Constraint for maintaining balance across attribute levels.
    
    Args:
        attribute_name (str): Name of the attribute to balance.
        min_frequency (Optional[int]): Minimum frequency for each level.
        max_frequency (Optional[int]): Maximum frequency for each level.
        tolerance (float): Tolerance for balance (0-1).
    """
    
    attribute_name: str = Field(description="Name of the attribute to balance")
    min_frequency: Optional[int] = Field(default=None, ge=0, description="Minimum frequency for each level")
    max_frequency: Optional[int] = Field(default=None, ge=0, description="Maximum frequency for each level")
    tolerance: float = Field(default=0.1, ge=0.0, le=1.0, description="Tolerance for balance")


class CustomRule(BaseModel):
    """
    Custom rule for design constraints.
    
    Args:
        name (str): Name of the rule.
        condition (str): Condition expression (simple format).
        action (str): Action to take when condition is met.
        description (Optional[str]): Description of the rule.
    """
    
    name: str = Field(description="Name of the rule")
    condition: str = Field(description="Condition expression")
    action: str = Field(description="Action to take when condition is met")
    description: Optional[str] = Field(default=None, description="Description of the rule")


class ConstraintSpec(BaseModel):
    """
    Complete constraint specification for a design.
    
    Args:
        prohibited_combinations (List[ProhibitedCombination]): List of prohibited combinations.
        required_combinations (List[RequiredCombination]): List of required combinations.
        level_balance_constraints (List[LevelBalanceConstraint]): List of balance constraints.
        custom_rules (List[CustomRule]): List of custom rules.
        max_complexity (Optional[int]): Maximum complexity per choice task.
    """
    
    prohibited_combinations: List[ProhibitedCombination] = Field(default_factory=list)
    required_combinations: List[RequiredCombination] = Field(default_factory=list)
    level_balance_constraints: List[LevelBalanceConstraint] = Field(default_factory=list)
    custom_rules: List[CustomRule] = Field(default_factory=list)
    max_complexity: Optional[int] = Field(default=None, ge=1, description="Maximum complexity per choice task")
