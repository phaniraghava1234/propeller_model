"""
Optimization routines for propeller loading distribution.
"""

import numpy as np
from scipy.optimize import minimize, Bounds, LinearConstraint
from dataclasses import dataclass
from typing import Callable, Optional, Dict
from .model import RadialActuatorDisk, FlowConditions


@dataclass
class OptimizationResult:
    """Container for optimization results."""
    success: bool
    optimal_coeffs: np.ndarray
    optimal_value: float
    thrust: float
    power: float
    iterations: int
    message: str
    history: Dict[str, list]


def optimize_loading(
    model: RadialActuatorDisk,
    flow: FlowConditions,
    objective: str = "min_power",
    thrust_target: Optional[float] = None,
    power_limit: Optional[float] = None,
    initial_guess: Optional[np.ndarray] = None,
    n_poly: int = 5,
    bounds: tuple = (0.0, 10.0),
    method: str = "SLSQP",
) -> OptimizationResult:
    """
    Optimize radial loading distribution.
    
    Parameters
    ----------
    model : RadialActuatorDisk
    flow : FlowConditions
    objective : str
        "min_power" - minimize power for target thrust
        "max_thrust" - maximize thrust with power limit
    thrust_target : float, optional
        Required thrust (N) for min_power
    power_limit : float, optional
        Maximum power (W) for max_thrust
    initial_guess : array, optional
        Starting coefficients
    n_poly : int
        Number of polynomial terms
    bounds : tuple
        (lower, upper) for all coefficients
    method : str
        Scipy optimizer: 'SLSQP', 'L-BFGS-B', 'trust-constr'
        
    Returns
    -------
    result : OptimizationResult
    """
    # History tracking
    history = {'iter': [], 'objective': [], 'thrust': [], 'power': []}
    iter_count = [0]
    
    # Initial guess
    if initial_guess is None:
        x0 = np.random.uniform(1.0, 3.0, n_poly)
    else:
        x0 = initial_guess
    
    # Define objective function
    def objective_function(coeffs: np.ndarray) -> float:
        T, Q, P, _, _ = model.compute_performance(coeffs, flow)
        
        # Record history
        history['iter'].append(iter_count[0])
        history['thrust'].append(T)
        history['power'].append(P)
        iter_count[0] += 1
        
        if objective == "min_power":
            obj = P
        elif objective == "max_thrust":
            obj = -T  # maximize = minimize negative
        else:
            raise ValueError(f"Unknown objective: {objective}")
        
        history['objective'].append(obj)
        return obj
    
    # Constraints
    constraints = []
    
    if objective == "min_power" and thrust_target is not None:
        # Thrust constraint: T >= T_target
        def thrust_constraint(coeffs):
            T, _, _, _, _ = model.compute_performance(coeffs, flow)
            return T - thrust_target
        
        constraints.append({
            'type': 'ineq',
            'fun': thrust_constraint,
        })
    
    if objective == "max_thrust" and power_limit is not None:
        # Power constraint: P <= P_max
        def power_constraint(coeffs):
            _, _, P, _, _ = model.compute_performance(coeffs, flow)
            return power_limit - P
        
        constraints.append({
            'type': 'ineq',
            'fun': power_constraint,
        })
    
    # Bounds
    opt_bounds = Bounds(
        lb=np.full(n_poly, bounds[0]),
        ub=np.full(n_poly, bounds[1]),
    )
    
    # Optimize
    res = minimize(
        objective_function,
        x0,
        method=method,
        bounds=opt_bounds,
        constraints=constraints,
        options={'maxiter': 200, 'disp': False},
    )
    
    # Final performance
    T_final, Q_final, P_final, _, _ = model.compute_performance(res.x, flow)
    
    return OptimizationResult(
        success=res.success,
        optimal_coeffs=res.x,
        optimal_value=res.fun,
        thrust=T_final,
        power=P_final,
        iterations=res.nit,
        message=res.message,
        history=history,
    )