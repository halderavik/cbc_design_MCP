#!/usr/bin/env python3
"""
Local Testing Suite for CBC Design Generator MCP Server

This script provides comprehensive local testing capabilities including:
- Design generation testing
- Parameter optimization testing
- Export functionality testing
- Performance benchmarking
- Error handling validation
"""

import asyncio
import json
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

import requests


class LocalTestSuite:
    """Comprehensive local testing suite for the MCP server."""
    
    def __init__(self, server_command: Optional[List[str]] = None):
        """
        Initialize the test suite.
        
        Args:
            server_command: Command to start the MCP server. Defaults to Python module.
        """
        self.server_command = server_command or [sys.executable, "-m", "conjoint_mcp.server"]
        self.test_results = []
        self.performance_metrics = {}
    
    def run_json_rpc_request(self, request: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        """
        Send a JSON-RPC request to the MCP server via stdio.
        
        Args:
            request: JSON-RPC request dictionary.
            timeout: Request timeout in seconds.
            
        Returns:
            Dict containing the response and metadata.
        """
        start_time = time.time()
        
        try:
            line = json.dumps(request) + "\n"
            proc = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            
            stdout_data, stderr_data = proc.communicate(input=line, timeout=timeout)
            duration = time.time() - start_time
            
            if stdout_data:
                response = json.loads(stdout_data.strip().splitlines()[0])
            else:
                response = {"error": "No response received"}
            
            return {
                "request": request,
                "response": response,
                "duration": duration,
                "stderr": stderr_data,
                "success": "error" not in response,
            }
            
        except subprocess.TimeoutExpired:
            proc.kill()
            return {
                "request": request,
                "response": {"error": "Request timeout"},
                "duration": time.time() - start_time,
                "stderr": "",
                "success": False,
            }
        except Exception as e:
            return {
                "request": request,
                "response": {"error": str(e)},
                "duration": time.time() - start_time,
                "stderr": "",
                "success": False,
            }
    
    def test_health_check(self) -> Dict[str, Any]:
        """Test health check functionality."""
        print("Testing health check...")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "health",
            "params": {},
        }
        
        result = self.run_json_rpc_request(request)
        self.test_results.append(result)
        
        if result["success"]:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            print(f"   Error: {result['response']}")
        
        return result
    
    def test_design_generation(self, method: str = "random") -> Dict[str, Any]:
        """Test design generation with specified method."""
        print(f"Testing design generation ({method})...")
        
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "design.generate",
            "params": {
                "method": method,
                "grid": {
                    "attributes": [
                        {"name": "Color", "levels": [{"name": "Red"}, {"name": "Blue"}, {"name": "Green"}]},
                        {"name": "Size", "levels": [{"name": "S"}, {"name": "M"}, {"name": "L"}]},
                        {"name": "Material", "levels": [{"name": "Cotton"}, {"name": "Polyester"}]},
                    ]
                },
                "options_per_screen": 3,
                "num_screens": 8,
            },
        }
        
        result = self.run_json_rpc_request(request)
        self.test_results.append(result)
        
        if result["success"]:
            tasks = result["response"]["result"]["tasks"]
            efficiency = result["response"]["result"]["efficiency"]
            print(f"✅ Design generation ({method}) passed")
            print(f"   Generated {len(tasks)} tasks with efficiency {efficiency:.3f}")
        else:
            print(f"❌ Design generation ({method}) failed")
            print(f"   Error: {result['response']}")
        
        return result
    
    def test_parameter_optimization(self) -> Dict[str, Any]:
        """Test parameter optimization."""
        print("Testing parameter optimization...")
        
        request = {
            "jsonrpc": "2.0",
            "id": 3,
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
                "max_respondents": 500,
            },
        }
        
        result = self.run_json_rpc_request(request)
        self.test_results.append(result)
        
        if result["success"]:
            opt_result = result["response"]["result"]
            print("✅ Parameter optimization passed")
            print(f"   Recommended: {opt_result['num_respondents']} respondents, "
                  f"{opt_result['num_screens']} screens, "
                  f"{opt_result['options_per_screen']} options/screen")
            print(f"   Expected power: {opt_result['expected_power']:.3f}")
        else:
            print("❌ Parameter optimization failed")
            print(f"   Error: {result['response']}")
        
        return result
    
    def test_export_functionality(self, format_type: str = "csv") -> Dict[str, Any]:
        """Test export functionality."""
        print(f"Testing export functionality ({format_type})...")
        
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "design.export",
            "params": {
                "design_request": {
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
                "format": format_type,
                "include_metadata": True,
            },
        }
        
        result = self.run_json_rpc_request(request)
        self.test_results.append(result)
        
        if result["success"]:
            content = result["response"]["result"]["content"]
            summary = result["response"]["result"]["summary"]
            print(f"✅ Export ({format_type}) passed")
            print(f"   Content length: {len(content)} characters")
            print(f"   Summary: {summary['total_tasks']} tasks, {summary['total_options']} options")
        else:
            print(f"❌ Export ({format_type}) failed")
            print(f"   Error: {result['response']}")
        
        return result
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling with invalid requests."""
        print("Testing error handling...")
        
        # Test invalid method
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "invalid.method",
            "params": {},
        }
        
        result = self.run_json_rpc_request(request)
        self.test_results.append(result)
        
        if not result["success"] and "error" in result["response"]:
            print("✅ Error handling passed (invalid method)")
        else:
            print("❌ Error handling failed (invalid method)")
        
        return result
    
    def run_performance_benchmark(self) -> Dict[str, Any]:
        """Run performance benchmark across different algorithms."""
        print("Running performance benchmark...")
        
        algorithms = ["random", "balanced", "orthogonal", "doptimal"]
        benchmark_results = {}
        
        for algorithm in algorithms:
            print(f"  Benchmarking {algorithm}...")
            result = self.test_design_generation(algorithm)
            benchmark_results[algorithm] = {
                "duration": result["duration"],
                "success": result["success"],
            }
        
        self.performance_metrics = benchmark_results
        
        print("\nPerformance Benchmark Results:")
        for algorithm, metrics in benchmark_results.items():
            status = "✅" if metrics["success"] else "❌"
            print(f"  {status} {algorithm}: {metrics['duration']:.3f}s")
        
        return benchmark_results
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test suite."""
        print("=" * 60)
        print("CBC Design Generator MCP Server - Local Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        self.test_health_check()
        print()
        
        self.test_design_generation("random")
        print()
        
        self.test_parameter_optimization()
        print()
        
        self.test_export_functionality("csv")
        print()
        
        self.test_export_functionality("json")
        print()
        
        self.test_error_handling()
        print()
        
        self.run_performance_benchmark()
        print()
        
        total_duration = time.time() - start_time
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Total duration: {total_duration:.3f}s")
        
        if failed_tests > 0:
            print("\nFailed tests:")
            for i, result in enumerate(self.test_results):
                if not result["success"]:
                    method = result["request"].get("method", "unknown")
                    print(f"  {i+1}. {method}: {result['response']}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "total_duration": total_duration,
            "performance_metrics": self.performance_metrics,
        }


def main():
    """Main entry point for the local test suite."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Local Test Suite for CBC Design Generator MCP Server")
    parser.add_argument("--server-command", nargs="+", help="Command to start the MCP server")
    parser.add_argument("--test", choices=["health", "generate", "optimize", "export", "error", "benchmark", "all"], 
                       default="all", help="Specific test to run")
    
    args = parser.parse_args()
    
    test_suite = LocalTestSuite(args.server_command)
    
    if args.test == "all":
        result = test_suite.run_comprehensive_test()
    elif args.test == "health":
        test_suite.test_health_check()
    elif args.test == "generate":
        test_suite.test_design_generation()
    elif args.test == "optimize":
        test_suite.test_parameter_optimization()
    elif args.test == "export":
        test_suite.test_export_functionality()
    elif args.test == "error":
        test_suite.test_error_handling()
    elif args.test == "benchmark":
        test_suite.run_performance_benchmark()
    
    # Exit with appropriate code
    if args.test == "all":
        sys.exit(0 if result["failed_tests"] == 0 else 1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
