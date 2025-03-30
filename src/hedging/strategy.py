from src.binance.perpetuals import PositionSide
import numpy as np


class UniswapHedgingStrategy:
    def __init__(self, uniswap_pool, binance_exchange, rebalance_threshold=0.05):
        """
        Initialize hedging strategy
        
        Args:
            uniswap_pool: UniswapV2Pool instance
            binance_exchange: BinancePerpetualExchange instance
            rebalance_threshold: Price change threshold (in %) to trigger rebalance
        """
        self.uniswap_pool = uniswap_pool
        self.binance_exchange = binance_exchange
        self.rebalance_threshold = rebalance_threshold
        self.lp_position = None
        self.last_rebalance_price = None
        self.symbol = "ETHUSDC"
        
    def provide_liquidity(self, eth_amount, usdc_amount):
        """Provide liquidity to Uniswap pool and set up initial hedge"""
        # Add liquidity to Uniswap pool
        self.lp_position = self.uniswap_pool.add_liquidity(eth_amount, usdc_amount)
        current_price = self.uniswap_pool.get_current_price()
        self.last_rebalance_price = current_price
        
        # Calculate delta exposure and create hedge
        self._update_hedge(current_price)
        
    def _update_hedge(self, current_price):
        """Update hedge position based on current price"""
        if self.lp_position is None:
            return
            
        # Calculate delta exposure that needs to be hedged
        # For Uniswap V2, we need to short approximately half of our ETH exposure
        eth_delta = self.lp_position.calculate_delta()
        
        # Close existing hedge if any
        if self.symbol in self.binance_exchange.positions:
            self.binance_exchange.close_position(self.symbol, current_price)
            
        # Open new short position to hedge delta exposure
        if eth_delta > 0:
            self.binance_exchange.open_position(
                symbol=self.symbol,
                side=PositionSide.SHORT,
                quantity=eth_delta,
                price=current_price,
                leverage=3  # Using 3x leverage for capital efficiency
            )
            
        self.last_rebalance_price = current_price
        
    def check_and_rebalance(self, current_price):
        """Check if rebalance is needed and perform if necessary"""
        if self.lp_position is None or self.last_rebalance_price is None:
            return False
            
        # Calculate price change since last rebalance
        price_change_pct = abs(current_price / self.last_rebalance_price - 1)
        
        # Rebalance if price changed beyond threshold
        if price_change_pct > self.rebalance_threshold:
            self._update_hedge(current_price)
            return True
            
        return False
        
    def get_total_pnl(self, current_price):
        """Calculate total PnL of the combined position (LP + hedge)"""
        if self.lp_position is None:
            return 0
            
        # Calculate LP position value
        lp_value = self.lp_position.value_at_price(current_price)
        initial_value = self.lp_position.hodl_value_at_price(self.lp_position.initial_price)
        lp_pnl = lp_value - initial_value
        
        # Calculate hedge PnL
        hedge_pnl = 0
        if self.symbol in self.binance_exchange.positions:
            position = self.binance_exchange.positions[self.symbol]
            hedge_pnl = position.pnl(current_price)
            
        return lp_pnl + hedge_pnl
