from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from conjoint_mcp.config.settings import get_settings


class RequestLogger:
    """
    Enhanced logging for MCP requests with performance monitoring.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger("conjoint_mcp")
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Setup logger with appropriate level and format."""
        self.logger.setLevel(getattr(logging, self.settings.log_level.upper()))
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_request_start(self, request_id: Any, method: str, params: Optional[Dict[str, Any]] = None) -> float:
        """
        Log the start of a request and return start time.
        
        Args:
            request_id: Request identifier.
            method: Method name.
            params: Request parameters.
            
        Returns:
            float: Start time for performance measurement.
        """
        start_time = time.time()
        self.logger.info(f"Request {request_id}: Starting {method}")
        if params:
            # Log params but exclude sensitive data
            safe_params = self._sanitize_params(params)
            self.logger.debug(f"Request {request_id}: Params: {safe_params}")
        return start_time
    
    def log_request_end(self, request_id: Any, method: str, start_time: float, success: bool = True) -> None:
        """
        Log the end of a request with performance metrics.
        
        Args:
            request_id: Request identifier.
            method: Method name.
            start_time: Start time from log_request_start.
            success: Whether the request was successful.
        """
        duration = time.time() - start_time
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"Request {request_id}: {method} {status} in {duration:.3f}s")
        
        # Log performance warnings
        if duration > 30:
            self.logger.warning(f"Request {request_id}: {method} took {duration:.3f}s (slow)")
        elif duration > 10:
            self.logger.warning(f"Request {request_id}: {method} took {duration:.3f}s (moderate)")
    
    def log_error(self, request_id: Any, method: str, error: Exception) -> None:
        """
        Log request errors with context.
        
        Args:
            request_id: Request identifier.
            method: Method name.
            error: Exception that occurred.
        """
        self.logger.error(f"Request {request_id}: {method} failed with {type(error).__name__}: {str(error)}")
    
    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize parameters for logging (remove sensitive data).
        
        Args:
            params: Parameters to sanitize.
            
        Returns:
            Dict[str, Any]: Sanitized parameters.
        """
        sanitized = {}
        for key, value in params.items():
            if key.lower() in ['password', 'token', 'key', 'secret']:
                sanitized[key] = "***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_params(value)
            elif isinstance(value, list) and len(value) > 10:
                sanitized[key] = f"[{len(value)} items]"
            else:
                sanitized[key] = value
        return sanitized


# Global request logger instance
request_logger = RequestLogger()
