# ChatGPT MCP Wrapper - Quick Reference

## Essential Files

```
your-wrapper/
├── app.py              # Main implementation
├── requirements.txt    # Dependencies
├── Procfile           # Heroku process
├── .python-version    # Python version
└── README.md          # Documentation
```

## Required Dependencies

```
httpx
uvicorn
starlette
```

## Core Implementation Pattern

```python
import os, json
from typing import Any, Dict, List
import httpx
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

# 1. Configuration
BASE_URL = os.getenv("UPSTREAM_URL", "https://api.example.com")
API_KEY = os.getenv("UPSTREAM_API_KEY")

# 2. Your API tools
async def your_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{BASE_URL}/endpoint", json=params, headers=headers)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return {"error": str(e)}

# 3. REQUIRED: Search and fetch tools
def _catalog() -> List[Dict[str, str]]:
    return [{"id": "doc1", "title": "Documentation", "url": "https://docs.com"}]

async def search(query: str) -> Dict[str, Any]:
    catalog = _catalog()
    q = (query or "").lower()
    filtered = [r for r in catalog if q in r["title"].lower()] if q else catalog
    return {"results": filtered}

async def fetch(id: str) -> Dict[str, Any]:
    items = _catalog()
    match = next((r for r in items if r["id"] == id), None)
    return {"results": [match] if match else []}

# 4. MCP JSON-RPC handler
async def mcp_handler(request):
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        if method == "initialize":
            return JSONResponse({
                "jsonrpc": "2.0", "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "resources": {}},
                    "serverInfo": {"name": "your-wrapper", "version": "1.0.0"}
                }
            })
        
        elif method == "tools/list":
            tools = [
                {
                    "name": "your_tool",
                    "description": "Your tool description",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"params": {"type": "object"}},
                        "required": ["params"]
                    }
                },
                {
                    "name": "search",
                    "description": "Search resources",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"]
                    }
                },
                {
                    "name": "fetch",
                    "description": "Fetch resource by ID",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"id": {"type": "string"}},
                        "required": ["id"]
                    }
                }
            ]
            return JSONResponse({"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}})
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "your_tool":
                result = await your_tool(arguments.get("params", {}))
            elif tool_name == "search":
                result = await search(arguments.get("query", ""))
            elif tool_name == "fetch":
                result = await fetch(arguments.get("id", ""))
            else:
                return JSONResponse({
                    "jsonrpc": "2.0", "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {tool_name}"}
                })
            
            return JSONResponse({
                "jsonrpc": "2.0", "id": request_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
            })
        
        else:
            return JSONResponse({
                "jsonrpc": "2.0", "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            })
    
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0", "id": request_id if 'request_id' in locals() else None,
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
        })

# 5. Create app
app = Starlette()
app.add_route("/", lambda _: PlainTextResponse("Wrapper running"))
app.add_route("/healthz", lambda _: JSONResponse({"ok": True}))
app.add_route("/mcp", mcp_handler, methods=["POST"])
```

## Deployment Files

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

## Testing Commands

```bash
# Local testing
uvicorn app:app --host 0.0.0.0 --port 8000

# Test initialize
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"initialize","params":{"protocolVersion":"2024-11-05","clientInfo":{"name":"test","version":"1.0"},"capabilities":{}}}'

# Test tools/list
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"2","method":"tools/list","params":{}}'

# Test tool call
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"3","method":"tools/call","params":{"name":"your_tool","arguments":{"params":{}}}}'
```

## Heroku Deployment

```bash
# Create app
heroku create your-wrapper-name

# Set environment variables
heroku config:set UPSTREAM_URL=https://api.example.com
heroku config:set UPSTREAM_API_KEY=your-key

# Deploy
git init
git add .
git commit -m "Initial wrapper"
git push heroku main
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Missing session ID" | Use JSON-RPC MCP, not Streamable HTTP |
| "Method not found" | Implement all required methods: initialize, tools/list, tools/call |
| "Object not JSON serializable" | Return Dict[str, Any], not complex objects |
| ChatGPT not showing tools | Ensure search and fetch tools are implemented |
| Upstream API errors | Wrap in try-catch, return error objects |

## Required Methods Checklist

- [ ] `initialize` - Protocol handshake
- [ ] `tools/list` - List available tools
- [ ] `tools/call` - Execute tools
- [ ] `search` tool - Search functionality (REQUIRED)
- [ ] `fetch` tool - Fetch by ID (REQUIRED)
- [ ] Error handling for all methods
- [ ] JSON-serializable return values
- [ ] Proper MCP response format

## Response Format Template

```json
{
  "jsonrpc": "2.0",
  "id": "request_id",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"your\": \"data\"}"
      }
    ]
  }
}
```

## Environment Variables

```bash
# Required
UPSTREAM_URL=https://your-api.com

# Optional
UPSTREAM_API_KEY=your-api-key
WRAPPER_API_KEY=wrapper-auth-key
```

This quick reference covers the essential patterns for building ChatGPT MCP wrappers. For detailed explanations, see the full guide.
