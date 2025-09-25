# Task: Deploy an MCP Wrapper for CBC Design API and Connect It to an MCP‑aware Client

This guide walks you through deploying a **separate** MCP wrapper app on **Heroku** that proxies to your existing CBC Design REST API, then connecting that wrapper to an MCP‑capable client (e.g., ChatGPT custom connector or Claude custom connector).

---

## 0) Overview & Architecture

**You already have (upstream):**

* `GET  https://cbc-design-mcp-5881195c8e73.herokuapp.com/health`
* `POST https://cbc-design-mcp-5881195c8e73.herokuapp.com/api/design/generate`
* `POST https://cbc-design-mcp-5881195c8e73.herokuapp.com/api/design/optimize`
* `POST https://cbc-design-mcp-5881195c8e73.herokuapp.com/api/design/export`

**You will add (wrapper app):**

* `GET  /healthz` — wrapper health
* `ANY /mcp` — a **single MCP endpoint** (streamable HTTP) that exposes tools:

  * `health_check`
  * `generate_design(spec)`
  * `optimize_parameters(spec)`
  * `export_design(spec)`

The wrapper forwards calls to your upstream endpoints and returns their results to the MCP client.

---

## 1) Create a new folder (separate app)

```
cbc-mcp-wrapper/
├─ app.py
├─ requirements.txt
├─ Procfile
└─ runtime.txt        # optional
```

---

## 2) Paste the wrapper code

> **Notes**
>
> * Set `CBC_BASE_URL` to your upstream base URL (defaults to your current one).
> * Optional inbound auth: set `WRAPPER_API_KEY` to require callers to send `x-api-key`.
> * Optional upstream auth passthrough: set `CBC_API_KEY` and/or `CBC_BEARER`.

**`app.py`**

```python
import os
import base64
from typing import Any, Dict

import httpx
from fastmcp import FastMCP, http_server
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
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

# Build the MCP ASGI app (single endpoint)
mcp_asgi = http_server(mcp)

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

# Root ASGI app
app = Starlette(
    routes=[
        Route("/", endpoint=root),
        Route("/healthz", endpoint=wrapper_health),
        Mount("/mcp", app=mcp_asgi),
    ]
)
app.add_middleware(RequireAPIKey)
```

**`requirements.txt`**

```
fastmcp
httpx
uvicorn
starlette
```

**`Procfile`**

```
web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

**`runtime.txt`** (optional, but helps pin)

```
python-3.11.9
```

---

## 3) Deploy to Heroku

```bash
# In the wrapper folder
heroku create cbc-mcp-wrapper
heroku buildpacks:set heroku/python

# Point wrapper at your existing API (defaults to this already)
heroku config:set CBC_BASE_URL=https://cbc-design-mcp-5881195c8e73.herokuapp.com

# (Optional) Pass upstream credentials if needed by your API
# heroku config:set CBC_API_KEY=... CBC_BEARER=...

# (Optional) Require a key to call /mcp on the wrapper itself
# heroku config:set WRAPPER_API_KEY=some-long-random-string

# Deploy
git init
git add .
git commit -m "MCP wrapper"
git push heroku main
```

**Smoke test**

```bash
curl https://cbc-mcp-wrapper.herokuapp.com/healthz
# Expect: {"ok": true, ...}
```

---

## 4) Connect the wrapper to your MCP client

You now have a remote MCP endpoint at:

```
https://cbc-mcp-wrapper.herokuapp.com/mcp
```

In your MCP‑aware client (e.g., ChatGPT custom connector or Claude custom connector):

1. Open **Settings → Connectors → Add custom connector**.
2. Enter the URL above.
3. If you set `WRAPPER_API_KEY`, add header `x-api-key: <your value>` in the connector’s advanced/header settings.
4. Save/enable the connector, then in a chat call the `health_check` tool to verify connectivity.

> Tip: If your client supports per‑tool permissions, enable only the three tools you need.

---

## 5) Usage examples (prompts)

* **Health check**: “Run `health_check`.”
* **Generate**: “Use `generate_design` with `{...json payload...}` and show me the design summary.”
* **Optimize**: “Call `optimize_parameters` on design ID X with constraints Y.”
* **Export**: “Call `export_design` for design ID X; if `content_base64` is returned, save as CSV.”

---

## 6) Troubleshooting & Ops

* **Heroku timeouts**: The router expects the first bytes of a response within \~30s and may close idle streams around \~55s. If upstream work can be long‑running, prefer shorter upstream chunks or asynchronous jobs, and return progress periodically.
* **Logs**: `heroku logs -t` to tail; look for 401 (wrapper auth) vs 4xx/5xx from upstream.
* **Scaling**: `heroku ps:scale web=2` to add dynos if connector usage grows.
* **CORS/Headers**: MCP over HTTP doesn’t need CORS for server‑to‑server calls, but inbound header requirements (like `x-api-key`) must be configured in the client.
* **Export files**: Non‑JSON exports are base64‑encoded; decode and write bytes on the client side.

---

## 7) Optional: Single‑app alternative

If you prefer to mount `/mcp` inside your existing API instead of a separate app, copy the MCP section from `app.py` and `Mount("/mcp", app=mcp_asgi)` into your API’s ASGI app. Re‑deploy your API. (This couples deploys and scaling; the separate wrapper is usually cleaner.)

---

## 8) Security checklist

* Inbound protection: set `WRAPPER_API_KEY` and rotate regularly.
* Outbound protection: use `CBC_API_KEY` / `CBC_BEARER` to authenticate to your upstream.
* Rate limits: consider a lightweight proxy (e.g., Cloudflare or Heroku add‑ons) if you need throttling.
* Least privilege: expose only the tools you need.

---

## 9) Done — verification steps

* Connector can execute `health_check` successfully.
* `generate_design`, `optimize_parameters`, and `export_design` return expected JSON (or base64 for files).
* Wrapper logs show 2xx to upstream; no 401/403.

> If any step fails, capture the wrapper and upstream response bodies/status codes from logs and adjust auth, payloads, or timeouts accordingly.
