import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.uniswap.pool import UniswapV2Pool
from src.binance.perpetuals import BinancePerpetualExchange
from src.hedging.strategy import UniswapHedgingStrategy


class BacktestRunner:
    def __init__(self, price_data, initial_price, eth_reserve=1000, usdc_reserve=None):
        """
        Initialize backtest runner
        
        Args:
            price_data: DataFrame with columns ['timestamp', 'price']
            initial_price: Initial ETH price
            eth_reserve: Initial ETH reserve in pool
            usdc_reserve: Initial USDC reserve in pool (calculated from price if None)
        """
        if usdc_reserve is None:
            usdc_reserve = eth_reserve * initial_price
            
        self.price_data = price_data
        self.uniswap_pool = UniswapV2Pool(initial_price, eth_reserve, usdc_reserve)
        self.binance_exchange = BinancePerpetualExchange()
        self.strategy = UniswapHedgingStrategy(self.uniswap_pool, self.binance_exchange)
        self.results = None
        
    def run(self, eth_amount=10, usdc_amount=None, rebalance_threshold=0.05):
        """
        Run backtest
        
        Args:
            eth_amount: ETH amount to provide as liquidity
            usdc_amount: USDC amount (calculated from price if None)
            rebalance_threshold: Price change threshold to trigger rebalance
        """
        if usdc_amount is None:
            usdc_amount = eth_amount * self.price_data['price'].iloc[0]
            
        self.strategy.rebalance_threshold = rebalance_threshold
        
        # Provide initial liquidity
        self.strategy.provide_liquidity(eth_amount, usdc_amount)
        
        # Initialize results tracking
        results = []
        initial_value = eth_amount * self.price_data['price'].iloc[0] + usdc_amount
        
        # Track funding payments (every 8 hours)
        funding_interval = pd.Timedelta(hours=8)
        last_funding = self.price_data['timestamp'].iloc[0]
        
        # Run through price data
        for _, row in self.price_data.iterrows():
            current_price = row['price']
            timestamp = row['timestamp']
            
            # Update pool price
            self.uniswap_pool.update_price(current_price)
            
            # Check and possibly rebalance hedge
            rebalanced = self.strategy.check_and_rebalance(current_price)
            
            # Apply funding payment if 8 hours have passed
            if timestamp - last_funding >= funding_interval:
                self.binance_exchange.apply_funding_payment(self.strategy.symbol)
                last_funding = timestamp
            
            # Calculate position stats
            lp_position = self.strategy.lp_position
            lp_value = lp_position.value_at_price(current_price)
            hodl_value = lp_position.hodl_value_at_price(current_price)
            il_pct = lp_position.impermanent_loss_pct(current_price)
            
            # Calculate combined PnL
            total_pnl = self.strategy.get_total_pnl(current_price)
            total_value = initial_value + total_pnl
            
            # Get hedge position if exists
            hedge_position = None
            hedge_pnl = 0
            if self.strategy.symbol in self.binance_exchange.positions:
                hedge_position = self.binance_exchange.positions[self.strategy.symbol]
                hedge_pnl = hedge_position.pnl(current_price)
            
            # Record results
            results.append({
                'timestamp': timestamp,
                'price': current_price,
                'lp_value': lp_value,
                'hodl_value': hodl_value,
                'il_pct': il_pct,
                'hedge_pnl': hedge_pnl,
                'total_pnl': total_pnl,
                'total_value': total_value,
                'rebalanced': rebalanced
            })
            
        self.results = pd.DataFrame(results)
        return self.results
    
    def plot_results(self):
        """Plot backtest results"""
        if self.results is None:
            raise ValueError("No results to plot. Run backtest first.")
            
        fig, axes = plt.subplots(3, 1, figsize=(14, 18), sharex=True)
        
        # Plot 1: ETH Price
        axes[0].plot(self.results['timestamp'], self.results['price'], label='ETH Price')
        axes[0].set_title('ETH Price')
        axes[0].set_ylabel('USD')
        axes[0].legend()
        axes[0].grid(True)
        
        # Plot 2: Value Comparison
        axes[1].plot(self.results['timestamp'], self.results['lp_value'], label='LP Value')
        axes[1].plot(self.results['timestamp'], self.results['hodl_value'], label='HODL Value')
        axes[1].plot(self.results['timestamp'], self.results['total_value'], label='Total Value (LP + Hedge)')
        axes[1].set_title('Value Comparison')
        axes[1].set_ylabel('USD')
        axes[1].legend()
        axes[1].grid(True)
        
        # Plot 3: PnL and IL
        axes[2].plot(self.results['timestamp'], self.results['il_pct'] * 100, label='Impermanent Loss %')
        axes[2].plot(self.results['timestamp'], self.results['hedge_pnl'], label='Hedge PnL')
        axes[2].plot(self.results['timestamp'], self.results['total_pnl'], label='Total PnL')
        
        # Mark rebalance points
        rebalance_points = self.results[self.results['rebalanced']]
        axes[2].scatter(rebalance_points['timestamp'], rebalance_points['total_pnl'], 
                       color='red', marker='^', label='Rebalance')
                       
        axes[2].set_title('PnL and Impermanent Loss')
        axes[2].set_ylabel('USD / Percent')
        axes[2].legend()
        axes[2].grid(True)
        
        plt.tight_layout()
        return fig, axes
