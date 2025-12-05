"""
Performance metrics and non-dimensional coefficients.
"""

import numpy as np
from typing import Dict
from .model import PropellerGeometry, FlowConditions


def compute_coefficients(
    thrust: float,
    power: float,
    geometry: PropellerGeometry,
    flow: FlowConditions,
) -> Dict[str, float]:
    """
    Compute non-dimensional propeller coefficients.
    
    Parameters
    ----------
    thrust : float (N)
    power : float (W)
    geometry : PropellerGeometry
    flow : FlowConditions
    
    Returns
    -------
    coeffs : dict
        {'J': advance_ratio, 'CT': thrust_coeff, 'CP': power_coeff, 'eta': efficiency}
    """
    n = flow.n  # rev/s
    D = geometry.diameter
    rho = flow.rho
    V_inf = flow.velocity_inf
    
    # Advance ratio
    J = V_inf / (n * D + 1e-9)
    
    # Thrust coefficient
    CT = thrust / (rho * n**2 * D**4 + 1e-12)
    
    # Power coefficient
    CP = power / (rho * n**3 * D**5 + 1e-12)
    
    # Efficiency
    eta = (J * CT) / (CP + 1e-12) if CP > 1e-9 else 0.0
    
    return {
        'J': J,
        'CT': CT,
        'CP': CP,
        'eta': eta,
    }


def compute_efficiency(thrust: float, power: float, velocity: float) -> float:
    """
    Propulsive efficiency: η = T·V / P
    
    Parameters
    ----------
    thrust : float (N)
    power : float (W)
    velocity : float (m/s)
    
    Returns
    -------
    eta : float
    """
    if power < 1e-6:
        return 0.0
    return (thrust * velocity) / power


def performance_sweep(
    model,
    coeffs: np.ndarray,
    rpm_range: np.ndarray,
    velocity: float,
    rho: float = 1.225,
) -> Dict[str, np.ndarray]:
    """
    Sweep RPM and compute performance maps.
    
    Parameters
    ----------
    model : RadialActuatorDisk
    coeffs : array
        Loading coefficients
    rpm_range : array
        RPM values to sweep
    velocity : float
        Freestream velocity (m/s)
    rho : float
        Density
        
    Returns
    -------
    results : dict of arrays
        Keys: 'rpm', 'thrust', 'power', 'J', 'CT', 'CP', 'eta'
    """
    n_points = len(rpm_range)
    results = {
        'rpm': rpm_range,
        'thrust': np.zeros(n_points),
        'power': np.zeros(n_points),
        'J': np.zeros(n_points),
        'CT': np.zeros(n_points),
        'CP': np.zeros(n_points),
        'eta': np.zeros(n_points),
    }
    
    for i, rpm in enumerate(rpm_range):
        flow = FlowConditions(velocity_inf=velocity, rpm=rpm, rho=rho)
        T, Q, P, _, _ = model.compute_performance(coeffs, flow)
        coeffs_dict = compute_coefficients(T, P, model.geom, flow)
        
        results['thrust'][i] = T
        results['power'][i] = P
        results['J'][i] = coeffs_dict['J']
        results['CT'][i] = coeffs_dict['CT']
        results['CP'][i] = coeffs_dict['CP']
        results['eta'][i] = coeffs_dict['eta']
    
    return results