# Uniswap V2 Impermanent Loss Hedging Bot

This project implements a trading bot that hedges impermanent loss on Uniswap V2 ETH/USDC pools using perpetuals on Binance.

## Strategy Overview

The strategy mitigates impermanent loss for liquidity providers by:
1. Monitoring LP positions in Uniswap V2 ETH/USDC pool
2. Calculating exposure changes caused by price movements
3. Opening corresponding hedge positions on Binance perpetuals
4. Rebalancing the hedge when necessary based on price thresholds

## Project Structure

- `src/`: Source code for the bot
  - `uniswap/`: Uniswap V2 pool simulation and interface
  - `binance/`: Binance perpetuals API interface
  - `hedging/`: Core hedging strategy logic
  - `backtesting/`: Backtesting framework
- `data/`: Historical price and liquidity data
- `notebooks/`: Analysis notebooks
- `tests/`: Test cases
- `config/`: Configuration files

## Setup and Usage

See [SETUP.md](./SETUP.md) for installation and usage instructions.
