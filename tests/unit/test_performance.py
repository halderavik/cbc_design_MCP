import time
import pytest
from conjoint_mcp.algorithms.random import generate_random_design
from conjoint_mcp.algorithms.balanced import generate_balanced_overlap_design
from conjoint_mcp.algorithms.orthogonal import generate_orthogonal_array_design
from conjoint_mcp.algorithms.doptimal import generate_doptimal_design
from conjoint_mcp.models.requests import DesignGrid, Attribute, AttributeLevel


def create_large_test_grid() -> DesignGrid:
    """Create a larger test design grid for performance testing."""
    return DesignGrid(
        attributes=[
            Attribute(
                name="Color",
                levels=[
                    AttributeLevel(name="Red"),
                    AttributeLevel(name="Blue"),
                    AttributeLevel(name="Green"),
                    AttributeLevel(name="Yellow"),
                    AttributeLevel(name="Purple"),
                ]
            ),
            Attribute(
                name="Size",
                levels=[
                    AttributeLevel(name="XS"),
                    AttributeLevel(name="S"),
                    AttributeLevel(name="M"),
                    AttributeLevel(name="L"),
                    AttributeLevel(name="XL"),
                ]
            ),
            Attribute(
                name="Material",
                levels=[
                    AttributeLevel(name="Cotton"),
                    AttributeLevel(name="Polyester"),
                    AttributeLevel(name="Wool"),
                ]
            ),
        ]
    )


def measure_execution_time(func, *args, **kwargs):
    """Measure execution time of a function."""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time


def test_random_design_performance():
    """Test random design generation performance."""
    grid = create_large_test_grid()
    
    # Test with moderate size
    design, duration = measure_execution_time(
        generate_random_design, grid, options_per_screen=4, num_screens=20
    )
    
    assert len(design) == 20
    assert duration < 1.0  # Should complete within 1 second


def test_balanced_overlap_design_performance():
    """Test balanced overlap design generation performance."""
    grid = create_large_test_grid()
    
    design, duration = measure_execution_time(
        generate_balanced_overlap_design, grid, options_per_screen=4, num_screens=20
    )
    
    assert len(design) == 20
    assert duration < 2.0  # Should complete within 2 seconds


def test_orthogonal_array_design_performance():
    """Test orthogonal array design generation performance."""
    grid = create_large_test_grid()
    
    design, duration = measure_execution_time(
        generate_orthogonal_array_design, grid, options_per_screen=4, num_screens=20
    )
    
    assert len(design) == 20
    assert duration < 2.0  # Should complete within 2 seconds


def test_doptimal_design_performance():
    """Test D-optimal design generation performance."""
    grid = create_large_test_grid()
    
    design, duration = measure_execution_time(
        generate_doptimal_design, grid, num_screens=20, options_per_screen=4
    )
    
    assert len(design) == 20
    assert duration < 10.0  # D-optimal can take longer due to optimization


def test_algorithm_scalability():
    """Test how algorithms scale with design size."""
    grid = create_large_test_grid()
    
    # Test different sizes
    sizes = [(5, 3), (10, 4), (15, 5)]
    
    for num_screens, options_per_screen in sizes:
        # Random design should scale linearly
        design, duration = measure_execution_time(
            generate_random_design, grid, options_per_screen, num_screens
        )
        assert len(design) == num_screens
        assert duration < 2.0  # Should remain fast
        
        # D-optimal should scale but may take longer
        design, duration = measure_execution_time(
            generate_doptimal_design, grid, num_screens, options_per_screen
        )
        assert len(design) == num_screens
        assert duration < 15.0  # Allow more time for larger designs


def test_memory_usage():
    """Test memory usage with larger designs."""
    grid = create_large_test_grid()
    
    # Generate a reasonably large design
    design = generate_random_design(grid, options_per_screen=5, num_screens=50)
    
    # Check that we can generate the design without memory issues
    assert len(design) == 50
    total_options = sum(len(task["options"]) for task in design)
    assert total_options == 250  # 50 screens * 5 options each
    
    # Verify all options are properly structured
    for task in design:
        for option in task["options"]:
            assert "Color" in option
            assert "Size" in option
            assert "Material" in option


def test_concurrent_design_generation():
    """Test that multiple designs can be generated concurrently."""
    import concurrent.futures
    
    grid = create_large_test_grid()
    
    def generate_design():
        return generate_random_design(grid, options_per_screen=3, num_screens=10)
    
    # Generate multiple designs concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(generate_design) for _ in range(3)]
        designs = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    # All designs should be valid
    assert len(designs) == 3
    for design in designs:
        assert len(design) == 10
        for task in design:
            assert len(task["options"]) == 3


def test_algorithm_consistency():
    """Test that algorithms produce consistent results with same parameters."""
    grid = create_large_test_grid()
    
    # Test random design (should be different each time)
    design1 = generate_random_design(grid, options_per_screen=3, num_screens=5)
    design2 = generate_random_design(grid, options_per_screen=3, num_screens=5)
    
    # Random designs should be different
    assert design1 != design2
    
    # But both should have same structure
    assert len(design1) == len(design2)
    for i in range(len(design1)):
        assert len(design1[i]["options"]) == len(design2[i]["options"])
