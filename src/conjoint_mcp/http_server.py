#!/usr/bin/env python3
"""
HTTP server for Heroku deployment with health checks and MCP endpoints.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from conjoint_mcp.config.settings import get_settings
from conjoint_mcp.handlers.generation import handle_generate_design
from conjoint_mcp.handlers.optimization import handle_optimize_parameters
from conjoint_mcp.handlers.export import handle_export_design
from conjoint_mcp.models.requests import GenerateDesignRequest, OptimizeParametersRequest
from conjoint_mcp.models.responses import GenerateDesignResponse, OptimizeParametersResponse
from conjoint_mcp.constraints.models import ConstraintSpec
from conjoint_mcp.utils.performance import get_system_info, get_performance_limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CBC Design Generator MCP Server",
    description="HTTP interface for Choice Based Conjoint design generation",
    version="1.0.0"
)

settings = get_settings()


@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "service": "CBC Design Generator MCP Server",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Heroku monitoring."""
    try:
        # Basic health check - could be extended with more checks
        return {
            "status": "healthy",
            "service": settings.app_name,
            "environment": settings.environment,
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system information."""
    try:
        import platform
        
        system_info = get_system_info()
        performance_limiter = get_performance_limiter()
        
        return {
            "status": "healthy",
            "service": settings.app_name,
            "environment": settings.environment,
            "version": "1.0.0",
            "system": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "memory": system_info["memory"],
                "cpu": system_info["cpu"],
                "disk": system_info["disk"]
            },
            "settings": {
                "max_respondents": settings.max_respondents,
                "max_tasks_per_respondent": settings.max_tasks_per_respondent,
                "max_options_per_task": settings.max_options_per_task
            },
            "performance_limits": {
                "max_memory_mb": performance_limiter.max_memory_mb,
                "max_execution_time_s": performance_limiter.max_execution_time,
                "max_respondents": performance_limiter.max_respondents,
                "max_tasks_per_respondent": performance_limiter.max_tasks_per_respondent,
                "max_options_per_task": performance_limiter.max_options_per_task
            }
        }
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "service": settings.app_name
        }


@app.post("/api/design/generate")
async def generate_design_endpoint(request_data: Dict[str, Any]):
    """Generate a CBC design via HTTP."""
    try:
        # Convert dict to request model
        gen_req = GenerateDesignRequest(**request_data)
        
        # Call the handler
        result = handle_generate_design(gen_req)
        
        # Convert response to dict
        return result.dict()
        
    except Exception as e:
        logger.error(f"Design generation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/design/optimize")
async def optimize_parameters_endpoint(request_data: Dict[str, Any]):
    """Optimize design parameters via HTTP."""
    try:
        # Convert dict to request model
        opt_req = OptimizeParametersRequest(**request_data)
        
        # Call the handler
        result = handle_optimize_parameters(opt_req)
        
        # Convert response to dict
        return result.dict()
        
    except Exception as e:
        logger.error(f"Parameter optimization failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/design/export")
async def export_design_endpoint(request_data: Dict[str, Any]):
    """Export a design via HTTP."""
    try:
        from conjoint_mcp.handlers.export import ExportRequest
        
        # Convert dict to request model
        export_req = ExportRequest(**request_data)
        
        # Call the handler
        result = handle_export_design(export_req)
        
        # Convert response to dict
        return result.dict()
        
    except Exception as e:
        logger.error(f"Design export failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/tools")
async def list_tools():
    """List available MCP tools."""
    return {
        "tools": [
            {
                "name": "generate_design",
                "description": "Generate a CBC design using various algorithms"
            },
            {
                "name": "optimize_parameters", 
                "description": "Optimize study parameters for statistical power"
            },
            {
                "name": "export_design",
                "description": "Export generated designs in various formats"
            },
            {
                "name": "save_design_file",
                "description": "Save design to file in project directory"
            }
        ]
    }


@app.get("/api/resources")
async def list_resources():
    """List available MCP resources."""
    return {
        "resources": [
            {
                "uri": "cbc://algorithms",
                "name": "Available Algorithms",
                "description": "List of supported design generation algorithms"
            },
            {
                "uri": "cbc://examples",
                "name": "Example Scenarios", 
                "description": "Sample design scenarios for different industries"
            }
        ]
    }


def main():
    """Main entry point for HTTP server."""
    # Heroku sets PORT environment variable
    port = int(os.environ.get("PORT", settings.port))
    host = "0.0.0.0"  # Heroku requires binding to 0.0.0.0
    
    logger.info(f"Starting HTTP server on {host}:{port}")
    logger.info(f"Environment: {settings.environment}")
    
    uvicorn.run(
        "conjoint_mcp.http_server:app",
        host=host,
        port=port,
        log_level=settings.log_level.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main()
