"""
fetch_and_clean.py
-------------------
Pulls current market data for a fixed list of cryptocurrencies from the
CoinGecko public API (free, no API key required), cleans/reshapes it
with pandas, and appends it to a running history CSV. Run it once for a
single snapshot, or on a schedule (cron / Task Scheduler) to build up a
price history over time.

API docs: https://www.coingecko.com/en/api/documentation
Endpoint used: GET /api/v3/coins/markets  (free tier, no key needed)

Usage:
    python fetch_and_clean.py
"""

import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

API_URL = "https://api.coingecko.com/api/v3/coins/markets"

# Coins to track. Keep this list small and explicit -- easy to explain
# in an interview, and avoids hitting the free tier's rate limits.
COIN_IDS = ["bitcoin", "ethereum", "solana", "dogecoin", "cardano"]

DATA_DIR = Path(__file__).parent / "data"
HISTORY_CSV = DATA_DIR / "crypto_price_history.csv"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
log = logging.getLogger(__name__)


def fetch_market_data(coin_ids, vs_currency="usd", max_retries=3):
    """Call the CoinGecko markets endpoint and return the raw JSON list.
    Retries on failure since free public APIs occasionally rate-limit."""
    params = {
        "vs_currency": vs_currency,
        "ids": ",".join(coin_ids),
        "order": "market_cap_desc",
        "price_change_percentage": "24h",
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(API_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            log.warning(f"Attempt {attempt}/{max_retries} failed: {exc}")
            if attempt == max_retries:
                raise
            time.sleep(2 * attempt)  # simple backoff


def clean_market_data(raw_json: list) -> pd.DataFrame:
    """Turn the raw API response into a tidy, well-typed DataFrame with
    only the columns this project actually needs."""
    df = pd.DataFrame(raw_json)

    keep_cols = {
        "id": "coin_id",
        "symbol": "symbol",
        "current_price": "price_usd",
        "market_cap": "market_cap_usd",
        "total_volume": "volume_24h_usd",
        "price_change_percentage_24h": "price_change_pct_24h",
        "circulating_supply": "circulating_supply",
    }
    df = df[list(keep_cols.keys())].rename(columns=keep_cols)

    df["symbol"] = df["symbol"].str.upper()
    df["price_change_pct_24h"] = df["price_change_pct_24h"].round(2)
    df["fetched_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Basic sanity checks -- drop any row missing a price, log if it happens
    before = len(df)
    df = df.dropna(subset=["price_usd"])
    if len(df) < before:
        log.warning(f"Dropped {before - len(df)} row(s) with missing price data.")

    return df.sort_values("market_cap_usd", ascending=False).reset_index(drop=True)


def append_to_history(df: pd.DataFrame):
    """Append this run's snapshot to the history CSV, creating it with a
    header if it doesn't exist yet."""
    DATA_DIR.mkdir(exist_ok=True)
    file_exists = HISTORY_CSV.exists()
    df.to_csv(HISTORY_CSV, mode="a", header=not file_exists, index=False)


def main():
    log.info(f"Fetching market data for: {', '.join(COIN_IDS)}")
    raw = fetch_market_data(COIN_IDS)

    log.info("Cleaning and reshaping response ...")
    clean_df = clean_market_data(raw)

    log.info("Appending snapshot to history CSV ...")
    append_to_history(clean_df)

    print("\nLatest snapshot:")
    print(clean_df[["symbol", "price_usd", "price_change_pct_24h", "market_cap_usd"]].to_string(index=False))
    log.info(f"History file -> {HISTORY_CSV}")


if __name__ == "__main__":
    main()
