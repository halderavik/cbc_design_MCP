import asyncio
import pytest
from conjoint_mcp.server import handle_request


@pytest.mark.asyncio
async def test_complete_workflow():
    """Test complete workflow from design generation to export."""
    # Step 1: Generate a design
    generate_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "design.generate",
        "params": {
            "method": "random",
            "grid": {
                "attributes": [
                    {"name": "Color", "levels": [{"name": "Red"}, {"name": "Blue"}]},
                    {"name": "Size", "levels": [{"name": "S"}, {"name": "L"}]},
                ]
            },
            "options_per_screen": 3,
            "num_screens": 5,
        },
    }
    
    generate_resp = await handle_request(generate_req)
    assert generate_resp["id"] == 1
    assert "result" in generate_resp
    assert len(generate_resp["result"]["tasks"]) == 5
    
    # Step 2: Optimize parameters
    optimize_req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "design.optimize",
        "params": {
            "grid": {
                "attributes": [
                    {"name": "Color", "levels": [{"name": "Red"}, {"name": "Blue"}]},
                    {"name": "Size", "levels": [{"name": "S"}, {"name": "L"}]},
                ]
            },
            "target_power": 0.8,
            "effect_size": 0.2,
            "alpha": 0.05,
        },
    }
    
    optimize_resp = await handle_request(optimize_req)
    assert optimize_resp["id"] == 2
    assert "result" in optimize_resp
    assert "num_respondents" in optimize_resp["result"]
    assert "num_screens" in optimize_resp["result"]
    
    # Step 3: Export the design
    export_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "design.export",
        "params": {
            "design_request": generate_req["params"],
            "format": "csv",
            "include_metadata": True,
        },
    }
    
    export_resp = await handle_request(export_req)
    assert export_resp["id"] == 3
    assert "result" in export_resp
    assert export_resp["result"]["format"] == "csv"
    assert "CBC Design Export" in export_resp["result"]["content"]


@pytest.mark.asyncio
async def test_error_handling_workflow():
    """Test error handling throughout the workflow."""
    # Test invalid method
    invalid_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "invalid.method",
        "params": {},
    }
    
    resp = await handle_request(invalid_req)
    assert resp["id"] == 1
    assert "error" in resp
    assert resp["error"]["code"] == -32601
    
    # Test invalid parameters
    invalid_params_req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "design.generate",
        "params": {
            "method": "random",
            "grid": {
                "attributes": []  # Empty attributes should fail
            },
        },
    }
    
    resp = await handle_request(invalid_params_req)
    assert resp["id"] == 2
    assert "error" in resp
    assert resp["error"]["code"] == -32603  # Internal error for validation failure


@pytest.mark.asyncio
async def test_multiple_formats_workflow():
    """Test exporting designs in multiple formats."""
    base_params = {
        "method": "random",
        "grid": {
            "attributes": [
                {"name": "Color", "levels": [{"name": "Red"}, {"name": "Blue"}]},
            ]
        },
        "options_per_screen": 2,
        "num_screens": 3,
    }
    
    formats = ["csv", "json", "qualtrics"]
    
    for format_type in formats:
        export_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "design.export",
            "params": {
                "design_request": base_params,
                "format": format_type,
            },
        }
        
        resp = await handle_request(export_req)
        assert resp["id"] == 1
        assert "result" in resp
        assert resp["result"]["format"] == format_type
        assert "content" in resp["result"]


@pytest.mark.asyncio
async def test_constraint_workflow():
    """Test workflow with constraints."""
    # Generate design with constraints
    generate_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "design.generate",
        "params": {
            "method": "random",
            "grid": {
                "attributes": [
                    {"name": "Color", "levels": [{"name": "Red"}, {"name": "Blue"}]},
                    {"name": "Size", "levels": [{"name": "S"}, {"name": "L"}]},
                ]
            },
            "options_per_screen": 3,
            "num_screens": 5,
            "constraints": {
                "prohibited_combinations": [
                    {
                        "attributes": {"Color": "Red", "Size": "S"},
                        "reason": "Red small items not available"
                    }
                ]
            },
        },
    }
    
    generate_resp = await handle_request(generate_req)
    assert generate_resp["id"] == 1
    assert "result" in generate_resp
    
    # Export with constraint validation
    export_req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "design.export",
        "params": {
            "design_request": generate_req["params"],
            "format": "csv",
            "constraints": {
                "prohibited_combinations": [
                    {
                        "attributes": {"Color": "Red", "Size": "S"},
                        "reason": "Red small items not available"
                    }
                ]
            },
        },
    }
    
    export_resp = await handle_request(export_req)
    assert export_resp["id"] == 2
    assert "result" in export_resp
    assert "validation_results" in export_resp["result"]


@pytest.mark.asyncio
async def test_algorithm_comparison_workflow():
    """Test comparing different algorithms."""
    base_params = {
        "grid": {
            "attributes": [
                {"name": "Color", "levels": [{"name": "Red"}, {"name": "Blue"}]},
                {"name": "Size", "levels": [{"name": "S"}, {"name": "L"}]},
            ]
        },
        "options_per_screen": 3,
        "num_screens": 5,
    }
    
    algorithms = ["random", "balanced", "orthogonal", "doptimal"]
    results = {}
    
    for algorithm in algorithms:
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "design.generate",
            "params": {
                "method": algorithm,
                **base_params,
            },
        }
        
        resp = await handle_request(req)
        assert resp["id"] == 1
        assert "result" in resp
        
        results[algorithm] = {
            "efficiency": resp["result"]["efficiency"],
            "tasks": len(resp["result"]["tasks"]),
        }
    
    # All algorithms should produce the same number of tasks
    task_counts = [results[alg]["tasks"] for alg in algorithms]
    assert all(count == task_counts[0] for count in task_counts)
    
    # D-optimal efficiency can vary, just ensure it's a valid number
    assert 0.0 <= results["doptimal"]["efficiency"] <= 1.0
    assert 0.0 <= results["random"]["efficiency"] <= 1.0


@pytest.mark.asyncio
async def test_health_check_workflow():
    """Test health check functionality."""
    health_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "health",
        "params": {},
    }
    
    resp = await handle_request(health_req)
    assert resp["id"] == 1
    assert "result" in resp
    assert resp["result"]["status"] == "ok"
    assert "version" in resp["result"]
    
    # Test ping as well
    ping_req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "ping",
        "params": {},
    }
    
    resp = await handle_request(ping_req)
    assert resp["id"] == 2
    assert "result" in resp
    assert resp["result"]["status"] == "ok"
