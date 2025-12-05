"""
Edge case and boundary condition tests.
"""

import pytest
import numpy as np
from propforce.model import RadialActuatorDisk, PropellerGeometry, FlowConditions
from propforce.utils import validate_inputs


def test_zero_velocity():
    """Model should handle zero freestream velocity (static thrust)."""
    geom = PropellerGeometry(diameter=0.25, num_blades=2)
    model = RadialActuatorDisk(geom, num_radial_stations=20)
    coeffs = np.array([2.0, 1.0, 0.0, 0.0, 0.0])
    flow = FlowConditions(velocity_inf=0.0, rpm=5000)
    
    T, _, P, _, _ = model.compute_performance(coeffs, flow)
    assert T > 0, "Should produce thrust at zero velocity"
    assert P > 0, "Should require power at zero velocity"


def test_very_high_rpm():
    """Model should remain stable at high RPM."""
    geom = PropellerGeometry(diameter=0.25, num_blades=2)
    model = RadialActuatorDisk(geom, num_radial_stations=20)
    coeffs = np.array([1.0, 1.0, 1.0, 0.0, 0.0])
    flow = FlowConditions(velocity_inf=10.0, rpm=15000)
    
    T, _, P, _, _ = model.compute_performance(coeffs, flow)
    assert np.isfinite(T), "Thrust should be finite at high RPM"
    assert np.isfinite(P), "Power should be finite at high RPM"


def test_small_diameter():
    """Model should work with small propellers."""
    geom = PropellerGeometry(diameter=0.05, num_blades=2)
    model = RadialActuatorDisk(geom, num_radial_stations=15)
    coeffs = np.array([2.0, 0.5, 0.0, 0.0, 0.0])
    flow = FlowConditions(velocity_inf=5.0, rpm=10000)
    
    T, _, P, _, _ = model.compute_performance(coeffs, flow)
    assert T > 0, "Small propeller should still produce thrust"


def test_input_validation():
    """Input validation should catch invalid parameters."""
    with pytest.raises(ValueError):
        validate_inputs(diameter=0.01, rpm=5000, velocity=10.0)  # diameter too small
    
    with pytest.raises(ValueError):
        validate_inputs(diameter=0.25, rpm=50, velocity=10.0)  # RPM too low
    
    with pytest.raises(ValueError):
        validate_inputs(diameter=0.25, rpm=5000, velocity=200.0)  # velocity too high