# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import argparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

from data_fetcher import fetch_data
from cleaner import clean_data
from metrics import calculate_metrics
from plotter import plot_all

DARK_BG  = "#0d1117"
GRID_COL = "#21262d"
TEXT_COL = "#e6edf3"

# Color palette to distinguish tickers on the comparison chart
COLORS = ["#58a6ff", "#3fb950", "#f85149", "#d29922", "#bc8cff",
          "#ff7b72", "#79c0ff", "#56d364", "#ffa657", "#f0883e"]


def run_pipeline(ticker, start, end):
    """Run the full pipeline for a single ticker and display individual charts."""
    print("\n" + "="*50)
    print("  Market Data Pipeline -- " + ticker)
    print("="*50 + "\n")

    print("[1/4] Fetching data...")
    raw_df = fetch_data(ticker, start, end)
    print("  OK - {} days retrieved ({} -> {})\n".format(
        len(raw_df), raw_df.index[0].date(), raw_df.index[-1].date()))

    print("[2/4] Cleaning data...")
    clean_df = clean_data(raw_df)
    print("  OK - {} days after filtering\n".format(len(clean_df)))

    print("[3/4] Computing metrics...")
    df = calculate_metrics(clean_df)
    print("  OK - Returns, Volatility, Sharpe, Drawdown computed\n")

    print("[4/4] Rendering charts...")
    plot_all(df, ticker)
    print("  OK - Charts displayed\n")

    total_return = (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100
    annual_vol   = df["Volatility_30d"].iloc[-1] * 100
    max_dd       = df["Drawdown"].min() * 100
    last_sharpe  = df["Sharpe_30d"].dropna().iloc[-1]

    print("-"*50)
    print("  SUMMARY -- " + ticker)
    print("-"*50)
    print("  Total Return    : {:+.2f}%".format(total_return))
    print("  Volatility 30d  : {:.2f}%".format(annual_vol))
    print("  Max Drawdown    : {:.2f}%".format(max_dd))
    print("  Sharpe 30d      : {:.2f}".format(last_sharpe))
    print("-"*50 + "\n")

    return df


def plot_comparison(all_data, start, end, benchmarks=None):
    """
    Display cumulative returns of all tickers on a single chart.
    CAC 40 and S&P 500 are shown as dotted benchmark reference lines.
    Interactive crosshair via blitting for smooth performance.
    """
    if len(all_data) < 1:
        return
    if benchmarks is None:
        benchmarks = {}

    fig, ax = plt.subplots(figsize=(14, 7), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)
    fig.suptitle(
        "Cumulative Return Comparison  |  {} -> {}".format(start, end),
        color=TEXT_COL, fontsize=13, fontweight="bold", y=0.98
    )

    # Store series for crosshair
    series_list = []

    for i, (ticker, df) in enumerate(all_data.items()):
        color = COLORS[i % len(COLORS)]
        ret   = df["Cumulative_Return"] * 100
        final = ret.iloc[-1]

        ax.plot(df.index, ret, color=color, linewidth=1.8,
                label="{} ({:+.1f}%)".format(ticker, final), zorder=3)
        ax.annotate("{:+.1f}%".format(final),
                    xy=(df.index[-1], final),
                    xytext=(8, 0), textcoords="offset points",
                    color=color, fontsize=9, fontweight="bold", va="center")
        series_list.append((ticker, ret.values, df.index, color))

    # Benchmarks as dotted lines
    BENCH_COLORS = {"S&P 500": "#ffffff", "CAC 40": "#aaaaaa"}
    for bname, bdf in benchmarks.items():
        bret   = bdf["Cumulative_Return"] * 100
        bfinal = bret.iloc[-1]
        bcol   = BENCH_COLORS.get(bname, "#888888")
        ax.plot(bdf.index, bret, color=bcol, linewidth=1.2, linestyle=":",
                label="{} ({:+.1f}%)".format(bname, bfinal), zorder=2, alpha=0.8)
        ax.annotate("{:+.1f}%".format(bfinal),
                    xy=(bdf.index[-1], bfinal),
                    xytext=(8, 0), textcoords="offset points",
                    color=bcol, fontsize=8, fontweight="bold", va="center", alpha=0.8)
        series_list.append((bname, bret.values, bdf.index, bcol))

    # Zero reference line
    ax.axhline(0, color=TEXT_COL, linewidth=0.7, linestyle="--", alpha=0.4)

    # Style
    ax.tick_params(colors=TEXT_COL, labelsize=9)
    ax.xaxis.label.set_color(TEXT_COL)
    ax.yaxis.label.set_color(TEXT_COL)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)
    ax.grid(True, color=GRID_COL, linewidth=0.5, linestyle="--", alpha=0.6)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center", fontsize=9)
    ax.set_ylabel("Cumulative Return (%)", color=TEXT_COL)
    ax.legend(fontsize=10, facecolor=GRID_COL, edgecolor="#444",
              labelcolor=TEXT_COL, loc="upper left", framealpha=0.9, borderpad=0.8)

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # --- Smooth crosshair via blitting ---
    ref_index  = list(all_data.values())[0].index
    dates_num  = mdates.date2num(ref_index.to_pydatetime())

    vline = ax.axvline(x=ref_index[0], color=TEXT_COL, linewidth=0.8,
                       linestyle="--", alpha=0.5, visible=False, animated=True)
    dots  = [ax.plot([], [], "o", color=color, ms=6, zorder=10, animated=True)[0]
             for _, _, _, color in series_list]
    tooltip = ax.text(0.01, 0.60, "", transform=ax.transAxes,
                      fontsize=8, color=TEXT_COL, va="top", ha="left",
                      bbox=dict(boxstyle="round,pad=0.5", facecolor=GRID_COL,
                                edgecolor="#444", alpha=0.92, linewidth=1.2),
                      zorder=20, visible=False, animated=True)

    background = [None]

    def on_draw(event):
        background[0] = fig.canvas.copy_from_bbox(ax.bbox)

    fig.canvas.mpl_connect("draw_event", on_draw)

    def on_move(event):
        if background[0] is None:
            return
        fig.canvas.restore_region(background[0])

        if event.inaxes != ax or event.xdata is None:
            fig.canvas.blit(ax.bbox)
            return

        idx   = int(np.searchsorted(dates_num, event.xdata))
        idx   = min(max(idx, 0), len(dates_num) - 1)
        x_val = dates_num[idx]
        date_str = ref_index[idx].strftime("%d %b %Y")

        vline.set_xdata([x_val])
        vline.set_visible(True)
        ax.draw_artist(vline)

        lines = [date_str]
        for j, (ticker, values, t_index, color) in enumerate(series_list):
            t_dates_num = mdates.date2num(t_index.to_pydatetime())
            t_idx = int(np.searchsorted(t_dates_num, event.xdata))
            t_idx = min(max(t_idx, 0), len(values) - 1)
            val   = values[t_idx]
            dots[j].set_data([t_dates_num[t_idx]], [val])
            ax.draw_artist(dots[j])
            lines.append("{} : {:+.2f}%".format(ticker, val))

        xlim   = ax.get_xlim()
        x_frac = (x_val - xlim[0]) / (xlim[1] - xlim[0]) if xlim[1] != xlim[0] else 0
        if x_frac > 0.55:
            tooltip.set_position((0.01, 0.60))
            tooltip.set_ha("left")
        else:
            tooltip.set_position((0.99, 0.60))
            tooltip.set_ha("right")

        tooltip.set_text("\n".join(lines))
        tooltip.set_visible(True)
        ax.draw_artist(tooltip)
        fig.canvas.blit(ax.bbox)

    fig.canvas.mpl_connect("motion_notify_event", on_move)
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Market Data Pipeline")
    parser.add_argument("--tickers", type=str, default=None,
                        help="One or more tickers separated by commas. Ex: AAPL,TSLA,MC.PA")
    parser.add_argument("--start",   type=str, default="2020-01-01",
                        help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end",     type=str, default="2024-12-31",
                        help="End date in YYYY-MM-DD format")
    parser.add_argument("--compare-only", action="store_true",
                        help="Skip individual charts, show only the comparison chart")
    args = parser.parse_args()

    if args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(",")]
    else:
        print("\nNo ticker provided.")
        print("Examples: AAPL, TSLA, MC.PA, BTC-USD")
        raw = input("Enter one or more tickers (comma-separated): ").strip().upper()
        tickers = [t.strip() for t in raw.split(",")] if raw else ["AAPL"]

    # Run pipeline for each ticker
    all_data = {}
    for ticker in tickers:
        if args.compare_only:
            # Fast mode: fetch + clean + metrics without rendering individual charts
            print("Loading {} ...".format(ticker))
            raw_df   = fetch_data(ticker, args.start, args.end)
            clean_df = clean_data(raw_df)
            df       = calculate_metrics(clean_df)
            all_data[ticker] = df
        else:
            df = run_pipeline(ticker, args.start, args.end)
            all_data[ticker] = df

    # Load benchmarks (CAC 40 and S&P 500)
    benchmarks = {}
    for bname, bticker in [("S&P 500", "^GSPC"), ("CAC 40", "^FCHI")]:
        try:
            print("Loading benchmark {} ...".format(bname))
            braw   = fetch_data(bticker, args.start, args.end)
            bclean = clean_data(braw)
            bdf    = calculate_metrics(bclean)
            benchmarks[bname] = bdf
        except Exception as e:
            print("  Benchmark {} unavailable: {}".format(bname, e))

    # Show comparison chart if 2+ tickers or --compare-only mode
    if len(all_data) >= 2 or args.compare_only:
        print("\nRendering comparison chart...\n")
        plot_comparison(all_data, args.start, args.end, benchmarks)
    elif len(all_data) == 1 and not args.compare_only:
        pass  # Single ticker: individual charts already shown
    else:
        print("Need at least 2 tickers for the comparison chart.")


if __name__ == "__main__":
    main()


# ── Quick launch commands ──────────────────────────────────────────────────────
# cd "c:\Users\Léo\Doc PC Léo\Projet Python Perso\Market Data Pipeline"
#C:\ProgramData\anaconda3\python.exe pipeline.py --tickers AAPL,TSLA
# C:\ProgramData\anaconda3\python.exe pipeline.py --tickers AAPL,TSLA,MC.PA,BTC-USD,MSFT --start 2023-01-01 --end 2026-05-01
# C:\ProgramData\anaconda3\python.exe pipeline.py --tickers AAPL,TSLA,MC.PA,btc-usd --start 2023-01-01 --end 2026-04-29 --compare-only
