"""
PropForce: Fast parametric body-force propeller model.

A radial actuator disk implementation for rapid thrust/torque prediction
and gradient-based optimization without CFD.
"""

__version__ = "0.1.0"

from .model import RadialActuatorDisk
from .metrics import compute_coefficients, compute_efficiency
from .optimize import optimize_loading, OptimizationResult

__all__ = [
    "RadialActuatorDisk",
    "compute_coefficients",
    "compute_efficiency",
    "optimize_loading",
    "OptimizationResult",
]