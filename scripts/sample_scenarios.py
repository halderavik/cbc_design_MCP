#!/usr/bin/env python3
"""
Sample Design Scenarios for CBC Design Generator MCP Server

This script provides pre-defined design scenarios for testing and demonstration:
- Product design scenarios (clothing, electronics, food)
- Service design scenarios (travel, healthcare, education)
- Complex multi-attribute scenarios
- Constraint-based scenarios
"""

import json
from typing import Dict, List, Any


class SampleScenarios:
    """Collection of sample design scenarios for testing and demonstration."""
    
    @staticmethod
    def get_clothing_scenario() -> Dict[str, Any]:
        """Get clothing product design scenario."""
        return {
            "name": "Clothing Product Design",
            "description": "Design for a new clothing line with color, size, material, and price attributes",
            "grid": {
                "attributes": [
                    {
                        "name": "Color",
                        "levels": [
                            {"name": "Black"},
                            {"name": "White"},
                            {"name": "Blue"},
                            {"name": "Red"},
                        ]
                    },
                    {
                        "name": "Size",
                        "levels": [
                            {"name": "XS"},
                            {"name": "S"},
                            {"name": "M"},
                            {"name": "L"},
                            {"name": "XL"},
                        ]
                    },
                    {
                        "name": "Material",
                        "levels": [
                            {"name": "Cotton"},
                            {"name": "Polyester"},
                            {"name": "Wool"},
                            {"name": "Silk"},
                        ]
                    },
                    {
                        "name": "Price",
                        "levels": [
                            {"name": "$29"},
                            {"name": "$49"},
                            {"name": "$79"},
                            {"name": "$99"},
                        ]
                    },
                ]
            },
            "options_per_screen": 4,
            "num_screens": 12,
            "constraints": {
                "prohibited_combinations": [
                    {
                        "attributes": {"Material": "Silk", "Price": "$29"},
                        "reason": "Silk cannot be sold at low price point"
                    }
                ]
            }
        }
    
    @staticmethod
    def get_electronics_scenario() -> Dict[str, Any]:
        """Get electronics product design scenario."""
        return {
            "name": "Electronics Product Design",
            "description": "Design for a new smartphone with brand, storage, camera, and price attributes",
            "grid": {
                "attributes": [
                    {
                        "name": "Brand",
                        "levels": [
                            {"name": "TechCorp"},
                            {"name": "MobileMax"},
                            {"name": "SmartPhone Inc"},
                        ]
                    },
                    {
                        "name": "Storage",
                        "levels": [
                            {"name": "64GB"},
                            {"name": "128GB"},
                            {"name": "256GB"},
                            {"name": "512GB"},
                        ]
                    },
                    {
                        "name": "Camera",
                        "levels": [
                            {"name": "12MP"},
                            {"name": "24MP"},
                            {"name": "48MP"},
                            {"name": "108MP"},
                        ]
                    },
                    {
                        "name": "Price",
                        "levels": [
                            {"name": "$299"},
                            {"name": "$499"},
                            {"name": "$699"},
                            {"name": "$999"},
                        ]
                    },
                ]
            },
            "options_per_screen": 3,
            "num_screens": 15,
            "constraints": {
                "required_combinations": [
                    {
                        "attributes": {"Brand": "TechCorp", "Storage": "512GB"},
                        "reason": "TechCorp premium model must be available"
                    }
                ]
            }
        }
    
    @staticmethod
    def get_food_delivery_scenario() -> Dict[str, Any]:
        """Get food delivery service design scenario."""
        return {
            "name": "Food Delivery Service Design",
            "description": "Design for food delivery service with cuisine, delivery time, price, and rating attributes",
            "grid": {
                "attributes": [
                    {
                        "name": "Cuisine",
                        "levels": [
                            {"name": "Italian"},
                            {"name": "Chinese"},
                            {"name": "Mexican"},
                            {"name": "Indian"},
                            {"name": "American"},
                        ]
                    },
                    {
                        "name": "Delivery Time",
                        "levels": [
                            {"name": "15 min"},
                            {"name": "30 min"},
                            {"name": "45 min"},
                            {"name": "60 min"},
                        ]
                    },
                    {
                        "name": "Price Range",
                        "levels": [
                            {"name": "$10-15"},
                            {"name": "$15-25"},
                            {"name": "$25-35"},
                            {"name": "$35-50"},
                        ]
                    },
                    {
                        "name": "Rating",
                        "levels": [
                            {"name": "4.0 stars"},
                            {"name": "4.3 stars"},
                            {"name": "4.6 stars"},
                            {"name": "4.9 stars"},
                        ]
                    },
                ]
            },
            "options_per_screen": 4,
            "num_screens": 10,
        }
    
    @staticmethod
    def get_travel_scenario() -> Dict[str, Any]:
        """Get travel package design scenario."""
        return {
            "name": "Travel Package Design",
            "description": "Design for vacation packages with destination, duration, accommodation, and price attributes",
            "grid": {
                "attributes": [
                    {
                        "name": "Destination",
                        "levels": [
                            {"name": "Paris"},
                            {"name": "Tokyo"},
                            {"name": "New York"},
                            {"name": "Sydney"},
                            {"name": "Dubai"},
                        ]
                    },
                    {
                        "name": "Duration",
                        "levels": [
                            {"name": "3 days"},
                            {"name": "5 days"},
                            {"name": "7 days"},
                            {"name": "10 days"},
                        ]
                    },
                    {
                        "name": "Accommodation",
                        "levels": [
                            {"name": "3-star hotel"},
                            {"name": "4-star hotel"},
                            {"name": "5-star hotel"},
                            {"name": "Luxury resort"},
                        ]
                    },
                    {
                        "name": "Price",
                        "levels": [
                            {"name": "$800"},
                            {"name": "$1200"},
                            {"name": "$1800"},
                            {"name": "$2500"},
                        ]
                    },
                ]
            },
            "options_per_screen": 3,
            "num_screens": 12,
            "constraints": {
                "prohibited_combinations": [
                    {
                        "attributes": {"Accommodation": "Luxury resort", "Price": "$800"},
                        "reason": "Luxury resort cannot be offered at budget price"
                    }
                ]
            }
        }
    
    @staticmethod
    def get_healthcare_scenario() -> Dict[str, Any]:
        """Get healthcare service design scenario."""
        return {
            "name": "Healthcare Service Design",
            "description": "Design for healthcare service with provider type, appointment time, location, and cost attributes",
            "grid": {
                "attributes": [
                    {
                        "name": "Provider Type",
                        "levels": [
                            {"name": "General Practitioner"},
                            {"name": "Specialist"},
                            {"name": "Nurse Practitioner"},
                            {"name": "Telemedicine"},
                        ]
                    },
                    {
                        "name": "Appointment Time",
                        "levels": [
                            {"name": "Same day"},
                            {"name": "Next day"},
                            {"name": "Within 3 days"},
                            {"name": "Within 1 week"},
                        ]
                    },
                    {
                        "name": "Location",
                        "levels": [
                            {"name": "Downtown clinic"},
                            {"name": "Suburban office"},
                            {"name": "Hospital"},
                            {"name": "Virtual visit"},
                        ]
                    },
                    {
                        "name": "Cost",
                        "levels": [
                            {"name": "$50"},
                            {"name": "$100"},
                            {"name": "$150"},
                            {"name": "$200"},
                        ]
                    },
                ]
            },
            "options_per_screen": 4,
            "num_screens": 8,
        }
    
    @staticmethod
    def get_complex_scenario() -> Dict[str, Any]:
        """Get complex multi-attribute scenario for advanced testing."""
        return {
            "name": "Complex Multi-Attribute Design",
            "description": "Complex scenario with many attributes and levels for stress testing",
            "grid": {
                "attributes": [
                    {
                        "name": "Category",
                        "levels": [
                            {"name": "Premium"},
                            {"name": "Standard"},
                            {"name": "Budget"},
                        ]
                    },
                    {
                        "name": "Feature A",
                        "levels": [
                            {"name": "Basic"},
                            {"name": "Advanced"},
                            {"name": "Professional"},
                        ]
                    },
                    {
                        "name": "Feature B",
                        "levels": [
                            {"name": "Standard"},
                            {"name": "Enhanced"},
                            {"name": "Premium"},
                        ]
                    },
                    {
                        "name": "Feature C",
                        "levels": [
                            {"name": "Included"},
                            {"name": "Optional"},
                            {"name": "Not Available"},
                        ]
                    },
                    {
                        "name": "Support",
                        "levels": [
                            {"name": "Email"},
                            {"name": "Phone"},
                            {"name": "24/7"},
                        ]
                    },
                    {
                        "name": "Price",
                        "levels": [
                            {"name": "$99"},
                            {"name": "$199"},
                            {"name": "$299"},
                            {"name": "$399"},
                        ]
                    },
                ]
            },
            "options_per_screen": 4,
            "num_screens": 20,
            "constraints": {
                "prohibited_combinations": [
                    {
                        "attributes": {"Category": "Budget", "Support": "24/7"},
                        "reason": "Budget category cannot include 24/7 support"
                    },
                    {
                        "attributes": {"Category": "Premium", "Feature C": "Not Available"},
                        "reason": "Premium category must have all features available"
                    }
                ],
                "required_combinations": [
                    {
                        "attributes": {"Category": "Premium", "Support": "24/7"},
                        "reason": "Premium category must include 24/7 support"
                    }
                ]
            }
        }
    
    @staticmethod
    def get_all_scenarios() -> List[Dict[str, Any]]:
        """Get all available scenarios."""
        return [
            SampleScenarios.get_clothing_scenario(),
            SampleScenarios.get_electronics_scenario(),
            SampleScenarios.get_food_delivery_scenario(),
            SampleScenarios.get_travel_scenario(),
            SampleScenarios.get_healthcare_scenario(),
            SampleScenarios.get_complex_scenario(),
        ]
    
    @staticmethod
    def save_scenario_to_file(scenario: Dict[str, Any], filename: str) -> None:
        """Save a scenario to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(scenario, f, indent=2)
    
    @staticmethod
    def load_scenario_from_file(filename: str) -> Dict[str, Any]:
        """Load a scenario from a JSON file."""
        with open(filename, 'r') as f:
            return json.load(f)


def main():
    """Main entry point for scenario management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sample Design Scenarios for CBC Design Generator")
    parser.add_argument("--list", action="store_true", help="List all available scenarios")
    parser.add_argument("--scenario", choices=[
        "clothing", "electronics", "food", "travel", "healthcare", "complex"
    ], help="Get specific scenario")
    parser.add_argument("--save", help="Save scenario to file")
    parser.add_argument("--load", help="Load scenario from file")
    
    args = parser.parse_args()
    
    if args.list:
        scenarios = SampleScenarios.get_all_scenarios()
        print("Available scenarios:")
        for i, scenario in enumerate(scenarios, 1):
            print(f"{i}. {scenario['name']}")
            print(f"   {scenario['description']}")
            print()
    
    elif args.scenario:
        scenario_map = {
            "clothing": SampleScenarios.get_clothing_scenario(),
            "electronics": SampleScenarios.get_electronics_scenario(),
            "food": SampleScenarios.get_food_delivery_scenario(),
            "travel": SampleScenarios.get_travel_scenario(),
            "healthcare": SampleScenarios.get_healthcare_scenario(),
            "complex": SampleScenarios.get_complex_scenario(),
        }
        
        scenario = scenario_map[args.scenario]
        print(json.dumps(scenario, indent=2))
        
        if args.save:
            SampleScenarios.save_scenario_to_file(scenario, args.save)
            print(f"Scenario saved to {args.save}")
    
    elif args.load:
        scenario = SampleScenarios.load_scenario_from_file(args.load)
        print(json.dumps(scenario, indent=2))


if __name__ == "__main__":
    main()
