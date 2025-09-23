import asyncio
import json

import pytest


@pytest.mark.asyncio
async def test_handle_ping(monkeypatch):
    # Import inside test to avoid event loop creation at import time
    from conjoint_mcp.server import handle_request

    req = {"jsonrpc": "2.0", "id": 1, "method": "ping"}
    resp = await handle_request(req)
    assert resp["id"] == 1
    assert resp["result"]["status"] == "ok"


@pytest.mark.asyncio
async def test_handle_unknown_method():
    from conjoint_mcp.server import handle_request

    req = {"jsonrpc": "2.0", "id": 2, "method": "does_not_exist"}
    resp = await handle_request(req)
    assert resp["id"] == 2
    assert "error" in resp
    assert resp["error"]["code"] == -32601


@pytest.mark.asyncio
async def test_handle_missing_id():
    from conjoint_mcp.server import handle_request

    req = {"jsonrpc": "2.0", "method": "ping"}
    resp = await handle_request(req)
    # Should still return result with id None per JSON-RPC spec tolerance here
    assert resp.get("id") is None
    assert resp["result"]["status"] == "ok"


