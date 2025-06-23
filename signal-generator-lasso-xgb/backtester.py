import random
import matplotlib.pyplot as plt

DEFAULT_PARAMS = {
    'INITIAL_BALANCE': 100.0,           # Starting capital for the strategy
    'LEVERAGE': 5,                      # Leverage factor applied to each trade
    'MAX_RISK': 0.05,                   # Maximum risk per trade as a fraction of balance
    'MAKER_FEE': 0.0002,                # Fee per trade (e.g., for placing limit orders)
    'ATR_MULTIPLIER': 2,                # Multiplier for ATR or volatility-based entry conditions
    'STOP_ATR_MULTIPLIER': 0,           # Multiplier for stop loss based on ATR/volatility
    'TARGET_ATR_MULTIPLIER': 0,         # Multiplier for take profit based on ATR/volatility
    'MAX_WAIT_BARS': 5,                 # Max number of bars to wait for entry after signal
    'TARGET_RETURN': 0.1,               # Default profit target as a fraction of price (if no ATR target used)
    'K_VOL': 2.0                        # Volatility threshold for filters (optional use)
}

def run_backtest(df, df_1m, params=DEFAULT_PARAMS):
    """
    Executes a modular execution-aware backtest on trading signals.

    Parameters:
    - df: DataFrame containing main OHLC data and signal column ('Position')
    - df_1m: DataFrame containing finer-granularity features (e.g., volatility)
    - params: Dictionary of configurable strategy parameters

    Returns:
    - Dictionary containing equity curve, timestamps, trades, and summary statistics
    """
    balance = params['INITIAL_BALANCE']
    peak_balance = balance
    equity_curve = []
    timestamps = []
    trades = []

    in_position = False
    entry_price = None
    entry_index = None
    trade_direction = None
    lowest_equity_in_trade = None
    waiting_for_entry = False
    waiting_direction = None
    waiting_signal_index = None
    waiting_trigger_price = None
    waiting_bar_count = 0
    stop_price = None
    target_price = None

    win_count = 0
    lose_count = 0
    ambiguous_count = 0
    ambiguous_indexes = []
    max_drawdown = 0

    for i in range(1, len(df)):
        current_signal = df['Position'].iloc[i]

        # [ ... full loop logic goes here ... same as before, use params['KEY'] instead of globals ... ]

        equity_curve.append(balance)
        timestamps.append(i)

    # --- Summary Metrics ---
    summary = {
        "final_balance": balance,  # Final account balance after all trades
        "peak_balance": peak_balance,  # Highest balance reached during the backtest
        "max_drawdown": max_drawdown,  # Maximum drawdown as a percentage from peak
        "win_count": win_count,  # Total number of winning trades
        "lose_count": lose_count,  # Total number of losing trades
        "ambiguous_count": ambiguous_count,  # Number of ambiguous outcomes where both SL/TP hit
        "win_rate": win_count / (win_count + lose_count) if (win_count + lose_count) > 0 else 0,  # Win rate as %
        "ambiguous_rate": ambiguous_count / (win_count + lose_count) if (win_count + lose_count) > 0 else 0,  # Ambiguity rate
        "ambiguous_indexes": ambiguous_indexes  # Indices of bars with ambiguous trade outcomes
    }

    return {
        "equity_curve": equity_curve,
        "timestamps": timestamps,
        "trades": trades,
        "summary": summary
    }

def plot_equity_curve(timestamps, equity_curve):
    """
    Plot the account balance (equity curve) over time.

    Parameters:
    - timestamps: List of time indices (typically bar numbers) where equity was recorded.
    - equity_curve: List of account balance values corresponding to each timestamp.

    Displays a matplotlib line plot showing how the equity evolved during the backtest.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, equity_curve, label='Equity Curve')
    plt.title('Equity Curve')
    plt.xlabel('Bar Index')
    plt.ylabel('Balance')
    plt.grid(True)
    plt.legend()
    plt.show()
