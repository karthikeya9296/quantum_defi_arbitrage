import pandas as pd
import json
import os
import time
import random
import matplotlib.pyplot as plt
from web3 import Web3
from datetime import datetime

# File paths
ARBITRAGE_FILE = "data/processed/optimized_arbitrage.csv"
TRADE_LOG_FILE = "results/logs/arbitrage_trades.csv"
PLOT_FILE = "results/plots/arbitrage_execution.png"

# Ensure necessary folders exist
os.makedirs("results/logs", exist_ok=True)
os.makedirs("results/plots", exist_ok=True)

# Load API parameters
def load_config():
    try:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
        return config
    except (FileNotFoundError, json.JSONDecodeError):
        print("[ERROR] Failed to load config.json.")
        return {}

# Load optimized arbitrage trade
def load_best_trade():
    if not os.path.exists(ARBITRAGE_FILE):
        print("[ERROR] No optimized arbitrage file found. Run quantum_optimization.py first.")
        return None, None

    try:
        df = pd.read_csv(ARBITRAGE_FILE)
        latest_trade = df.iloc[-1]
        print(f"[INFO] Loaded trade: {latest_trade['best_trade']} with profit {latest_trade['profit']}")
        return latest_trade["best_trade"], float(latest_trade["profit"].replace("%", ""))
    except Exception as e:
        print(f"[ERROR] Failed to load arbitrage trade: {str(e)}")
        return None, None

# Simulate trade execution
def execute_trade(best_trade, profit_percentage):
    if not best_trade:
        print("[ERROR] No trade available for execution.")
        return None

    # Simulating execution success rate (real trades will be executed via Web3.py)
    execution_success = random.choice([True, False])

    # Simulated execution time (in seconds)
    execution_time = round(random.uniform(1, 5), 2)

    if execution_success:
        print(f"[SUCCESS] Trade Executed: {best_trade} | Profit: {profit_percentage:.2f}% | Time: {execution_time}s")
    else:
        print(f"[FAILURE] Trade Failed: {best_trade} | Profit: {profit_percentage:.2f}% | Time: {execution_time}s")

    return execution_success, execution_time

# Save trade execution results
def log_trade(best_trade, profit_percentage, execution_success, execution_time):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([{
        "timestamp": timestamp,
        "best_trade": best_trade,
        "profit": f"{profit_percentage:.2f}%",
        "status": "Success" if execution_success else "Failure",
        "execution_time": execution_time
    }])

    # Append to the log file
    if os.path.exists(TRADE_LOG_FILE):
        df.to_csv(TRADE_LOG_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(TRADE_LOG_FILE, index=False)

    print(f"[INFO] Trade logged to {TRADE_LOG_FILE}")

# Plot execution results
def plot_trade_results():
    if not os.path.exists(TRADE_LOG_FILE):
        print("[WARNING] No trade logs found for plotting.")
        return

    try:
        df = pd.read_csv(TRADE_LOG_FILE)
        
        # Count success and failures
        success_count = df["status"].value_counts().get("Success", 0)
        failure_count = df["status"].value_counts().get("Failure", 0)

        plt.figure(figsize=(6, 4))
        plt.bar(["Success", "Failure"], [success_count, failure_count], color=["green", "red"])
        plt.xlabel("Trade Execution Status")
        plt.ylabel("Number of Trades")
        plt.title("Arbitrage Trade Execution Results")
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        # Save the plot
        plt.savefig(PLOT_FILE)
        print(f"[SUCCESS] Trade execution plot saved to {PLOT_FILE}")

    except Exception as e:
        print(f"[ERROR] Failed to generate trade execution plot: {str(e)}")

# Main function
def main():
    print("[INFO] Starting Arbitrage Trade Execution")

    # Load configuration
    config = load_config()

    # Load the best trade
    best_trade, profit_percentage = load_best_trade()
    if best_trade:
        execution_success, execution_time = execute_trade(best_trade, profit_percentage)
        log_trade(best_trade, profit_percentage, execution_success, execution_time)

    # Generate trade execution plot
    plot_trade_results()

# Run the main function
if __name__ == "__main__":
    main()
