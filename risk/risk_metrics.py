import numpy as np
from scipy import stats

class RiskMetrics:
    @staticmethod
    def value_at_risk(returns, confidence=0.95):
        return -np.percentile(returns, 100 * (1 - confidence))
    
    @staticmethod
    def conditional_var(returns, confidence=0.95):
        var = RiskMetrics.value_at_risk(returns, confidence)
        return -np.mean(returns[returns <= -var])
    
    @staticmethod
    def sharpe_ratio(returns, risk_free_rate=0):
        excess_returns = returns - risk_free_rate
        return np.mean(excess_returns) / np.std(excess_returns)
    
    @staticmethod
    def maximum_drawdown(equity_curve):
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - peak) / peak
        return np.min(drawdown)
    
    @staticmethod
    def greeks(S, K, T, r, sigma, option_type='call'):
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type.lower() == 'call':
            delta = stats.norm.cdf(d1)
            theta = -(S * stats.norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * stats.norm.cdf(d2)
        else:
            delta = stats.norm.cdf(d1) - 1
            theta = -(S * stats.norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * stats.norm.cdf(-d2)
        
        gamma = stats.norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * np.sqrt(T) * stats.norm.pdf(d1)
        rho = K * T * np.exp(-r * T) * stats.norm.cdf(d2) if option_type.lower() == 'call' else -K * T * np.exp(-r * T) * stats.norm.cdf(-d2)
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'rho': rho
        } 