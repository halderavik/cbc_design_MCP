import asyncio
import pytest


@pytest.mark.asyncio
async def test_design_export_csv():
    from conjoint_mcp.server import handle_request

    req = {
        "jsonrpc": "2.0",
        "id": 401,
        "method": "design.export",
        "params": {
            "design_request": {
                "method": "random",
                "grid": {
                    "attributes": [
                        {"name": "Color", "levels": [{"name": "Red"}, {"name": "Blue"}]},
                        {"name": "Size", "levels": [{"name": "S"}, {"name": "L"}]},
                    ]
                },
                "options_per_screen": 2,
                "num_screens": 2,
            },
            "format": "csv",
            "include_metadata": True,
        },
    }
    resp = await handle_request(req)
    assert resp["id"] == 401
    result = resp["result"]
    assert "content" in result
    assert "format" in result
    assert "summary" in result
    assert result["format"] == "csv"
    assert "CBC Design Export" in result["content"]


@pytest.mark.asyncio
async def test_design_export_json():
    from conjoint_mcp.server import handle_request

    req = {
        "jsonrpc": "2.0",
        "id": 402,
        "method": "design.export",
        "params": {
            "design_request": {
                "method": "random",
                "grid": {
                    "attributes": [
                        {"name": "Color", "levels": [{"name": "Red"}, {"name": "Blue"}]},
                    ]
                },
                "options_per_screen": 2,
                "num_screens": 1,
            },
            "format": "json",
        },
    }
    resp = await handle_request(req)
    assert resp["id"] == 402
    result = resp["result"]
    assert result["format"] == "json"
    assert "metadata" in result["content"]
    assert "tasks" in result["content"]


@pytest.mark.asyncio
async def test_design_export_qualtrics():
    from conjoint_mcp.server import handle_request

    req = {
        "jsonrpc": "2.0",
        "id": 403,
        "method": "design.export",
        "params": {
            "design_request": {
                "method": "random",
                "grid": {
                    "attributes": [
                        {"name": "Color", "levels": [{"name": "Red"}, {"name": "Blue"}]},
                    ]
                },
                "options_per_screen": 2,
                "num_screens": 1,
            },
            "format": "qualtrics",
        },
    }
    resp = await handle_request(req)
    assert resp["id"] == 403
    result = resp["result"]
    assert result["format"] == "qualtrics"
    assert "Task,Option,Attribute,Level" in result["content"]
