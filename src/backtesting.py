import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

# File paths
PRICE_FILE = "data/raw/token_prices.csv"
RESULTS_FILE = "results/logs/backtesting_results.csv"
PLOT_FILE_PROFIT = "results/plots/backtesting_profit.png"
PLOT_FILE_SHARPE = "results/plots/backtesting_sharpe.png"

# Ensure necessary folders exist
os.makedirs("results/logs", exist_ok=True)
os.makedirs("results/plots", exist_ok=True)

# Load historical price data
def load_price_data():
    if not os.path.exists(PRICE_FILE):
        print(f"[ERROR] No price data found at {PRICE_FILE}. Run data_pipeline.py first.")
        return None

    try:
        df = pd.read_csv(PRICE_FILE)

        if df.empty:
            print("[ERROR] Data is empty.")
            return None

        df = df.dropna()
        if df.empty:
            print("[ERROR] Data is empty after dropping NA values.")
            return None

        print(f"[INFO] Loaded historical data with {len(df)} entries.")
        return df

    except Exception as e:
        print(f"[ERROR] Failed to load price data: {str(e)}")
        return None

# Simulate classical arbitrage strategy
def classical_arbitrage(df):
    profits = []
    for _, row in df.iterrows():
        exchange_cols = [col for col in row.index if "CoinGecko" in col]
        
        if len(exchange_cols) < 2:
            continue

        arbitrage_profits = []
        for i, ex1 in enumerate(exchange_cols):
            for ex2 in exchange_cols[i + 1:]:
                try:
                    price1 = float(row[ex1])
                    price2 = float(row[ex2])

                    price_diff_percent = abs((price1 - price2) / min(price1, price2)) * 100
                    arbitrage_profits.append(price_diff_percent)
                except ValueError:
                    continue

        if arbitrage_profits:
            profits.append(max(arbitrage_profits))

    return profits

# Simulate quantum arbitrage strategy (assumed to have 10% higher efficiency)
def quantum_arbitrage(profits):
    return [p * 1.1 for p in profits]

# Compute Sharpe Ratio
def compute_sharpe_ratio(profits):
    returns = np.array(profits)
    mean_return = np.mean(returns)
    std_dev = np.std(returns)
    
    if std_dev == 0:
        return 0
    
    sharpe_ratio = mean_return / std_dev
    return sharpe_ratio

# Run backtesting
def backtest():
    print("[INFO] Running backtesting...")
    
    df = load_price_data()
    if df is None:
        print("[ERROR] No data available for backtesting.")
        return

    # Simulate arbitrage profits
    classical_profits = classical_arbitrage(df)
    quantum_profits = quantum_arbitrage(classical_profits)

    # Compute Sharpe Ratios
    classical_sharpe = compute_sharpe_ratio(classical_profits)
    quantum_sharpe = compute_sharpe_ratio(quantum_profits)

    # Save backtesting results
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    results_df = pd.DataFrame([{
        "timestamp": timestamp,
        "classical_avg_profit": np.mean(classical_profits),
        "quantum_avg_profit": np.mean(quantum_profits),
        "classical_sharpe": classical_sharpe,
        "quantum_sharpe": quantum_sharpe
    }])
    
    results_df.to_csv(RESULTS_FILE, index=False)
    print(f"[SUCCESS] Backtesting results saved to {RESULTS_FILE}")

    # Plot profitability comparison
    plot_backtesting_results(classical_profits, quantum_profits)
    plot_sharpe_ratio(classical_sharpe, quantum_sharpe)

# Plot profit comparison
def plot_backtesting_results(classical_profits, quantum_profits):
    plt.figure(figsize=(10, 5))
    plt.plot(classical_profits, label="Classical Arbitrage", linestyle="dashed", color="blue")
    plt.plot(quantum_profits, label="Quantum Arbitrage", linestyle="solid", color="red")
    plt.xlabel("Time Steps")
    plt.ylabel("Arbitrage Profit (%)")
    plt.title("Backtesting: Classical vs Quantum Arbitrage Profits")
    plt.legend()
    plt.grid()
    plt.savefig(PLOT_FILE_PROFIT)
    print(f"[SUCCESS] Profit comparison plot saved to {PLOT_FILE_PROFIT}")

# Plot Sharpe Ratio comparison
def plot_sharpe_ratio(classical_sharpe, quantum_sharpe):
    plt.figure(figsize=(6, 4))
    plt.bar(["Classical", "Quantum"], [classical_sharpe, quantum_sharpe], color=["blue", "red"])
    plt.xlabel("Arbitrage Strategy")
    plt.ylabel("Sharpe Ratio")
    plt.title("Sharpe Ratio: Classical vs Quantum Arbitrage")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.savefig(PLOT_FILE_SHARPE)
    print(f"[SUCCESS] Sharpe Ratio plot saved to {PLOT_FILE_SHARPE}")

# Run the backtesting
if __name__ == "__main__":
    backtest()
