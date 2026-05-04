# Market Data Pipeline

Financial data pipeline: Pull → Clean → Calculate → Plot

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Getting Started

Open a terminal and navigate to the project folder first:

```bash
cd "path\to\your\folder\Market Data Pipeline"
```

If `python` is not recognized, use the full path to your Python executable (e.g. `C:\ProgramData\anaconda3\python.exe`). You can find it by running `where python` in the terminal.

---

## Usage

### 1. Basic — tickers only (default date range: 2020-01-01 → 2024-12-31)
```bash
python pipeline.py --tickers AAPL,TSLA
```

### 2. With custom date range
```bash
python pipeline.py --tickers AAPL,TSLA,MC.PA,BTC-USD,MSFT --start 2023-01-01 --end 2026-05-01
```

### 3. Comparison chart only (skips individual charts)
```bash
python pipeline.py --tickers AAPL,TSLA,MC.PA,BTC-USD --start 2023-01-01 --end 2026-04-29 --compare-only
```

Tickers are comma-separated with no spaces. The `--compare-only` flag silently fetches data and jumps straight to the comparison chart — useful when you just want a quick multi-asset overview.

---

## Project Structure

```
Market Data Pipeline/
│
├── pipeline.py       # Entry point — orchestrates the pipeline and comparison chart
├── data_fetcher.py   # Downloads price data via yfinance with input validation
├── cleaner.py        # Cleans data: NaN, duplicates, outliers, negative prices
├── metrics.py        # Computes quantitative metrics
├── plotter.py        # Dark mode charts with interactive crosshair
└── requirements.txt  # Dependencies
```

---

## Computed Metrics

| Metric | Description | Formula |
|---|---|---|
| **Daily Return** | Day-over-day price change | `(P_t - P_{t-1}) / P_{t-1}` |
| **Cumulative Return** | Total performance since start | `∏(1 + r_t) - 1` |
| **Volatility 30d** | Annualized rolling volatility | `std(r, 30d) × √252` |
| **Sharpe Ratio 30d** | Risk-adjusted return (rf = 4%) | `(mean(r)×252 - 0.04) / std(r)×√252` |
| **Drawdown** | Decline from all-time high | `(P - max(P)) / max(P)` |

---

## Charts

For each ticker, a window opens with 4 charts:

- **Close Price** — price curve with MA50 and MA200 moving averages
- **Sharpe Ratio 30d** — risk-adjusted return, green zones (positive) and red zones (negative), reference lines at ±1 and ±2
- **Rolling Volatility 30d** — annualized risk with average line
- **Drawdown** — maximum loss from peak, with annotation at the worst point

When multiple tickers are provided, an additional comparison window shows:
- Cumulative returns of all tickers on the same axis
- **CAC 40** and **S&P 500** as dotted benchmark reference lines
- Final performance annotated on each curve

All charts are interactive:
- **Hover** → displays exact value + date at cursor position
- **Slider** → zoom into a specific time range (individual charts)

---

## Valid Ticker Examples

| Type | Examples |
|---|---|
| US Stocks | `AAPL`, `TSLA`, `MSFT`, `GOOGL` |
| French Stocks | `MC.PA`, `AIR.PA`, `TTE.PA` |
| German Stocks | `SAP.DE`, `SIE.DE` |
| Crypto | `BTC-USD`, `ETH-USD` |
| ETFs | `SPY`, `QQQ` |
| Indices | `^FCHI` (CAC 40), `^GSPC` (S&P 500) |

If a ticker is not found, the pipeline prints a clear error message and stops. Double-check the exact symbol on [finance.yahoo.com](https://finance.yahoo.com).

---

## How to Read the Metrics

**Sharpe Ratio** — measures whether the return justifies the risk taken.
- Below 0 → losing money relative to the risk-free rate
- Between 0 and 1 → acceptable but could be better
- Between 1 and 2 → good
- Above 2 → excellent
- On a 30-day rolling window, spikes to ±5 are normal during short strongly trending periods

**Drawdown** — shows the maximum pain an investor would have felt buying at the peak. A -30% drawdown means the price fell 30% from its last all-time high.

**Volatility** — the higher it is, the more violently the asset moves each day. BTC-USD will always show much higher volatility than AAPL or MC.PA.
