#!/usr/bin/env python3
"""
MCP-compliant server for CBC Design Generator - Version 2.

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
                        "num_respondents": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 5000,
                            "description": "Number of respondents. If not provided, system will suggest optimal number based on statistical power analysis."
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
                                "num_screens": {"type": "integer"},
                                "num_respondents": {"type": "integer"}
                            }
                        },
                        "format": {
                            "type": "string",
                            "enum": ["csv", "json", "qualtrics"],
                            "default": "csv",
                            "description": "Export format"
                        },
                        "save_to_file": {
                            "type": "boolean",
                            "default": False,
                            "description": "Save the exported content to a file in the project directory"
                        },
                        "filename": {
                            "type": "string",
                            "description": "Custom filename for the exported file (optional)"
                        }
                    },
                    "required": ["design_request"]
                }
            ),
            MCPTool(
                name="save_design_file",
                description="Save a generated design to a file in the project directory",
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
                                "num_screens": {"type": "integer"},
                                "num_respondents": {"type": "integer"}
                            }
                        },
                        "format": {
                            "type": "string",
                            "enum": ["csv", "json", "qualtrics"],
                            "default": "csv",
                            "description": "Export format"
                        },
                        "filename": {
                            "type": "string",
                            "description": "Filename for the saved file (without extension)"
                        }
                    },
                    "required": ["design_request"]
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
                
                # Calculate total observations
                total_observations = result.num_respondents * len(result.tasks) * len(result.tasks[0].options) if result.tasks else 0
                
                response_text = f"✅ Generated CBC design successfully!\n\n"
                response_text += f"📊 Design Summary:\n"
                response_text += f"- Algorithm: {gen_req.method}\n"
                response_text += f"- Tasks per respondent: {len(result.tasks)}\n"
                response_text += f"- Options per task: {len(result.tasks[0].options) if result.tasks else 0}\n"
                response_text += f"- Number of respondents: {result.num_respondents}\n"
                response_text += f"- Total observations: {total_observations:,}\n"
                response_text += f"- Efficiency score: {result.efficiency:.3f}\n\n"
                
                if result.suggested_respondents:
                    response_text += f"💡 Suggested {result.suggested_respondents} respondents based on statistical power analysis.\n\n"
                
                if result.notes:
                    response_text += f"📝 Notes: {result.notes}\n\n"
                
                response_text += f"📋 Sample Tasks (showing first 3):\n"
                for i, task in enumerate(result.tasks[:3]):
                    response_text += f"Task {task.task_index}:\n"
                    for j, option in enumerate(task.options):
                        response_text += f"  Option {j+1}: {option}\n"
                    response_text += "\n"
                
                if len(result.tasks) > 3:
                    response_text += f"... and {len(result.tasks) - 3} more tasks\n\n"
                
                response_text += f"💾 The design is ready for export. Each respondent will see the same {len(result.tasks)} tasks, and the export will include a 'respondent_ID' column for all {result.num_respondents} respondents."
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": response_text
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
                
                # Get the generated design from the export result
                # The export handler generates the design internally
                design_response = handle_generate_design(export_req.design_request)
                
                # Calculate total rows in export
                total_rows = design_response.num_respondents * len(design_response.tasks) * len(design_response.tasks[0].options) if design_response.tasks else 0
                
                response_text = f"✅ Design exported successfully in {result.format.upper()} format!\n\n"
                response_text += f"📊 Export Summary:\n"
                response_text += f"- Format: {result.format}\n"
                response_text += f"- Number of respondents: {design_response.num_respondents}\n"
                response_text += f"- Tasks per respondent: {len(design_response.tasks)}\n"
                response_text += f"- Options per task: {len(design_response.tasks[0].options) if design_response.tasks else 0}\n"
                response_text += f"- Total rows in export: {total_rows:,}\n"
                response_text += f"- Content size: {len(result.content):,} characters\n\n"
                
                if result.format == "csv":
                    response_text += f"📋 CSV Structure:\n"
                    response_text += f"- Column 1: respondent_ID (1 to {design_response.num_respondents})\n"
                    response_text += f"- Column 2: Task_Index\n"
                    response_text += f"- Column 3: Option_Index\n"
                    response_text += f"- Columns 4+: Attribute values\n\n"
                    response_text += f"💡 Each respondent will see the same {len(design_response.tasks)} tasks, but with unique respondent_ID values.\n\n"
                
                # Handle file saving if requested
                save_to_file = arguments.get("save_to_file", False)
                filename = arguments.get("filename")
                
                if save_to_file:
                    import os
                    from datetime import datetime
                    
                    # Generate filename if not provided
                    if not filename:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"cbc_design_{timestamp}"
                    
                    # Add appropriate extension
                    file_extension = result.format
                    if file_extension == "csv":
                        file_extension = "csv"
                    elif file_extension == "json":
                        file_extension = "json"
                    elif file_extension == "qualtrics":
                        file_extension = "csv"
                    
                    full_filename = f"{filename}.{file_extension}"
                    file_path = os.path.join(os.getcwd(), full_filename)
                    
                    # Save the file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(result.content)
                    
                    response_text += f"💾 File saved successfully!\n"
                    response_text += f"- Filename: {full_filename}\n"
                    response_text += f"- Location: {file_path}\n"
                    response_text += f"- Size: {len(result.content):,} characters\n\n"
                else:
                    response_text += f"💡 To save the complete file, use the 'save_to_file' parameter or the 'save_design_file' tool.\n\n"
                
                # Show preview of content
                if len(result.content) > 1000:
                    response_text += f"📄 Preview (first 1000 characters of {len(result.content):,} total):\n"
                    response_text += f"```\n{result.content[:1000]}...\n```"
                else:
                    response_text += f"📄 Complete content:\n"
                    response_text += f"```\n{result.content}\n```"
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": response_text
                        }
                    ]
                }
            
            elif name == "save_design_file":
                export_req = ExportRequest(**arguments)
                result = handle_export_design(export_req)
                
                # Get the generated design from the export result
                design_response = handle_generate_design(export_req.design_request)
                
                # Calculate total rows in export
                total_rows = design_response.num_respondents * len(design_response.tasks) * len(design_response.tasks[0].options) if design_response.tasks else 0
                
                # Save the file
                import os
                from datetime import datetime
                
                filename = arguments.get("filename", f"cbc_design_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                file_extension = result.format
                if file_extension == "qualtrics":
                    file_extension = "csv"
                
                full_filename = f"{filename}.{file_extension}"
                file_path = os.path.join(os.getcwd(), full_filename)
                
                # Save the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(result.content)
                
                response_text = f"✅ Design file saved successfully!\n\n"
                response_text += f"📊 File Details:\n"
                response_text += f"- Filename: {full_filename}\n"
                response_text += f"- Location: {file_path}\n"
                response_text += f"- Format: {result.format.upper()}\n"
                response_text += f"- Size: {len(result.content):,} characters\n"
                response_text += f"- Number of respondents: {design_response.num_respondents}\n"
                response_text += f"- Tasks per respondent: {len(design_response.tasks)}\n"
                response_text += f"- Options per task: {len(design_response.tasks[0].options) if design_response.tasks else 0}\n"
                response_text += f"- Total rows: {total_rows:,}\n\n"
                
                if result.format == "csv":
                    response_text += f"📋 CSV Structure:\n"
                    response_text += f"- Column 1: respondent_ID (1 to {design_response.num_respondents})\n"
                    response_text += f"- Column 2: Task_Index\n"
                    response_text += f"- Column 3: Option_Index\n"
                    response_text += f"- Columns 4+: Attribute values\n\n"
                
                response_text += f"💡 The complete file is now saved and ready for use in your survey platform or analysis software."
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": response_text
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
        
        # Ensure request_id is never None for JSON-RPC compliance
        if request_id is None:
            request_id = 0
        
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
    
    # Configure logging to stderr to avoid interfering with JSON-RPC
    logging.basicConfig(
        level=logging.WARNING,  # Reduce log level to avoid noise
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr  # Log to stderr
    )
    logger = logging.getLogger("cbc-mcp-server")
    
    try:
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                request = json.loads(line)
                response = await server.handle_request(request)
                
                # Ensure response is valid JSON-RPC
                if "jsonrpc" not in response:
                    response["jsonrpc"] = "2.0"
                if "id" not in response:
                    response["id"] = request.get("id", 0)
                
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
