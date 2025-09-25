# Connecting CBC Design Generator MCP Server to Claude Desktop

This guide shows you how to connect the CBC Design Generator MCP Server to Claude Desktop. You have two options:

## Option 1: Connect to Local MCP Server (Recommended)

This connects Claude Desktop to your local MCP server running on your machine.

### Step 1: Locate Claude Desktop Configuration

Claude Desktop stores its configuration in different locations depending on your operating system:

#### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```
Full path: `C:\Users\[YourUsername]\AppData\Roaming\Claude\claude_desktop_config.json`

#### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### Linux
```
~/.config/claude/claude_desktop_config.json
```

### Step 2: Create or Edit Configuration File

#### For Windows (Your System):

1. **Navigate to the Claude Desktop config directory**:
   ```cmd
   cd %APPDATA%\Claude
   ```

2. **Create or edit the configuration file**:
   ```json
   {
     "mcpServers": {
       "cbc-design-generator": {
         "command": "python",
         "args": ["-m", "conjoint_mcp.mcp_server_v2"],
         "cwd": "C:\\Users\\Avik Halder\\my_dev\\CBC_design_MCP",
         "env": {
           "PYTHONPATH": "C:\\Users\\Avik Halder\\my_dev\\CBC_design_MCP\\src",
           "LOG_LEVEL": "WARNING"
         }
       }
     }
   }
   ```

### Step 3: Test the Local MCP Server

Before connecting to Claude Desktop, test the MCP server manually:

```cmd
# Navigate to the project directory
cd "C:\Users\Avik Halder\my_dev\CBC_design_MCP"

# Test the server
echo {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}} | python -m conjoint_mcp.mcp_server_v2
```

### Step 4: Restart Claude Desktop

1. **Close Claude Desktop completely**
2. **Wait a few seconds**
3. **Restart Claude Desktop**
4. **The MCP server should now be available**

---

## Option 2: Connect to Heroku-Deployed Server (Alternative)

This connects Claude Desktop to the server running on Heroku. This requires creating a bridge or using HTTP endpoints.

### Option 2A: Use HTTP API Endpoints

Since the Heroku server provides HTTP endpoints, you can use them directly:

#### Available Endpoints:
- **Health Check**: `https://cbc-design-mcp-5881195c8e73.herokuapp.com/health`
- **Generate Design**: `https://cbc-design-mcp-5881195c8e73.herokuapp.com/api/design/generate`
- **Optimize Parameters**: `https://cbc-design-mcp-5881195c8e73.herokuapp.com/api/design/optimize`
- **Export Design**: `https://cbc-design-mcp-5881195c8e73.herokuapp.com/api/design/export`
- **List Tools**: `https://cbc-design-mcp-5881195c8e73.herokuapp.com/api/tools`
- **List Resources**: `https://cbc-design-mcp-5881195c8e73.herokuapp.com/api/resources`

#### Example Usage:
```bash
# Test health endpoint
curl https://cbc-design-mcp-5881195c8e73.herokuapp.com/health

# Generate a design
curl -X POST https://cbc-design-mcp-5881195c8e73.herokuapp.com/api/design/generate \
  -H "Content-Type: application/json" \
  -d '{
    "method": "random",
    "grid": {
      "attributes": [
        {
          "name": "Brand",
          "levels": [
            {"name": "TechCorp"},
            {"name": "MobileMax"}
          ]
        },
        {
          "name": "Price",
          "levels": [
            {"name": "$299"},
            {"name": "$499"}
          ]
        }
      ]
    },
    "options_per_screen": 2,
    "num_screens": 3
  }'
```

### Option 2B: Create MCP-to-HTTP Bridge (Advanced)

For a more seamless integration, you could create a local MCP server that acts as a bridge to the Heroku HTTP API.

---

## Recommended Approach: Option 1 (Local MCP Server)

**I recommend using Option 1** (local MCP server) because:

1. **Better Integration**: Direct MCP protocol communication
2. **Faster Response**: No network latency
3. **Offline Capability**: Works without internet
4. **Full Feature Set**: Access to all MCP methods
5. **Better Error Handling**: Direct error reporting

---

## Step 5: Verify Connection

### Check MCP Server Status

