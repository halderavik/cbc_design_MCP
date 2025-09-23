from conjoint_mcp.algorithms.balanced import generate_balanced_overlap_design
from conjoint_mcp.algorithms.orthogonal import generate_orthogonal_array_design
from conjoint_mcp.models.requests import Attribute, AttributeLevel, DesignGrid


def base_grid():
    color = Attribute(name="Color", levels=[AttributeLevel(name="Red"), AttributeLevel(name="Blue")])
    size = Attribute(name="Size", levels=[AttributeLevel(name="S"), AttributeLevel(name="L")])
    return DesignGrid(attributes=[color, size])


def test_balanced_overlap_shapes():
    grid = base_grid()
    tasks = generate_balanced_overlap_design(grid, options_per_screen=2, num_screens=4)
    assert len(tasks) == 4
    for t in tasks:
        assert len(t["options"]) == 2


def test_orthogonal_two_level_shapes():
    grid = base_grid()
    tasks = generate_orthogonal_array_design(grid, options_per_screen=2, num_screens=3)
    assert len(tasks) == 3
    for t in tasks:
        assert len(t["options"]) == 2


