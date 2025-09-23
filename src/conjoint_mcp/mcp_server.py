#!/usr/bin/env python3
"""
MCP-compliant server for CBC Design Generator.

This server implements the Model Context Protocol (MCP) specification
and provides CBC design generation capabilities.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from conjoint_mcp.handlers.generation import handle_generate_design
from conjoint_mcp.handlers.optimization import handle_optimize_parameters, OptimizationRequest
from conjoint_mcp.handlers.export import handle_export_design, ExportRequest
from conjoint_mcp.models.requests import GenerateDesignRequest


# MCP Protocol Models
class MCPInitializeRequest(BaseModel):
    """MCP initialize request."""
    protocolVersion: str
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    clientInfo: Dict[str, str] = Field(default_factory=dict)


class MCPInitializeResponse(BaseModel):
    """MCP initialize response."""
    protocolVersion: str
    capabilities: Dict[str, Any]
    serverInfo: Dict[str, str]


class MCPTool(BaseModel):
    """MCP tool definition."""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class MCPResource(BaseModel):
    """MCP resource definition."""
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None


class MCPError(BaseModel):
    """MCP error response."""
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None


class MCPResponse(BaseModel):
    """MCP response."""
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    result: Optional[Any] = None
    error: Optional[MCPError] = None


# MCP Server Implementation
class CBCDesignMCPServer:
    """MCP-compliant server for CBC Design Generator."""
    
    def __init__(self):
        self.initialized = False
        self.capabilities = {
            "tools": {},
            "resources": {}
        }
        self.tools = self._define_tools()
        self.resources = self._define_resources()
    
    def _define_tools(self) -> List[MCPTool]:
        """Define available MCP tools."""
        return [
            MCPTool(
                name="generate_design",
                description="Generate a CBC (Choice Based Conjoint) design using specified algorithm and parameters",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "method": {
                            "type": "string",
                            "enum": ["random", "balanced", "orthogonal", "doptimal"],
                            "description": "Algorithm to use for design generation"
                        },
                        "grid": {
                            "type": "object",
                            "properties": {
                                "attributes": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "levels": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "name": {"type": "string"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "required": ["attributes"]
                        },
                        "options_per_screen": {
                            "type": "integer",
                            "minimum": 2,
                            "maximum": 10,
                            "default": 3,
                            "description": "Number of options per choice task"
                        },
                        "num_screens": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 10,
                            "description": "Number of choice tasks"
                        },
                        "constraints": {
                            "type": "object",
                            "description": "Optional constraint specification",
                            "properties": {
                                "prohibited_combinations": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "attributes": {"type": "object"},
                                            "reason": {"type": "string"}
                                        }
                                    }
                                },
                                "required_combinations": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "attributes": {"type": "object"},
                                            "reason": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "required": ["method", "grid"]
                }
            ),
            MCPTool(
                name="optimize_parameters",
                description="Optimize design parameters based on statistical requirements",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "grid": {
                            "type": "object",
                            "properties": {
                                "attributes": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "levels": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "name": {"type": "string"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "required": ["attributes"]
                        },
                        "target_power": {
                            "type": "number",
                            "minimum": 0.1,
                            "maximum": 1.0,
                            "default": 0.8,
                            "description": "Target statistical power"
                        },
                        "effect_size": {
                            "type": "number",
                            "minimum": 0.1,
                            "maximum": 1.0,
                            "default": 0.2,
                            "description": "Expected effect size"
                        },
                        "alpha": {
                            "type": "number",
                            "minimum": 0.01,
                            "maximum": 0.1,
                            "default": 0.05,
                            "description": "Significance level"
                        },
                        "max_respondents": {
                            "type": "integer",
                            "minimum": 10,
                            "maximum": 10000,
                            "default": 1000,
                            "description": "Maximum number of respondents"
                        }
                    },
                    "required": ["grid"]
                }
            ),
            MCPTool(
                name="export_design",
                description="Export a generated design in specified format",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "design_request": {
                            "type": "object",
                            "description": "Original design generation request",
                            "properties": {
                                "method": {"type": "string"},
                                "grid": {"type": "object"},
                                "options_per_screen": {"type": "integer"},
                                "num_screens": {"type": "integer"}
                            }
                        },
                        "format": {
                            "type": "string",
                            "enum": ["csv", "json", "qualtrics"],
                            "default": "csv",
                            "description": "Export format"
                        },
                        "include_metadata": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include metadata in export"
                        }
                    },
                    "required": ["design_request"]
                }
            ),
            MCPTool(
                name="health_check",
                description="Check server health and status",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    
    def _define_resources(self) -> List[MCPResource]:
        """Define available MCP resources."""
        return [
            MCPResource(
                uri="cbc://algorithms",
                name="Available Algorithms",
                description="List of available design generation algorithms",
                mimeType="application/json"
            ),
            MCPResource(
                uri="cbc://examples",
                name="Sample Scenarios",
                description="Pre-defined design scenarios for testing",
                mimeType="application/json"
            )
        ]
    
    async def handle_initialize(self, request: MCPInitializeRequest) -> MCPInitializeResponse:
        """Handle MCP initialize request."""
        self.initialized = True
        
        return MCPInitializeResponse(
            protocolVersion="2025-06-18",
            capabilities={
                "tools": {
                    "listChanged": True
                },
                "resources": {
                    "subscribe": True,
                    "listChanged": True
                }
            },
            serverInfo={
                "name": "cbc-design-generator",
                "version": "0.1.0"
            }
        )
    
    async def handle_tools_list(self) -> Dict[str, Any]:
        """Handle tools/list request."""
        return {
            "tools": [tool.model_dump() for tool in self.tools]
        }
    
    async def handle_tools_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        try:
            if name == "generate_design":
                gen_req = GenerateDesignRequest(**arguments)
                result = handle_generate_design(gen_req)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Generated CBC design with {len(result.tasks)} tasks and efficiency score {result.efficiency:.3f}.\n\nTasks:\n" + 
                                   "\n".join([f"Task {task.task_index}: {task.options}" for task in result.tasks[:3]]) +
                                   (f"\n... and {len(result.tasks) - 3} more tasks" if len(result.tasks) > 3 else "")
                        }
                    ]
                }
            
            elif name == "optimize_parameters":
                opt_req = OptimizationRequest(**arguments)
                result = handle_optimize_parameters(opt_req)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Optimized parameters:\n" +
                                   f"- Respondents: {result.num_respondents}\n" +
                                   f"- Screens: {result.num_screens}\n" +
                                   f"- Options per screen: {result.options_per_screen}\n" +
                                   f"- Expected power: {result.expected_power:.3f}\n" +
                                   f"- Parameter count: {result.parameter_count}\n" +
                                   (f"- Notes: {result.notes}" if result.notes else "")
                        }
                    ]
                }
            
            elif name == "export_design":
                export_req = ExportRequest(**arguments)
                result = handle_export_design(export_req)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Design exported in {result.format} format.\n" +
                                   f"Content length: {len(result.content)} characters\n" +
                                   f"Summary: {result.summary['total_tasks']} tasks, {result.summary['total_options']} options\n\n" +
                                   f"First 500 characters of content:\n{result.content[:500]}..."
                        }
                    ]
                }
            
            elif name == "health_check":
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "CBC Design Generator MCP Server is healthy and running.\nVersion: 0.1.0\nStatus: OK"
                        }
                    ]
                }
            
            else:
                raise ValueError(f"Unknown tool: {name}")
                
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing tool {name}: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def handle_resources_list(self) -> Dict[str, Any]:
        """Handle resources/list request."""
        return {
            "resources": [resource.model_dump() for resource in self.resources]
        }
    
    async def handle_resources_read(self, uri: str) -> Dict[str, Any]:
        """Handle resources/read request."""
        if uri == "cbc://algorithms":
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps({
                            "algorithms": [
                                {
                                    "name": "random",
                                    "description": "Fast, simple random assignment",
                                    "speed": "Very fast",
                                    "efficiency": "Low to moderate",
                                    "use_case": "Testing, prototyping"
                                },
                                {
                                    "name": "balanced",
                                    "description": "Ensures attribute level balance",
                                    "speed": "Fast",
                                    "efficiency": "Moderate",
                                    "use_case": "General purpose"
                                },
                                {
                                    "name": "orthogonal",
                                    "description": "Classical orthogonal design support",
                                    "speed": "Moderate",
                                    "efficiency": "High",
                                    "use_case": "High-quality studies"
                                },
                                {
                                    "name": "doptimal",
                                    "description": "Maximizes statistical efficiency",
                                    "speed": "Slow",
                                    "efficiency": "Highest",
                                    "use_case": "Final studies"
                                }
                            ]
                        }, indent=2)
                    }
                ]
            }
        
        elif uri == "cbc://examples":
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps({
                            "examples": [
                                {
                                    "name": "Smartphone Design",
                                    "description": "Design for a new smartphone",
                                    "attributes": [
                                        {"name": "Brand", "levels": ["TechCorp", "MobileMax", "SmartPhone Inc"]},
                                        {"name": "Storage", "levels": ["64GB", "128GB", "256GB"]},
                                        {"name": "Price", "levels": ["$299", "$499", "$699"]}
                                    ]
                                },
                                {
                                    "name": "Coffee Shop",
                                    "description": "Design for a coffee shop",
                                    "attributes": [
                                        {"name": "Price", "levels": ["$2.99", "$3.99", "$4.99"]},
                                        {"name": "Size", "levels": ["Small", "Medium", "Large"]},
                                        {"name": "Flavor", "levels": ["Vanilla", "Chocolate", "Caramel"]}
                                    ]
                                }
                            ]
                        }, indent=2)
                    }
                ]
            }
        
        else:
            raise ValueError(f"Unknown resource: {uri}")
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request."""
        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params", {})
        
        try:
            if method == "initialize":
                if not self.initialized:
                    init_req = MCPInitializeRequest(**params)
                    result = await self.handle_initialize(init_req)
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result.model_dump()
                    }
                else:
                    raise ValueError("Server already initialized")
            
            elif method == "tools/list":
                result = await self.handle_tools_list()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                result = await self.handle_tools_call(tool_name, tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            elif method == "resources/list":
                result = await self.handle_resources_list()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            elif method == "resources/read":
                uri = params.get("uri")
                result = await self.handle_resources_read(uri)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }


async def main():
    """Main entry point for MCP server."""
    server = CBCDesignMCPServer()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger("cbc-mcp-server")
    
    logger.info("Starting CBC Design Generator MCP Server...")
    
    try:
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = await server.handle_request(request)
                
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
            
            except Exception as e:
                logger.error(f"Error processing request: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
    
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
