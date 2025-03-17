import numpy as np
from flask import Flask, jsonify, request, render_template
import logging
from models.stochastic_processes import StochasticProcesses
from models.option_pricing import OptionPricing
from risk.risk_metrics import RiskMetrics
from utils.optimization import parallel_monte_carlo
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def home():
    return "Quantitative Finance API is running!"

@app.route('/simulate', methods=['POST', 'OPTIONS'])
def simulate():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input data"}), 400
    
    # Extract parameters
    initial_price = data.get('initialPrice', 100)
    strike_price = data.get('strikePrice', 100)
    time_to_maturity = data.get('timeToMaturity', 1)
    risk_free_rate = data.get('riskFreeRate', 0.05)
    num_simulations = min(data.get('numSimulations', 1000), 10000)
    num_steps = min(data.get('numSteps', 252), 1000)
    option_type = data.get('optionType', 'call')
    
    # Simple simulation for visualization
    dt = time_to_maturity / num_steps
    volatility = 0.2
    
    # Generate simulation data points
    visualization_data = []
    
    # Limit the number of simulations for visualization
    vis_simulations = min(50, num_simulations)
    vis_steps = min(50, num_steps + 1)
    
    for i in range(vis_simulations):
        path_volatility = np.random.uniform(0.1, 0.3)
        
        price = initial_price
        for step in range(vis_steps):
            time = step * dt
            
            visualization_data.append({
                'time': float(time),
                'price': float(price),
                'volatility': float(path_volatility)
            })
            
            if step < vis_steps - 1:
                z = np.random.standard_normal()
                price = price * np.exp((risk_free_rate - 0.5 * path_volatility**2) * dt + path_volatility * np.sqrt(dt) * z)
    
    return jsonify(visualization_data)

@app.route('/pricing', methods=['POST'])
def pricing():
    """Endpoint for quick option pricing"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input data"}), 400
    
    S0 = data.get('spot', 100)
    K = data.get('strike', 100)
    T = data.get('maturity', 1)
    r = data.get('rate', 0.05)
    sigma = data.get('volatility', 0.2)
    option_type = data.get('type', 'call')
    
    bs_price = OptionPricing.black_scholes(S0, K, T, r, sigma, option_type)
    
    mc_price = parallel_monte_carlo(S0, K, T, r, sigma, 100000, 252, option_type)
    
    greeks = RiskMetrics.greeks(S0, K, T, r, sigma, option_type)
    
    return jsonify({
        'black_scholes_price': float(bs_price),
        'monte_carlo_price': float(mc_price),
        'greeks': {k: float(v) for k, v in greeks.items()}
    })

@app.route('/risk', methods=['POST'])
def risk_analysis():
    """Endpoint for portfolio risk analysis"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input data"}), 400
    
    portfolio = data.get('portfolio', [])
    if not portfolio:
        return jsonify({"error": "Empty portfolio"}), 400
    
    portfolio_paths = []
    weights = []
    
    for asset in portfolio:
        S0 = asset.get('spot', 100)
        sigma = asset.get('volatility', 0.2)
        weight = asset.get('weight', 1.0)
        
        paths = StochasticProcesses.geometric_brownian_motion(
            S0, data.get('rate', 0.05), sigma, 
            data.get('horizon', 1), 252, 1000
        )
        
        portfolio_paths.append(paths)
        weights.append(weight)
    
    weights = np.array(weights) / sum(weights)
    
    portfolio_values = np.zeros((1000, 253))
    for i, paths in enumerate(portfolio_paths):
        portfolio_values += paths * weights[i]
    
    portfolio_returns = np.diff(portfolio_values, axis=1) / portfolio_values[:, :-1]
    
    var_95 = RiskMetrics.value_at_risk(portfolio_returns.flatten(), 0.95)
    cvar_95 = RiskMetrics.conditional_var(portfolio_returns.flatten(), 0.95)
    sharpe = RiskMetrics.sharpe_ratio(portfolio_returns.flatten(), data.get('rate', 0.05)/252)
    max_dd = RiskMetrics.maximum_drawdown(portfolio_values.mean(axis=0))
    
    return jsonify({
        'value_at_risk_95': float(var_95),
        'conditional_var_95': float(cvar_95),
        'sharpe_ratio': float(sharpe),
        'maximum_drawdown': float(max_dd),
        'expected_return': float(np.mean(portfolio_returns) * 252),
        'volatility': float(np.std(portfolio_returns) * np.sqrt(252))
    })

if __name__ == '__main__':
    port = 5001
    print(f"Starting Quantitative Finance API at http://localhost:{port}/")
    app.run(debug=True, host='0.0.0.0', port=port) 