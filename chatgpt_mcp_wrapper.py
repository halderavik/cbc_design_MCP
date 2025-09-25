import os
import base64
from typing import Any, Dict, List
import json
import asyncio

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, Resource, TextContent
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse, StreamingResponse
from starlette.routing import Mount, Route
from starlette.middleware.base import BaseHTTPMiddleware

# ---------- CONFIG ----------
BASE_URL = os.getenv(
    "CBC_BASE_URL",
    "https://cbc-design-mcp-5881195c8e73.herokuapp.com"
)
HEALTH_URL   = f"{BASE_URL}/health"
GENERATE_URL = f"{BASE_URL}/api/design/generate"
OPTIMIZE_URL = f"{BASE_URL}/api/design/optimize"
EXPORT_URL   = f"{BASE_URL}/api/design/export"

# Upstream auth headers (optional)
def _upstream_headers() -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if (api_key := os.getenv("CBC_API_KEY")):
        headers["x-api-key"] = api_key
    if (bearer := os.getenv("CBC_BEARER")):
        headers["Authorization"] = f"Bearer {bearer}"
    return headers

# Shared HTTPX client timeout (tune if your upstream is slow)
HTTPX_TIMEOUT = httpx.Timeout(connect=10.0, read=60.0, write=60.0, pool=60.0)

# ---------- MCP TOOLS ----------
mcp = FastMCP("cbc-design")

@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """Ping the upstream CBC server health endpoint."""
    try:
        async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as client:
            r = await client.get(HEALTH_URL, headers=_upstream_headers())
            r.raise_for_status()
            if "application/json" in r.headers.get("content-type", ""):
                return r.json()
            return {"status": "ok", "text": r.text}
    except httpx.HTTPStatusError as e:
        return {"error": "upstream_status_error", "status": e.response.status_code, "detail": e.response.text}
    except httpx.RequestError as e:
        return {"error": "upstream_request_error", "detail": str(e)}

