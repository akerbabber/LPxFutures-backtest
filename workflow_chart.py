import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import numpy as np
import os

def create_workflow_chart():
    """Create a workflow chart for the hedging bot strategy"""
    fig, ax = plt.subplots(figsize=(12, 12))
    
    # Helper functions for creating boxes and arrows
    def create_box(x, y, width, height, label, color='skyblue', alpha=0.8):
        rect = Rectangle((x, y), width, height, facecolor=color, alpha=alpha, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x + width/2, y + height/2, label, ha='center', va='center', fontweight='bold')
        return rect
    
    def create_arrow(start, end, label=None, color='black'):
        arrow = FancyArrowPatch(start, end, arrowstyle='->', linewidth=1.5, color=color, 
                                connectionstyle='arc3,rad=0.1', shrinkA=5, shrinkB=5)
        ax.add_patch(arrow)
        if label:
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            ax.text(mid_x, mid_y, label, ha='center', va='center', fontsize=9)
        return arrow
    
    # Create the workflow boxes
    price_monitor = create_box(2, 9, 4, 1, "ETH Price Monitor")
    lp_position = create_box(2, 7, 4, 1, "Uniswap V2 LP Position")
    delta_calc = create_box(2, 5, 4, 1, "Delta Exposure Calculation")
    hedge_position = create_box(2, 3, 4, 1, "Binance Perpetual Short")
    rebalancing = create_box(8, 6, 4, 1, "Rebalancing Logic")
    
    # Create arrows
    create_arrow((4, 9), (4, 8), "Price Updates")
    create_arrow((4, 8), (4, 7))
    create_arrow((4, 7), (4, 6), "Position Data")
    create_arrow((4, 6), (4, 5))
    create_arrow((4, 5), (4, 4), "Calculated Delta")
    create_arrow((4, 4), (4, 3))
    create_arrow((6, 9), (8, 6.5), "Price Change > Threshold?")
    create_arrow((8, 6), (6, 3.5), "Trigger Rebalance")
    
    # Add event flow on the left
    events = [
        "1. LP Deposits ETH+USDC",
        "2. ETH Price Changes",
        "3. AMM Rebalances Pool",
        "4. IL Risk Increases",
        "5. Bot Detects & Hedges",
        "6. Neutralizes Delta Exposure"
    ]
    
    for i, event in enumerate(events):
        ax.text(0.5, 9 - i*1.2, event, ha='left', va='center', fontsize=10, 
                bbox=dict(facecolor='lightyellow', alpha=0.5, boxstyle='round,pad=0.5'))
    
    # Add notes on the right
    notes = [
        "• Strategy monitors impermanent loss risk",
        "• ETH price movements trigger rebalancing",
        "• Short futures position neutralizes delta",
        "• Hedging cost minimized via threshold",
        "• Performance metrics tracked & reported"
    ]
    
    for i, note in enumerate(notes):
        ax.text(10, 3 - i*0.6, note, ha='left', va='center', fontsize=10, 
                bbox=dict(facecolor='lightgreen', alpha=0.3, boxstyle='round,pad=0.3'))
    
    # Add title and labels
    ax.set_title('Uniswap V2 Impermanent Loss Hedging Bot - Workflow', fontsize=14, fontweight='bold')
    
    # Set limits and remove axes
    ax.set_xlim(0, 13)
    ax.set_ylim(1, 11)
    ax.axis('off')
    
    # Save the chart
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/workflow_chart.png', dpi=300, bbox_inches='tight')
    plt.tight_layout()
    
    return fig, ax

if __name__ == "__main__":
    fig, ax = create_workflow_chart()
    plt.show()
