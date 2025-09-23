#!/usr/bin/env python3
"""
Interactive Testing Interface for CBC Design Generator MCP Server

This script provides an interactive command-line interface for testing the MCP server:
- Interactive design generation
- Real-time parameter adjustment
- Live export functionality
- Performance monitoring
- Error handling demonstration
"""

import json
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

from sample_scenarios import SampleScenarios


class InteractiveTester:
    """Interactive testing interface for the MCP server."""
    
    def __init__(self):
        """Initialize the interactive tester."""
        self.server_command = [sys.executable, "-m", "conjoint_mcp.server"]
        self.current_scenario = None
        self.session_history = []
    
    def run_json_rpc_request(self, request: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        """Send a JSON-RPC request to the MCP server."""
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
            
            if stdout_data:
                response = json.loads(stdout_data.strip().splitlines()[0])
                return {"success": "error" not in response, "data": response}
            else:
                return {"success": False, "data": {"error": "No response received"}}
                
        except Exception as e:
            return {"success": False, "data": {"error": str(e)}}
    
    def display_menu(self):
        """Display the main menu."""
        print("\n" + "=" * 60)
        print("CBC Design Generator MCP Server - Interactive Tester")
        print("=" * 60)
        print("1. Load sample scenario")
        print("2. Create custom scenario")
        print("3. Generate design")
        print("4. Optimize parameters")
        print("5. Export design")
        print("6. Test health check")
        print("7. View session history")
        print("8. Performance benchmark")
        print("9. Help")
        print("0. Exit")
        print("=" * 60)
    
    def load_sample_scenario(self):
        """Load a sample scenario."""
        print("\nAvailable sample scenarios:")
        scenarios = SampleScenarios.get_all_scenarios()
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"{i}. {scenario['name']}")
            print(f"   {scenario['description']}")
        
        try:
            choice = int(input("\nSelect scenario (1-{}): ".format(len(scenarios))))
            if 1 <= choice <= len(scenarios):
                self.current_scenario = scenarios[choice - 1]
                print(f"\n✅ Loaded scenario: {self.current_scenario['name']}")
                self._display_scenario_info()
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def create_custom_scenario(self):
        """Create a custom scenario interactively."""
        print("\nCreating custom scenario...")
        
        scenario = {
            "name": input("Scenario name: "),
            "description": input("Description: "),
            "grid": {"attributes": []},
            "options_per_screen": 3,
            "num_screens": 10,
        }
        
        # Add attributes
        while True:
            attr_name = input("\nAttribute name (or 'done' to finish): ")
            if attr_name.lower() == 'done':
                break
            
            levels = []
            print(f"Enter levels for '{attr_name}' (one per line, empty line to finish):")
            while True:
                level = input("  Level: ")
                if not level:
                    break
                levels.append({"name": level})
            
            if levels:
                scenario["grid"]["attributes"].append({
                    "name": attr_name,
                    "levels": levels
                })
                print(f"✅ Added attribute '{attr_name}' with {len(levels)} levels")
        
        # Set parameters
        try:
            scenario["options_per_screen"] = int(input(f"\nOptions per screen (default {scenario['options_per_screen']}): ") or scenario["options_per_screen"])
            scenario["num_screens"] = int(input(f"Number of screens (default {scenario['num_screens']}): ") or scenario["num_screens"])
        except ValueError:
            print("❌ Invalid number, using defaults")
        
        self.current_scenario = scenario
        print(f"\n✅ Created custom scenario: {scenario['name']}")
        self._display_scenario_info()
    
    def _display_scenario_info(self):
        """Display current scenario information."""
        if not self.current_scenario:
            return
        
        print(f"\nCurrent Scenario: {self.current_scenario['name']}")
        print(f"Description: {self.current_scenario['description']}")
        print(f"Attributes: {len(self.current_scenario['grid']['attributes'])}")
        for attr in self.current_scenario['grid']['attributes']:
            print(f"  - {attr['name']}: {len(attr['levels'])} levels")
        print(f"Options per screen: {self.current_scenario['options_per_screen']}")
        print(f"Number of screens: {self.current_scenario['num_screens']}")
    
    def generate_design(self):
        """Generate a design using the current scenario."""
        if not self.current_scenario:
            print("❌ No scenario loaded. Please load or create a scenario first.")
            return
        
        print("\nAvailable algorithms:")
        algorithms = ["random", "balanced", "orthogonal", "doptimal"]
        for i, algo in enumerate(algorithms, 1):
            print(f"{i}. {algo}")
        
        try:
            choice = int(input("\nSelect algorithm (1-4): "))
            if 1 <= choice <= 4:
                algorithm = algorithms[choice - 1]
                self._run_design_generation(algorithm)
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def _run_design_generation(self, algorithm: str):
        """Run design generation with specified algorithm."""
        print(f"\n🔄 Generating design using {algorithm} algorithm...")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "design.generate",
            "params": {
                "method": algorithm,
                "grid": self.current_scenario["grid"],
                "options_per_screen": self.current_scenario["options_per_screen"],
                "num_screens": self.current_scenario["num_screens"],
                "constraints": self.current_scenario.get("constraints"),
            },
        }
        
        start_time = time.time()
        result = self.run_json_rpc_request(request)
        duration = time.time() - start_time
        
        self.session_history.append({
            "action": "generate_design",
            "algorithm": algorithm,
            "duration": duration,
            "success": result["success"],
            "timestamp": time.time(),
        })
        
        if result["success"]:
            response_data = result["data"]["result"]
            tasks = response_data["tasks"]
            efficiency = response_data["efficiency"]
            
            print(f"✅ Design generated successfully!")
            print(f"   Algorithm: {algorithm}")
            print(f"   Duration: {duration:.3f}s")
            print(f"   Tasks: {len(tasks)}")
            print(f"   Efficiency: {efficiency:.3f}")
            
            # Show sample tasks
            print(f"\nSample tasks (first 3):")
            for i, task in enumerate(tasks[:3], 1):
                print(f"  Task {task['task_index']}:")
                for j, option in enumerate(task["options"], 1):
                    option_str = ", ".join([f"{k}: {v}" for k, v in option.items()])
                    print(f"    Option {j}: {option_str}")
        else:
            print(f"❌ Design generation failed: {result['data']}")
    
    def optimize_parameters(self):
        """Optimize design parameters."""
        if not self.current_scenario:
            print("❌ No scenario loaded. Please load or create a scenario first.")
            return
        
        print("\n🔄 Optimizing parameters...")
        
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "design.optimize",
            "params": {
                "grid": self.current_scenario["grid"],
                "target_power": 0.8,
                "effect_size": 0.2,
                "alpha": 0.05,
            },
        }
        
        start_time = time.time()
        result = self.run_json_rpc_request(request)
        duration = time.time() - start_time
        
        self.session_history.append({
            "action": "optimize_parameters",
            "duration": duration,
            "success": result["success"],
            "timestamp": time.time(),
        })
        
        if result["success"]:
            opt_result = result["data"]["result"]
            print(f"✅ Parameter optimization completed!")
            print(f"   Duration: {duration:.3f}s")
            print(f"   Recommended respondents: {opt_result['num_respondents']}")
            print(f"   Recommended screens: {opt_result['num_screens']}")
            print(f"   Recommended options per screen: {opt_result['options_per_screen']}")
            print(f"   Expected power: {opt_result['expected_power']:.3f}")
            
            if opt_result.get("notes"):
                print(f"   Notes: {opt_result['notes']}")
        else:
            print(f"❌ Parameter optimization failed: {result['data']}")
    
    def export_design(self):
        """Export the last generated design."""
        if not self.session_history or not any(h["action"] == "generate_design" and h["success"] for h in self.session_history):
            print("❌ No successful design generation found. Please generate a design first.")
            return
        
        print("\nAvailable export formats:")
        formats = ["csv", "json", "qualtrics"]
        for i, fmt in enumerate(formats, 1):
            print(f"{i}. {fmt}")
        
        try:
            choice = int(input("\nSelect format (1-3): "))
            if 1 <= choice <= 3:
                format_type = formats[choice - 1]
                self._run_export(format_type)
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def _run_export(self, format_type: str):
        """Run export with specified format."""
        print(f"\n🔄 Exporting design in {format_type} format...")
        
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "design.export",
            "params": {
                "design_request": {
                    "method": "random",  # This would be from the last generation
                    "grid": self.current_scenario["grid"],
                    "options_per_screen": self.current_scenario["options_per_screen"],
                    "num_screens": self.current_scenario["num_screens"],
                },
                "format": format_type,
                "include_metadata": True,
            },
        }
        
        start_time = time.time()
        result = self.run_json_rpc_request(request)
        duration = time.time() - start_time
        
        self.session_history.append({
            "action": "export_design",
            "format": format_type,
            "duration": duration,
            "success": result["success"],
            "timestamp": time.time(),
        })
        
        if result["success"]:
            export_result = result["data"]["result"]
            content = export_result["content"]
            summary = export_result["summary"]
            
            print(f"✅ Export completed!")
            print(f"   Format: {format_type}")
            print(f"   Duration: {duration:.3f}s")
            print(f"   Content length: {len(content)} characters")
            print(f"   Summary: {summary['total_tasks']} tasks, {summary['total_options']} options")
            
            # Save to file
            filename = f"export_{int(time.time())}.{format_type}"
            with open(filename, 'w') as f:
                f.write(content)
            print(f"   Saved to: {filename}")
        else:
            print(f"❌ Export failed: {result['data']}")
    
    def test_health_check(self):
        """Test health check functionality."""
        print("\n🔄 Testing health check...")
        
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "health",
            "params": {},
        }
        
        start_time = time.time()
        result = self.run_json_rpc_request(request)
        duration = time.time() - start_time
        
        self.session_history.append({
            "action": "health_check",
            "duration": duration,
            "success": result["success"],
            "timestamp": time.time(),
        })
        
        if result["success"]:
            health_data = result["data"]["result"]
            print(f"✅ Health check passed!")
            print(f"   Duration: {duration:.3f}s")
            print(f"   Status: {health_data['status']}")
            print(f"   Version: {health_data.get('version', 'unknown')}")
        else:
            print(f"❌ Health check failed: {result['data']}")
    
    def view_session_history(self):
        """View session history."""
        if not self.session_history:
            print("❌ No session history available.")
            return
        
        print(f"\nSession History ({len(self.session_history)} actions):")
        print("-" * 60)
        
        for i, entry in enumerate(self.session_history, 1):
            status = "✅" if entry["success"] else "❌"
            timestamp = time.strftime("%H:%M:%S", time.localtime(entry["timestamp"]))
            
            if entry["action"] == "generate_design":
                print(f"{i}. {status} {timestamp} - Generate design ({entry['algorithm']}) - {entry['duration']:.3f}s")
            elif entry["action"] == "optimize_parameters":
                print(f"{i}. {status} {timestamp} - Optimize parameters - {entry['duration']:.3f}s")
            elif entry["action"] == "export_design":
                print(f"{i}. {status} {timestamp} - Export design ({entry['format']}) - {entry['duration']:.3f}s")
            elif entry["action"] == "health_check":
                print(f"{i}. {status} {timestamp} - Health check - {entry['duration']:.3f}s")
    
    def performance_benchmark(self):
        """Run performance benchmark."""
        if not self.current_scenario:
            print("❌ No scenario loaded. Please load or create a scenario first.")
            return
        
        print("\n🔄 Running performance benchmark...")
        
        algorithms = ["random", "balanced", "orthogonal", "doptimal"]
        results = {}
        
        for algorithm in algorithms:
            print(f"  Testing {algorithm}...")
            
            request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "design.generate",
                "params": {
                    "method": algorithm,
                    "grid": self.current_scenario["grid"],
                    "options_per_screen": self.current_scenario["options_per_screen"],
                    "num_screens": self.current_scenario["num_screens"],
                },
            }
            
            start_time = time.time()
            result = self.run_json_rpc_request(request)
            duration = time.time() - start_time
            
            results[algorithm] = {
                "success": result["success"],
                "duration": duration,
            }
        
        print(f"\nPerformance Benchmark Results:")
        print("-" * 40)
        for algorithm, metrics in results.items():
            status = "✅" if metrics["success"] else "❌"
            print(f"{status} {algorithm}: {metrics['duration']:.3f}s")
    
    def show_help(self):
        """Show help information."""
        print("\n" + "=" * 60)
        print("HELP - Interactive Tester")
        print("=" * 60)
        print("This interactive tester allows you to:")
        print("1. Load pre-defined sample scenarios or create custom ones")
        print("2. Generate designs using different algorithms")
        print("3. Optimize design parameters for statistical power")
        print("4. Export designs in multiple formats")
        print("5. Monitor performance and view session history")
        print("\nTips:")
        print("- Start by loading a sample scenario (option 1)")
        print("- Generate a design (option 3) before exporting (option 5)")
        print("- Use the session history (option 7) to track your actions")
        print("- Run benchmarks (option 8) to compare algorithm performance")
        print("=" * 60)
    
    def run(self):
        """Run the interactive tester."""
        print("Welcome to the CBC Design Generator Interactive Tester!")
        
        while True:
            self.display_menu()
            
            try:
                choice = input("\nEnter your choice (0-9): ").strip()
                
                if choice == "0":
                    print("Goodbye!")
                    break
                elif choice == "1":
                    self.load_sample_scenario()
                elif choice == "2":
                    self.create_custom_scenario()
                elif choice == "3":
                    self.generate_design()
                elif choice == "4":
                    self.optimize_parameters()
                elif choice == "5":
                    self.export_design()
                elif choice == "6":
                    self.test_health_check()
                elif choice == "7":
                    self.view_session_history()
                elif choice == "8":
                    self.performance_benchmark()
                elif choice == "9":
                    self.show_help()
                else:
                    print("❌ Invalid choice. Please enter 0-9.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                input("Press Enter to continue...")


def main():
    """Main entry point for the interactive tester."""
    tester = InteractiveTester()
    tester.run()


if __name__ == "__main__":
    main()
