import asyncio
import pytest


@pytest.mark.asyncio
async def test_design_generate_doptimal():
    from conjoint_mcp.server import handle_request

    req = {
        "jsonrpc": "2.0",
        "id": 301,
        "method": "design.generate",
        "params": {
            "method": "doptimal",
            "grid": {
                "attributes": [
                    {"name": "Color", "levels": [{"name": "Red"}, {"name": "Blue"}]},
                    {"name": "Size", "levels": [{"name": "S"}, {"name": "L"}]},
                ]
            },
            "options_per_screen": 2,
            "num_screens": 3,
        },
    }
    resp = await handle_request(req)
    assert resp["id"] == 301
    result = resp["result"]
    assert len(result["tasks"]) == 3
    assert "efficiency" in result
    assert result["efficiency"] >= 0


@pytest.mark.asyncio
async def test_design_generate_doptimal_alternative_name():
    from conjoint_mcp.server import handle_request

    req = {
        "jsonrpc": "2.0",
        "id": 302,
        "method": "design.generate",
        "params": {
            "method": "d-optimal",
            "grid": {
                "attributes": [
                    {"name": "Color", "levels": [{"name": "Red"}, {"name": "Blue"}]},
                ]
            },
            "options_per_screen": 2,
            "num_screens": 2,
        },
    }
    resp = await handle_request(req)
    assert resp["id"] == 302
    result = resp["result"]
    assert len(result["tasks"]) == 2
    assert "efficiency" in result
