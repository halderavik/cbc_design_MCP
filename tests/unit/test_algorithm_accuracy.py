import pytest
from conjoint_mcp.algorithms.random import generate_random_design
from conjoint_mcp.algorithms.balanced import generate_balanced_overlap_design
from conjoint_mcp.algorithms.orthogonal import generate_orthogonal_array_design
from conjoint_mcp.algorithms.doptimal import generate_doptimal_design
from conjoint_mcp.models.requests import DesignGrid, Attribute, AttributeLevel


def create_test_grid() -> DesignGrid:
    """Create a test design grid."""
    return DesignGrid(
        attributes=[
            Attribute(
                name="Color",
                levels=[
                    AttributeLevel(name="Red"),
                    AttributeLevel(name="Blue"),
                    AttributeLevel(name="Green"),
                ]
            ),
            Attribute(
                name="Size",
                levels=[
                    AttributeLevel(name="S"),
                    AttributeLevel(name="M"),
                    AttributeLevel(name="L"),
                ]
            ),
        ]
    )


def test_random_design_accuracy():
    """Test random design generation accuracy."""
    grid = create_test_grid()
    design = generate_random_design(grid, options_per_screen=3, num_screens=5)
    
    # Check structure
    assert len(design) == 5
    for task in design:
        assert "task_index" in task
        assert "options" in task
        assert len(task["options"]) == 3
        
        # Check each option has all attributes
        for option in task["options"]:
            assert "Color" in option
            assert "Size" in option
            assert option["Color"] in ["Red", "Blue", "Green"]
            assert option["Size"] in ["S", "M", "L"]


def test_balanced_overlap_design_accuracy():
    """Test balanced overlap design generation accuracy."""
    grid = create_test_grid()
    design = generate_balanced_overlap_design(grid, options_per_screen=3, num_screens=5)
    
    # Check structure
    assert len(design) == 5
    for task in design:
        assert "task_index" in task
        assert "options" in task
        assert len(task["options"]) == 3
        
        # Check each option has all attributes
        for option in task["options"]:
            assert "Color" in option
            assert "Size" in option
            assert option["Color"] in ["Red", "Blue", "Green"]
            assert option["Size"] in ["S", "M", "L"]


def test_orthogonal_array_design_accuracy():
    """Test orthogonal array design generation accuracy."""
    grid = create_test_grid()
    design = generate_orthogonal_array_design(grid, options_per_screen=3, num_screens=5)
    
    # Check structure
    assert len(design) == 5
    for task in design:
        assert "task_index" in task
        assert "options" in task
        assert len(task["options"]) == 3
        
        # Check each option has all attributes
        for option in task["options"]:
            assert "Color" in option
            assert "Size" in option
            assert option["Color"] in ["Red", "Blue", "Green"]
            assert option["Size"] in ["S", "M", "L"]


def test_doptimal_design_accuracy():
    """Test D-optimal design generation accuracy."""
    grid = create_test_grid()
    design = generate_doptimal_design(grid, num_screens=5, options_per_screen=3)
    
    # Check structure
    assert len(design) == 5
    for task in design:
        assert "task_index" in task
        assert "options" in task
        assert len(task["options"]) == 3
        
        # Check each option has all attributes
        for option in task["options"]:
            assert "Color" in option
            assert "Size" in option
            assert option["Color"] in ["Red", "Blue", "Green"]
            assert option["Size"] in ["S", "M", "L"]


def test_design_uniqueness():
    """Test that designs are not identical across runs."""
    grid = create_test_grid()
    
    # Generate multiple designs
    designs = []
    for _ in range(3):
        design = generate_random_design(grid, options_per_screen=2, num_screens=3)
        designs.append(design)
    
    # Check that at least some tasks differ
    all_identical = True
    for i in range(len(designs[0])):
        for j in range(i + 1, len(designs)):
            if designs[0][i] != designs[j][i]:
                all_identical = False
                break
        if not all_identical:
            break
    
    # It's very unlikely all designs would be identical
    assert not all_identical


def test_design_completeness():
    """Test that designs include all required attributes and levels."""
    grid = create_test_grid()
    design = generate_random_design(grid, options_per_screen=3, num_screens=10)
    
    # Collect all attribute values used
    colors_used = set()
    sizes_used = set()
    
    for task in design:
        for option in task["options"]:
            colors_used.add(option["Color"])
            sizes_used.add(option["Size"])
    
    # With enough screens, we should see all levels
    assert len(colors_used) >= 2  # At least 2 colors should appear
    assert len(sizes_used) >= 2   # At least 2 sizes should appear


def test_design_task_indexing():
    """Test that task indices are correct."""
    grid = create_test_grid()
    design = generate_random_design(grid, options_per_screen=2, num_screens=5)
    
    expected_indices = list(range(1, 6))  # 1, 2, 3, 4, 5
    actual_indices = [task["task_index"] for task in design]
    
    assert actual_indices == expected_indices
