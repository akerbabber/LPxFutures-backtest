```mermaid
flowchart TD
    A[Start: Initialize Bot & Load Configurations]
    B[Gather Uniswap V2 Pool Data\n& Binance Market Data]
    C[Calculate Pool Delta Exposure\n& Impermanent Loss Risk]
    D[Determine Hedge Requirements\n(Target Binance Position)]
    E[Submit Hedge Orders on Binance]
    F[Monitor Order Fill & Update Exposure]
    G[Risk Management & Rebalancing Check]
    H[Log Trades, Metrics & Update Dashboard]
    I[Backtest Module:\nReplay Historical Data]
    J[Analyze Backtest Performance\n& Metrics]
    K[End/Wait for Next Cycle]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> K
    F --> I
    I --> J
```
