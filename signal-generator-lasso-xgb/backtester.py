"""
Custom Backtester with Execution Logic
- ATR and Volatility-triggered Entry
- Fixed or dynamic SL/TP
- Handles ambiguous bars (both stop and target hit)
"""

import pandas as pd
import random
import matplotlib.pyplot as plt

# --- Tunable Parameters ---
TARGET_RETURN = 0.1          # Fixed target return
LEVERAGE = 5                 # Position leverage
MAX_RISK = 0.05              # Max loss per trade (5%)
MAKER_FEE = 0.0002 * LEVERAGE
ATR_MULTIPLIER = 2           # ATR-based entry filter (set to 0 to disable)
STOP_ATR_MULTIPLIER = 0      # SL multiplier based on ATR or volatility
TARGET_ATR_MULTIPLIER = 0    # TP multiplier based on ATR or volatility
MAX_WAIT_BARS = 5            # Max bars to wait for trigger after signal

# --- Initialize State ---
balance = 100.0
peak_balance = balance
max_drawdown = 0.0
entry_price = entry_index = None
lowest_equity_in_trade = None
in_position = False
waiting_for_entry = False
waiting_direction = None
waiting_trigger_price = None
waiting_bar_count = 0
stop_price = target_price = None

trades = []
equity_curve = []
timestamps = []
win_count = lose_count = ambiguous_count = 0
ambiguous_indexes = []

# --- Replace with actual data loading ---
df = pd.DataFrame()     # should contain Position, High, Low, Close, Rolling_TR
df_1m = pd.DataFrame()  # should contain Realized_Vol_6

# --- Helper: Resolve ambiguous bar ---
def resolve_ambiguous_trade(bar_low, bar_high, stop, target, direction):
    if direction > 0:
        ambiguous = bar_low <= stop and bar_high >= target
    else:
        ambiguous = bar_low <= target and bar_high >= stop
    return target if random.random() < 0.5 else stop if ambiguous else None

# --- Main Loop ---
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

# --- Reporting ---
print(f"Final Balance: {balance:.2f}")
print(f"Max Drawdown: {max_drawdown:.2%}")
print(f"Wins: {win_count}, Losses: {lose_count}, Win Rate: {win_count / max(1, (win_count + lose_count)):.2%}")
print(f"Ambiguous Trades: {ambiguous_count}")

# --- Plot Equity ---
plt.figure(figsize=(12,6))
plt.plot(timestamps, equity_curve, label='Equity Curve')
plt.title('Equity Curve (Execution-Aware Backtest)')
plt.xlabel('Bar Index')
plt.ylabel('Balance')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
