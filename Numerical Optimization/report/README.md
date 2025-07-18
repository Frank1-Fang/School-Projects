Report fot the project.

# Final Report – Quadratic Programming: Algorithms and Applications

This document summarizes the final report submitted for the course **SI152 - Numerical Optimization** at ShanghaiTech University.  
The project investigates the formulation, implementation, and empirical evaluation of algorithms for **Quadratic Programming (QP)**, with a focus on IRWA and ADAL methods.


## 1. Background & Motivation

Quadratic Programming (QP) problems are defined as:

$$
\min_{x} \quad \frac{1}{2} x^T Q x + c^T x \quad \text{s.t.} \quad A x \leq b, \quad E x = d
$$

They are widely applied in:
- **Machine Learning** (e.g., Support Vector Machines)
- **Finance** (e.g., Portfolio Optimization)
- **Engineering and Control** (e.g., MPC, path planning)
- **Signal Processing** (e.g., beamforming)

This project explores QP not only as a practical tool but also as a theoretical bridge to advanced optimization concepts (e.g., non-convexity, penalty methods).

## 2. Literature Review

We surveyed three major classes of QP solvers:

- **Active-set methods** (e.g., qpOASES): Fast for small problems; suitable for real-time applications like MPC.
- **Interior-point methods** (e.g., HPIPM, OOQP): Stable and robust; efficient for medium to large convex QPs.
- **ADMM-based methods** (e.g., OSQP): Modular, scalable, and compatible with embedded optimization and code generation.

## 3. Algorithm Implementation

We implemented two matrix-free algorithms from Burke et al. (2015):

### IRWA – Iteratively Reweighted Algorithm

- Replaces constraints with smoothed distance penalties
- Updates weights and solves weighted least squares in each iteration
- Handles infeasible and non-convex cases via eigenvalue correction of $H$

### ADAL – Alternating Direction Augmented Lagrangian

- Reformulates the problem using auxiliary variable $z$
- Uses ADMM-style updates on $x$, $z$, and multipliers
- Balances constraint enforcement and smoothness

Both solvers support infeasible cases and automatic convexity correction:

$$
H' = H - \lambda_{\min}(H) \cdot I
$$

## 4. Experimental Analysis

We conducted experiments on synthetically generated QPs to analyze:

### Parameter Sensitivity
- **IRWA**: Evaluated $\eta$, $\gamma$, $M_1$, $M_2$
- **ADAL**: Evaluated $\mu$, $\sigma$, $\sigma''$

> Insight: Some parameters (e.g., $\eta$, $\mu$) significantly influence convergence, while others (e.g., $\gamma$) are less impactful.

### Constraint Tolerance
- Tested convergence under varying termination criteria
- Showed that tighter tolerance increases iteration counts
- Boxplots and efficiency curves compared IRWA vs. ADAL

### Problem Size Scaling
- Problems with up to 800 variables tested
- Both methods scale similarly
- Iteration count increases with problem size; IRWA slightly more efficient

## 5. Conclusion

- IRWA is more robust for infeasible or poorly conditioned problems
- ADAL requires fine-tuning but can be effective
- Feature engineering of the QP formulation (e.g., positive definiteness correction) is critical
- Matrix-free methods are practical alternatives to traditional solvers, especially when memory or structure limits standard techniques

