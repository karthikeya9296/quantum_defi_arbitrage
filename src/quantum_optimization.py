import pandas as pd
import numpy as np
import json
import os
import matplotlib.pyplot as plt
from datetime import datetime

# File paths
PRICE_FILE = "data/raw/token_prices.csv"
OUTPUT_FILE = "data/processed/optimized_arbitrage.csv"
PLOT_FILE = "results/plots/arbitrage_opportunities.png"

# Ensure necessary folders exist
os.makedirs("data/processed", exist_ok=True)
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

# Load latest price data
def load_price_data():
    if not os.path.exists(PRICE_FILE):
        print(f"[ERROR] Price data not found at {PRICE_FILE}. Run data_pipeline.py first.")
        return None

    try:
        df = pd.read_csv(PRICE_FILE)

        if df.empty:
            print("[ERROR] Dataframe is empty")
            return None

        df = df.dropna()
        if df.empty:
            print("[ERROR] Dataframe is empty after dropping NA values")
            return None

        latest_data = df.iloc[-1]
        print(f"[INFO] Using latest data: {latest_data}")

        return latest_data

    except Exception as e:
        print(f"[ERROR] Failed to load price data: {str(e)}")
        return None

# Define arbitrage optimization using percentage threshold
def percentage_based_arbitrage(price_data, slippage_tolerance=0.005):
    print("[INFO] Running Improved Arbitrage Optimization...")

    exchange_cols = [col for col in price_data.index if "CoinGecko" in col]
    if len(exchange_cols) < 2:
        print("[ERROR] Not enough exchange price columns found for arbitrage analysis")
        return "None", 0.0, []

    arbitrage_opportunities = []
    for i, ex1 in enumerate(exchange_cols):
        for ex2 in exchange_cols[i + 1:]:
            try:
                price1 = float(price_data[ex1])
                price2 = float(price_data[ex2])

                price_diff_percent = abs((price1 - price2) / min(price1, price2)) * 100

                if price_diff_percent > slippage_tolerance * 100:
                    arbitrage_opportunities.append((ex1, ex2, price_diff_percent))
                    print(f"[INFO] Arbitrage found: {ex1} vs {ex2} -> {price_diff_percent:.4f}%")

            except ValueError:
                print(f"[WARNING] Invalid price data for {ex1} and {ex2}")

    if not arbitrage_opportunities:
        print("[ERROR] No valid arbitrage opportunities found")
        return "None", 0.0, []

    best_trade = max(arbitrage_opportunities, key=lambda x: x[2])
    print(f"[SUCCESS] Best Arbitrage Trade: {best_trade[0]} vs {best_trade[1]} with profit {best_trade[2]:.4f}%")

    return f"{best_trade[0]} vs {best_trade[1]}", best_trade[2], arbitrage_opportunities

# Save optimized trade signal
def save_optimized_trade(best_trade, profit_value):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([{"timestamp": timestamp, "best_trade": best_trade, "profit": f"{profit_value:.4f}%"}])

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[SUCCESS] Optimized trade saved to {OUTPUT_FILE}")

# Plot arbitrage opportunities
def plot_arbitrage_opportunities(arbitrage_opportunities):
    if not arbitrage_opportunities:
        print("[WARNING] No arbitrage opportunities to plot.")
        return

    pairs = [f"{t[0]} vs {t[1]}" for t in arbitrage_opportunities]
    profits = [t[2] for t in arbitrage_opportunities]

    plt.figure(figsize=(10, 5))
    plt.barh(pairs, profits, color="skyblue")
    plt.xlabel("Arbitrage Profit (%)")
    plt.ylabel("Exchange Pair")
    plt.title("Arbitrage Opportunities")
    plt.gca().invert_yaxis()
    plt.grid(axis="x", linestyle="--", alpha=0.7)

    plt.savefig(PLOT_FILE)
    print(f"[SUCCESS] Arbitrage opportunities plot saved to {PLOT_FILE}")

# Main function
def main():
    print("[INFO] Starting arbitrage optimization process")

    config = load_config()
    slippage_tolerance = config["PARAMETERS"].get("slippage_tolerance", 0.005)

    price_data = load_price_data()

    if price_data is not None:
        best_trade, profit_value, arbitrage_opportunities = percentage_based_arbitrage(price_data, slippage_tolerance)

        if best_trade != "None":
            save_optimized_trade(best_trade, profit_value)
            plot_arbitrage_opportunities(arbitrage_opportunities)
        else:
            print("[WARNING] No valid trades found, skipping save")
    else:
        print("[ERROR] Price data not available, cannot proceed")

# Run the main function
if __name__ == "__main__":
    main()
