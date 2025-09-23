from conjoint_mcp.algorithms.random import generate_random_design
from conjoint_mcp.models.requests import Attribute, AttributeLevel, DesignGrid


def test_generate_random_design_shapes():
    color = Attribute(name="Color", levels=[AttributeLevel(name="Red"), AttributeLevel(name="Blue")])
    size = Attribute(name="Size", levels=[AttributeLevel(name="S"), AttributeLevel(name="L")])
    grid = DesignGrid(attributes=[color, size])

    tasks = generate_random_design(grid, options_per_screen=3, num_screens=5)
    assert len(tasks) == 5
    for t in tasks:
        assert len(t["options"]) == 3
        for option in t["options"]:
            assert set(option.keys()) == {"Color", "Size"}


