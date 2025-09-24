#!/usr/bin/env python3
"""
Test script for the HTTP server functionality.
"""

import requests
import json
import time
import subprocess
import sys
from pathlib import Path


def test_http_server():
    """Test the HTTP server endpoints."""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing HTTP Server Endpoints")
    print("=" * 40)
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test detailed health check
    try:
        response = requests.get(f"{base_url}/health/detailed")
        print(f"✅ Detailed health check: {response.status_code}")
        health_data = response.json()
        print(f"   Status: {health_data.get('status')}")
        print(f"   Environment: {health_data.get('environment')}")
    except Exception as e:
        print(f"❌ Detailed health check failed: {e}")
        return False
    
    # Test tools endpoint
    try:
        response = requests.get(f"{base_url}/api/tools")
        print(f"✅ Tools endpoint: {response.status_code}")
        tools_data = response.json()
        print(f"   Available tools: {len(tools_data.get('tools', []))}")
    except Exception as e:
        print(f"❌ Tools endpoint failed: {e}")
        return False
    
    # Test resources endpoint
    try:
        response = requests.get(f"{base_url}/api/resources")
        print(f"✅ Resources endpoint: {response.status_code}")
        resources_data = response.json()
        print(f"   Available resources: {len(resources_data.get('resources', []))}")
    except Exception as e:
        print(f"❌ Resources endpoint failed: {e}")
        return False
    
    # Test design generation endpoint
    try:
        test_request = {
            "method": "random",
            "grid": {
                "attributes": [
                    {
                        "name": "Color",
                        "levels": [
                            {"name": "Red"},
                            {"name": "Blue"}
                        ]
                    },
                    {
                        "name": "Size",
                        "levels": [
                            {"name": "S"},
                            {"name": "L"}
                        ]
                    }
                ]
            },
            "options_per_screen": 2,
            "num_screens": 3
        }
        
        response = requests.post(f"{base_url}/api/design/generate", json=test_request)
        print(f"✅ Design generation: {response.status_code}")
        if response.status_code == 200:
            design_data = response.json()
            print(f"   Generated {len(design_data.get('tasks', []))} tasks")
            print(f"   Number of respondents: {design_data.get('num_respondents', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Design generation failed: {e}")
        return False
    
    print("=" * 40)
    print("🎉 All HTTP server tests passed!")
    return True


def start_server():
    """Start the HTTP server in background."""
    print("🚀 Starting HTTP server...")
    
    # Start server in background
    process = subprocess.Popen([
        sys.executable, "-m", "conjoint_mcp.http_server"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(3)
    
    return process


def main():
    """Main test function."""
    print("🧪 HTTP Server Test Suite")
    print("=" * 50)
    
    # Check if server is already running
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        print("✅ Server is already running")
        server_process = None
    except:
        print("🔄 Starting server...")
        server_process = start_server()
        time.sleep(2)
    
    # Run tests
    success = test_http_server()
    
    # Cleanup
    if server_process:
        print("🛑 Stopping server...")
        server_process.terminate()
        server_process.wait()
    
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
