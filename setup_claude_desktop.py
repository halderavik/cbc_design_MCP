#!/usr/bin/env python3
"""
Setup script for connecting CBC Design Generator MCP Server to Claude Desktop.
"""

import json
import os
import sys
from pathlib import Path


def get_claude_config_path():
    """Get the Claude Desktop configuration file path based on OS."""
    if sys.platform == "win32":
        # Windows
        config_dir = Path(os.environ["APPDATA"]) / "Claude"
    elif sys.platform == "darwin":
        # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    else:
        # Linux
        config_dir = Path.home() / ".config" / "claude"
    
    return config_dir / "claude_desktop_config.json"


def create_mcp_config():
    """Create the MCP server configuration."""
    # Get the current project directory
    project_dir = Path(__file__).parent.absolute()
    src_dir = project_dir / "src"
    
    # Create the configuration
    config = {
        "mcpServers": {
            "cbc-design-generator": {
                "command": "python",
                "args": ["-m", "conjoint_mcp.mcp_server_v2"],
                "cwd": str(project_dir),
                "env": {
                    "PYTHONPATH": str(src_dir),
                    "LOG_LEVEL": "WARNING"
                }
            }
        }
    }
    
    return config


def setup_claude_desktop():
    """Set up Claude Desktop configuration for the MCP server."""
    print("🔧 Setting up Claude Desktop configuration for CBC Design Generator MCP Server")
    print("=" * 70)
    
    # Get configuration file path
    config_path = get_claude_config_path()
    config_dir = config_path.parent
    
    print(f"📁 Configuration directory: {config_dir}")
    print(f"📄 Configuration file: {config_path}")
    
    # Create directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created configuration directory: {config_dir}")
    
    # Create MCP configuration
    mcp_config = create_mcp_config()
    
    # Check if config file already exists
    if config_path.exists():
        print(f"⚠️  Configuration file already exists: {config_path}")
        
        # Read existing config
        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print("❌ Error reading existing configuration file")
            existing_config = {}
        
        # Check if our MCP server is already configured
        if "mcpServers" in existing_config and "cbc-design-generator" in existing_config["mcpServers"]:
            print("✅ CBC Design Generator MCP server is already configured")
            response = input("🔄 Do you want to update the configuration? (y/N): ").strip().lower()
            if response != 'y':
                print("ℹ️  Configuration not updated")
                return
        
        # Merge configurations
        if "mcpServers" not in existing_config:
            existing_config["mcpServers"] = {}
        
        existing_config["mcpServers"]["cbc-design-generator"] = mcp_config["mcpServers"]["cbc-design-generator"]
        mcp_config = existing_config
    
    # Write configuration file
    try:
        with open(config_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        print(f"✅ Configuration file created/updated: {config_path}")
    except Exception as e:
        print(f"❌ Error writing configuration file: {e}")
        return
    
    # Display the configuration
    print("\n📋 Configuration Details:")
    print(f"   Command: {mcp_config['mcpServers']['cbc-design-generator']['command']}")
    print(f"   Args: {mcp_config['mcpServers']['cbc-design-generator']['args']}")
    print(f"   Working Directory: {mcp_config['mcpServers']['cbc-design-generator']['cwd']}")
    print(f"   Python Path: {mcp_config['mcpServers']['cbc-design-generator']['env']['PYTHONPATH']}")
    
    print("\n🎯 Next Steps:")
    print("1. Close Claude Desktop completely")
    print("2. Wait a few seconds")
    print("3. Restart Claude Desktop")
    print("4. The CBC Design Generator MCP server should now be available")
    
    print("\n🧪 Test the connection:")
    print("   Ask Claude: 'Generate a CBC design for a smartphone with brand, storage, and price attributes using the CBC Design Generator MCP server'")
    
    print("\n📚 For more information, see:")
    print("   - docs/claude_desktop_connection.md")
    print("   - docs/claude_quickstart.md")


def test_mcp_server():
    """Test if the MCP server can be imported and run."""
    print("\n🧪 Testing MCP server...")
    
    try:
        # Test import
        import conjoint_mcp.mcp_server_v2
        print("✅ MCP server module imported successfully")
        
        # Test if we can create the server
        print("✅ MCP server is ready to run")
        
    except ImportError as e:
        print(f"❌ Error importing MCP server: {e}")
        print("💡 Make sure you're running this script from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False
    
    return True


def main():
    """Main setup function."""
    print("🚀 CBC Design Generator MCP Server - Claude Desktop Setup")
    print("=" * 60)
    
    # Test MCP server first
    if not test_mcp_server():
        print("\n❌ MCP server test failed. Please fix the issues above before continuing.")
        return
    
    # Set up Claude Desktop configuration
    setup_claude_desktop()
    
    print("\n🎉 Setup complete!")
    print("   The CBC Design Generator MCP Server is now configured for Claude Desktop")


if __name__ == "__main__":
    main()
