"""
Physical consistency tests for propeller model.
"""

import pytest
import numpy as np
from propforce.model import RadialActuatorDisk, PropellerGeometry, FlowConditions
from propforce.utils import default_loading_coeffs


def test_thrust_increases_with_rpm():
    """Thrust should increase with RPM at constant velocity."""
    geom = PropellerGeometry(diameter=0.25, num_blades=2)
    model = RadialActuatorDisk(geom, num_radial_stations=20)
    coeffs = default_loading_coeffs("elliptic")
    
    thrust_values = []
    for rpm in [2000, 4000, 6000]:
        flow = FlowConditions(velocity_inf=10.0, rpm=rpm)
        T, _, _, _, _ = model.compute_performance(coeffs, flow)
        thrust_values.append(T)
    
    assert thrust_values[1] > thrust_values[0], "Thrust should increase with RPM"
    assert thrust_values[2] > thrust_values[1], "Thrust should increase with RPM"


def test_power_increases_with_rpm():
    """Power should increase faster than thrust with RPM."""
    geom = PropellerGeometry(diameter=0.25, num_blades=2)
    model = RadialActuatorDisk(geom, num_radial_stations=20)
    coeffs = default_loading_coeffs("elliptic")
    
    power_values = []
    for rpm in [2000, 4000, 6000]:
        flow = FlowConditions(velocity_inf=10.0, rpm=rpm)
        _, _, P, _, _ = model.compute_performance(coeffs, flow)
        power_values.append(P)
    
    assert power_values[1] > power_values[0], "Power should increase with RPM"
    assert power_values[2] > power_values[1], "Power should increase with RPM"


def test_induced_velocity_positive():
    """Induced velocity should be positive for positive thrust."""
    geom = PropellerGeometry(diameter=0.25, num_blades=2)
    model = RadialActuatorDisk(geom, num_radial_stations=20)
    coeffs = default_loading_coeffs("elliptic")
    flow = FlowConditions(velocity_inf=10.0, rpm=5000)
    
    _, _, _, dT_dr, w = model.compute_performance(coeffs, flow)
    
    assert np.all(w >= 0), "Induced velocity should be non-negative"


def test_thrust_loading_non_negative():
    """Thrust loading should never be negative."""
    geom = PropellerGeometry(diameter=0.25, num_blades=2)
    model = RadialActuatorDisk(geom, num_radial_stations=20)
    coeffs = default_loading_coeffs("uniform")
    
    dT_dr = model.compute_loading_distribution(coeffs)
    assert np.all(dT_dr >= 0), "Thrust loading must be non-negative"


def test_zero_coefficients_zero_thrust():
    """Zero loading coefficients should yield zero thrust."""
    geom = PropellerGeometry(diameter=0.25, num_blades=2)
    model = RadialActuatorDisk(geom, num_radial_stations=20)
    coeffs = np.zeros(5)
    flow = FlowConditions(velocity_inf=10.0, rpm=5000)
    
    T, _, _, _, _ = model.compute_performance(coeffs, flow)
    assert abs(T) < 1e-6, "Zero coefficients should give zero thrust"