'''mermaid
flowchart TD
    A[Start: Initialize Bot & Load Configurations]
    B[Gather Uniswap V2 Pool Data<br/>& Binance Market Data]
    C[Calculate Pool Delta Exposure<br/>& Impermanent Loss Risk]
    D[Determine Hedge Requirements<br/>(Target Binance Position)]
    E[Submit Hedge Orders on Binance]
    F[Monitor Order Fill & Update Exposure]
    G[Risk Management & Rebalancing Check]
    H[Log Trades, Metrics & Update Dashboard]
    I[Backtest Module:<br/>Replay Historical Data]
    J[Analyze Backtest Performance<br/>& Metrics]
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
'''