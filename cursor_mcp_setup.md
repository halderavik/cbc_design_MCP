# Connecting CBC Design Generator MCP Server to Cursor

This guide will help you connect the CBC Design Generator MCP Server to Cursor IDE.

## Prerequisites

1. **Cursor IDE** installed and running
2. **Python 3.11+** installed
3. **CBC Design Generator MCP Server** set up (this project)

## Step 1: Verify MCP Server Installation

First, make sure the MCP server is properly installed and working:

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

## Step 2: Configure Cursor for MCP

### Option A: Using Cursor Settings (Recommended)

1. **Open Cursor Settings**:
   - Press `Ctrl+,` (Windows/Linux) or `Cmd+,` (Mac)
   - Or go to File → Preferences → Settings

2. **Search for MCP**:
   - In the search bar, type "mcp"
   - Look for "MCP Servers" or "Model Context Protocol" settings

3. **Add MCP Server Configuration**:
   - Click "Edit in settings.json"
   - Add the following configuration:

```json
{
  "mcp.servers": {
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

### Option B: Using Configuration File

1. **Create MCP Configuration File**:
   - Create a file named `mcp_config.json` in your project root
   - Use the provided configuration from `mcp_config.json`

2. **Reference in Cursor Settings**:
   ```json
   {
     "mcp.configFile": "C:\\Users\\Avik Halder\\my_dev\\CBC_design_MCP\\mcp_config.json"
   }
   ```

## Step 3: Restart Cursor

After adding the MCP configuration:

1. **Save the settings**
2. **Restart Cursor completely**
3. **Reopen your project**

## Step 4: Verify MCP Connection

### Check MCP Server Status

1. **Open Command Palette**:
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)

2. **Search for MCP Commands**:
   - Type "MCP" to see available MCP-related commands
   - Look for commands like "MCP: List Servers" or "MCP: Restart Server"

3. **Test the Connection**:
   - Try using the MCP server in a chat or code completion
   - The server should appear in the available tools/resources

### Test MCP Functionality

Try asking Cursor to use the CBC Design Generator:

```
"Generate a CBC design for a smartphone with brand, storage, and price attributes using the MCP server"
```

Or:

```
"Use the CBC Design Generator MCP server to optimize parameters for a study with 3 attributes and 3 levels each"
```

## Step 5: Troubleshooting

### Common Issues

#### 1. MCP Server Not Found
**Error**: "MCP server not found" or "Command not found"

**Solutions**:
- Verify Python path: `python --version`
- Check if the module is installed: `python -c "import conjoint_mcp"`
- Ensure you're in the correct directory

#### 2. Permission Errors
**Error**: "Permission denied" or "Access denied"

**Solutions**:
- Run Cursor as administrator (Windows)
- Check file permissions
- Ensure Python has execute permissions

#### 3. Path Issues
**Error**: "Module not found" or "No such file or directory"

**Solutions**:
- Use absolute paths in configuration
- Verify the `cwd` (current working directory) is correct
- Check that `PYTHONPATH` includes the src directory

#### 4. Server Not Responding
**Error**: Timeout or no response

**Solutions**:
- Test the server manually first
- Check for port conflicts
- Verify the server starts without errors

### Debug Steps

1. **Test Server Manually**:
   ```bash
   cd "C:\Users\Avik Halder\my_dev\CBC_design_MCP"
   python -m conjoint_mcp.server
   ```

2. **Check Cursor Logs**:
   - Open Developer Tools: `Ctrl+Shift+I`
   - Check Console for MCP-related errors
   - Look for connection attempts and failures

3. **Verify Configuration**:
   - Double-check the JSON syntax in settings
   - Ensure all paths are correct and escaped properly
   - Verify environment variables

## Step 6: Using the MCP Server

Once connected, you can use the CBC Design Generator through Cursor in several ways:

### 1. Chat Integration
Ask Cursor to use the MCP server:
```
"Generate a CBC design for a new product with the following attributes:
- Brand: TechCorp, MobileMax, SmartPhone Inc
- Storage: 64GB, 128GB, 256GB
- Price: $299, $499, $699

Use the CBC Design Generator MCP server to create an optimal design."
```

### 2. Code Completion
The MCP server can provide context-aware suggestions for:
- Design parameters
- Algorithm selection
- Constraint specifications
- Export formats

### 3. Documentation Access
Ask for help with the MCP server:
```
"How do I use the CBC Design Generator MCP server?"
"What algorithms are available in the CBC Design Generator?"
"Show me examples of constraint specifications for the CBC Design Generator."
```

## Available MCP Methods

The CBC Design Generator MCP Server provides these methods:

1. **`health`** - Check server status
2. **`design.generate`** - Generate CBC designs
3. **`design.optimize`** - Optimize study parameters
4. **`design.export`** - Export designs in various formats

## Example Usage

### Generate a Design
```
"Use the CBC Design Generator MCP server to generate a random design with:
- 3 attributes (Color, Size, Material)
- 3 levels each
- 5 choice tasks
- 3 options per task"
```

### Optimize Parameters
```
"Use the CBC Design Generator MCP server to optimize parameters for a study with:
- 2 attributes with 2 levels each
- Target power of 0.8
- Effect size of 0.2"
```

### Export Design
```
"Use the CBC Design Generator MCP server to export a design to CSV format with metadata"
```

## Advanced Configuration

### Custom Environment Variables
You can add custom environment variables to the MCP configuration:

```json
{
  "mcp.servers": {
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
  "mcp.servers": {
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
2. **Review Cursor's MCP documentation**
3. **Test the server manually first**
4. **Check Cursor's developer console for errors**
5. **Verify all paths and permissions**

## Next Steps

Once the MCP server is connected:

1. **Explore the available methods** through Cursor's chat
2. **Try different design scenarios** using the sample scenarios
3. **Test the interactive features** like parameter optimization
4. **Use the export functionality** for your designs
5. **Integrate with your workflow** for CBC study design

The CBC Design Generator MCP Server is now ready to help you create optimal Choice Based Conjoint designs directly within Cursor!