1. **Open Claude Desktop**
2. **Look for MCP server indicators** in the interface
3. **Check if the CBC Design Generator appears** in available tools

### Test MCP Functionality

Try asking Claude to use the CBC Design Generator:

```
"Generate a CBC design for a smartphone with brand, storage, and price attributes using the CBC Design Generator MCP server"
```

Or:

```
"Use the CBC Design Generator to optimize parameters for a study with 3 attributes and 3 levels each"
```

---

## Step 6: Troubleshooting

### Common Issues

#### 1. MCP Server Not Appearing
**Problem**: Claude Desktop doesn't show the MCP server

**Solutions**:
- Check the configuration file path and syntax
- Ensure JSON is valid (use a JSON validator)
- Restart Claude Desktop completely
- Check Claude Desktop logs for errors

#### 2. Path Issues
**Problem**: "Module not found" or "No such file or directory"

**Solutions**:
- Use absolute paths in the configuration
- Verify the `cwd` (current working directory) is correct
- Check that `PYTHONPATH` includes the src directory
- Test the server manually first

#### 3. Permission Errors
**Problem**: "Permission denied" or "Access denied"

**Solutions**:
- Run Claude Desktop as administrator (Windows)
- Check file permissions
- Ensure Python has execute permissions

#### 4. Server Not Responding
**Problem**: Timeout or no response from MCP server

**Solutions**:
- Test the server manually first
- Check for port conflicts
- Verify the server starts without errors
- Check system resources (memory, CPU)

### Debug Steps

1. **Test Server Manually**:
   ```cmd
   cd "C:\Users\Avik Halder\my_dev\CBC_design_MCP"
   python -m conjoint_mcp.mcp_server_v2
   ```

2. **Check Configuration File**:
   - Validate JSON syntax
   - Verify all paths are correct
   - Ensure proper escaping of backslashes on Windows

3. **Check Claude Desktop Logs**:
   - Look for MCP-related error messages
   - Check if the server is being started
   - Verify connection attempts

4. **Verify Python Environment**:
   ```cmd
   python --version
   python -c "import conjoint_mcp; print('Module imported successfully')"
   ```

---

## Step 7: Using the MCP Server

Once connected, you can use the CBC Design Generator through Claude Desktop:

### 1. Generate CBC Designs
```
"Generate a CBC design for a new product with:
- Brand: TechCorp, MobileMax, SmartPhone Inc
- Storage: 64GB, 128GB, 256GB
- Price: $299, $499, $699

Use the CBC Design Generator MCP server to create an optimal design."
```

### 2. Optimize Study Parameters
```
"Use the CBC Design Generator MCP server to optimize parameters for a study with:
- 2 attributes with 2 levels each
- Target power of 0.8
- Effect size of 0.2
- Alpha level of 0.05"
```

### 3. Export Designs
```
"Use the CBC Design Generator MCP server to export a design to CSV format with metadata"
```

### 4. Get Algorithm Recommendations
```
"What's the best algorithm to use for a CBC study with 5 attributes and 4 levels each? Use the CBC Design Generator MCP server to help decide"
```

### 5. Constraint-Based Designs
```
"Generate a CBC design with constraints:
- Prohibited combination: Premium brand cannot be sold at budget price
- Required combination: Premium brand must include premium features

Use the CBC Design Generator MCP server"
```

---

## Available MCP Methods

The CBC Design Generator MCP Server provides these methods:

1. **`initialize`** - Initialize MCP connection
2. **`tools/list`** - List available tools
3. **`tools/call`** - Call specific tools:
   - `generate_design` - Generate CBC designs using different algorithms
   - `optimize_parameters` - Optimize study parameters for statistical power
   - `export_design` - Export designs in various formats
   - `save_design_file` - Save design to file
4. **`resources/list`** - List available resources
5. **`resources/read`** - Read specific resources

### Design Generation Algorithms:
- `random` - Fast, simple random assignment
- `balanced` - Ensures attribute level balance
- `orthogonal` - Classical orthogonal design support
- `doptimal` - Maximizes statistical efficiency

### Export Formats:
- `csv` - CSV format for survey platforms
- `json` - JSON format for data processing
- `qualtrics` - Qualtrics-compatible format

