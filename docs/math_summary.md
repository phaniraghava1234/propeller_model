# Mathematical Model Summary

## 1. Actuator Disk Theory

The propeller is modeled as an **axisymmetric actuator disk** spanning radius `R` with prescribed radial thrust loading.

### 1.1 Radial Thrust Loading

Parametric form (polynomial):

```
dT/dr = ρ V² R · Σᵢ₌₀ⁿ cᵢ (r/R)ⁱ
```

where:
- `cᵢ` = polynomial coefficients (design variables)
- `r` = radial coordinate
- `R` = tip radius
- `ρ` = air density
- `V` = reference velocity (e.g., resultant velocity)

**Constraint:** `dT/dr ≥ 0` (enforced in code via `np.maximum`)

---

## 2. Momentum Theory

### 2.1 Induced Velocity

From momentum conservation, the axial induced velocity `w(r)` satisfies:

```
dT = 2 ρ A(r) V_eff w dr
```

where `A(r) = 2π r dr` (annular area).

Rearranging:

```
w(r) = dT/dr / (4π ρ V_eff r)
```

**Iterative refinement (1 iteration):**

```
V_eff = V∞ + 0.5 · w
```

This avoids full BEMT iteration while capturing primary induced effects.

---

## 3. Integrated Performance

### 3.1 Thrust

```
T = ∫₀ᴿ dT/dr dr
```

Numerical integration via trapezoidal rule.

### 3.2 Torque

Torque arises from tangential induced velocity (swirl). Simplified model:

```
dQ/dr = k_swirl · dT/dr · r / R
```

where `k_swirl ≈ 0.05` is an empirical swirl factor.

```
Q = ∫₀ᴿ dQ/dr dr
```

### 3.3 Power

```
P = T · (V∞ + w_avg) + Q · Ω
```

where:
- `w_avg = mean(w(r))`
- `Ω = 2π n` (angular velocity, rad/s)

---

## 4. Non-Dimensional Coefficients

### 4.1 Advance Ratio

```
J = V∞ / (n D)
```

where `n` = rotational speed (rev/s), `D = 2R`.

### 4.2 Thrust Coefficient

```
CT = T / (ρ n² D⁴)
```

### 4.3 Power Coefficient

```
CP = P / (ρ n³ D⁵)
```

### 4.4 Efficiency

```
η = J CT / CP = (T V∞) / P
```

---

## 5. Tip Loss Correction

Finite-blade effects reduce loading near the tip. Implemented as:

```
f_tip(r) = 1 - (1 - F_tip) · (r - 0.7R) / (0.3R)
```

where `F_tip ≈ 0.95` (empirical).

Applied as:

```
dT/dr := dT/dr · f_tip(r)
```

---

## 6. Optimization Formulation

### 6.1 Minimize Power for Target Thrust

```
minimize     P(c)
subject to   T(c) ≥ T_target
             0 ≤ cᵢ ≤ c_max
```

### 6.2 Maximize Thrust for Power Limit

```
minimize     -T(c)
subject to   P(c) ≤ P_max
             0 ≤ cᵢ ≤ c_max
```

**Solver:** SciPy `SLSQP` (Sequential Least Squares Programming).

---

## 7. Assumptions

1. **Axisymmetric flow:** No azimuthal variation
2. **Incompressible:** Mach << 1
3. **Quasi-steady:** No time-varying effects
4. **Small angle:** Induced angle << blade pitch
5. **No stall:** Blade loading within attached-flow regime
6. **Uniform far-field:** V∞ constant upstream

---

## 8. Parameter Ranges (Validation Domain)

| Parameter | Symbol | Range | Units |
|-----------|--------|-------|-------|
| Diameter | D | [0.1, 1.0] | m |
| RPM | n·60 | [1000, 15000] | rev/min |
| Velocity | V∞ | [0, 50] | m/s |
| Advance Ratio | J | [0.1, 1.5] | - |
| Thrust Coeff | CT | [0.01, 0.2] | - |
| Power Coeff | CP | [0.01, 0.15] | - |

---

## References

1. **Glauert, H.** (1935). *Airplane Propellers*. In *Aerodynamic Theory* (Vol. IV, Div. L). Springer, Berlin.

2. **Conway, J. T.** (1998). *Analytical solutions for the actuator disk with variable radial distribution of load*. Journal of Fluid Mechanics, 297, 327-355. DOI: [https://doi.org/10.1017/S0022112095003120](https://doi.org/10.1017/S0022112098003093)

3. **Adkins, C. N., & Liebeck, R. H.** (1994). *Design of optimum propellers*. Journal of Propulsion and Power, 10(5), 676-682. DOI: [10.2514/3.23779](https://doi.org/10.2514/3.23779)

4. **Drela, M.** (2007). *QPROP Formulation*. MIT Aero & Astro. [http://web.mit.edu/drela/Public/web/qprop/](http://web.mit.edu/drela/Public/web/qprop/)

5. **Selig, M. S.** *UIUC Propeller Database*. University of Illinois. [https://m-selig.ae.illinois.edu/props/propDB.html](https://m-selig.ae.illinois.edu/props/propDB.html)

6. **Goldstein, S.** (1929). *On the vortex theory of screw propellers*. Proceedings of the Royal Society of London. Series A, 123(792), 440-465.