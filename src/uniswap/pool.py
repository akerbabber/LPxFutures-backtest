import numpy as np
from dataclasses import dataclass


@dataclass
class UniswapV2Position:
    eth_amount: float
    usdc_amount: float
    initial_price: float
    
    @property
    def k(self):
        """Calculate constant product k"""
        return self.eth_amount * self.usdc_amount
    
    def value_at_price(self, current_price):
        """Calculate the dollar value of position at current ETH price"""
        # Calculate implied amounts based on constant product formula
        # x * y = k
        sqrt_ratio = np.sqrt(current_price / self.initial_price)
        eth_new = self.eth_amount / sqrt_ratio
        usdc_new = self.usdc_amount * sqrt_ratio
        
        # Calculate dollar value
        return eth_new * current_price + usdc_new
    
    def hodl_value_at_price(self, current_price):
        """Calculate what the dollar value would be if just held"""
        return self.eth_amount * current_price + self.usdc_amount
    
    def impermanent_loss_pct(self, current_price):
        """Calculate impermanent loss as a percentage"""
        lp_value = self.value_at_price(current_price)
        hodl_value = self.hodl_value_at_price(current_price)
        return (lp_value / hodl_value) - 1
    
    def calculate_delta(self):
        """Calculate the delta exposure of the position"""
        # Delta of ETH in the pool
        # This is less than the actual amount due to the pool rebalancing
        return self.eth_amount * 0.5


class UniswapV2Pool:
    def __init__(self, initial_eth_price, initial_eth_reserve, initial_usdc_reserve):
        self.eth_price = initial_eth_price
        self.eth_reserve = initial_eth_reserve
        self.usdc_reserve = initial_usdc_reserve
        self.k = initial_eth_reserve * initial_usdc_reserve
    
    def add_liquidity(self, eth_amount, usdc_amount):
        """Add liquidity to the pool and return a position object"""
        self.eth_reserve += eth_amount
        self.usdc_reserve += usdc_amount
        self.k = self.eth_reserve * self.usdc_reserve
        
        return UniswapV2Position(
            eth_amount=eth_amount,
            usdc_amount=usdc_amount,
            initial_price=self.eth_price
        )
    
    def update_price(self, new_eth_price):
        """Update the pool based on a new ETH price"""
        # Calculate new reserves based on constant product formula
        # ETH price = USDC / ETH
        # Therefore: USDC reserve / ETH reserve = ETH price
        # And k = ETH reserve * USDC reserve
        
        self.eth_reserve = np.sqrt(self.k / new_eth_price)
        self.usdc_reserve = np.sqrt(self.k * new_eth_price)
        self.eth_price = new_eth_price
        
    def get_current_price(self):
        """Return the current ETH price in the pool"""
        return self.usdc_reserve / self.eth_reserve