@mcp.tool()
async def generate_design(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a CBC design.
    Args:
        spec: JSON payload expected by /api/design/generate
    """
    try:
        async with httpx.AsyncClient(timeout=None) as client:  # None = no overall timeout
            r = await client.post(GENERATE_URL, json=spec, headers=_upstream_headers())
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as e:
        return {"error": "upstream_status_error", "status": e.response.status_code, "detail": e.response.text}
    except httpx.RequestError as e:
        return {"error": "upstream_request_error", "detail": str(e)}

@mcp.tool()
async def optimize_parameters(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimize design parameters.
    Args:
        spec: JSON payload expected by /api/design/optimize
    """
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            r = await client.post(OPTIMIZE_URL, json=spec, headers=_upstream_headers())
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as e:
        return {"error": "upstream_status_error", "status": e.response.status_code, "detail": e.response.text}
    except httpx.RequestError as e:
        return {"error": "upstream_request_error", "detail": str(e)}

@mcp.tool()
async def export_design(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Export a design. If upstream returns a file (CSV/XLSX), returns base64 bytes.
    Args:
        spec: JSON payload expected by /api/design/export
    """
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            r = await client.post(EXPORT_URL, json=spec, headers=_upstream_headers())
            r.raise_for_status()
            ctype = r.headers.get("content-type", "")
            if "application/json" in ctype:
                return r.json()
            return {
                "content_type": ctype or "application/octet-stream",
                "content_base64": base64.b64encode(r.content).decode("ascii"),
                "note": "Decode base64 to get file bytes"
            }
    except httpx.HTTPStatusError as e:
        return {"error": "upstream_status_error", "status": e.response.status_code, "detail": e.response.text}
    except httpx.RequestError as e:
        return {"error": "upstream_request_error", "detail": str(e)}

# --- ChatGPT-required: search and fetch tools ---
def _catalog() -> list[dict[str, str]]:
    return [
        {
            "id": "doc-chatgpt-quickstart",
            "title": "ChatGPT MCP Wrapper Quickstart (CBC Design)",
            "url": "https://raw.githubusercontent.com/halderavik/cbc_design_MCP/main/docs/chatgpt_quickstart.md"
        },
        {
            "id": "doc-claude-quickstart",
            "title": "Claude Quickstart (local MCP)",
            "url": "https://raw.githubusercontent.com/halderavik/cbc_design_MCP/main/docs/claude_quickstart.md"
        },
        {
            "id": "doc-examples",
            "title": "CBC Examples & Prompts",
            "url": "https://raw.githubusercontent.com/halderavik/cbc_design_MCP/main/docs/examples.md"
        },
        {
            "id": "api-health",
            "title": "Upstream Health Endpoint",
            "url": f"{BASE_URL}/health"
        },
        {
            "id": "api-generate",
            "title": "Generate Design API",
            "url": f"{BASE_URL}/api/design/generate"
        },
        {
            "id": "api-optimize",
            "title": "Optimize Parameters API",
            "url": f"{BASE_URL}/api/design/optimize"
        },
        {
            "id": "api-export",
            "title": "Export Design API",
            "url": f"{BASE_URL}/api/design/export"
        }
    ]

@mcp.tool()
async def search(query: str) -> Dict[str, Any]:
    """Return a list of relevant resources for a query."""
    catalog = _catalog()
    q = (query or "").lower()
    if q:
        filtered = [r for r in catalog if q in r["title"].lower() or q in r["id"].lower()]
    else:
        filtered = catalog
    
    payload = {"results": filtered}
    return payload

@mcp.tool()
async def fetch(id: str) -> Dict[str, Any]:
    """Fetch a single item by id (ChatGPT requires an id parameter)."""
    items = _catalog()
    match = next((r for r in items if r["id"] == id), None)
    payload = {"results": [match] if match else []}
    return payload

# ---------- JSON-RPC MCP Server for ChatGPT ----------
async def mcp_handler(request):
    """Handle JSON-RPC MCP requests for ChatGPT."""
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        if method == "initialize":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": "cbc-design-mcp",
                        "version": "1.0.0"
                    }
                }
            })
        
        elif method == "tools/list":
            tools = [
                {
                    "name": "health_check",
                    "description": "Ping the upstream CBC server health endpoint",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "generate_design",
                    "description": "Generate a CBC design",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "spec": {
                                "type": "object",
                                "description": "Design specification"
                            }
                        },
                        "required": ["spec"]
                    }
                },
                {
                    "name": "optimize_parameters",
                    "description": "Optimize design parameters",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "spec": {
                                "type": "object",
                                "description": "Optimization specification"
                            }
                        },
                        "required": ["spec"]
                    }
                },
                {
                    "name": "export_design",
                    "description": "Export a design",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "spec": {
                                "type": "object",
                                "description": "Export specification"
                            }
                        },
                        "required": ["spec"]
                    }
                },
                {
                    "name": "search",
                    "description": "Search for resources",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "fetch",
                    "description": "Fetch a resource by ID",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "Resource ID"
                            }
                        },
                        "required": ["id"]
                    }
                }
            ]
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools}
            })
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "health_check":
                result = await health_check()
            elif tool_name == "generate_design":
                result = await generate_design(arguments.get("spec", {}))
            elif tool_name == "optimize_parameters":
                result = await optimize_parameters(arguments.get("spec", {}))
            elif tool_name == "export_design":
                result = await export_design(arguments.get("spec", {}))
            elif tool_name == "search":
                result = await search(arguments.get("query", ""))
            elif tool_name == "fetch":
                result = await fetch(arguments.get("id", ""))
            else:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {tool_name}"}
                })
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
            })
        
        elif method == "resources/list":
            resources = [
                {
                    "uri": f"cbc-design://{r['id']}",
                    "name": r["title"],
                    "description": r["url"],
                    "mimeType": "text/plain"
                }
                for r in _catalog()
            ]
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"resources": resources}
            })
        
        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            })
    
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id if 'request_id' in locals() else None,
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
        })

# ---------- Inbound auth middleware (optional) ----------
class RequireAPIKey(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        key = os.getenv("WRAPPER_API_KEY")
        # Only protect /mcp; leave / and /healthz open
        if key and request.url.path.startswith("/mcp"):
            if request.headers.get("x-api-key") != key:
                return JSONResponse({"error": "unauthorized"}, status_code=401)
        return await call_next(request)

# ---------- Wrapper health & root ----------
async def wrapper_health(_request):
    return JSONResponse({"ok": True, "service": "cbc-mcp-wrapper", "mcp_endpoint": "/mcp"})

async def root(_request):
    return PlainTextResponse("CBC MCP wrapper is running. Use /mcp for MCP and /healthz for wrapper health.")

# Create the main Starlette app
app = Starlette()

# Optional inbound auth middleware
app.add_middleware(RequireAPIKey)

# Add routes
app.add_route("/", root)
app.add_route("/healthz", wrapper_health)
app.add_route("/mcp", mcp_handler, methods=["POST"])

# --- Debug/diagnostic REST endpoints for ChatGPT verification ---
async def tools_list_rest(_request):
    return JSONResponse({
        "tools": [
            {"name": "health_check", "description": "Ping the upstream CBC server health endpoint"},
            {"name": "generate_design", "description": "Generate a CBC design"},
            {"name": "optimize_parameters", "description": "Optimize design parameters"},
            {"name": "export_design", "description": "Export a design"},
            {"name": "search", "description": "Query docs/API endpoints and return results array"},
            {"name": "fetch", "description": "Fetch a single catalog item by id"}
        ]
    })

async def resources_list_rest(_request):
    return JSONResponse({
        "resources": [
            {"id": r["id"], "name": r["title"], "description": r["url"]}
            for r in _catalog()
        ]
    })

async def resources_read_rest(request):
    params = dict(request.query_params)
    item_id = params.get("id", "")
    items = _catalog()
    match = next((r for r in items if r["id"] == item_id), None)
    return JSONResponse({"results": [match] if match else []})

app.add_route("/tools/list", tools_list_rest)
app.add_route("/resources/list", resources_list_rest)
app.add_route("/resources/read", resources_read_rest)