---

## Example Conversations

### Basic Design Generation
```
User: "Generate a simple CBC design for a coffee shop with price, size, and flavor attributes"

Claude: I'll use the CBC Design Generator MCP server to create a design for your coffee shop study.

[Claude uses the MCP server to generate the design]

Here's your CBC design:
- Task 1: $3.99 Large Vanilla, $2.99 Medium Chocolate, $4.99 Large Caramel
- Task 2: $2.99 Small Vanilla, $4.99 Large Chocolate, $3.99 Medium Caramel
- [continues with more tasks...]
```

### Parameter Optimization
```
User: "I need to optimize my study parameters for a product with 3 attributes and 3 levels each"

Claude: I'll use the CBC Design Generator MCP server to optimize your study parameters.

[Claude uses the MCP server to optimize parameters]

Based on your design specifications, I recommend:
- 300 respondents (default commercial target)
- 12 choice tasks
- 3 options per task
- Expected statistical power: 0.82
```

### Export and Analysis
```
User: "Export my design to CSV format for use in a survey platform"

Claude: I'll use the CBC Design Generator MCP server to export your design to CSV format.

[Claude uses the MCP server to export the design]

Your design has been exported to CSV format with:
- 5 choice tasks
- 15 total options
- Metadata included
- Ready for survey platform import
```

---

## Advanced Configuration

### Custom Environment Variables
You can add custom environment variables to the MCP configuration:

```json
{
  "mcpServers": {
    "cbc-design-generator": {
      "command": "python",
      "args": ["-m", "conjoint_mcp.mcp_server_v2"],
      "cwd": "C:\\Users\\Avik Halder\\my_dev\\CBC_design_MCP",
      "env": {
        "PYTHONPATH": "C:\\Users\\Avik Halder\\my_dev\\CBC_design_MCP\\src",
        "LOG_LEVEL": "DEBUG",
        "MAX_RESPONSE_TIME": "60",
        "MAX_MEMORY_USAGE": "1GB"
      }
    }
  }
}
```

### Multiple MCP Servers
You can configure multiple MCP servers:

```json
{
  "mcpServers": {
    "cbc-design-generator": {
      "command": "python",
      "args": ["-m", "conjoint_mcp.mcp_server_v2"],
      "cwd": "C:\\Users\\Avik Halder\\my_dev\\CBC_design_MCP"
    },
    "other-mcp-server": {
      "command": "node",
      "args": ["server.js"],
      "cwd": "C:\\path\\to\\other\\server"
    }
  }
}
```

---

## Support

If you encounter issues:

1. **Check the troubleshooting section above**
2. **Test the server manually first**
3. **Verify the configuration file syntax**
4. **Check Claude Desktop logs**
5. **Ensure all paths are correct**

---

## Next Steps

Once the MCP server is connected:

1. **Explore the available methods** through Claude Desktop
2. **Try different design scenarios** using the sample scenarios
3. **Test the interactive features** like parameter optimization
4. **Use the export functionality** for your designs
5. **Integrate with your workflow** for CBC study design

The CBC Design Generator MCP Server is now ready to help you create optimal Choice Based Conjoint designs directly within Claude Desktop!

---

## Quick Start Commands

### For Windows Users:

1. **Create the config file**:
   ```cmd
   echo { "mcpServers": { "cbc-design-generator": { "command": "python", "args": ["-m", "conjoint_mcp.mcp_server_v2"], "cwd": "C:\\Users\\Avik Halder\\my_dev\\CBC_design_MCP", "env": { "PYTHONPATH": "C:\\Users\\Avik Halder\\my_dev\\CBC_design_MCP\\src", "LOG_LEVEL": "WARNING" } } } } > "%APPDATA%\Claude\claude_desktop_config.json"
   ```

2. **Test the server**:
   ```cmd
   cd "C:\Users\Avik Halder\my_dev\CBC_design_MCP"
   python -m conjoint_mcp.mcp_server_v2
   ```

3. **Restart Claude Desktop**

4. **Test with Claude**:
   ```
   "Generate a CBC design for a laptop with processor, storage, and price attributes using the CBC Design Generator MCP server"
   ```
