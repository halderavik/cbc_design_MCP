## ChatGPT MCP Wrapper Quickstart (CBC Design)

Use this with ChatGPT Custom Connector pointing to:

`https://cbc-mcp-wrapper-7c7742685b78.herokuapp.com/mcp`

### 1) Verify connection

- Run `health_check`.

Expected: JSON with `status: healthy` (proxied from upstream `/health`).

### 2) List tools

- “List available tools.”

Expected: `health_check`, `generate_design`, `optimize_parameters`, `export_design`.

### 3) Generate a small design (random)

Prompt:

```
Use `generate_design` with spec:
{
  "method": "random",
  "grid": {
    "attributes": [
      {"name": "Brand", "levels": [{"name": "A"}, {"name": "B"}]},
      {"name": "Price", "levels": [{"name": "Low"}, {"name": "High"}]}
    ]
  },
  "options_per_screen": 2,
  "num_screens": 3
}
Return the summary and number of tasks.
```

### 4) Optimize parameters (sample)

Prompt:

```
Call `optimize_parameters` with spec:
{
  "grid": {
    "attributes": [
      {"name": "Processor & RAM", "levels": [{"name": "i5/8GB"}, {"name": "i7/16GB"}, {"name": "i9/32GB"}]},
      {"name": "Storage", "levels": [{"name": "256GB"}, {"name": "512GB"}, {"name": "1TB"}]},
      {"name": "Display", "levels": [{"name": "13 FHD"}, {"name": "14 2K"}, {"name": "16 4K"}]},
      {"name": "Price", "levels": [{"name": "$999"}, {"name": "$1,499"}, {"name": "$2,199"}]}
    ]
  },
  "num_screens": 12,
  "options_per_screen": 3
}
Report the suggested respondents and rationale (Johnson–Orme).
```

### 5) Export a design (CSV preview)

Prompt:

```
Use `export_design` with spec:
{
  "method": "balanced",
  "grid": {
    "attributes": [
      {"name": "Brand", "levels": [{"name": "A"}, {"name": "B"}]},
      {"name": "Price", "levels": [{"name": "Low"}, {"name": "High"}]}
    ]
  },
  "options_per_screen": 2,
  "num_screens": 3
}
If content_base64 is returned, summarize the first 5 lines after decoding.
```

### 6) Larger laptop example (D-optimal)

Prompt:

```
Use `generate_design` with spec:
{
  "method": "doptimal",
  "grid": {
    "attributes": [
      {"name": "Processor & RAM", "levels": [{"name": "i5/8GB"}, {"name": "i7/16GB"}, {"name": "i9/32GB"}]},
      {"name": "Storage", "levels": [{"name": "256GB"}, {"name": "512GB"}, {"name": "1TB"}]},
      {"name": "Display", "levels": [{"name": "13 FHD"}, {"name": "14 2K"}, {"name": "16 4K"}]},
      {"name": "Price", "levels": [{"name": "$999"}, {"name": "$1,499"}, {"name": "$2,199"}]}
    ]
  },
  "options_per_screen": 3,
  "num_screens": 12
}
Return efficiency and task count.
```

### Notes

- The wrapper proxies to the upstream CBC API; long runs may take time on free dynos.
- For files, wrapper returns base64; ask ChatGPT to decode and show a preview.

