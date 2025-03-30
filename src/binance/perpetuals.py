import pandas as pd
from dataclasses import dataclass
from enum import Enum


class PositionSide(Enum):
    LONG = 'LONG'
    SHORT = 'SHORT'


@dataclass
class PerpetualPosition:
    symbol: str
    entry_price: float
    quantity: float
    side: PositionSide
    leverage: int = 1
    
    def pnl(self, current_price):
        """Calculate PnL of the position"""
        if self.side == PositionSide.LONG:
            return self.quantity * (current_price - self.entry_price)
        else:
            return self.quantity * (self.entry_price - current_price)
    
    def liquidation_price(self):
        """Calculate liquidation price based on leverage"""
        maintenance_margin = 0.02  # 2% maintenance margin
        if self.side == PositionSide.LONG:
            return self.entry_price * (1 - (1 / self.leverage) + maintenance_margin)
        else:
            return self.entry_price * (1 + (1 / self.leverage) - maintenance_margin)


class BinancePerpetualExchange:
    def __init__(self, starting_balance=10000):
        self.balance = starting_balance
        self.positions = {}
        self.trade_history = []
        self.funding_rate = 0.0001  # 0.01% per funding interval (8h)
        
    def open_position(self, symbol, side, quantity, price, leverage=1):
        """Open a new perpetual futures position"""
        position_cost = quantity * price / leverage
        
        if position_cost > self.balance:
            raise ValueError(f"Insufficient balance: {self.balance} < {position_cost}")
            
        position = PerpetualPosition(
            symbol=symbol,
            entry_price=price,
            quantity=quantity,
            side=side,
            leverage=leverage
        )
        
        self.positions[symbol] = position
        self.balance -= position_cost
        
        # Record trade
        self.trade_history.append({
            'timestamp': pd.Timestamp.now(),
            'symbol': symbol,
            'side': side.value,
            'action': 'OPEN',
            'quantity': quantity,
            'price': price,
            'balance': self.balance
        })
        
        return position
    
    def close_position(self, symbol, price):
        """Close an existing position"""
        if symbol not in self.positions:
            raise ValueError(f"No open position for {symbol}")
            
        position = self.positions[symbol]
        pnl = position.pnl(price)
        
        # Return initial margin + PnL
        position_cost = position.quantity * position.entry_price / position.leverage
        self.balance += position_cost + pnl
        
        # Record trade
        self.trade_history.append({
            'timestamp': pd.Timestamp.now(),
            'symbol': symbol,
            'side': position.side.value,
            'action': 'CLOSE',
            'quantity': position.quantity,
            'price': price,
            'pnl': pnl,
            'balance': self.balance
        })
        
        del self.positions[symbol]
        return pnl
    
    def apply_funding_payment(self, symbol, funding_rate=None):
        """Apply funding payment to position"""
        if funding_rate is None:
            funding_rate = self.funding_rate
            
        if symbol in self.positions:
            position = self.positions[symbol]
            # Longs pay shorts when funding rate is positive
            # Shorts pay longs when funding rate is negative
            payment = position.quantity * position.entry_price * funding_rate
            
            if position.side == PositionSide.LONG:
                self.balance -= payment
            else:
                self.balance += payment
                
            self.trade_history.append({
                'timestamp': pd.Timestamp.now(),
                'symbol': symbol,
                'action': 'FUNDING',
                'amount': payment,
                'balance': self.balance
            })
