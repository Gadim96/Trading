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

def resolve_ambiguous_trade(target_price, stop_price):
    """
    Resolve an ambiguous trade where both stop and target are touched in the same bar.

    Randomly selects whether the trade hit the target or stop loss.

    Returns:
    - exit_price: Price at which the trade is considered exited
    - result: 'win' or 'loss'
    """
    if random.random() < 0.5:
        return target_price, 'win'
    else:
        return stop_price, 'loss'

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
        bar_high = df['High'].iloc[i]
        bar_low = df['Low'].iloc[i]
    
        # --- Waiting for Trigger ---
        if waiting_for_entry:
            if waiting_direction == 1 and bar_low <= waiting_trigger_price:
                entry_price = waiting_trigger_price
            elif waiting_direction == -1 and bar_high >= waiting_trigger_price:
                entry_price = waiting_trigger_price
            else:
                waiting_bar_count += 1
                if waiting_bar_count >= MAX_WAIT_BARS:
                    waiting_for_entry = False
                equity_curve.append(balance)
                timestamps.append(i)
                continue
    
            in_position = True
            trade_direction = waiting_direction
            entry_index = i
            atr = df['Rolling_TR'].iloc[i]
            vol_at_entry = df_1m['Realized_Vol_6'].iat[i]
            entry_balance = balance * (1 - MAKER_FEE)
            balance = entry_balance
            lowest_equity_in_trade = balance
            waiting_for_entry = False
    
            # Set SL/TP
            if STOP_ATR_MULTIPLIER and TARGET_ATR_MULTIPLIER:
                stop_price = entry_price - trade_direction * atr * STOP_ATR_MULTIPLIER
                target_price = entry_price + trade_direction * atr * TARGET_ATR_MULTIPLIER
            else:
                stop_price = entry_price * (1 - MAX_RISK / LEVERAGE) if trade_direction == 1 else entry_price * (1 + MAX_RISK / LEVERAGE)
                target_price = entry_price * (1 + trade_direction * TARGET_RETURN / LEVERAGE)
    
        # --- In Trade ---
        if in_position:
            exit_price = resolve_ambiguous_trade(bar_low, bar_high, stop_price, target_price, trade_direction)
    
            if exit_price is not None:
                ambiguous_count += 1
                ambiguous_indexes.append(i)
            elif (trade_direction == 1 and bar_low <= stop_price) or (trade_direction == -1 and bar_high >= stop_price):
                exit_price = stop_price
                lose_count += 1
            elif (trade_direction == 1 and bar_high >= target_price) or (trade_direction == -1 and bar_low <= target_price):
                exit_price = target_price
                win_count += 1
    
            if exit_price:
                pnl_pct = (exit_price - entry_price) / entry_price * trade_direction
                raw_pnl = pnl_pct * entry_balance * LEVERAGE
                fee = entry_balance * LEVERAGE * MAKER_FEE
                trade_pnl = raw_pnl - fee
                balance += trade_pnl
    
                trades.append({
                    'entry_index': entry_index, 'exit_index': i,
                    'entry_price': entry_price, 'exit_price': exit_price,
                    'pnl': trade_pnl, 'balance_after': balance,
                    'direction': trade_direction
                })
    
                in_position = False
                stop_price = target_price = None
                if balance > peak_balance:
                    peak_balance = balance
                max_drawdown = max(max_drawdown, (peak_balance - balance) / peak_balance)
    
        # --- New Signal ---
        if not in_position and not waiting_for_entry and current_signal != 0:
            atr = df['Rolling_TR'].iloc[i]
            vol_at_entry = df_1m['Realized_Vol_6'].iat[i]
            close_price = df['Close'].iloc[i]
            if ATR_MULTIPLIER == 0:
                entry_price = close_price
                in_position = True
                trade_direction = current_signal
                entry_index = i
                entry_balance = balance * (1 - MAKER_FEE)
                balance = entry_balance
                lowest_equity_in_trade = balance
            else:
                if pd.isna(vol_at_entry):
                    continue
                trigger_price = close_price - vol_at_entry * ATR_MULTIPLIER * close_price if current_signal == 1 else close_price + vol_at_entry * ATR_MULTIPLIER * close_price
                waiting_for_entry = True
                waiting_direction = current_signal
                waiting_trigger_price = trigger_price
                waiting_bar_count = 0
    
        equity_curve.append(balance)
        timestamps.append(i)

            

    # --- Summary Metrics ---
    summary = {
        "final_balance": balance,
        "peak_balance": peak_balance,
        "max_drawdown": max_drawdown,
        "win_count": win_count,
        "lose_count": lose_count,

        # Number of trades with ambiguous bar outcomes (both SL/TP touched)
        "ambiguous_count": ambiguous_count,

        "win_rate": win_count / (win_count + lose_count) if (win_count + lose_count) > 0 else 0,

        # Ambiguity rate: ambiguous trades as a fraction of total trades
        "ambiguous_rate": ambiguous_count / (win_count + lose_count) if (win_count + lose_count) > 0 else 0,

        "ambiguous_indexes": ambiguous_indexes
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
