# ChatGPT + CBC Design MCP — Deployment & Connection Guide

This guide shows how to deploy a **remote MCP wrapper** on **Heroku** (as a separate app) that proxies to your existing CBC Design REST API, and how to connect it as a **Custom Connector** in **ChatGPT**.

> Your upstream API:
>
> * `GET  https://cbc-design-mcp-5881195c8e73.herokuapp.com/health`
> * `POST https://cbc-design-mcp-5881195c8e73.herokuapp.com/api/design/generate`
> * `POST https://cbc-design-mcp-5881195c8e73.herokuapp.com/api/design/optimize`
> * `POST https://cbc-design-mcp-5881195c8e73.herokuapp.com/api/design/export`

> Your wrapper example URL (after deploy):
>
> * `https://cbc-mcp-wrapper-7c7742685b78.herokuapp.com/mcp`

---

## 0) Requirements

* ChatGPT plan that supports **Custom Connectors (MCP)** (Pro, Business/Enterprise, EDU). In org workspaces, an **admin/owner** may need to add connectors.
* Heroku account & CLI.
* Python 3.11 runtime (Heroku manages this via `runtime.txt`).

---

## 1) Create the wrapper app (separate Heroku app)

Create a new folder, e.g. `cbc-mcp-wrapper/`, with these files:

```
cbc-mcp-wrapper/
├─ app.py
├─ requirements.txt
├─ Procfile
└─ runtime.txt          # optional but recommended
```

### 1.1 `requirements.txt`

```
mcp[cli]
httpx
uvicorn
starlette
```

### 1.2 `Procfile`

```
web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

### 1.3 `runtime.txt` (optional)

```
python-3.11.9
```

### 1.4 `app.py` — **Official MCP Python SDK** + Streamable HTTP

> Important: The SDK’s Streamable HTTP app already serves at **`/mcp`** internally. **Mount it at `/`** (not `/mcp`) to avoid a `/mcp/mcp` path.

```python
import os, base64
from typing import Any, Dict
import httpx
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Mount, Route
from mcp.server.fastmcp import FastMCP

# Upstream base URL for CBC Design API
BASE_URL = os.getenv("CBC_BASE_URL", "https://cbc-design-mcp-5881195c8e73.herokuapp.com")
HEALTH_URL   = f"{BASE_URL}/health"
GENERATE_URL = f"{BASE_URL}/api/design/generate"
OPTIMIZE_URL = f"{BASE_URL}/api/design/optimize"
EXPORT_URL   = f"{BASE_URL}/api/design/export"

# Optional upstream auth headers
def _up_headers() -> Dict[str, str]:
    h: Dict[str, str] = {}
    if (k := os.getenv("CBC_API_KEY")):
        h["x-api-key"] = k
    if (b := os.getenv("CBC_BEARER")):
        h["Authorization"] = f"Bearer {b}"
    return h

# Create MCP server and expose tools
mcp = FastMCP("cbc-design")

@mcp.tool()
async def health_check() -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(HEALTH_URL, headers=_up_headers())
        r.raise_for_status()
        ct = r.headers.get("content-type", "")
        return r.json() if "application/json" in ct else {"status": "ok", "text": r.text}

@mcp.tool()
async def generate_design(spec: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=None) as c:
        r = await c.post(GENERATE_URL, json=spec, headers=_up_headers())
        r.raise_for_status()
        return r.json()

@mcp.tool()
async def optimize_parameters(spec: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=None) as c:
        r = await c.post(OPTIMIZE_URL, json=spec, headers=_up_headers())
        r.raise_for_status()
        return r.json()

@mcp.tool()
async def export_design(spec: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=None) as c:
        r = await c.post(EXPORT_URL, json=spec, headers=_up_headers())
        r.raise_for_status()
        ct = r.headers.get("content-type", "")
        if "application/json" in ct:
            return r.json()
        return {
            "content_type": ct or "application/octet-stream",
            "content_base64": base64.b64encode(r.content).decode("ascii"),
        }

# Build the Streamable HTTP app (already serves at /mcp)
starlette_mcp = mcp.streamable_http_app()

# Optional basic endpoints
async def root(_):
    return PlainTextResponse("CBC MCP wrapper running. MCP at /mcp; health at /healthz.")

async def healthz(_):
    return JSONResponse({"ok": True, "endpoint": "/mcp"})

