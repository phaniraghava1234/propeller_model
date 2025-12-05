# PropForce: Fast Parametric Propeller Body-Force Model

[![CI](https://github.com/phaniraghava1234/propeller-mini-project/workflows/CI/badge.svg)](https://github.com/phaniraghava1234/propeller-mini-project/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-quality, fast, parametric radial actuator disk model for propeller analysis and optimization **without CFD**. Computes thrust, torque, power, and performance maps in milliseconds, suitable for gradient-based optimization and rapid design exploration.

---

## Features

✅ **Fast:** ~10ms runtime, no CFD required  
✅ **Parametric:** Polynomial radial loading distribution  
✅ **Optimizable:** SciPy-based gradient optimization for thrust/power targets  
✅ **Validated:** Error metrics vs. UIUC propeller database  
✅ **Well-tested:** Physics, regression, and boundary-case unit tests  
✅ **CI/CD Ready:** GitHub Actions workflow included  

---

## Quick Start

### Installation

```bash
git clone https://github.com/phaniraghava1234/propeller-mini-project.git
cd propeller-mini-project
pip install -r requirements.txt
```

Or install as package:

```bash
pip install -e .
```

### Run Demo

```bash
cd examples
python run_demo.py
```

**Expected output:**
- 4 plots in `examples/outputs/`:
  - Radial thrust and induced velocity distributions
  - Performance maps (CT, CP vs J)
  - Thrust/Power vs RPM
  - Optimization convergence
- Console output with performance metrics

### Run Tests

```bash
pytest tests/ -v
```

---

## Mathematical Model

### Radial Actuator Disk Theory

The model represents a propeller as an axisymmetric actuator disk with **radial thrust loading distribution**:

```
dT/dr = Σᵢ cᵢ · (r/R)ⁱ
```

where:
- `cᵢ` = polynomial coefficients (optimization parameters)
- `r` = radial position
- `R` = propeller tip radius

**Induced velocity** from momentum theory (simplified):

```
w(r) ≈ dT/dr / (4π ρ V_eff r)
```

**Integrated performance:**

```
Thrust:  T = ∫₀ᴿ dT/dr dr
Power:   P = T·(V∞ + w_avg) + Q·Ω
```

**Non-dimensional coefficients:**

```
J  = V∞ / (n·D)           (advance ratio)
CT = T / (ρ·n²·D⁴)        (thrust coeff)
CP = P / (ρ·n³·D⁵)        (power coeff)
η  = J·CT / CP            (efficiency)
```

See [`docs/math_summary.md`](docs/math_summary.md) for detailed derivations.

---

## Usage Examples

### Basic Analysis

```python
from propforce.model import RadialActuatorDisk, PropellerGeometry, FlowConditions
from propforce.utils import default_loading_coeffs
from propforce.metrics import compute_coefficients

# Define propeller
geom = PropellerGeometry(diameter=0.254, num_blades=2)
model = RadialActuatorDisk(geom, num_radial_stations=30)

# Operating condition
flow = FlowConditions(velocity_inf=10.0, rpm=5000, rho=1.225)

# Use default elliptic loading
coeffs = default_loading_coeffs("elliptic")

# Compute performance
T, Q, P, dT_dr, w = model.compute_performance(coeffs, flow)
perf = compute_coefficients(T, P, geom, flow)

print(f"Thrust: {T:.2f} N")
print(f"Power:  {P:.2f} W")
print(f"Efficiency: {perf['eta']:.3f}")
```

### Optimization Example

```python
from propforce.optimize import optimize_loading

# Minimize power for 15 N thrust target
opt_result = optimize_loading(
    model,
    flow,
    objective="min_power",
    thrust_target=15.0,
    n_poly=5,
    bounds=(0.0, 8.0),
    method="SLSQP",
)

print(f"Optimal coefficients: {opt_result.optimal_coeffs}")
print(f"Minimized power: {opt_result.power:.2f} W")
```

### Performance Sweep

```python
from propforce.metrics import performance_sweep
import numpy as np

rpm_range = np.linspace(2000, 8000, 30)
results = performance_sweep(model, coeffs, rpm_range, velocity=10.0)

# Plot CT vs J
import matplotlib.pyplot as plt
plt.plot(results['J'], results['CT'])
plt.xlabel('Advance Ratio J')
plt.ylabel('Thrust Coefficient CT')
plt.show()
```

---

## Validation

### UIUC Propeller Database

Download experimental data:

1. Visit [UIUC Propeller Database](https://m-selig.ae.illinois.edu/props/propDB.html)
2. Download CSV for a propeller (e.g., APC 10x7)
3. Place in `data/validation/`

Run validation:

```python
from propforce.utils import load_uiuc_data, compute_error_metrics

# Load experimental data
df = load_uiuc_data("data/validation/apc10x7.csv")

# Compute predictions (loop over test points)
# ... (see examples/run_demo.py for full code)

# Compute errors
rmse, mae, r2 = compute_error_metrics(df['CT'], CT_pred)
print(f"RMSE: {rmse:.4f}, MAE: {mae:.4f}, R²: {r2:.3f}")
```

**Expected accuracy:** RMSE(CT) < 0.01, R² > 0.85 for typical propellers.

---

## Parameter Defaults

| Parameter | Default | Range | Units |
|-----------|---------|-------|-------|
| Diameter | 0.254 | [0.05, 2.0] | m |
| Num Blades | 2 | [2, 6] | - |
| Hub Ratio | 0.2 | [0.1, 0.4] | - |
| RPM | 5000 | [1000, 15000] | rev/min |
| Velocity | 10.0 | [0, 100] | m/s |
| Density | 1.225 | [0.5, 2.0] | kg/m³ |
| Radial Stations | 30 | [15, 50] | - |
| Tip Loss | 0.95 | [0.9, 1.0] | - |

---

## Known Limitations

⚠️ **Simplified momentum theory:** Linearized induced velocity (not fully iterative BEMT)  
⚠️ **No compressibility:** Valid only for Mach < 0.3  
⚠️ **No blade geometry:** Cannot predict stall or detailed blade forces  
⚠️ **Empirical swirl:** Torque uses simplified swirl factor  
⚠️ **Uniform inflow:** Does not model axial variation or wake contraction  

**Use cases:** Preliminary design, optimization studies, parameter sweeps, educational demonstrations.

**Not suitable for:** High-fidelity performance prediction, off-design stall analysis, unsteady flows.

---

## Next Steps / Extensions

1. **Full BEMT:** Add iterative blade-element momentum theory
2. **Tip-loss refinement:** Implement Prandtl-Glauert correction rigorously
3. **Unsteady effects:** Add time-varying inflow, dynamic wake
4. **Multi-objective optimization:** Pareto front for thrust vs. efficiency
5. **3D wake model:** Vortex lattice or panel method coupling
6. **Experimental tuning:** Fit swirl factor to test data

---

## References

See [`docs/math_summary.md`](docs/math_summary.md) for full citations.

---

## Contributing

Contributions welcome! Please:
- Add tests for new features
- Follow PEP 8 style
- Update documentation
- Ensure CI passes

---

## License

MIT License. See [LICENSE](LICENSE).

---

## Contact

**Author:** phaniraghava1234  
**Issues:** [GitHub Issues](https://github.com/phaniraghava1234/propeller-mini-project/issues)

---

**Runtime:** Full demo completes in **< 5 seconds** on a standard laptop (no GPU required).