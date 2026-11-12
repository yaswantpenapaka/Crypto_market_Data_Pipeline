# Crypto Market Data Pipeline

## What this is
A small, honest ETL script: pull live market data for 5 cryptocurrencies
from a public API, clean/reshape it, and append it to a growing CSV
history - the kind of small automated data-collection job a data
analyst is regularly asked to build.

## Data source
[CoinGecko public API](https://www.coingecko.com/en/api/documentation)
- free, no account or API key required for the endpoint this project
uses (`/api/v3/coins/markets`). Rate limit on the free tier is generous
enough for occasional/scheduled runs (roughly 10-30 calls/minute); this
script makes exactly one call per run. Treat those rate figures as the
docs' guidance and check CoinGecko's current limits before quoting them.

## What it does
1. Calls the API for: Bitcoin, Ethereum, Solana, Dogecoin, Cardano
2. Cleans the response: keeps only the relevant fields, renames them,
   converts the symbol to uppercase, rounds the 24h % change, and drops
   any row with missing price data (with a logged warning)
3. Appends the cleaned snapshot to `data/crypto_price_history.csv`,
   tagged with a UTC timestamp, so running it repeatedly (e.g. via cron)
   builds up a genuine price-history dataset over time

## How to run it
```bash
pip install -r requirements.txt
python fetch_and_clean.py
```
Needs outbound HTTPS to CoinGecko. On success you should see an INFO log
for each stage and a short printed snapshot of the five coins. Each run
appends five rows to `data/crypto_price_history.csv` (header only on the
first write).

## To turn this into a repeating "pipeline" (optional, still simple)
Add a cron job (Linux/Mac) or Task Scheduler entry (Windows) that runs
`python fetch_and_clean.py` every hour. No code changes needed - the
`append_to_history` function already handles adding to the existing
file rather than overwriting it.

## Quick Overview
- Built a Python ETL script that pulls live market data from a REST
  API, cleans and validates the response, and appends it to a
  time-stamped historical dataset
- Added retry with backoff and null-price handling so brief network or
  rate-limit blips do not kill a run
- Designed to run unattended on a schedule, producing a continuously
  growing price-history dataset from a single command
