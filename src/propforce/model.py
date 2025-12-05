"""
Radial actuator disk body-force propeller model.

Implements a fast, parametric radial loading distribution
with momentum-theory-based induced velocity calculation.
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class PropellerGeometry:
    """Propeller geometric parameters."""
    diameter: float  # meters
    num_blades: int = 2
    hub_radius_ratio: float = 0.2  # r_hub / R
    
    @property
    def radius(self) -> float:
        return self.diameter / 2.0
    
    @property
    def hub_radius(self) -> float:
        return self.radius * self.hub_radius_ratio


@dataclass
class FlowConditions:
    """Operating conditions."""
    velocity_inf: float  # m/s, freestream
    rpm: float  # revolutions per minute
    rho: float = 1.225  # kg/m³, air density
    
    @property
    def omega(self) -> float:
        """Angular velocity in rad/s."""
        return self.rpm * 2 * np.pi / 60.0
    
    @property
    def n(self) -> float:
        """Rotational speed in rev/s."""
        return self.rpm / 60.0


class RadialActuatorDisk:
    """
    Radial actuator disk propeller model with parametric loading.
    
    The thrust loading distribution is parameterized as a polynomial:
        dT/dr = sum_i coeffs[i] * (r/R)^i
    
    Induced velocity is computed via simplified momentum theory.
    """
    
    def __init__(
        self,
        geometry: PropellerGeometry,
        num_radial_stations: int = 30,
        tip_loss_factor: float = 0.95,
    ):
        """
        Parameters
        ----------
        geometry : PropellerGeometry
            Propeller dimensions
        num_radial_stations : int
            Radial discretization points
        tip_loss_factor : float
            Empirical tip loss (0.9-1.0), mimics Prandtl correction
        """
        self.geom = geometry
        self.n_stations = num_radial_stations
        self.tip_loss = tip_loss_factor
        
        # Radial grid from hub to tip
        r_hub = self.geom.hub_radius
        r_tip = self.geom.radius
        self.r_stations = np.linspace(r_hub, r_tip, num_radial_stations)
        self.r_norm = self.r_stations / self.geom.radius  # normalized radius
        
    def compute_loading_distribution(self, coeffs: np.ndarray) -> np.ndarray:
        """
        Compute radial thrust loading from polynomial coefficients.
        
        Parameters
        ----------
        coeffs : array, shape (n_poly,)
            Polynomial coefficients [c0, c1, c2, ...]
            
        Returns
        -------
        dT_dr : array, shape (n_stations,)
            Thrust loading per unit radius (N/m)
        """
        dT_dr = np.zeros_like(self.r_stations)
        for i, c in enumerate(coeffs):
            dT_dr += c * self.r_norm**i
        
        # Apply tip loss taper
        taper = 1.0 - (1.0 - self.tip_loss) * (self.r_norm - 0.7) / 0.3
        taper = np.clip(taper, self.tip_loss, 1.0)
        dT_dr *= taper
        
        return np.maximum(dT_dr, 0.0)  # physical constraint
    
    def compute_induced_velocity(
        self,
        dT_dr: np.ndarray,
        flow: FlowConditions,
    ) -> np.ndarray:
        """
        Compute axial induced velocity from loading via momentum theory.
        
        Simplified momentum equation (linearized):
            w(r) ≈ dT/dr / (4 * pi * rho * V_eff * r)
        
        Parameters
        ----------
        dT_dr : array
            Radial thrust distribution (N/m)
        flow : FlowConditions
            Operating conditions
            
        Returns
        -------
        w : array
            Induced velocity (m/s) at each station
        """
        V_eff = flow.velocity_inf + 1e-3  # avoid singularity
        denominator = 4 * np.pi * flow.rho * V_eff * self.r_stations
        w = dT_dr / (denominator + 1e-6)
        
        # Iterative correction (1 iteration for speed)
        V_eff_corrected = flow.velocity_inf + 0.5 * w
        w = dT_dr / (4 * np.pi * flow.rho * V_eff_corrected * self.r_stations + 1e-6)
        
        return w
    
    def compute_performance(
        self,
        coeffs: np.ndarray,
        flow: FlowConditions,
    ) -> Tuple[float, float, float, np.ndarray, np.ndarray]:
        """
        Compute thrust, torque, power, and radial distributions.
        
        Parameters
        ----------
        coeffs : array
            Loading polynomial coefficients
        flow : FlowConditions
            Operating state
            
        Returns
        -------
        thrust : float (N)
        torque : float (N·m)
        power : float (W)
        dT_dr : array (N/m)
        w : array (m/s), induced velocity
        """
        dT_dr = self.compute_loading_distribution(coeffs)
        w = self.compute_induced_velocity(dT_dr, flow)
        
        # Integrate thrust
        dr = np.gradient(self.r_stations)
        thrust = np.trapz(dT_dr, dx=dr[0])
        
        # Torque from swirl (simplified, proportional to loading and radius)
        # Assumes tangential force ~ dT/dr * (r / R) / (2 * pi * efficiency_factor)
        swirl_factor = 0.05  # empirical, represents induced swirl losses
        # dQ_dr = swirl_factor * dT_dr * self.r_stations / self.geom.radius
        dQ_dr = swirl_factor * dT_dr * self.r_stations
        torque = np.trapz(dQ_dr, dx=dr[0])
        
        # # Power: P = T * (V_inf + w_avg) + Q * omega
        # w_avg = np.mean(w)
        # power_axial = thrust * (flow.velocity_inf + w_avg)
        # power_rotational = torque * flow.omega
        # power = power_axial + power_rotational
                # Power: Integrate dP = dT * (V + w) + dQ * omega
        # 1. Axial Power (Thrust * local velocity)
        #    P_axial = Integral( (V_inf + w(r)) * dT/dr ) dr
        local_axial_velocity = flow.velocity_inf + w
        dP_axial_dr = dT_dr * local_axial_velocity
        power_axial = np.trapz(dP_axial_dr, dx=dr[0])
        
        # 2. Rotational Power
        power_rotational = torque * flow.omega
        
        power = power_axial + power_rotational
        
        return thrust, torque, power, dT_dr, w