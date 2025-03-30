# Impermanent Loss Hedging: ETH/USDC Uniswap V2 + Binance Perpetuals

## Strategy Overview

This project implements a trading bot that mitigates impermanent loss for liquidity providers in the Uniswap V2 ETH/USDC pool by utilizing perpetual futures contracts on Binance.

### Problem: Impermanent Loss

Liquidity providers in AMMs like Uniswap V2 face impermanent loss when:
- Asset prices diverge from their initial ratio
- The pool automatically rebalances (sells appreciating assets, buys depreciating ones)
- This can cause significant underperformance compared to just holding the assets

### Solution: Delta Hedging with Perpetuals

Our strategy:
1. **Monitor** LP position in Uniswap V2 ETH/USDC pool
2. **Calculate** delta exposure (effective ETH exposure)
3. **Hedge** by shorting equivalent ETH on Binance perpetuals
4. **Rebalance** when price movements exceed a threshold

## Implementation Details

### Architecture

![Workflow Chart](results/workflow_chart.png)

### Key Components

1. **Uniswap V2 Pool Simulation**
   - Models constant-product AMM mechanics
   - Calculates impermanent loss dynamically
   - Tracks effective asset exposure

2. **Binance Perpetuals Interface**
   - Manages short positions for hedging
   - Handles position sizing and leverage
   - Accounts for funding rates

3. **Hedging Strategy Logic**
   - Dynamic delta calculation
   - Threshold-based rebalancing
   - PnL tracking and performance analysis

## Backtest Results

The strategy was backtested on historical ETH/USD price data from 2022:

### Performance Metrics:
- **LP Only:** Significant impermanent loss during volatile periods
- **LP + Hedge:** Substantially reduced volatility with competitive returns
- **HODL Comparison:** Outperforms LP-only during directional price movements

### Parameter Optimization:
- **Rebalancing Threshold:** 5% provides good balance between hedging costs and protection
- **Position Size:** 10 ETH offers optimal capital efficiency
- **Leverage:** 3x maximizes capital efficiency without excessive liquidation risk

## Conclusion

The hedging strategy successfully:
- Mitigates impermanent loss risk for Uniswap V2 LP positions
- Creates a delta-neutral exposure that performs more consistently
- Maintains competitive returns with significantly reduced volatility
- Automatically adapts to changing market conditions

## Future Improvements

1. Add multi-asset support for concentrated liquidity positions (Uniswap V3)
2. Implement cross-exchange arbitrage to further enhance returns
3. Incorporate on-chain gas optimization for mainnet deployment
4. Add risk management features like stop-loss and position sizing
