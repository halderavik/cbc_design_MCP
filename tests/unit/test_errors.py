from conjoint_mcp.utils.errors import (
    ConjointMCPError,
    ValidationError,
    MethodNotFoundError,
    InternalError,
    DesignGenerationError,
    ConstraintViolationError,
    create_error_response,
)


def test_conjoint_mcp_error():
    """Test base ConjointMCPError."""
    error = ConjointMCPError("Test error", code=-32000, data={"key": "value"})
    assert error.message == "Test error"
    assert error.code == -32000
    assert error.data == {"key": "value"}


def test_validation_error():
    """Test ValidationError."""
    validation_errors = [{"field": "test", "message": "invalid"}]
    error = ValidationError("Validation failed", validation_errors)
    assert error.message == "Validation failed"
    assert error.code == -32602
    assert error.data == {"validation_errors": validation_errors}


def test_method_not_found_error():
    """Test MethodNotFoundError."""
    error = MethodNotFoundError("unknown.method")
    assert error.message == "Method not found: unknown.method"
    assert error.code == -32601


def test_internal_error():
    """Test InternalError."""
    details = {"component": "test"}
    error = InternalError("Internal failure", details)
    assert error.message == "Internal failure"
    assert error.code == -32603
    assert error.data == details


def test_design_generation_error():
    """Test DesignGenerationError."""
    details = {"reason": "algorithm_failed"}
    error = DesignGenerationError("Generation failed", "doptimal", details)
    assert error.message == "Generation failed"
    assert error.code == -32001
    assert error.data == {"method": "doptimal", "details": details}


def test_constraint_violation_error():
    """Test ConstraintViolationError."""
    violations = ["Prohibited combination found"]
    error = ConstraintViolationError("Constraint violated", violations)
    assert error.message == "Constraint violated"
    assert error.code == -32002
    assert error.data == {"violations": violations}


def test_create_error_response():
    """Test create_error_response function."""
    error = ValidationError("Test validation error")
    response = create_error_response(123, error)
    
    expected = {
        "jsonrpc": "2.0",
        "id": 123,
        "error": {
            "code": -32602,
            "message": "Test validation error",
            "data": {"validation_errors": None}
        }
    }
    assert response == expected


def test_create_error_response_with_data():
    """Test create_error_response with additional data."""
    error = InternalError("Test internal error", {"details": "test"})
    response = create_error_response(456, error)
    
    assert response["error"]["data"] == {"details": "test"}
