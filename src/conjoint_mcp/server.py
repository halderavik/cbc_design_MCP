from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from typing import Any

from pydantic import BaseModel, ValidationError as PydanticValidationError

from conjoint_mcp.handlers.generation import handle_generate_design
from conjoint_mcp.handlers.optimization import handle_optimize_parameters, OptimizationRequest
from conjoint_mcp.handlers.export import handle_export_design, ExportRequest
from conjoint_mcp.models.requests import GenerateDesignRequest
from conjoint_mcp.utils.errors import (
    ConjointMCPError,
    ValidationError,
    MethodNotFoundError,
    InternalError,
    create_error_response,
)
from conjoint_mcp.utils.logging import request_logger


class HealthResponse(BaseModel):
    """
    Health check response model.

    Returns:
        HealthResponse: Contains server status and version.
    """

    status: str
    version: str


def configure_logging() -> None:
    """
    Configure root logger for the application.
    """

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


async def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    """
    Enhanced JSON-RPC handler with comprehensive error handling and logging.

    Args:
        request (dict[str, Any]): JSON-RPC request object.

    Returns:
        dict[str, Any]: JSON-RPC response object.
    """

    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params", {})

    # Start request logging
    start_time = request_logger.log_request_start(request_id, method, params)

    try:
        # Validate JSON-RPC structure
        if not isinstance(request, dict):
            raise ValidationError("Request must be a JSON object")
        
        if "jsonrpc" not in request:
            raise ValidationError("Missing 'jsonrpc' field")
        
        if request.get("jsonrpc") != "2.0":
            raise ValidationError("Unsupported JSON-RPC version")
        
        if "method" not in request:
            raise ValidationError("Missing 'method' field")

        # Route to appropriate handler
        if method in ("ping", "health"):
            response = HealthResponse(status="ok", version=os.getenv("APP_VERSION", "0.1.0"))
            result = {"jsonrpc": "2.0", "id": request_id, "result": response.model_dump()}
            request_logger.log_request_end(request_id, method, start_time, success=True)
            return result

        elif method == "design.generate":
            try:
                gen_req = GenerateDesignRequest(**params)
                result = handle_generate_design(gen_req)
                response = {"jsonrpc": "2.0", "id": request_id, "result": result.model_dump()}
                request_logger.log_request_end(request_id, method, start_time, success=True)
                return response
            except PydanticValidationError as ve:
                error = ValidationError("Invalid parameters for design generation", ve.errors())
                request_logger.log_error(request_id, method, error)
                return create_error_response(request_id, error)
            except Exception as e:
                error = InternalError(f"Design generation failed: {str(e)}")
                request_logger.log_error(request_id, method, error)
                return create_error_response(request_id, error)

        elif method == "design.optimize":
            try:
                opt_req = OptimizationRequest(**params)
                result = handle_optimize_parameters(opt_req)
                response = {"jsonrpc": "2.0", "id": request_id, "result": result.model_dump()}
                request_logger.log_request_end(request_id, method, start_time, success=True)
                return response
            except PydanticValidationError as ve:
                error = ValidationError("Invalid parameters for optimization", ve.errors())
                request_logger.log_error(request_id, method, error)
                return create_error_response(request_id, error)
            except Exception as e:
                error = InternalError(f"Parameter optimization failed: {str(e)}")
                request_logger.log_error(request_id, method, error)
                return create_error_response(request_id, error)

        elif method == "design.export":
            try:
                export_req = ExportRequest(**params)
                result = handle_export_design(export_req)
                response = {"jsonrpc": "2.0", "id": request_id, "result": result.model_dump()}
                request_logger.log_request_end(request_id, method, start_time, success=True)
                return response
            except PydanticValidationError as ve:
                error = ValidationError("Invalid parameters for export", ve.errors())
                request_logger.log_error(request_id, method, error)
                return create_error_response(request_id, error)
            except Exception as e:
                error = InternalError(f"Design export failed: {str(e)}")
                request_logger.log_error(request_id, method, error)
                return create_error_response(request_id, error)

        else:
            error = MethodNotFoundError(method)
            request_logger.log_error(request_id, method, error)
            return create_error_response(request_id, error)

    except ConjointMCPError:
        # Re-raise ConjointMCPError to be handled by outer try-catch
        raise
    except Exception as e:
        # Handle unexpected errors
        error = InternalError(f"Unexpected error: {str(e)}")
        request_logger.log_error(request_id, method, error)
        return create_error_response(request_id, error)


async def stdio_server() -> None:
    """
    Very small stdio JSON-RPC loop to be MCP-compatible in spirit for now.
    """

    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    loop = asyncio.get_event_loop()
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    writer_transport, writer_protocol = await loop.connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout
    )
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, loop)

    while True:
        line = await reader.readline()
        if not line:
            break
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = await handle_request(req)
        writer.write(json.dumps(resp) + "\n")
        await writer.drain()


def stdio_server_sync() -> None:
    """
    Synchronous stdio loop that reads lines from stdin and writes responses to stdout.
    Compatible with Windows PowerShell/cmd.
    """

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        # Run handler synchronously using asyncio loop for async function
        resp = asyncio.run(handle_request(req))
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


def main() -> None:
    """
    Entry point for running the server. Uses stdio loop for now.
    """

    configure_logging()
    try:
        if os.name == "nt":
            stdio_server_sync()
        else:
            asyncio.run(stdio_server())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()


