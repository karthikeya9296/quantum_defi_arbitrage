import requests
import pandas as pd
import time
import json
import os
from datetime import datetime

# Load API keys from config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)
    COINGECKO_API_KEY = config["API_KEYS"].get("coingecko")

# Ensure the API key is set
if not COINGECKO_API_KEY:
    raise ValueError("[ERROR] CoinGecko API key is missing! Check config.json")

# Tokens to track (IDs used in CoinGecko API)
COINGECKO_TOKENS = {
    "ethereum": "ETH",
    "tether": "USDT",
    "dai": "DAI",
    "wrapped-bitcoin": "WBTC"
}

# API call counter
api_call_count = 0

# Fetch real-time token prices from CoinGecko
def fetch_prices():
    global api_call_count
    api_call_count += 1

    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(COINGECKO_TOKENS.keys()),
        "vs_currencies": "usd",
        "x_cg_api_key": COINGECKO_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if "error" in data:
            print(f"[ERROR] CoinGecko API error: {data['error']}")
            return {}

        prices = {}
        for token_id, symbol in COINGECKO_TOKENS.items():
            if token_id in data:
                prices[f"CoinGecko_{symbol}"] = data[token_id]["usd"]

        print(f"[SUCCESS] API Call #{api_call_count}: Fetched token prices from CoinGecko.")
        return prices

    except Exception as e:
        print(f"[ERROR] Failed to fetch prices from CoinGecko: {e}")
        return {}

# Store fetched prices into a structured CSV file
def save_prices():
    csv_file = "data/raw/token_prices.csv"

    # Avoid unnecessary API calls (Only fetch if last fetch was >5 minutes ago)
    if os.path.exists(csv_file):
        existing_df = pd.read_csv(csv_file)
        last_timestamp = pd.to_datetime(existing_df["timestamp"]).max()
        time_diff = (datetime.utcnow() - last_timestamp).total_seconds()

        if time_diff < 300:  # 5 minutes = 300 seconds
            print("[INFO] Skipping API call (last fetch <5 minutes ago).")
            return

    # Fetch prices
    prices = fetch_prices()
    if not prices:
        print("[WARNING] No price data fetched. Skipping file save.")
        return

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([{"timestamp": timestamp, **prices}])

    # Append new data if file exists
    try:
        existing_df = pd.read_csv(csv_file)
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        pass

    df.to_csv(csv_file, index=False)
    print(f"[SUCCESS] Prices saved to {csv_file}")

# Run price fetching every 60 seconds
if __name__ == "__main__":
    while True:
        save_prices()
        time.sleep(60)  # Run every 60 seconds
