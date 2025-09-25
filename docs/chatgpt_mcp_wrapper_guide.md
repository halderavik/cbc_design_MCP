# ChatGPT MCP Wrapper Development Guide

This guide provides step-by-step instructions for building MCP (Model Context Protocol) wrappers that work with ChatGPT's Custom Connectors feature.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Understanding ChatGPT MCP Requirements](#understanding-chatgpt-mcp-requirements)
4. [Project Structure](#project-structure)
5. [Implementation Steps](#implementation-steps)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [Example: Complete Wrapper](#example-complete-wrapper)

## Overview

ChatGPT Custom Connectors allow you to integrate external APIs and services through MCP wrappers. Unlike Claude Desktop which uses stdio-based MCP, ChatGPT expects HTTP-based JSON-RPC MCP servers.

### Key Differences from Claude MCP:
- **Protocol**: JSON-RPC over HTTP (not stdio)
- **Session Management**: No session persistence required
- **Required Tools**: Must implement `search` and `fetch` tools
- **Response Format**: Specific MCP content array format

## Prerequisites

- Python 3.11+
- Heroku account (for deployment)
- Basic understanding of:
  - Python async/await
  - JSON-RPC protocol
  - HTTP APIs
  - Starlette/FastAPI

## Understanding ChatGPT MCP Requirements

### Required MCP Methods

ChatGPT expects your MCP server to implement these JSON-RPC methods:

1. **`initialize`** - Protocol handshake
2. **`tools/list`** - List available tools
3. **`tools/call`** - Execute specific tools
4. **`resources/list`** - List available resources (optional but recommended)

### Required Tools

Your wrapper **must** implement these two tools:

- **`search`** - Search functionality for ChatGPT's search capability
- **`fetch`** - Fetch specific resources by ID

### Response Format

All tool responses must follow this format:

```json
{
  "jsonrpc": "2.0",
  "id": "request_id",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "JSON string of your data"
      }
    ]
  }
}
```

## Project Structure

```
your-mcp-wrapper/
├── app.py                 # Main MCP server implementation
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku process definition
├── runtime.txt           # Python version (deprecated, use .python-version)
├── .python-version       # Python version specification
├── .gitignore           # Git ignore rules
├── README.md            # Project documentation
└── docs/                # Additional documentation
    └── quickstart.md    # User quickstart guide
```

## Implementation Steps

### Step 1: Create the Basic Structure

Create your main `app.py` file:

```python
import os
import json
from typing import Any, Dict, List
import httpx
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route
from starlette.middleware.base import BaseHTTPMiddleware

# Configuration
BASE_URL = os.getenv("UPSTREAM_BASE_URL", "https://your-api.com")
API_KEY = os.getenv("UPSTREAM_API_KEY")  # Optional

# HTTP client configuration
HTTPX_TIMEOUT = httpx.Timeout(connect=10.0, read=60.0, write=60.0, pool=60.0)
```

### Step 2: Implement Your API Tools

Create functions that call your upstream API:

```python
async def health_check() -> Dict[str, Any]:
    """Check upstream API health."""
    try:
        headers = {}
        if API_KEY:
            headers["Authorization"] = f"Bearer {API_KEY}"
        
        async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/health", headers=headers)
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as e:
        return {"error": "upstream_error", "status": e.response.status_code}
    except httpx.RequestError as e:
        return {"error": "request_error", "detail": str(e)}

async def your_main_tool(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Your main API functionality."""
    try:
        headers = {"Content-Type": "application/json"}
        if API_KEY:
            headers["Authorization"] = f"Bearer {API_KEY}"
        
        async with httpx.AsyncClient(timeout=None) as client:
            r = await client.post(f"{BASE_URL}/api/endpoint", json=spec, headers=headers)
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as e:
        return {"error": "upstream_error", "status": e.response.status_code}
    except httpx.RequestError as e:
        return {"error": "request_error", "detail": str(e)}
```

### Step 3: Implement Required Search/Fetch Tools

```python
def _catalog() -> List[Dict[str, str]]:
    """Define your resource catalog."""
    return [
        {
            "id": "doc-quickstart",
            "title": "Quickstart Guide",
            "url": "https://your-docs.com/quickstart"
        },
        {
            "id": "api-reference",
            "title": "API Reference",
            "url": "https://your-docs.com/api"
        }
    ]

async def search(query: str) -> Dict[str, Any]:
    """Search functionality - REQUIRED for ChatGPT."""
    catalog = _catalog()
    q = (query or "").lower()
    
    if q:
        filtered = [r for r in catalog if q in r["title"].lower() or q in r["id"].lower()]
    else:
        filtered = catalog
    
    return {"results": filtered}

async def fetch(id: str) -> Dict[str, Any]:
    """Fetch specific resource - REQUIRED for ChatGPT."""
    items = _catalog()
    match = next((r for r in items if r["id"] == id), None)
    return {"results": [match] if match else []}
```

### Step 4: Implement JSON-RPC MCP Handler

```python
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
                        "name": "your-mcp-wrapper",
                        "version": "1.0.0"
                    }
                }
            })
        
        elif method == "tools/list":
            tools = [
                {
                    "name": "health_check",
                    "description": "Check API health",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "your_main_tool",
                    "description": "Your main functionality",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "spec": {
                                "type": "object",
                                "description": "Tool specification"
                            }
                        },
                        "required": ["spec"]
                    }
                },
                {
                    "name": "search",
                    "description": "Search resources",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "fetch",
                    "description": "Fetch resource by ID",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Resource ID"}
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
            
            # Route to appropriate tool function
            if tool_name == "health_check":
                result = await health_check()
            elif tool_name == "your_main_tool":
                result = await your_main_tool(arguments.get("spec", {}))
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
                    "uri": f"your-service://{r['id']}",
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
```

### Step 5: Create the Starlette App

```python
# Optional authentication middleware
class RequireAPIKey(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        key = os.getenv("WRAPPER_API_KEY")
        if key and request.url.path.startswith("/mcp"):
            if request.headers.get("x-api-key") != key:
                return JSONResponse({"error": "unauthorized"}, status_code=401)
        return await call_next(request)

# Health and root endpoints
async def wrapper_health(_request):
    return JSONResponse({"ok": True, "service": "your-mcp-wrapper", "mcp_endpoint": "/mcp"})

async def root(_request):
    return PlainTextResponse("Your MCP wrapper is running. Use /mcp for MCP and /healthz for health.")

# Create the main app
app = Starlette()
app.add_middleware(RequireAPIKey)  # Optional
app.add_route("/", root)
app.add_route("/healthz", wrapper_health)
app.add_route("/mcp", mcp_handler, methods=["POST"])

# Optional: Add REST endpoints for debugging
async def tools_list_rest(_request):
    return JSONResponse({
        "tools": [
            {"name": "health_check", "description": "Check API health"},
            {"name": "your_main_tool", "description": "Your main functionality"},
            {"name": "search", "description": "Search resources"},
            {"name": "fetch", "description": "Fetch resource by ID"}
        ]
    })

app.add_route("/tools/list", tools_list_rest)
```

## Testing

### Local Testing

Create a test script to verify your MCP server:

```python
# test_mcp.py
import asyncio
import httpx
import json

async def test_mcp_server():
    base_url = "http://localhost:8000"
    
    # Test initialize
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "id": "1",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "clientInfo": {"name": "test", "version": "1.0"},
                    "capabilities": {}
                }
            }
        )
        print("Initialize:", response.json())
        
        # Test tools/list
        response = await client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "id": "2",
                "method": "tools/list",
                "params": {}
            }
        )
        print("Tools list:", response.json())
        
        # Test health_check
        response = await client.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "id": "3",
                "method": "tools/call",
                "params": {
                    "name": "health_check",
                    "arguments": {}
                }
            }
        )
        print("Health check:", response.json())

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
```

### Run Local Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app:app --host 0.0.0.0 --port 8000

# Test
python test_mcp.py
```

## Deployment

### Heroku Deployment

1. **Create Heroku App**:
   ```bash
   heroku create your-mcp-wrapper
   ```

2. **Create Required Files**:

   **requirements.txt**:
   ```
   httpx
   uvicorn
   starlette
   ```

   **Procfile**:
   ```
   web: uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

   **.python-version**:
   ```
   3.11
   ```

3. **Deploy**:
   ```bash
   git init
   git add .
   git commit -m "Initial MCP wrapper"
   git push heroku main
   ```

4. **Set Environment Variables** (if needed):
   ```bash
   heroku config:set UPSTREAM_BASE_URL=https://your-api.com
   heroku config:set UPSTREAM_API_KEY=your-api-key
   heroku config:set WRAPPER_API_KEY=your-wrapper-key  # Optional
   ```

### Testing Deployed Wrapper

```bash
# Test initialize
curl -X POST https://your-mcp-wrapper.herokuapp.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"initialize","params":{"protocolVersion":"2024-11-05","clientInfo":{"name":"test","version":"1.0"},"capabilities":{}}}'

# Test tools/list
curl -X POST https://your-mcp-wrapper.herokuapp.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"2","method":"tools/list","params":{}}'

# Test health check
curl -X POST https://your-mcp-wrapper.herokuapp.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"3","method":"tools/call","params":{"name":"health_check","arguments":{}}}'
```

## Troubleshooting

### Common Issues

1. **"Missing session ID" Error**:
   - This is expected for Streamable HTTP MCP
   - ChatGPT handles sessions automatically
   - Use standard JSON-RPC MCP instead

2. **"Method not found" Error**:
   - Ensure you're implementing all required methods
   - Check method names match exactly

3. **"Object not JSON serializable" Error**:
   - Ensure all tool functions return JSON-serializable data
   - Don't return complex objects like `TextContent`

4. **ChatGPT Not Showing Tools**:
   - Verify `search` and `fetch` tools are implemented
   - Check that `tools/list` returns proper schema
   - Ensure all responses follow MCP format

5. **Upstream API Errors**:
   - Implement proper error handling
   - Return meaningful error messages
   - Use appropriate HTTP status codes

### Debug Endpoints

Add these REST endpoints for debugging:

```python
# Add to your app
app.add_route("/tools/list", tools_list_rest)
app.add_route("/resources/list", resources_list_rest)
app.add_route("/health", wrapper_health)
```

## Best Practices

### 1. Error Handling
- Always wrap API calls in try-catch blocks
- Return meaningful error messages
- Use appropriate HTTP status codes

### 2. Timeouts
- Set reasonable timeouts for upstream API calls
- Use different timeouts for different operations
- Handle timeout exceptions gracefully

### 3. Authentication
- Support multiple auth methods (API key, Bearer token)
- Make authentication optional for health checks
- Use environment variables for sensitive data

### 4. Logging
- Log all requests and responses
- Include request IDs for tracing
- Log errors with context

### 5. Documentation
- Create comprehensive README
- Document all available tools
- Provide example usage

### 6. Testing
- Write unit tests for all tools
- Test error scenarios
- Test with real upstream APIs

## Example: Complete Wrapper

Here's a complete example wrapper for a hypothetical "Weather API":

```python
import os
import json
from typing import Any, Dict, List
import httpx
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

# Configuration
WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://api.weather.com")
API_KEY = os.getenv("WEATHER_API_KEY")

async def get_weather(city: str) -> Dict[str, Any]:
    """Get weather for a city."""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{WEATHER_API_URL}/weather",
                params={"city": city, "key": API_KEY}
            )
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as e:
        return {"error": "weather_api_error", "status": e.response.status_code}
    except httpx.RequestError as e:
        return {"error": "request_error", "detail": str(e)}

def _catalog() -> List[Dict[str, str]]:
    return [
        {
            "id": "weather-docs",
            "title": "Weather API Documentation",
            "url": "https://weather.com/docs"
        },
        {
            "id": "weather-examples",
            "title": "Weather API Examples",
            "url": "https://weather.com/examples"
        }
    ]

async def search(query: str) -> Dict[str, Any]:
    catalog = _catalog()
    q = (query or "").lower()
    if q:
        filtered = [r for r in catalog if q in r["title"].lower() or q in r["id"].lower()]
    else:
        filtered = catalog
    return {"results": filtered}

async def fetch(id: str) -> Dict[str, Any]:
    items = _catalog()
    match = next((r for r in items if r["id"] == id), None)
    return {"results": [match] if match else []}

async def mcp_handler(request):
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
                    "capabilities": {"tools": {}, "resources": {}},
                    "serverInfo": {"name": "weather-mcp", "version": "1.0.0"}
                }
            })
        
        elif method == "tools/list":
            tools = [
                {
                    "name": "get_weather",
                    "description": "Get weather for a city",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string", "description": "City name"}
                        },
                        "required": ["city"]
                    }
                },
                {
                    "name": "search",
                    "description": "Search weather documentation",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "fetch",
                    "description": "Fetch documentation by ID",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Resource ID"}
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
            
            if tool_name == "get_weather":
                result = await get_weather(arguments.get("city", ""))
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

app = Starlette()
app.add_route("/", lambda _: PlainTextResponse("Weather MCP wrapper running"))
app.add_route("/healthz", lambda _: JSONResponse({"ok": True}))
app.add_route("/mcp", mcp_handler, methods=["POST"])
```

## Conclusion

Building ChatGPT MCP wrappers requires understanding the JSON-RPC protocol and implementing the required methods and tools. The key is to:

1. **Implement proper JSON-RPC handlers** for `initialize`, `tools/list`, `tools/call`
2. **Always include `search` and `fetch` tools** (required by ChatGPT)
3. **Return data in the correct MCP format** with content arrays
4. **Handle errors gracefully** and return meaningful messages
5. **Test thoroughly** before deployment
6. **Document everything** for future maintenance

This guide provides the foundation for building robust, production-ready MCP wrappers that work seamlessly with ChatGPT's Custom Connectors feature.
