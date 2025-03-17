import numpy as np
from scipy.stats import norm

class OptionPricing:
    @staticmethod
    def black_scholes(S, K, T, r, sigma, option_type='call'):
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type.lower() == 'call':
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            
        return price
    
    @staticmethod
    def monte_carlo_european(S0, K, T, r, sigma, paths, steps, option_type='call'):
        dt = T / steps
        S = np.zeros((paths, steps + 1))
        S[:, 0] = S0
        
        for t in range(1, steps + 1):
            Z = np.random.standard_normal(paths)
            S[:, t] = S[:, t-1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z)
        
        if option_type.lower() == 'call':
            payoff = np.maximum(S[:, -1] - K, 0)
        else:
            payoff = np.maximum(K - S[:, -1], 0)
            
        price = np.exp(-r * T) * np.mean(payoff)
        return price
    
    @staticmethod
    def monte_carlo_american(S0, K, T, r, sigma, paths, steps, option_type='call'):
        dt = T / steps
        df = np.exp(-r * dt)
        
        S = np.zeros((paths, steps + 1))
        S[:, 0] = S0
        
        for t in range(1, steps + 1):
            Z = np.random.standard_normal(paths)
            S[:, t] = S[:, t-1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z)
        
        if option_type.lower() == 'call':
            h = np.maximum(S - K, 0)
        else:
            h = np.maximum(K - S, 0)
        
        V = np.copy(h)
        
        for t in range(steps-1, 0, -1):
            itm = h[:, t] > 0
            
            if np.sum(itm) > 0:
                X = S[itm, t]
                Y = V[itm, t+1] * df
                
                A = np.vstack([np.ones(len(X)), X, X**2]).T
                beta = np.linalg.lstsq(A, Y, rcond=None)[0]
                
                C = np.zeros(paths)
                C[itm] = np.dot(np.vstack([np.ones(len(X)), X, X**2]).T, beta)
                
                exercise = h[:, t] > C
                V[exercise, t] = h[exercise, t]
                V[~exercise, t] = V[~exercise, t+1] * df
            else:
                V[:, t] = V[:, t+1] * df
        
        price = np.mean(V[:, 1] * df)
        return price 