# IMPORTANT: Mount MCP app at "/" (not "/mcp") to avoid /mcp/mcp
app = Starlette(routes=[
    Route("/", endpoint=root),
    Route("/healthz", endpoint=healthz),
    Mount("/", app=starlette_mcp),
])
```

> **Optional inbound auth**: If you want the wrapper itself to require a header (e.g., `x-api-key`) from callers, add a Starlette middleware that checks `request.headers.get('x-api-key')` and `401`s when missing; set a `WRAPPER_API_KEY` in Heroku Config Vars and have ChatGPT send it under **Advanced → Headers** for the connector.

---

## 2) Deploy to Heroku

From the wrapper folder:

```bash
heroku create cbc-mcp-wrapper-7c7742685b78   # or choose your app name
heroku buildpacks:set heroku/python

# Point wrapper to your existing upstream API (defaults to this already)
heroku config:set CBC_BASE_URL=https://cbc-design-mcp-5881195c8e73.herokuapp.com

# (Optional) Upstream creds if your API needs them
# heroku config:set CBC_API_KEY=... CBC_BEARER=...

# Deploy
git init
git add .
git commit -m "Deploy CBC MCP wrapper (official SDK)"
git push heroku main
```

**Smoke test (wrapper health):**

```bash
curl https://cbc-mcp-wrapper-7c7742685b78.herokuapp.com/healthz
```

---

## 3) Verify the MCP handshake (curl)

> These two POSTs validate the Streamable HTTP JSON‑RPC flow that ChatGPT expects.

**Initialize**

```bash
curl -i -X POST https://cbc-mcp-wrapper-7c7742685b78.herokuapp.com/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  --data '{
    "jsonrpc":"2.0",
    "id":"1",
    "method":"initialize",
    "params":{"clientInfo":{"name":"diag","version":"1.0"},"capabilities":{}}
  }'
```

Expected: `200` with a JSON‑RPC `result`.

**List tools**

```bash
curl -i -X POST https://cbc-mcp-wrapper-7c7742685b78.herokuapp.com/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  --data '{"jsonrpc":"2.0","id":"2","method":"tools/list"}'
```

Expected: a list that includes `health_check`, `generate_design`, `optimize_parameters`, `export_design`.

> If you see 301/302/307 to `/mcp/` or 404, your mount path is off. Ensure `Mount("/", app=starlette_mcp)` is used (not `Mount("/mcp", ...)`).

---

## 4) Add as a **Custom Connector** in ChatGPT

1. Open **ChatGPT → Settings → Connectors → Add custom connector**.
2. URL: `https://cbc-mcp-wrapper-7c7742685b78.herokuapp.com/mcp`
3. (Optional) If you added inbound auth to the wrapper, add header `x-api-key: <your-key>` under **Advanced**.
4. Save. In a chat, open **Search & tools** and enable your connector’s tools.

**Quick test in chat**

* “Run `health_check`.”
* “Use `generate_design` with this JSON: `{ ... }`.”

---

## 5) Troubleshooting

* **Plan/permission**: Ensure your ChatGPT plan supports **Custom Connectors (MCP)**; orgs may require admin role to add.
* **Handshake failure**: Use the curl tests above. If `initialize` or `tools/list` fails, check logs: `heroku logs -t`.
* **Wrong path**: 404 or redirect to `/mcp/` during POST usually means MCP app mounted at `/mcp`. Mount at `/`.
* **Heroku timeouts**: Long upstream jobs can idle out. Consider chunking/streaming progress or moving long work off the request path.
* **CORS**: Not required for MCP server‑to‑server. Headers (e.g., `x-api-key`) must match what the wrapper checks.
* **File exports**: Non‑JSON payloads come back base64‑encoded; decode in client if you need a file.

---

## 6) Optional hardening

* **Inbound key** for wrapper (middleware + `WRAPPER_API_KEY`).
* **Rate‑limits** via a proxy/CDN or Heroku add‑on.
* **Logging/metrics**: include request IDs; consider structured logs.
* **Least privilege**: expose only required tools.

---

## 7) Done — final checks

* `initialize` and `tools/list` succeed via curl.
* ChatGPT lists your four tools and can call them successfully.
* Heroku logs show 2xx to upstream; no auth errors.

If anything fails, copy the error body/status from the logs and adjust config (env vars, headers, payloads) accordingly.
