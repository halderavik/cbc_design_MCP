import asyncio
import pytest


@pytest.mark.asyncio
async def test_design_optimize_basic():
    from conjoint_mcp.server import handle_request

    req = {
        "jsonrpc": "2.0",
        "id": 201,
        "method": "design.optimize",
        "params": {
            "grid": {
                "attributes": [
                    {"name": "Color", "levels": [{"name": "Red"}, {"name": "Blue"}]},
                    {"name": "Size", "levels": [{"name": "S"}, {"name": "L"}]},
                ]
            },
            "target_power": 0.8,
        },
    }
    resp = await handle_request(req)
    assert resp["id"] == 201
    result = resp["result"]
    assert "num_respondents" in result
    assert "num_screens" in result
    assert "options_per_screen" in result
    assert "expected_power" in result
    assert result["expected_power"] >= 0


@pytest.mark.asyncio
async def test_design_optimize_with_constraints():
    from conjoint_mcp.server import handle_request

    req = {
        "jsonrpc": "2.0",
        "id": 202,
        "method": "design.optimize",
        "params": {
            "grid": {
                "attributes": [
                    {"name": "Color", "levels": [{"name": "Red"}, {"name": "Blue"}]},
                ]
            },
            "target_power": 0.8,
            "fixed_respondents": 100,
            "fixed_screens": 8,
        },
    }
    resp = await handle_request(req)
    assert resp["id"] == 202
    result = resp["result"]
    assert result["num_respondents"] == 100
    assert result["num_screens"] == 8
