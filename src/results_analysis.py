import pandas as pd
import matplotlib.pyplot as plt
import os

# File paths
ARBITRAGE_LOGS = "results/logs/arbitrage_trades.csv"
BACKTESTING_RESULTS = "results/logs/backtesting_results.csv"
PLOT_PROFIT_DIST = "results/plots/profitability_distribution.png"
PLOT_EXECUTION_TIMES = "results/plots/execution_times_histogram.png"

# Ensure results/plots directory exists
os.makedirs("results/plots", exist_ok=True)

# Load trade execution logs
def load_trade_logs():
    if not os.path.exists(ARBITRAGE_LOGS):
        print(f"[ERROR] No arbitrage trade logs found at {ARBITRAGE_LOGS}.")
        return None
    return pd.read_csv(ARBITRAGE_LOGS)

# Load backtesting results
def load_backtesting_results():
    if not os.path.exists(BACKTESTING_RESULTS):
        print(f"[ERROR] No backtesting results found at {BACKTESTING_RESULTS}.")
        return None
    return pd.read_csv(BACKTESTING_RESULTS)

# Plot profit distribution
def plot_profit_distribution(df):
    plt.figure(figsize=(8, 5))
    plt.hist(df["profit"], bins=10, color="blue", alpha=0.7, edgecolor="black")
    plt.xlabel("Arbitrage Profit (%)")
    plt.ylabel("Frequency")
    plt.title("Distribution of Arbitrage Profitability")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.savefig(PLOT_PROFIT_DIST)
    print(f"[SUCCESS] Profitability distribution plot saved to {PLOT_PROFIT_DIST}")

# Plot execution time histogram
def plot_execution_times(df):
    plt.figure(figsize=(8, 5))
    plt.hist(df["execution_time"], bins=5, color="green", alpha=0.7, edgecolor="black")
    plt.xlabel("Execution Time (seconds)")
    plt.ylabel("Frequency")
    plt.title("Histogram of Arbitrage Execution Times")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.savefig(PLOT_EXECUTION_TIMES)
    print(f"[SUCCESS] Execution times histogram saved to {PLOT_EXECUTION_TIMES}")

# Run results analysis
def analyze_results():
    print("[INFO] Starting results analysis...")

    # Load trade logs
    trade_logs = load_trade_logs()
    if trade_logs is not None and not trade_logs.empty:
        print(f"[INFO] Analyzing {len(trade_logs)} executed trades...")
        plot_profit_distribution(trade_logs)
        plot_execution_times(trade_logs)
    else:
        print("[WARNING] No executed trades available for analysis.")

    # Load backtesting results
    backtesting_results = load_backtesting_results()
    if backtesting_results is not None and not backtesting_results.empty:
        print("[INFO] Backtesting results summary:")
        print(backtesting_results)

# Run the results analysis
if __name__ == "__main__":
    analyze_results()
