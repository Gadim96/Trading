import numpy as np

def evaluate_trades(trades, risk_free_rate=0.0, periods_per_year=1460):
    """
    Evaluate trade performance: mean return, std dev, Sharpe ratio, win rate, etc.
    
    Args:
        trades (list of dicts): Each trade must have 'pnl' and 'entry_balance'.
        risk_free_rate (float): Optional, usually 0 for crypto.
        periods_per_year (int): Annualization factor, e.g., 1460 for ~4 trades/day.
    
    Returns:
        dict: Performance metrics.
    """
    if not trades:
        return None

    # Compute returns as return on capital at risk (not asset price!)
    returns = np.array([
        trade['pnl'] / trade['entry_balance'] 
        for trade in trades 
        if trade['entry_balance'] > 0
    ])

    if len(returns) == 0:
        return None

    mean_return = np.mean(returns)
    std_return = np.std(returns)
    sharpe = (mean_return - risk_free_rate) / std_return if std_return != 0 else np.nan
    annualized_sharpe = sharpe * np.sqrt(periods_per_year) if not np.isnan(sharpe) else np.nan

    win_count = np.sum(returns > 0)
    loss_count = np.sum(returns <= 0)
    win_rate = win_count / (win_count + loss_count) if (win_count + loss_count) > 0 else np.nan

    return {
        'Mean Return (per trade)': mean_return,
        'Std of Return (per trade)': std_return,
        'Sharpe (per trade)': sharpe,
        'Sharpe (annualized)': annualized_sharpe,
        'Win Rate': win_rate,
        'Num Trades': len(returns)
    }
