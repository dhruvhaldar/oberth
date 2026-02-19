import pytest
import numpy as np
from oberth.nozzle import MethodOfCharacteristics

def test_mesh_generation_unique_lines():
    """
    Verifies that the generated mesh lines are unique, even when the requested
    number of lines exceeds the resolution of the contour.
    """
    # Create an instance with a large number of requested lines
    lines_requested = 200
    moc = MethodOfCharacteristics(lines=lines_requested)

    # Solve to generate mesh
    moc.solve()

    mesh = moc.mesh

    # Extract end points of the mesh lines
    # mesh format: list of lists of points [[(start_x, start_y), (end_x, end_y)], ...]
    # we know start points are (0,0), so we check end points
    end_points = [(line[1][0], line[1][1]) for line in mesh]

    # Check for uniqueness
    unique_end_points = set(end_points)

    # Assert that we don't have duplicate lines
    assert len(mesh) == len(unique_end_points), f"Expected {len(unique_end_points)} unique lines, but got {len(mesh)}"

    # Assert that the number of lines is capped by the resolution (100 points in contour)
    # The current implementation uses 100 points for x
    assert len(mesh) <= 100, f"Expected at most 100 lines, but got {len(mesh)}"
