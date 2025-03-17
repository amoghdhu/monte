import numpy as np
from scipy.stats import norm

class StochasticProcesses:
    @staticmethod
    def geometric_brownian_motion(S0, mu, sigma, T, steps, paths):
        dt = T / steps
        S = np.zeros((paths, steps + 1))
        S[:, 0] = S0
        
        for t in range(1, steps + 1):
            Z = np.random.standard_normal(paths)
            S[:, t] = S[:, t-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z)
        
        return S
    
    @staticmethod
    def heston_model(S0, v0, kappa, theta, sigma, rho, r, T, steps, paths):
        dt = T / steps
        S = np.zeros((paths, steps + 1))
        v = np.zeros((paths, steps + 1))
        S[:, 0] = S0
        v[:, 0] = v0
        
        for t in range(1, steps + 1):
            Z1 = np.random.standard_normal(paths)
            Z2 = rho * Z1 + np.sqrt(1 - rho**2) * np.random.standard_normal(paths)
            
            v[:, t] = np.maximum(v[:, t-1] + kappa * (theta - v[:, t-1]) * dt + sigma * np.sqrt(v[:, t-1] * dt) * Z2, 0)
            S[:, t] = S[:, t-1] * np.exp((r - 0.5 * v[:, t-1]) * dt + np.sqrt(v[:, t-1] * dt) * Z1)
        
        return S, v
    
    @staticmethod
    def jump_diffusion(S0, mu, sigma, lambda_jump, mu_jump, sigma_jump, T, steps, paths):
        dt = T / steps
        S = np.zeros((paths, steps + 1))
        S[:, 0] = S0
        
        for t in range(1, steps + 1):
            Z = np.random.standard_normal(paths)
            poisson = np.random.poisson(lambda_jump * dt, paths)
            jumps = np.zeros(paths)
            
            for i in range(paths):
                if poisson[i] > 0:
                    jumps[i] = np.sum(np.random.normal(mu_jump, sigma_jump, poisson[i]))
            
            S[:, t] = S[:, t-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z + jumps)
        
        return S 