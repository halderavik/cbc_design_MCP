import asyncio

import pytest


@pytest.mark.asyncio
async def test_design_generate_random():
    from conjoint_mcp.server import handle_request

    req = {
        "jsonrpc": "2.0",
        "id": 101,
        "method": "design.generate",
        "params": {
            "method": "random",
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
    assert resp["id"] == 101
    result = resp["result"]
    assert len(result["tasks"]) == 3
    assert "efficiency" in result


@pytest.mark.asyncio
async def test_design_generate_balanced():
    from conjoint_mcp.server import handle_request

    req = {
        "jsonrpc": "2.0",
        "id": 103,
        "method": "design.generate",
        "params": {
            "method": "balanced",
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
    assert resp["id"] == 103
    result = resp["result"]
    assert len(result["tasks"]) == 3


@pytest.mark.asyncio
async def test_design_generate_orthogonal():
    from conjoint_mcp.server import handle_request

    req = {
        "jsonrpc": "2.0",
        "id": 104,
        "method": "design.generate",
        "params": {
            "method": "orthogonal",
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
    assert resp["id"] == 104
    result = resp["result"]
    assert len(result["tasks"]) == 3


@pytest.mark.asyncio
async def test_design_generate_invalid_params():
    from conjoint_mcp.server import handle_request

    req = {"jsonrpc": "2.0", "id": 102, "method": "design.generate", "params": {}}
    resp = await handle_request(req)
    assert resp["id"] == 102
    assert "error" in resp
    assert resp["error"]["code"] == -32602


