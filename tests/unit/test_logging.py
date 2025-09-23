import logging
import time
from unittest.mock import patch

from conjoint_mcp.utils.logging import RequestLogger


def test_request_logger_setup():
    """Test RequestLogger initialization."""
    logger = RequestLogger()
    assert logger.logger is not None
    assert logger.logger.name == "conjoint_mcp"


def test_log_request_start():
    """Test request start logging."""
    logger = RequestLogger()
    start_time = logger.log_request_start(123, "test.method", {"param": "value"})
    
    assert isinstance(start_time, float)
    assert start_time > 0


def test_log_request_end():
    """Test request end logging."""
    logger = RequestLogger()
    start_time = time.time() - 0.1  # Simulate 100ms duration
    
    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_request_end(123, "test.method", start_time, success=True)
        mock_info.assert_called_once()
        call_args = mock_info.call_args[0][0]
        assert "SUCCESS" in call_args
        assert "test.method" in call_args


def test_log_request_end_failed():
    """Test request end logging for failed requests."""
    logger = RequestLogger()
    start_time = time.time() - 0.1
    
    with patch.object(logger.logger, 'info') as mock_info:
        logger.log_request_end(123, "test.method", start_time, success=False)
        mock_info.assert_called_once()
        call_args = mock_info.call_args[0][0]
        assert "FAILED" in call_args


def test_log_error():
    """Test error logging."""
    logger = RequestLogger()
    error = ValueError("Test error")
    
    with patch.object(logger.logger, 'error') as mock_error:
        logger.log_error(123, "test.method", error)
        mock_error.assert_called_once()
        call_args = mock_error.call_args[0][0]
        assert "ValueError" in call_args
        assert "Test error" in call_args


def test_sanitize_params():
    """Test parameter sanitization."""
    logger = RequestLogger()
    
    params = {
        "normal_param": "value",
        "password": "secret123",
        "token": "abc123",
        "nested": {
            "key": "secret",
            "normal": "value"
        },
        "large_list": list(range(15))  # Should be truncated
    }
    
    sanitized = logger._sanitize_params(params)
    
    assert sanitized["normal_param"] == "value"
    assert sanitized["password"] == "***"
    assert sanitized["token"] == "***"
    assert sanitized["nested"]["key"] == "***"
    assert sanitized["nested"]["normal"] == "value"
    assert sanitized["large_list"] == "[15 items]"


def test_performance_warning_slow():
    """Test performance warning for slow requests."""
    logger = RequestLogger()
    start_time = time.time() - 35  # Simulate 35 second duration
    
    with patch.object(logger.logger, 'warning') as mock_warning:
        logger.log_request_end(123, "slow.method", start_time, success=True)
        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        assert "slow" in call_args.lower()


def test_performance_warning_moderate():
    """Test performance warning for moderate duration requests."""
    logger = RequestLogger()
    start_time = time.time() - 15  # Simulate 15 second duration
    
    with patch.object(logger.logger, 'warning') as mock_warning:
        logger.log_request_end(123, "moderate.method", start_time, success=True)
        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        assert "moderate" in call_args.lower()
