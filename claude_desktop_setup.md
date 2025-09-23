# Connecting CBC Design Generator MCP Server to Claude Desktop

This guide will help you connect the CBC Design Generator MCP Server to Claude Desktop application.

## Prerequisites

1. **Claude Desktop** installed and running
2. **Python 3.11+** installed
3. **CBC Design Generator MCP Server** set up (this project)

## Step 1: Locate Claude Desktop Configuration

Claude Desktop stores its configuration in different locations depending on your operating system:

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```
Full path: `C:\Users\[YourUsername]\AppData\Roaming\Claude\claude_desktop_config.json`

### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Linux
```
~/.config/claude/claude_desktop_config.json
```

## Step 2: Create or Edit Configuration File

### Option A: Create New Configuration File

1. **Navigate to the Claude Desktop config directory**:
   ```bash
   # Windows
   cd %APPDATA%\Claude
   
   # macOS
   cd ~/Library/Application\ Support/Claude
   
   # Linux
   cd ~/.config/claude
   ```

2. **Create the configuration file**:
   ```bash
   # Create the file (it may not exist yet)
   touch claude_desktop_config.json
   ```

3. **Add the MCP server configuration**:
   ```json
   {
     "mcpServers": {
       "cbc-design-generator": {
         "command": "python",
         "args": ["-m", "conjoint_mcp.server"],
         "cwd": "C:\\Users\\Avik Halder\\my_dev\\CBC_design_MCP",
         "env": {
           "PYTHONPATH": "C:\\Users\\Avik Halder\\my_dev\\CBC_design_MCP\\src",
           "LOG_LEVEL": "INFO"
         }
       }
     }
   }
   ```

### Option B: Edit Existing Configuration File

If you already have a `claude_desktop_config.json` file:

1. **Open the existing file**
2. **Add the MCP server to the existing configuration**:
   ```json
   {
     "mcpServers": {
       "existing-server": {
         // ... existing server configuration
       },
       "cbc-design-generator": {
         "command": "python",
         "args": ["-m", "conjoint_mcp.server"],
         "cwd": "C:\\Users\\Avik Halder\\my_dev\\CBC_design_MCP",
         "env": {
           "PYTHONPATH": "C:\\Users\\Avik Halder\\my_dev\\CBC_design_MCP\\src",
           "LOG_LEVEL": "INFO"
         }
       }
     }
   }
   ```

## Step 3: Verify MCP Server Works

Before connecting to Claude Desktop, test the MCP server manually:

```bash
# Navigate to the project directory
cd "C:\Users\Avik Halder\my_dev\CBC_design_MCP"

# Test the server
echo '{"jsonrpc": "2.0", "id": 1, "method": "health", "params": {}}' | python -m conjoint_mcp.server
```

Expected output:
```json
{"jsonrpc": "2.0", "id": 1, "result": {"status": "ok", "version": "0.1.0"}}
```

## Step 4: Restart Claude Desktop

1. **Close Claude Desktop completely**
2. **Wait a few seconds**
3. **Restart Claude Desktop**
4. **The MCP server should now be available**

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
   ```bash
   cd "C:\Users\Avik Halder\my_dev\CBC_design_MCP"
   python -m conjoint_mcp.server
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
   ```bash
   python --version
   python -c "import conjoint_mcp; print('Module imported successfully')"
   ```

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

## Available MCP Methods

The CBC Design Generator MCP Server provides these methods:

1. **`health`** - Check server status and version
2. **`design.generate`** - Generate CBC designs using different algorithms:
   - `random` - Fast, simple random assignment
   - `balanced` - Ensures attribute level balance
   - `orthogonal` - Classical orthogonal design support
   - `doptimal` - Maximizes statistical efficiency
3. **`design.optimize`** - Optimize study parameters for statistical power
4. **`design.export`** - Export designs in various formats:
   - `csv` - CSV format for survey platforms
   - `json` - JSON format for data processing
   - `qualtrics` - Qualtrics-compatible format

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
- 200 respondents
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

## Advanced Configuration

### Custom Environment Variables
You can add custom environment variables to the MCP configuration:

```json
{
  "mcpServers": {
    "cbc-design-generator": {
      "command": "python",
      "args": ["-m", "conjoint_mcp.server"],
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
      "args": ["-m", "conjoint_mcp.server"],
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

## Support

If you encounter issues:

1. **Check the troubleshooting section above**
2. **Test the server manually first**
3. **Verify the configuration file syntax**
4. **Check Claude Desktop logs**
5. **Ensure all paths are correct**

## Next Steps

Once the MCP server is connected:

1. **Explore the available methods** through Claude Desktop
2. **Try different design scenarios** using the sample scenarios
3. **Test the interactive features** like parameter optimization
4. **Use the export functionality** for your designs
5. **Integrate with your workflow** for CBC study design

The CBC Design Generator MCP Server is now ready to help you create optimal Choice Based Conjoint designs directly within Claude Desktop!
