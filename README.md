# Monte Carlo Simulation Platform

A comprehensive platform for option pricing, risk analysis, and financial modeling using Monte Carlo methods.

### Stochastic Differential Equations
The simulations are based on various stochastic differential equations:

- **Geometric Brownian Motion (GBM)**:
  $dS_t = \mu S_t dt + \sigma S_t dW_t$

- **Heston Model**:
  $dS_t = \mu S_t dt + \sqrt{v_t} S_t dW_t^S$
  $dv_t = \kappa(\theta - v_t)dt + \sigma_v \sqrt{v_t}dW_t^v$
  $dW_t^S dW_t^v = \rho dt$

- **Merton Jump Diffusion**:
  $dS_t = \mu S_t dt + \sigma S_t dW_t + S_t dJ_t$

### Option Pricing
For European options, the price is calculated as:
$C = e^{-rT} \mathbb{E}[\max(S_T - K, 0)]$

For American options, the Least Squares Monte Carlo method is used to estimate the optimal exercise boundary.

## Installation and Usage

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Start the server: `python monte_carlo_server.py`
4. http://localhost:5001/
5. Open `index.html` in a web browser

