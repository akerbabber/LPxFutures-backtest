# Setup Instructions

This document provides instructions for setting up the Uniswap V2 Impermanent Loss Hedging Bot project.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for version control)

## Installation

1. Clone the repository (or download and extract the ZIP file):
   ```
   git clone https://github.com/yourusername/LPxFutures-backtest.git
   cd LPxFutures-backtest
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS and Linux
   source venv/bin/activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Backtest

To run the backtest with default parameters:

```
python main.py
```

This will:
1. Download historical ETH price data (or use cached data if available)
2. Run the hedging strategy backtest
3. Generate performance plots and save them to the `results/` directory
4. Print a summary of the backtest results

## Configuration

You can modify the backtest parameters by editing the `main.py` file:

- Change the date range by modifying the `start_date` and `end_date` parameters in the `fetch_price_data()` call
- Adjust the ETH amount for liquidity provision by modifying the `eth_amount` parameter in the `run_backtest()` call
- Change the rebalancing threshold by modifying the `rebalance_threshold` parameter

## Parameter Optimization

To find optimal strategy parameters, uncomment the parameter optimization section in `main.py`:

```python
# Uncomment to run parameter optimization
optimization_results = run_parameter_optimization(price_data)
print(optimization_results.sort_values('sharpe_ratio', ascending=False))
```

This will run multiple backtests with different parameters and return metrics for each combination.
