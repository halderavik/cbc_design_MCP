# CBC Design MCP Wrapper

This is an MCP (Model Context Protocol) wrapper that provides HTTP-based MCP endpoints for the CBC Design Generator API.

## Architecture

- **Upstream API**: `https://cbc-design-mcp-5881195c8e73.herokuapp.com`
- **Wrapper Endpoints**:
  - `GET /` - Root endpoint
  - `GET /healthz` - Wrapper health check
  - `ANY /mcp` - MCP protocol endpoint

## Available MCP Tools

1. **`health_check()`** - Ping upstream CBC server health
2. **`generate_design(spec)`** - Generate CBC designs
3. **`optimize_parameters(spec)`** - Optimize design parameters
4. **`export_design(spec)`** - Export designs (returns base64 for files)

## Environment Variables

- `CBC_BASE_URL` - Upstream API base URL (defaults to your deployed API)
- `CBC_API_KEY` - Optional upstream API key
- `CBC_BEARER` - Optional upstream bearer token
- `WRAPPER_API_KEY` - Optional wrapper API key for /mcp endpoint protection

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app:app --host 0.0.0.0 --port 8000

# Test endpoints
curl http://localhost:8000/healthz
curl http://localhost:8000/
```

## Deployment

This wrapper is designed to be deployed on Heroku as a separate app from the main CBC Design API.

## Usage

Once deployed, MCP clients can connect to:
```
https://your-wrapper-app.herokuapp.com/mcp
```

The wrapper forwards all MCP tool calls to the upstream CBC Design API and returns the results in MCP format.
