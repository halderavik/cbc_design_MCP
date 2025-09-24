#!/usr/bin/env python3
"""
Startup script for Heroku deployment.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the HTTP server
from conjoint_mcp.http_server import main

if __name__ == "__main__":
    main()
