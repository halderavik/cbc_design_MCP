#!/usr/bin/env python3
"""
Performance Monitoring Script for CBC Design Generator MCP Server

This script provides comprehensive performance monitoring capabilities:
- Real-time performance metrics
- Memory usage tracking
- Response time analysis
- Throughput measurement
- Performance regression detection
"""

import json
import psutil
import subprocess
import sys
import time
from collections import deque
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np


class PerformanceMonitor:
    """Performance monitoring for the MCP server."""
    
    def __init__(self, server_command: Optional[List[str]] = None, history_size: int = 1000):
        """
        Initialize the performance monitor.
        
        Args:
            server_command: Command to start the MCP server.
            history_size: Maximum number of metrics to keep in memory.
        """
        self.server_command = server_command or [sys.executable, "-m", "conjoint_mcp.server"]
        self.history_size = history_size
        
        # Performance metrics storage
        self.response_times = deque(maxlen=history_size)
        self.memory_usage = deque(maxlen=history_size)
        self.cpu_usage = deque(maxlen=history_size)
        self.timestamps = deque(maxlen=history_size)
        self.request_types = deque(maxlen=history_size)
        self.success_rates = deque(maxlen=history_size)
        
        # Current session metrics
        self.session_start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # Performance thresholds
        self.response_time_threshold = 5.0  # seconds
        self.memory_threshold = 500 * 1024 * 1024  # 500MB
        self.cpu_threshold = 80.0  # percentage
    
    def run_json_rpc_request(self, request: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        """Send a JSON-RPC request and collect performance metrics."""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        start_cpu = psutil.cpu_percent()
        
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
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            end_cpu = psutil.cpu_percent()
            
            response_time = end_time - start_time
            memory_delta = end_memory - start_memory
            
            # Record metrics
            self.response_times.append(response_time)
            self.memory_usage.append(end_memory)
            self.cpu_usage.append(end_cpu)
            self.timestamps.append(end_time)
            self.request_types.append(request.get("method", "unknown"))
            
            # Determine success
            success = False
            if stdout_data:
                try:
                    response = json.loads(stdout_data.strip().splitlines()[0])
                    success = "error" not in response
                except json.JSONDecodeError:
                    success = False
            
            self.success_rates.append(1.0 if success else 0.0)
            
            # Update session metrics
            self.total_requests += 1
            if success:
                self.successful_requests += 1
            else:
                self.failed_requests += 1
            
            return {
                "success": success,
                "response_time": response_time,
                "memory_usage": end_memory,
                "cpu_usage": end_cpu,
                "stdout": stdout_data,
                "stderr": stderr_data,
            }
            
        except subprocess.TimeoutExpired:
            proc.kill()
            return {
                "success": False,
                "response_time": timeout,
                "memory_usage": psutil.Process().memory_info().rss,
                "cpu_usage": psutil.cpu_percent(),
                "stdout": "",
                "stderr": "Request timeout",
            }
        except Exception as e:
            return {
                "success": False,
                "response_time": time.time() - start_time,
                "memory_usage": psutil.Process().memory_info().rss,
                "cpu_usage": psutil.cpu_percent(),
                "stdout": "",
                "stderr": str(e),
            }
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        if not self.response_times:
            return {}
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (self.successful_requests / self.total_requests) * 100 if self.total_requests > 0 else 0,
            "avg_response_time": np.mean(self.response_times),
            "max_response_time": np.max(self.response_times),
            "min_response_time": np.min(self.response_times),
            "current_memory_usage": self.memory_usage[-1] if self.memory_usage else 0,
            "avg_memory_usage": np.mean(self.memory_usage),
            "current_cpu_usage": self.cpu_usage[-1] if self.cpu_usage else 0,
            "avg_cpu_usage": np.mean(self.cpu_usage),
            "session_duration": time.time() - self.session_start_time,
        }
    
    def check_performance_alerts(self) -> List[str]:
        """Check for performance issues and return alerts."""
        alerts = []
        
        if not self.response_times:
            return alerts
        
        # Response time alerts
        recent_response_times = list(self.response_times)[-10:]  # Last 10 requests
        if recent_response_times and np.mean(recent_response_times) > self.response_time_threshold:
            alerts.append(f"High response time: {np.mean(recent_response_times):.2f}s (threshold: {self.response_time_threshold}s)")
        
        # Memory usage alerts
        if self.memory_usage and self.memory_usage[-1] > self.memory_threshold:
            memory_mb = self.memory_usage[-1] / (1024 * 1024)
            threshold_mb = self.memory_threshold / (1024 * 1024)
            alerts.append(f"High memory usage: {memory_mb:.1f}MB (threshold: {threshold_mb:.1f}MB)")
        
        # CPU usage alerts
        if self.cpu_usage and self.cpu_usage[-1] > self.cpu_threshold:
            alerts.append(f"High CPU usage: {self.cpu_usage[-1]:.1f}% (threshold: {self.cpu_threshold}%)")
        
        # Success rate alerts
        recent_success_rates = list(self.success_rates)[-20:]  # Last 20 requests
        if recent_success_rates and np.mean(recent_success_rates) < 0.9:
            success_rate = np.mean(recent_success_rates) * 100
            alerts.append(f"Low success rate: {success_rate:.1f}% (threshold: 90%)")
        
        return alerts
    
    def run_load_test(self, num_requests: int = 100, request_interval: float = 0.1) -> Dict[str, Any]:
        """Run a load test with specified parameters."""
        print(f"Starting load test: {num_requests} requests with {request_interval}s interval...")
        
        # Test request
        test_request = {
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
        
        start_time = time.time()
        results = []
        
        for i in range(num_requests):
            print(f"Request {i+1}/{num_requests}", end="\r")
            
            result = self.run_json_rpc_request(test_request)
            results.append(result)
            
            if request_interval > 0:
                time.sleep(request_interval)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Analyze results
        successful_requests = sum(1 for r in results if r["success"])
        failed_requests = num_requests - successful_requests
        response_times = [r["response_time"] for r in results]
        
        load_test_results = {
            "total_requests": num_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / num_requests) * 100,
            "total_duration": total_duration,
            "requests_per_second": num_requests / total_duration,
            "avg_response_time": np.mean(response_times),
            "min_response_time": np.min(response_times),
            "max_response_time": np.max(response_times),
            "p95_response_time": np.percentile(response_times, 95),
            "p99_response_time": np.percentile(response_times, 99),
        }
        
        print(f"\nLoad test completed!")
        print(f"Success rate: {load_test_results['success_rate']:.1f}%")
        print(f"Requests per second: {load_test_results['requests_per_second']:.2f}")
        print(f"Average response time: {load_test_results['avg_response_time']:.3f}s")
        print(f"95th percentile response time: {load_test_results['p95_response_time']:.3f}s")
        
        return load_test_results
    
    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report."""
        metrics = self.get_current_metrics()
        
        if not metrics:
            return "No performance data available."
        
        report = []
        report.append("=" * 60)
        report.append("PERFORMANCE REPORT")
        report.append("=" * 60)
        report.append(f"Session Duration: {metrics['session_duration']:.1f}s")
        report.append(f"Total Requests: {metrics['total_requests']}")
        report.append(f"Successful Requests: {metrics['successful_requests']}")
        report.append(f"Failed Requests: {metrics['failed_requests']}")
        report.append(f"Success Rate: {metrics['success_rate']:.1f}%")
        report.append("")
        report.append("Response Time Metrics:")
        report.append(f"  Average: {metrics['avg_response_time']:.3f}s")
        report.append(f"  Minimum: {metrics['min_response_time']:.3f}s")
        report.append(f"  Maximum: {metrics['max_response_time']:.3f}s")
        report.append("")
        report.append("Resource Usage:")
        report.append(f"  Current Memory: {metrics['current_memory_usage'] / (1024*1024):.1f}MB")
        report.append(f"  Average Memory: {metrics['avg_memory_usage'] / (1024*1024):.1f}MB")
        report.append(f"  Current CPU: {metrics['current_cpu_usage']:.1f}%")
        report.append(f"  Average CPU: {metrics['avg_cpu_usage']:.1f}%")
        
        # Performance alerts
        alerts = self.check_performance_alerts()
        if alerts:
            report.append("")
            report.append("PERFORMANCE ALERTS:")
            for alert in alerts:
                report.append(f"  ⚠️  {alert}")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def plot_performance_metrics(self, save_path: Optional[str] = None):
        """Plot performance metrics over time."""
        if not self.timestamps:
            print("No performance data to plot.")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Convert timestamps to relative time
        start_time = self.timestamps[0]
        relative_times = [(t - start_time) for t in self.timestamps]
        
        # Response times
        ax1.plot(relative_times, self.response_times, 'b-', alpha=0.7)
        ax1.axhline(y=self.response_time_threshold, color='r', linestyle='--', label=f'Threshold ({self.response_time_threshold}s)')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Response Time (s)')
        ax1.set_title('Response Time Over Time')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Memory usage
        memory_mb = [m / (1024*1024) for m in self.memory_usage]
        ax2.plot(relative_times, memory_mb, 'g-', alpha=0.7)
        ax2.axhline(y=self.memory_threshold / (1024*1024), color='r', linestyle='--', label=f'Threshold ({self.memory_threshold/(1024*1024):.0f}MB)')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Memory Usage (MB)')
        ax2.set_title('Memory Usage Over Time')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # CPU usage
        ax3.plot(relative_times, self.cpu_usage, 'orange', alpha=0.7)
        ax3.axhline(y=self.cpu_threshold, color='r', linestyle='--', label=f'Threshold ({self.cpu_threshold}%)')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('CPU Usage (%)')
        ax3.set_title('CPU Usage Over Time')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Success rate (rolling average)
        window_size = min(20, len(self.success_rates))
        if window_size > 1:
            rolling_success = []
            for i in range(len(self.success_rates)):
                start_idx = max(0, i - window_size + 1)
                window_data = list(self.success_rates)[start_idx:i+1]
                rolling_success.append(np.mean(window_data) * 100)
            
            ax4.plot(relative_times, rolling_success, 'purple', alpha=0.7)
            ax4.axhline(y=90, color='r', linestyle='--', label='Threshold (90%)')
            ax4.set_xlabel('Time (s)')
            ax4.set_ylabel('Success Rate (%)')
            ax4.set_title('Success Rate Over Time (Rolling Average)')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Performance plot saved to {save_path}")
        else:
            plt.show()
    
    def run_continuous_monitoring(self, duration: int = 300, interval: float = 1.0):
        """Run continuous performance monitoring."""
        print(f"Starting continuous monitoring for {duration} seconds...")
        print("Press Ctrl+C to stop early.")
        
        end_time = time.time() + duration
        
        try:
            while time.time() < end_time:
                # Run a test request
                test_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "health",
                    "params": {},
                }
                
                self.run_json_rpc_request(test_request)
                
                # Check for alerts
                alerts = self.check_performance_alerts()
                if alerts:
                    print(f"\n⚠️  Performance Alerts:")
                    for alert in alerts:
                        print(f"   {alert}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
        
        print("\nContinuous monitoring completed.")
        print(self.generate_performance_report())


def main():
    """Main entry point for the performance monitor."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Performance Monitor for CBC Design Generator MCP Server")
    parser.add_argument("--server-command", nargs="+", help="Command to start the MCP server")
    parser.add_argument("--load-test", type=int, help="Run load test with specified number of requests")
    parser.add_argument("--monitor", type=int, help="Run continuous monitoring for specified duration (seconds)")
    parser.add_argument("--report", action="store_true", help="Generate performance report")
    parser.add_argument("--plot", help="Generate performance plot and save to specified file")
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor(args.server_command)
    
    if args.load_test:
        monitor.run_load_test(args.load_test)
    elif args.monitor:
        monitor.run_continuous_monitoring(args.monitor)
    elif args.report:
        print(monitor.generate_performance_report())
    elif args.plot:
        monitor.plot_performance_metrics(args.plot)
    else:
        # Interactive mode
        print("Performance Monitor - Interactive Mode")
        print("1. Run load test")
        print("2. Run continuous monitoring")
        print("3. Generate report")
        print("4. Generate plot")
        
        choice = input("Select option (1-4): ").strip()
        
        if choice == "1":
            num_requests = int(input("Number of requests: ") or "100")
            monitor.run_load_test(num_requests)
        elif choice == "2":
            duration = int(input("Duration in seconds: ") or "300")
            monitor.run_continuous_monitoring(duration)
        elif choice == "3":
            print(monitor.generate_performance_report())
        elif choice == "4":
            filename = input("Output filename (e.g., performance.png): ") or "performance.png"
            monitor.plot_performance_metrics(filename)


if __name__ == "__main__":
    main()
