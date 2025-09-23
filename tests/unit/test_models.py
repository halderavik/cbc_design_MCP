from conjoint_mcp.models.requests import (
    Attribute,
    AttributeLevel,
    DesignGrid,
    GenerateDesignRequest,
)


def test_generate_design_request_validation():
    color = Attribute(name="Color", levels=[AttributeLevel(name="Red"), AttributeLevel(name="Blue")])
    size = Attribute(name="Size", levels=[AttributeLevel(name="S"), AttributeLevel(name="L")])
    grid = DesignGrid(attributes=[color, size])

    req = GenerateDesignRequest(method="random", grid=grid, options_per_screen=3, num_screens=8)
    assert req.method == "random"
    assert req.options_per_screen == 3
    assert req.num_screens == 8
    assert len(req.grid.attributes) == 2


