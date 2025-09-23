from conjoint_mcp.algorithms.doptimal import (
    generate_doptimal_design,
    calculate_d_efficiency,
    _create_design_matrix,
    _calculate_d_optimality,
)
from conjoint_mcp.models.requests import Attribute, AttributeLevel, DesignGrid


def test_doptimal_design_generation():
    color = Attribute(name="Color", levels=[AttributeLevel(name="Red"), AttributeLevel(name="Blue")])
    size = Attribute(name="Size", levels=[AttributeLevel(name="S"), AttributeLevel(name="L")])
    grid = DesignGrid(attributes=[color, size])
    
    design = generate_doptimal_design(grid, num_screens=3, options_per_screen=2, max_iterations=10)
    
    assert len(design) == 3
    for task in design:
        assert len(task["options"]) == 2
        for option in task["options"]:
            assert "Color" in option
            assert "Size" in option


def test_d_efficiency_calculation():
    color = Attribute(name="Color", levels=[AttributeLevel(name="Red"), AttributeLevel(name="Blue")])
    grid = DesignGrid(attributes=[color])
    
    # Simple design with 2 tasks, 2 options each
    design = [
        {"task_index": 1, "options": [{"Color": "Red"}, {"Color": "Blue"}]},
        {"task_index": 2, "options": [{"Color": "Blue"}, {"Color": "Red"}]},
    ]
    
    efficiency = calculate_d_efficiency(design, grid)
    assert 0 <= efficiency <= 1


def test_design_matrix_creation():
    color = Attribute(name="Color", levels=[AttributeLevel(name="Red"), AttributeLevel(name="Blue")])
    grid = DesignGrid(attributes=[color])
    
    design = [
        {"task_index": 1, "options": [{"Color": "Red"}, {"Color": "Blue"}]},
    ]
    
    X = _create_design_matrix(design, grid)
    assert X.shape[0] == 2  # 2 options
    assert X.shape[1] == 1  # 1 parameter (Blue level, Red is reference)


def test_d_optimality_calculation():
    import numpy as np
    
    # Simple 2x2 identity matrix
    X = np.array([[1, 0], [0, 1]])
    d_opt = _calculate_d_optimality(X)
    assert d_opt >= 0  # Should be non-negative for non-singular matrix
