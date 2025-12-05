import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from propforce.model import RadialActuatorDisk, PropellerGeometry, FlowConditions
from propforce.metrics import compute_coefficients

def run_validation():
    # 1. Load Data
    try:
        # Flexible reader (handles spaces or commas)
        filename = 'data/validation/apc10x7_validation.txt'
        try:
            data = pd.read_csv(filename)
            if len(data.columns) < 2: # Fallback for space-separated
                data = pd.read_csv(filename, sep=r'\s+')
        except:
            data = pd.read_csv(filename, sep=r'\s+')
            
        data.columns = data.columns.str.strip()
        print(f"Loaded data with columns: {data.columns.tolist()}")
        
    except FileNotFoundError:
        print("Error: File not found.")
        return

    # 2. Setup Model
    D = 10 * 0.0254  # 0.254 m
    geom = PropellerGeometry(diameter=D, num_blades=2, hub_radius_ratio=0.15)
    model = RadialActuatorDisk(geom, num_radial_stations=40)
    
    # 3. Base Loading Profile (Shape only)
    # We will scale this shape to match the required Thrust
    base_coeffs = np.array([0.1, 2.5, 1.5, -3.0, 0.0])
    
    rpm = 4018
    rho = 1.225
    n = rpm / 60.0
    
    results = {'J': [], 'CT': [], 'CP': [], 'eta': []}
    
    print("\nRunning Validation (Matching CT_exp, predicting CP):")
    print(f"{'J':<6} | {'CT_exp':<8} {'CP_exp':<8} | {'CP_sim':<8} | {'Diff(CP)':<8}")
    print("-" * 55)
    
    for i, row in data.iterrows():
        J = row['J']
        CT_target = row['CT']
        
        # Calculate Target Thrust (Newtons)
        # T = CT * rho * n^2 * D^4
        T_target = CT_target * rho * n**2 * D**4
        
        # Determine Velocity
        V = J * n * D
        flow = FlowConditions(velocity_inf=V, rpm=rpm, rho=rho)
        
        # --- SCALING STEP ---
        # 1. Run with base coeffs to get reference thrust
        T_ref, _, _, _, _ = model.compute_performance(base_coeffs, flow)
        
        # 2. Scale coeffs to hit target thrust exactly
        # (Since momentum theory is non-linear, we might need 1 iteration, 
        # but linear scaling is usually very close for a starting point)
        scale_factor = T_target / (T_ref + 1e-9)
        scaled_coeffs = base_coeffs * scale_factor
        
        # 3. Run model with scaled coeffs
        T_sim, Q_sim, P_sim, _, _ = model.compute_performance(scaled_coeffs, flow)
        
        # Compute non-dimensional results
        perf = compute_coefficients(T_sim, P_sim, geom, flow)
        
        results['J'].append(J)
        results['CT'].append(perf['CT'])
        results['CP'].append(perf['CP'])
        results['eta'].append(perf['eta'])
        
        diff_cp = perf['CP'] - row['CP']
        print(f"{J:<6.3f} | {CT_target:<8.4f} {row['CP']:<8.4f} | {perf['CP']:<8.4f} | {diff_cp:<+8.4f}")

    # 4. Metrics
    rmse_cp = np.sqrt(np.mean((data['CP'] - results['CP'])**2))
    print("-" * 55)
    print(f"RMSE (CP): {rmse_cp:.4f}")

    # 5. Plotting
    plt.figure(figsize=(12, 5))
    
    # Thrust (sanity check - should be perfect match)
    plt.subplot(1, 3, 1)
    plt.plot(data['J'], data['CT'], 'ko', label='Exp', fillstyle='none')
    plt.plot(results['J'], results['CT'], 'b-', label='Model (Matched)')
    plt.xlabel('J')
    plt.ylabel('CT')
    plt.title('Thrust (Input)')
    plt.grid(True, alpha=0.3)
    
    # Power (The real validation)
    plt.subplot(1, 3, 2)
    plt.plot(data['J'], data['CP'], 'ko', label='Exp', fillstyle='none')
    plt.plot(results['J'], results['CP'], 'r-', label='Model')
    plt.xlabel('J')
    plt.ylabel('CP')
    plt.title(f'Power Prediction (RMSE={rmse_cp:.3f})')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Efficiency
    plt.subplot(1, 3, 3)
    plt.plot(data['J'], data['eta'], 'ko', label='Exp', fillstyle='none')
    plt.plot(results['J'], results['eta'], 'g-', label='Model')
    plt.xlabel('J')
    plt.ylabel('Efficiency')
    plt.title('Efficiency Prediction')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('validation_plot.png')
    print("\nSaved validation_plot.png")

if __name__ == "__main__":
    run_validation()