# Crypto Market Data Pipeline

## What this is
A small, honest ETL script: pull live market data for 5 cryptocurrencies
from a public API, clean/reshape it, and append it to a growing CSV
history — the kind of small automated data-collection job a data
analyst is regularly asked to build.

## Data source
[CoinGecko public API](https://www.coingecko.com/en/api/documentation)
— free, no account or API key required for the endpoint this project
uses (`/api/v3/coins/markets`). Rate limit on the free tier is generous
enough for occasional/scheduled runs (roughly 10-30 calls/minute); this
script makes exactly one call per run.

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
This machine's sandbox can't reach the internet, so the API call
couldn't be tested live here — but the cleaning/reshaping logic
(`clean_market_data`) was verified against a realistic mock response
matching CoinGecko's actual schema, including a row with missing data
to confirm the drop-and-log behavior works. Run it yourself with
internet access and it will work as-is; if CoinGecko ever changes a
field name, the error will point you straight at the affected line.

## To turn this into a repeating "pipeline" (optional, still simple)
Add a cron job (Linux/Mac) or Task Scheduler entry (Windows) that runs
`python fetch_and_clean.py` every hour. No code changes needed — the
`append_to_history` function already handles adding to the existing
file rather than overwriting it.

## Quick Overview
- Built a Python ETL pipeline that pulls live market data from a REST
  API, cleans and validates the response, and appends it to a
  time-stamped historical dataset
- Added retry logic with exponential backoff and null-value handling
  to make the pipeline resilient to transient API failures
- Designed the script to run unattended on a schedule, producing a
  continuously growing price-history dataset from a single command

## What to say if asked "have you actually run this?"
Run it yourself before your interview — it takes 10 seconds — so you
can honestly say yes and show real output. The cleaning logic was
already verified against a realistic mock of the actual API response
(including a deliberately broken row, to prove the null-handling
works), but you should run the live version at least once yourself so
you've seen real numbers come through and can speak to it confidently.
