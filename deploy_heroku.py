#!/usr/bin/env python3
"""
Heroku deployment script for CBC Design Generator MCP Server.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def check_heroku_cli():
    """Check if Heroku CLI is installed."""
    try:
        subprocess.run(["heroku", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    """Main deployment function."""
    print("🚀 Starting Heroku deployment for CBC Design Generator MCP Server")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("Procfile").exists():
        print("❌ Procfile not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check Heroku CLI
    if not check_heroku_cli():
        print("❌ Heroku CLI not found. Please install it first:")
        print("   https://devcenter.heroku.com/articles/heroku-cli")
        sys.exit(1)
    
    # Get app name from environment or use default
    app_name = os.getenv("HEROKU_APP_NAME", "cbc-design-mcp")
    print(f"📱 Deploying to Heroku app: {app_name}")
    
    # Check if app exists
    if not run_command(f"heroku apps:info --app {app_name}", "Checking if Heroku app exists"):
        print(f"❌ App {app_name} not found. Please create it first:")
        print(f"   heroku create {app_name}")
        sys.exit(1)
    
    # Set environment variables
    env_vars = {
        "APP_ENVIRONMENT": "prod",
        "APP_LOG_LEVEL": "INFO",
        "MCP_LOG_LEVEL": "WARNING",
        "MAX_RESPONDENTS": "2000",
        "MAX_TASKS_PER_RESPONDENT": "20",
        "MAX_OPTIONS_PER_TASK": "5",
        "HEALTH_CHECK_ENABLED": "true",
        "HEALTH_CHECK_TIMEOUT": "30"
    }
    
    for key, value in env_vars.items():
        if not run_command(f"heroku config:set {key}={value} --app {app_name}", f"Setting {key}"):
            print(f"⚠️  Failed to set {key}, continuing...")
    
    # Deploy to Heroku
    if not run_command(f"git push heroku main", "Deploying to Heroku"):
        print("❌ Deployment failed")
        sys.exit(1)
    
    # Check deployment status
    if not run_command(f"heroku ps:scale web=1 --app {app_name}", "Scaling web dyno"):
        print("⚠️  Failed to scale web dyno")
    
    # Test health endpoint
    if not run_command(f"heroku run python -c 'import requests; print(requests.get(\"http://localhost:8000/health\").json())' --app {app_name}", "Testing health endpoint"):
        print("⚠️  Health check failed, but deployment may still be successful")
    
    print("=" * 60)
    print("🎉 Deployment completed!")
    print(f"🌐 Your app is available at: https://{app_name}.herokuapp.com")
    print(f"🏥 Health check: https://{app_name}.herokuapp.com/health")
    print(f"📊 API docs: https://{app_name}.herokuapp.com/docs")
    print()
    print("📋 Next steps:")
    print("1. Test the health endpoint")
    print("2. Test the API endpoints")
    print("3. Monitor logs: heroku logs --tail --app {app_name}")
    print("4. Scale if needed: heroku ps:scale web=1 --app {app_name}")


if __name__ == "__main__":
    main()
