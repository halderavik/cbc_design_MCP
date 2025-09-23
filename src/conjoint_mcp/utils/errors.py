from __future__ import annotations

from typing import Any, Dict, Optional


class ConjointMCPError(Exception):
    """
    Base exception for Conjoint MCP server errors.
    """
    
    def __init__(self, message: str, code: int = -32000, data: Optional[Dict[str, Any]] = None):
        """
        Initialize error with message, code, and optional data.
        
        Args:
            message (str): Error message.
            code (int): Error code.
            data (Optional[Dict[str, Any]]): Additional error data.
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data


class ValidationError(ConjointMCPError):
    """
    Error for validation failures.
    """
    
    def __init__(self, message: str, validation_errors: Optional[list] = None):
        """
        Initialize validation error.
        
        Args:
            message (str): Error message.
            validation_errors (Optional[list]): List of validation errors.
        """
        super().__init__(message, code=-32602, data={"validation_errors": validation_errors})


class MethodNotFoundError(ConjointMCPError):
    """
    Error for unknown methods.
    """
    
    def __init__(self, method: str):
        """
        Initialize method not found error.
        
        Args:
            method (str): Method name that was not found.
        """
        super().__init__(f"Method not found: {method}", code=-32601)


class InternalError(ConjointMCPError):
    """
    Error for internal server issues.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize internal error.
        
        Args:
            message (str): Error message.
            details (Optional[Dict[str, Any]]): Additional error details.
        """
        super().__init__(message, code=-32603, data=details)


class DesignGenerationError(ConjointMCPError):
    """
    Error for design generation failures.
    """
    
    def __init__(self, message: str, method: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize design generation error.
        
        Args:
            message (str): Error message.
            method (str): Design generation method that failed.
            details (Optional[Dict[str, Any]]): Additional error details.
        """
        super().__init__(message, code=-32001, data={"method": method, "details": details})


class ConstraintViolationError(ConjointMCPError):
    """
    Error for constraint violations.
    """
    
    def __init__(self, message: str, violations: list):
        """
        Initialize constraint violation error.
        
        Args:
            message (str): Error message.
            violations (list): List of constraint violations.
        """
        super().__init__(message, code=-32002, data={"violations": violations})


def create_error_response(request_id: Any, error: ConjointMCPError) -> Dict[str, Any]:
    """
    Create JSON-RPC error response from ConjointMCPError.
    
    Args:
        request_id: Request identifier.
        error: ConjointMCPError instance.
        
    Returns:
        Dict[str, Any]: JSON-RPC error response.
    """
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": error.code,
            "message": error.message,
        }
    }
    
    if error.data:
        response["error"]["data"] = error.data
    
    return response
