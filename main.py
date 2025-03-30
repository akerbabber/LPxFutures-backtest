import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta
import os
from src.backtesting.backtest import BacktestRunner

def fetch_price_data(start_date='2022-01-01', end_date='2022-12-31'):
    """
    Fetch ETH price data from Yahoo Finance
    """
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    cache_file = f"data/eth_prices_{start_date}_to_{end_date}.csv"
    
    # Check if we have cached data
    if os.path.exists(cache_file):
        print(f"Loading cached price data from {cache_file}")
        price_data = pd.read_csv(cache_file)
        price_data['timestamp'] = pd.to_datetime(price_data['timestamp'])
        return price_data
    
    print(f"Fetching ETH price data from {start_date} to {end_date}")
    eth_data = yf.download('ETH-USD', start=start_date, end=end_date, interval='1h')
    
    # Format data for our needs
    price_data = pd.DataFrame({
        'timestamp': eth_data.index,
        'price': eth_data['Close']
    }).dropna()
    
    # Save to cache
    price_data.to_csv(cache_file, index=False)
    
    return price_data

def run_backtest(price_data, eth_amount=10, rebalance_threshold=0.05):
    """
    Run the hedging strategy backtest
    """
    initial_price = price_data['price'].iloc[0]
    
    # Initialize and run backtest
    backtest = BacktestRunner(price_data, initial_price)
    results = backtest.run(
        eth_amount=eth_amount,
        rebalance_threshold=rebalance_threshold
    )
    
    # Generate plots
    fig, axes = backtest.plot_results()
    
    # Save plots
    os.makedirs('results', exist_ok=True)
    plt.savefig(f'results/backtest_eth_{eth_amount}_threshold_{rebalance_threshold}.png')
    
    # Save results data
    results.to_csv(f'results/backtest_results_eth_{eth_amount}_threshold_{rebalance_threshold}.csv', index=False)
    
    return backtest

def run_parameter_optimization(price_data, eth_amounts=[5, 10, 20], thresholds=[0.01, 0.05, 0.1]):
    """
    Run backtest with different parameters to find optimal settings
    """
    results = []
    
    for eth_amount in eth_amounts:
        for threshold in thresholds:
            print(f"Testing with ETH={eth_amount}, threshold={threshold}")
            
            backtest = BacktestRunner(price_data, price_data['price'].iloc[0])
            backtest_results = backtest.run(
                eth_amount=eth_amount,
                rebalance_threshold=threshold
            )
            
            # Calculate performance metrics
            final_value = backtest_results['total_value'].iloc[-1]
            initial_value = eth_amount * price_data['price'].iloc[0] * 2  # ETH + equivalent USDC
            roi = (final_value / initial_value - 1) * 100
            max_drawdown = ((backtest_results['total_value'].cummax() - backtest_results['total_value']) / 
                           backtest_results['total_value'].cummax()).max() * 100
            
            # Store results
            results.append({
                'eth_amount': eth_amount,
                'threshold': threshold,
                'final_value': final_value,
                'roi': roi,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': roi / max_drawdown if max_drawdown > 0 else np.inf
            })
    
    return pd.DataFrame(results)

def main():
    # Fetch price data
    price_data = fetch_price_data()
    
    # Run single backtest with default parameters
    backtest = run_backtest(price_data)
    
    # Optionally run parameter optimization
    # optimization_results = run_parameter_optimization(price_data)
    # print(optimization_results.sort_values('sharpe_ratio', ascending=False))
    
    # Display results summary
    print("\n--- Backtest Results Summary ---")
    print(f"Start Date: {price_data['timestamp'].min()}")
    print(f"End Date: {price_data['timestamp'].max()}")
    print(f"Initial ETH Price: ${price_data['price'].iloc[0]:.2f}")
    print(f"Final ETH Price: ${price_data['price'].iloc[-1]:.2f}")
    print(f"Price Change: {(price_data['price'].iloc[-1] / price_data['price'].iloc[0] - 1) * 100:.2f}%")
    
    results = backtest.results
    initial_value = results['lp_value'].iloc[0]
    final_lp_value = results['lp_value'].iloc[-1]
    final_hedged_value = results['total_value'].iloc[-1]
    
    print("\nPerformance:")
    print(f"LP Only Return: {(final_lp_value / initial_value - 1) * 100:.2f}%")
    print(f"LP + Hedge Return: {(final_hedged_value / initial_value - 1) * 100:.2f}%")
    print(f"HODL Return: {(results['hodl_value'].iloc[-1] / results['hodl_value'].iloc[0] - 1) * 100:.2f}%")
    print(f"Max Impermanent Loss: {results['il_pct'].min() * 100:.2f}%")
    
    num_rebalances = results['rebalanced'].sum()
    print(f"\nStrategy executed {num_rebalances} rebalances during the backtest period.")
    
    plt.show()

if __name__ == "__main__":
    main()
