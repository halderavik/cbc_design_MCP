from conjoint_mcp.handlers.optimization import handle_optimize_parameters, OptimizationRequest
from conjoint_mcp.models.requests import Attribute, AttributeLevel, DesignGrid


def test_optimize_parameters_basic():
    color = Attribute(name="Color", levels=[AttributeLevel(name="Red"), AttributeLevel(name="Blue")])
    size = Attribute(name="Size", levels=[AttributeLevel(name="S"), AttributeLevel(name="L")])
    grid = DesignGrid(attributes=[color, size])
    
    req = OptimizationRequest(grid=grid, target_power=0.8)
    result = handle_optimize_parameters(req)
    
    assert result.num_respondents > 0
    assert result.num_screens > 0
    assert result.options_per_screen >= 2
    assert 0 <= result.expected_power <= 1
    assert result.parameter_count > 0
    assert result.design_complexity > 0


def test_optimize_parameters_with_constraints():
    color = Attribute(name="Color", levels=[AttributeLevel(name="Red"), AttributeLevel(name="Blue")])
    grid = DesignGrid(attributes=[color])
    
    req = OptimizationRequest(
        grid=grid,
        target_power=0.8,
        fixed_respondents=50,
        fixed_screens=5,
        fixed_options=3
    )
    result = handle_optimize_parameters(req)
    
    assert result.num_respondents == 50
    assert result.num_screens == 5
    assert result.options_per_screen == 3
