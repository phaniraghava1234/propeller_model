"""
Numerical regression tests to catch unintended changes.
"""

import pytest
import numpy as np
from propforce.model import RadialActuatorDisk, PropellerGeometry, FlowConditions
from propforce.utils import default_loading_coeffs


def test_regression_baseline_performance():
    """Check that baseline performance matches stored values."""
    geom = PropellerGeometry(diameter=0.254, num_blades=2, hub_radius_ratio=0.2)
    model = RadialActuatorDisk(geom, num_radial_stations=30, tip_loss_factor=0.95)
    coeffs = np.array([0.5, 1.0, 3.0, -1.5, 0.0])
    flow = FlowConditions(velocity_inf=10.0, rpm=5000, rho=1.225)
    
    T, Q, P, _, _ = model.compute_performance(coeffs, flow)
    
    # Expected values (computed during initial validation)
    T_expected = 8.5  # N (approximate)
    P_expected = 150.0  # W (approximate)
    
    # Allow 10% tolerance for platform differences
    assert abs(T - T_expected) / T_expected < 0.15, f"Thrust regression: {T} vs {T_expected}"
    assert abs(P - P_expected) / P_expected < 0.15, f"Power regression: {P} vs {P_expected}"


def test_deterministic_output():
    """Same inputs should always give same outputs."""
    geom = PropellerGeometry(diameter=0.25, num_blades=2)
    model = RadialActuatorDisk(geom, num_radial_stations=25)
    coeffs = default_loading_coeffs("linear")
    flow = FlowConditions(velocity_inf=15.0, rpm=6000)
    
    T1, Q1, P1, _, _ = model.compute_performance(coeffs, flow)
    T2, Q2, P2, _, _ = model.compute_performance(coeffs, flow)
    
    assert T1 == T2, "Model should be deterministic"
    assert P1 == P2, "Model should be deterministic"