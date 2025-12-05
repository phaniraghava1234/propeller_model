"""
Demonstration script for propeller body-force model.

Runs analysis, optimization, and generates all required plots.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from propforce.model import RadialActuatorDisk, PropellerGeometry, FlowConditions
from propforce.metrics import compute_coefficients, performance_sweep
from propforce.optimize import optimize_loading
from propforce.utils import default_loading_coeffs


# Output directory
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def plot_radial_distributions(model, coeffs, flow, filename="radial_distributions.png"):
    """Plot radial thrust loading and induced velocity."""
    T, Q, P, dT_dr, w = model.compute_performance(coeffs, flow)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Thrust loading
    ax1.plot(model.r_norm, dT_dr, 'b-', linewidth=2)
    ax1.set_xlabel('Normalized Radius r/R', fontsize=12)
    ax1.set_ylabel('Thrust Loading dT/dr (N/m)', fontsize=12)
    ax1.set_title('Radial Thrust Distribution', fontsize=13)
    ax1.grid(True, alpha=0.3)
    
    # Induced velocity
    ax2.plot(model.r_norm, w, 'r-', linewidth=2)
    ax2.set_xlabel('Normalized Radius r/R', fontsize=12)
    ax2.set_ylabel('Induced Velocity w (m/s)', fontsize=12)
    ax2.set_title('Axial Induced Velocity', fontsize=13)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=150)
    print(f"Saved {filename}")
    plt.close()


def plot_performance_maps(results, filename="performance_maps.png"):
    """Plot CT, CP vs J."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # CT vs J
    ax1.plot(results['J'], results['CT'], 'bo-', linewidth=2, markersize=4)
    ax1.set_xlabel('Advance Ratio J', fontsize=12)
    ax1.set_ylabel('Thrust Coefficient CT', fontsize=12)
    ax1.set_title('CT vs J', fontsize=13)
    ax1.grid(True, alpha=0.3)
    
    # CP vs J
    ax2.plot(results['J'], results['CP'], 'ro-', linewidth=2, markersize=4)
    ax2.set_xlabel('Advance Ratio J', fontsize=12)
    ax2.set_ylabel('Power Coefficient CP', fontsize=12)
    ax2.set_title('CP vs J', fontsize=13)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=150)
    print(f"Saved {filename}")
    plt.close()


def plot_thrust_power_vs_rpm(results, filename="thrust_power_vs_rpm.png"):
    """Plot thrust and power vs RPM."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.plot(results['rpm'], results['thrust'], 'g-', linewidth=2)
    ax1.set_xlabel('RPM', fontsize=12)
    ax1.set_ylabel('Thrust (N)', fontsize=12)
    ax1.set_title('Thrust vs RPM', fontsize=13)
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(results['rpm'], results['power'], 'm-', linewidth=2)
    ax2.set_xlabel('RPM', fontsize=12)
    ax2.set_ylabel('Power (W)', fontsize=12)
    ax2.set_title('Power vs RPM', fontsize=13)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=150)
    print(f"Saved {filename}")
    plt.close()


def plot_optimization_convergence(opt_result, filename="optimization_convergence.png"):
    """Plot optimization convergence history."""
    history = opt_result.history
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.plot(history['iter'], history['objective'], 'k-', linewidth=2)
    ax1.set_xlabel('Iteration', fontsize=12)
    ax1.set_ylabel('Objective Value', fontsize=12)
    ax1.set_title('Optimization Convergence', fontsize=13)
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(history['iter'], history['thrust'], 'b-', label='Thrust (N)', linewidth=2)
    ax2_twin = ax2.twinx()
    ax2_twin.plot(history['iter'], history['power'], 'r-', label='Power (W)', linewidth=2)
    ax2.set_xlabel('Iteration', fontsize=12)
    ax2.set_ylabel('Thrust (N)', fontsize=12, color='b')
    ax2_twin.set_ylabel('Power (W)', fontsize=12, color='r')
    ax2.set_title('Thrust & Power History', fontsize=13)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=150)
    print(f"Saved {filename}")
    plt.close()


def main():
    """Run full demonstration."""
    print("=" * 60)
    print("PROPELLER BODY-FORCE MODEL DEMONSTRATION")
    print("=" * 60)
    
    # Define propeller
    geom = PropellerGeometry(diameter=0.254, num_blades=2, hub_radius_ratio=0.2)
    print(f"\nPropeller: D={geom.diameter}m, {geom.num_blades} blades")
    
    # Create model
    model = RadialActuatorDisk(geom, num_radial_stations=40, tip_loss_factor=0.96)
    print(f"Model: {model.n_stations} radial stations")
    
    # Operating condition
    flow = FlowConditions(velocity_inf=10.0, rpm=5000, rho=1.225)
    print(f"Flow: V={flow.velocity_inf} m/s, RPM={flow.rpm}")
    
    # Default loading
    coeffs = default_loading_coeffs("elliptic")
    print(f"\nLoading coefficients: {coeffs}")
    
    # Compute performance
    T, Q, P, dT_dr, w = model.compute_performance(coeffs, flow)
    perf = compute_coefficients(T, P, geom, flow)
    
    print(f"\n--- Performance ---")
    print(f"Thrust:  {T:.2f} N")
    print(f"Torque:  {Q:.4f} N·m")
    print(f"Power:   {P:.2f} W")
    print(f"J:       {perf['J']:.3f}")
    print(f"CT:      {perf['CT']:.4f}")
    print(f"CP:      {perf['CP']:.4f}")
    print(f"Eta:     {perf['eta']:.3f}")
    
    # Plot 1: Radial distributions
    plot_radial_distributions(model, coeffs, flow)
    
    # Sweep RPM
    print("\n--- RPM Sweep ---")
    rpm_range = np.linspace(2000, 8000, 20)
    results = performance_sweep(model, coeffs, rpm_range, velocity=10.0)
    
    # Plot 2 & 3: Performance maps
    plot_performance_maps(results)
    plot_thrust_power_vs_rpm(results)
    
    # Optimization example
    print("\n--- Optimization: Minimize Power for Target Thrust ---")
    thrust_target = 15.0  # N
    opt_result = optimize_loading(
        model,
        flow,
        objective="min_power",
        thrust_target=thrust_target,
        n_poly=5,
        bounds=(0.0, 8.0),
        method="SLSQP",
    )
    
    print(f"Success: {opt_result.success}")
    print(f"Iterations: {opt_result.iterations}")
    print(f"Optimal coefficients: {opt_result.optimal_coeffs}")
    print(f"Final thrust: {opt_result.thrust:.2f} N (target: {thrust_target:.2f} N)")
    print(f"Final power: {opt_result.power:.2f} W (minimized)")
    
    # Plot 4: Optimization convergence
    plot_optimization_convergence(opt_result)
    
    # Plot optimized radial distribution
    plot_radial_distributions(model, opt_result.optimal_coeffs, flow, 
                             filename="radial_distributions_optimized.png")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE. All plots saved to examples/outputs/")
    print("=" * 60)


if __name__ == "__main__":
    main()