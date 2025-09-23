from conjoint_mcp.constraints.manager import ConstraintManager
from conjoint_mcp.constraints.models import ConstraintSpec, ProhibitedCombination, RequiredCombination


def test_constraint_manager_prohibited_combinations():
    # Create constraint spec with prohibited combinations
    prohibited = ProhibitedCombination(
        attributes={"Color": "Red", "Size": "S"},
        reason="Red small items are not available"
    )
    constraint_spec = ConstraintSpec(prohibited_combinations=[prohibited])
    
    manager = ConstraintManager(constraint_spec)
    
    # Test valid combination
    valid_option = {"Color": "Blue", "Size": "S"}
    is_valid, reason = manager.is_combination_valid(valid_option)
    assert is_valid
    assert reason == ""
    
    # Test prohibited combination
    invalid_option = {"Color": "Red", "Size": "S"}
    is_valid, reason = manager.is_combination_valid(invalid_option)
    assert not is_valid
    assert "Prohibited combination" in reason


def test_constraint_manager_required_combinations():
    # Create constraint spec with required combinations
    required = RequiredCombination(
        attributes={"Color": "Blue", "Size": "L"},
        reason="Blue large items must be included"
    )
    constraint_spec = ConstraintSpec(required_combinations=[required])
    
    manager = ConstraintManager(constraint_spec)
    
    # Test design missing required combination
    design = [
        {"task_index": 1, "options": [{"Color": "Red", "Size": "S"}]},
        {"task_index": 2, "options": [{"Color": "Blue", "Size": "S"}]},
    ]
    is_valid, violations = manager.validate_design(design)
    assert not is_valid
    assert any("Missing required combination" in v for v in violations)
    
    # Test design with required combination
    design_with_required = [
        {"task_index": 1, "options": [{"Color": "Red", "Size": "S"}]},
        {"task_index": 2, "options": [{"Color": "Blue", "Size": "L"}]},
    ]
    is_valid, violations = manager.validate_design(design_with_required)
    assert is_valid
    assert len(violations) == 0


def test_constraint_manager_filter_options():
    prohibited = ProhibitedCombination(
        attributes={"Color": "Red", "Size": "S"},
        reason="Red small items are not available"
    )
    constraint_spec = ConstraintSpec(prohibited_combinations=[prohibited])
    
    manager = ConstraintManager(constraint_spec)
    
    options = [
        {"Color": "Red", "Size": "S"},  # Should be filtered out
        {"Color": "Blue", "Size": "S"},  # Should be kept
        {"Color": "Red", "Size": "L"},   # Should be kept
    ]
    
    valid_options = manager.filter_valid_options(None, options)
    assert len(valid_options) == 2
    assert {"Color": "Red", "Size": "S"} not in valid_options
