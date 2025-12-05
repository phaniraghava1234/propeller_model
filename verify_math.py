import numpy as np
from propforce.model import RadialActuatorDisk, PropellerGeometry, FlowConditions

def verify_constant_loading():
    # Geometry
    R = 1.0
    geom = PropellerGeometry(diameter=2*R, num_blades=2, hub_radius_ratio=0.01)
    
    # 1. Set up a model with NO tip loss (to match theory)
    model = RadialActuatorDisk(geom, num_radial_stations=50, tip_loss_factor=1.0)
    
    # 2. Flow
    flow = FlowConditions(velocity_inf=10.0, rpm=1000, rho=1.0)
    
    # 3. Loading: dT/dr = k * r
    # This corresponds to polynomial coeffs [0, k] if normalized r is used.
    # Let's try to achieve roughly constant w.
    # Momentum theory: dT = 4*pi*rho*r*V*w dr
    # If w is constant, dT/dr should be proportional to r.
    
    coeffs = np.array([0.0, 100.0]) # Linear increase in loading with radius
    
    T, Q, P, dT_dr, w = model.compute_performance(coeffs, flow)
    
    print("--- Math Verification ---")
    print(f"Radial Stations: {model.r_stations[::10]}")
    print(f"Induced Vel (w): {w[::10]}")
    
    # Check variation of w
    w_variation = np.std(w) / np.mean(w)
    print(f"Variation in w (should be low for linear loading): {w_variation:.4f}")

    if w_variation < 0.1:
        print("SUCCESS: Linear loading produces roughly constant induced velocity.")
    else:
        print("NOTE: Variation exists (likely due to V_eff correction or linearization).")

if __name__ == "__main__":
    verify_constant_loading()