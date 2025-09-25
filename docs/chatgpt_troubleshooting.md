# ChatGPT MCP Wrapper - Troubleshooting Guide

This guide helps you resolve common issues when using the CBC Design MCP with ChatGPT.

## Common Error: "Required fields missing: method and grid"

### Problem
You get an error like:
```
The CBC service rejected the request because two required fields are missing in the payload:
- method → specifies the design method (e.g., "random")
- grid → usually defines the attributes and levels grid
```

### Root Cause
The ChatGPT MCP wrapper expects a specific payload structure that's different from natural language prompts.

### Solution 1: Use Natural Language (Recommended)
**Just use natural language - ChatGPT will format it correctly:**

```
"Generate a CBC design for a smartphone with:
- Brand: Apple, Samsung, Google
- Storage: 64GB, 128GB, 256GB
- Price: $299, $499, $699
- Camera: 12MP, 48MP, 108MP

Use the random algorithm for 50 respondents"
```

### Solution 2: Explicit JSON Structure
If natural language fails, use explicit JSON:

```
"Use generate_design with this spec:
{
  'method': 'random',
  'grid': {
    'attributes': [
      {'name': 'Brand', 'levels': [{'name': 'Apple'}, {'name': 'Samsung'}, {'name': 'Google'}]},
      {'name': 'Storage', 'levels': [{'name': '64GB'}, {'name': '128GB'}, {'name': '256GB'}]},
      {'name': 'Price', 'levels': [{'name': '$299'}, {'name': '$499'}, {'name': '$699'}]},
      {'name': 'Camera', 'levels': [{'name': '12MP'}, {'name': '48MP'}, {'name': '108MP'}]}
    ]
  },
  'options_per_screen': 3,
  'num_screens': 10,
  'num_respondents': 50
}"
```

## Other Common Issues

### Issue: "ResourceNotFound" Error
**Problem:** ChatGPT can't find the MCP tools
**Solution:**
1. Refresh the connector in ChatGPT
2. Test with: `"Check if the CBC Design MCP is working by running a health check"`
3. List tools with: `"Show me all available CBC design tools"`

### Issue: "Connection Failed"
**Problem:** MCP wrapper is not responding
**Solution:**
1. Check if the wrapper is running: https://cbc-mcp-wrapper-7c7742685b78.herokuapp.com/healthz
2. Try reconnecting the ChatGPT connector
3. Wait a few minutes and try again

### Issue: "Design generation failed"
**Problem:** The design generation process fails
**Solution:**
1. Try with fewer attributes (2-3 instead of 4-5)
2. Use the random algorithm first
3. Reduce the number of respondents (try 20-50 first)

### Issue: "Export failed"
**Problem:** Can't export the generated design
**Solution:**
1. Make sure you've generated a design first
2. Try: `"Export the last generated design to CSV format"`
3. Check if the design was actually created successfully

## Testing Your Connection

### Step 1: Health Check
```
"Check if the CBC Design MCP is working by running a health check"
```
**Expected:** `{"status": "healthy", "service": "conjoint-mcp-server"}`

### Step 2: List Tools
```
"Show me all available CBC design tools"
```
**Expected:** List of tools including `health_check`, `generate_design`, `optimize_parameters`, `export_design`

### Step 3: Simple Test
```
"Generate a simple CBC design for coffee with brand (Starbucks, Dunkin) and price ($3, $5) using random algorithm for 10 respondents"
```
**Expected:** Successful design generation with sample data

## Correct Payload Structure

The ChatGPT MCP wrapper expects this structure:

```json
{
  "spec": {
    "method": "random|balanced|orthogonal|doptimal",
    "grid": {
      "attributes": [
        {
          "name": "AttributeName",
          "levels": [
            {"name": "Level1"},
            {"name": "Level2"},
            {"name": "Level3"}
          ]
        }
      ]
    },
    "options_per_screen": 3,
    "num_screens": 10,
    "num_respondents": 50
  }
}
```

## Quick Fixes

### If ChatGPT keeps failing:
1. **Restart the conversation** - Sometimes ChatGPT gets confused
2. **Use simpler prompts** - Start with 2 attributes, 2 levels each
3. **Check the connector** - Make sure it's properly connected
4. **Try different algorithms** - Start with "random" (fastest)

### If you get format errors:
1. **Use natural language** - Don't try to format JSON manually
2. **Be specific** - Include all required parameters
3. **Check spelling** - Make sure algorithm names are correct

## Working Examples

### Example 1: Simple Design
```
"Generate a CBC design for laptops with:
- Brand: Apple, Dell
- Price: $1000, $2000

Use random algorithm for 20 respondents"
```

### Example 2: Medium Complexity
```
"Create a CBC design for streaming services with:
- Service: Netflix, Disney+, Amazon Prime
- Price: $8, $12, $15
- Content: Movies, TV Shows, Sports

Use balanced algorithm for 100 respondents"
```

### Example 3: High Quality
```
"Generate a high-quality CBC design for cars with:
- Brand: Toyota, Honda, BMW
- Fuel Type: Gas, Hybrid, Electric
- Price: $25k, $35k, $45k

Use D-optimal algorithm for 200 respondents"
```

## Getting Help

If you're still having issues:

1. **Check the health endpoint**: https://cbc-mcp-wrapper-7c7742685b78.herokuapp.com/healthz
2. **Try the simple test** above
3. **Use the ChatGPT quickstart guide**: `docs/chatgpt_quickstart.md`
4. **Check the main user guide**: `docs/user_guide.md`

## Success Indicators

You'll know it's working when you see:
- ✅ No error messages
- ✅ Design summary with metrics
- ✅ Sample choice tasks displayed
- ✅ Export options offered
- ✅ Follow-up suggestions provided

The design generation should take 5-15 seconds and return structured, useful results.
