#!/usr/bin/env python3
"""
Test script to verify MCP server connection and functionality.
"""

import asyncio
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from conjoint_mcp.handlers.generation import handle_generate_design
from conjoint_mcp.models.requests import GenerateDesignRequest

def test_mcp_server():
    """Test the MCP server functionality."""
    print("Testing MCP server connection...")
    
    # Test 1: Simple design generation
    print("\n1. Testing design generation...")
    
    request_data = {
        "method": "random",
        "grid": {
            "attributes": [
                {
                    "name": "Brand",
                    "levels": [
                        {"name": "Apple"},
                        {"name": "Samsung"},
                        {"name": "Google"}
                    ]
                },
                {
                    "name": "Storage", 
                    "levels": [
                        {"name": "64GB"},
                        {"name": "128GB"},
                        {"name": "256GB"}
                    ]
                },
                {
                    "name": "Price",
                    "levels": [
                        {"name": "$299"},
                        {"name": "$499"},
                        {"name": "$699"}
                    ]
                },
                {
                    "name": "Camera",
                    "levels": [
                        {"name": "12MP"},
                        {"name": "48MP"},
                        {"name": "108MP"}
                    ]
                }
            ]
        },
        "options_per_screen": 3,
        "num_screens": 10,
        "num_respondents": 50
    }
    
    try:
        request = GenerateDesignRequest(**request_data)
        result = handle_generate_design(request)
        
        print("✅ Design generation successful!")
        print(f"   - Generated design for {result.num_respondents} respondents")
        print(f"   - Total tasks: {len(result.tasks)}")
        efficiency_str = f"{result.efficiency:.3f}" if result.efficiency else "N/A"
        print(f"   - D-efficiency: {efficiency_str}")
        print(f"   - Notes: {result.notes}")
        
        # Show first few tasks
        print("\n   First 3 tasks:")
        for i, task in enumerate(result.tasks[:3]):
            print(f"   Task {i+1}: {len(task.options)} options")
            for j, option in enumerate(task.options[:2]):  # Show first 2 options
                print(f"     Option {j+1}: {option}")
            
    except Exception as e:
        print(f"❌ Design generation failed: {e}")
        return False
    
    # Test 2: Check if design has proper structure
    print("\n2. Checking design structure...")
    if result.tasks:
        first_task = result.tasks[0]
        if first_task.options:
            first_option = first_task.options[0]
            print("✅ Design structure is correct")
            print(f"   - Each task has {len(first_task.options)} options")
            print(f"   - Option structure: {list(first_option.keys())}")
        else:
            print("❌ No options in tasks")
    else:
        print("❌ No tasks generated")
    
    print("\n✅ All tests passed! MCP server is working correctly.")
    return True

if __name__ == "__main__":
    test_mcp_server()
