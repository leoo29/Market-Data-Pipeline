# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.widgets import RangeSlider
import pandas as pd
import numpy as np

DARK_BG  = "#0d1117"
GRID_COL = "#21262d"
TEXT_COL = "#e6edf3"
ACCENT   = "#58a6ff"
GREEN    = "#3fb950"
RED      = "#f85149"
ORANGE   = "#d29922"
PURPLE   = "#bc8cff"


def _dates_to_num(index):
    return mdates.date2num(index.to_pydatetime())


def _apply_style(ax, title, show_dates=False):
    """Apply dark theme and axis formatting to a given axes object."""
    ax.set_facecolor(DARK_BG)
    ax.set_title(title, color=TEXT_COL, fontsize=11, fontweight="bold", pad=10)
    ax.tick_params(colors=TEXT_COL, labelsize=9)
    ax.yaxis.set_label_position("left")
    ax.xaxis.label.set_color(TEXT_COL)
    ax.yaxis.label.set_color(TEXT_COL)
    ax.tick_params(axis='y', labelsize=9, colors=TEXT_COL)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)
    ax.grid(True, color=GRID_COL, linewidth=0.5, linestyle="--", alpha=0.7)
    if show_dates:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.get_xticklabels(), rotation=0, ha="center", fontsize=9)
        ax.tick_params(axis='x', pad=6, bottom=True, labelbottom=True)
    else:
        ax.tick_params(axis='x', bottom=False, labelbottom=False)
        ax.spines['bottom'].set_visible(False)


def _annotate_minmax(ax, series, color_max, color_min, fmt, offset_max, offset_min):
    """
    Annotate the min and max values on a chart with arrows and date labels.
    Offsets push text away from the curve to avoid overlap.
    """
    max_val  = series.max()
    max_date = series.idxmax()
    min_val  = series.min()
    min_date = series.idxmin()

    ax.annotate(
        "Max: {}\n{}".format(fmt.format(max_val), max_date.strftime("%d/%m/%Y")),
        xy=(max_date, max_val),
        xytext=offset_max, textcoords="offset points",
        color=color_max, fontsize=7, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=color_max, lw=0.8),
        bbox=dict(boxstyle="round,pad=0.2", facecolor=DARK_BG, edgecolor=color_max, alpha=0.8)
    )
    ax.annotate(
        "Min: {}\n{}".format(fmt.format(min_val), min_date.strftime("%d/%m/%Y")),
        xy=(min_date, min_val),
        xytext=offset_min, textcoords="offset points",
        color=color_min, fontsize=7, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=color_min, lw=0.8),
        bbox=dict(boxstyle="round,pad=0.2", facecolor=DARK_BG, edgecolor=color_min, alpha=0.8)
    )


def plot_price(ax, df, ticker):
    """Close price with MA50 and MA200 moving averages."""
    ax.plot(df.index, df["Close"], color=ACCENT, linewidth=1.2, label="Close", zorder=3)
    ax.plot(df.index, df["Close"].rolling(50).mean(),  color=ORANGE, linewidth=1.0,
            linestyle="--", label="MA 50d",  alpha=0.85)
    ax.plot(df.index, df["Close"].rolling(200).mean(), color=PURPLE, linewidth=1.0,
            linestyle="--", label="MA 200d", alpha=0.85)
    ax.fill_between(df.index, df["Close"], df["Close"].min(), alpha=0.08, color=ACCENT)
    ax.legend(fontsize=8, facecolor=GRID_COL, edgecolor=GRID_COL, labelcolor=TEXT_COL, loc="upper left")
    ax.set_ylabel("Price ($)", color=TEXT_COL)

    _annotate_minmax(ax, df["Close"],
                     color_max=ACCENT, color_min=ACCENT,
                     fmt="${:.2f}",
                     offset_max=(15, 10),
                     offset_min=(15, -25))

    _apply_style(ax, ticker + " - Close Price", show_dates=True)


def plot_sharpe(ax, df):
    """
    Rolling 30-day Sharpe Ratio (annualized, rf=4%).
    > 1 : good | > 2 : excellent | < 0 : underperforming risk-free rate
    """
    sharpe_full = df["Sharpe_30d"]

    ax.plot(df.index, sharpe_full, color=PURPLE, linewidth=1.3, zorder=3)
    ax.axhline(0,  color=TEXT_COL, linewidth=0.6, linestyle="-",  alpha=0.4)
    ax.axhline(2,  color=GREEN,    linewidth=0.8, linestyle="--", alpha=0.7, label="Sharpe = 2 (excellent)")
    ax.axhline(1,  color=ORANGE,   linewidth=0.6, linestyle="--", alpha=0.5, label="Sharpe = 1 (good)")
    ax.axhline(-1, color=ORANGE,   linewidth=0.6, linestyle="--", alpha=0.5, label="Sharpe = -1")
    ax.axhline(-2, color=RED,      linewidth=0.8, linestyle="--", alpha=0.7, label="Sharpe = -2 (poor)")

    ax.fill_between(df.index, sharpe_full, 0,
                    where=(sharpe_full >= 0), alpha=0.15, color=GREEN, interpolate=True)
    ax.fill_between(df.index, sharpe_full, 0,
                    where=(sharpe_full < 0),  alpha=0.15, color=RED,   interpolate=True)

    ax.legend(fontsize=7, facecolor=GRID_COL, edgecolor=GRID_COL, labelcolor=TEXT_COL, loc="upper left")

    _annotate_minmax(ax, sharpe_full.dropna(),
                     color_max=GREEN, color_min=RED,
                     fmt="{:.2f}",
                     offset_max=(15, 10),
                     offset_min=(15, -25))

    ax.set_ylabel("Sharpe Ratio", color=TEXT_COL)
    _apply_style(ax, "Rolling 30d Sharpe Ratio (annualized, rf=4%)", show_dates=False)


def plot_volatility(ax, df):
    """Rolling 30-day annualized volatility with average reference line."""
    vol = df["Volatility_30d"] * 100
    ax.plot(df.index, vol, color=ORANGE, linewidth=1.1)
    ax.fill_between(df.index, vol, alpha=0.2, color=ORANGE)
    mean_vol = vol.mean()
    ax.axhline(mean_vol, color=ORANGE, linewidth=0.8, linestyle=":", alpha=0.7,
               label="Avg. {:.1f}%".format(mean_vol))
    ax.legend(fontsize=8, facecolor=GRID_COL, edgecolor=GRID_COL, labelcolor=TEXT_COL, loc="upper left")
    ax.set_ylabel("Ann. Volatility (%)", color=TEXT_COL)

    _annotate_minmax(ax, vol,
                     color_max=ORANGE, color_min=ORANGE,
                     fmt="{:.1f}%",
                     offset_max=(15, 10),
                     offset_min=(15, -25))

    _apply_style(ax, "Rolling 30d Volatility (annualized)", show_dates=False)


def plot_drawdown(ax, df):
    """Drawdown from all-time high with annotation at the worst point."""
    dd = df["Drawdown"] * 100
    ax.fill_between(df.index, dd, 0, alpha=0.5, color=RED)
    ax.plot(df.index, dd, color=RED, linewidth=0.8)
    ax.set_ylabel("Drawdown (%)", color=TEXT_COL)

    _annotate_minmax(ax, dd,
                     color_max=RED, color_min=RED,
                     fmt="{:.1f}%",
                     offset_max=(15, -20),
                     offset_min=(15, -20))

    _apply_style(ax, "Drawdown (vs all-time high)", show_dates=False)


def _add_crosshair_blit(fig, axes, df):
    """
    Smooth interactive crosshair using blitting.
    - Saves the background once after the first render
    - On each mouse move: restores background, then redraws only the vline + tooltip
    - Shows the value for the hovered chart only
    """
    configs = [
        {"series": df["Close"].values,                    "fmt": "Price: ${:.2f}",      "color": ACCENT},
        {"series": df["Sharpe_30d"].fillna(0).values,     "fmt": "Sharpe: {:.2f}",      "color": PURPLE},
        {"series": (df["Volatility_30d"] * 100).values,   "fmt": "Volatility: {:.2f}%", "color": ORANGE},
        {"series": (df["Drawdown"] * 100).values,         "fmt": "Drawdown: {:.2f}%",   "color": RED},
    ]

    # Pre-compute dates as floats for fast numpy lookup
    dates_num = _dates_to_num(df.index)

    # Animated artists — one per axis
    vlines   = [ax.axvline(x=df.index[0], color=TEXT_COL, linewidth=0.8,
                            linestyle="--", alpha=0.5, visible=False, animated=True)
                for ax in axes]
    dots     = [ax.plot([], [], 'o', color=cfg["color"], ms=5, zorder=10, animated=True)[0]
                for ax, cfg in zip(axes, configs)]
    tooltips = [ax.text(0.01, 0.95, "", transform=ax.transAxes,
                        fontsize=8, color=TEXT_COL, va="top", ha="left",
                        bbox=dict(boxstyle="round,pad=0.4", facecolor=GRID_COL,
                                  edgecolor=cfg["color"], alpha=0.90, linewidth=1.2),
                        zorder=20, visible=False, animated=True)
                for ax, cfg in zip(axes, configs)]

    backgrounds = [None] * len(axes)

    def on_draw(event):
        # Save background after each full redraw (e.g. after zoom)
        for i, ax in enumerate(axes):
            backgrounds[i] = fig.canvas.copy_from_bbox(ax.bbox)

    fig.canvas.mpl_connect("draw_event", on_draw)

    def on_move(event):
        if None in backgrounds:
            return

        # Restore all backgrounds first
        for i, ax in enumerate(axes):
            fig.canvas.restore_region(backgrounds[i])

        if event.inaxes not in axes:
            fig.canvas.blit(fig.bbox)
            return

        x_num = event.xdata
        if x_num is None:
            return

        # Find nearest date index via numpy (fast)
        idx   = int(np.searchsorted(dates_num, x_num))
        idx   = min(max(idx, 0), len(df) - 1)
        date  = df.index[idx]
        x_val = dates_num[idx]
        active_i = axes.index(event.inaxes)

        for i, (ax, vl, dot, tt, cfg) in enumerate(zip(axes, vlines, dots, tooltips, configs)):
            # Vertical crosshair line on all charts
            vl.set_xdata([x_val])
            vl.set_visible(True)
            ax.draw_artist(vl)

            # Dot on the curve
            val = cfg["series"][idx]
            dot.set_data([x_val], [val])
            ax.draw_artist(dot)

            # Tooltip only on the active chart
            if i == active_i:
                xlim   = ax.get_xlim()
                x_frac = (x_val - xlim[0]) / (xlim[1] - xlim[0]) if xlim[1] != xlim[0] else 0.5
                # Switch side to stay on screen
                if x_frac > 0.55:
                    tt.set_position((0.01, 0.95))
                    tt.set_ha("left")
                else:
                    tt.set_position((0.99, 0.95))
                    tt.set_ha("right")
                tt.set_text("{}\n{}".format(date.strftime("%d %b %Y"), cfg["fmt"].format(val)))
                tt.set_visible(True)
                ax.draw_artist(tt)
            else:
                tt.set_visible(False)

        # Blit only modified areas
        for ax in axes:
            fig.canvas.blit(ax.bbox)

    fig.canvas.mpl_connect("motion_notify_event", on_move)


def plot_all(df, ticker):
    """
    Main function — builds the full 4-chart figure for a single ticker.
    Charts: Close Price | Sharpe Ratio | Volatility | Drawdown
    """
    fig = plt.figure(figsize=(15, 19), facecolor=DARK_BG)
    gs  = fig.add_gridspec(5, 1, height_ratios=[3, 2.5, 2.5, 2.5, 0.4],
                           hspace=0.55, top=0.91, bottom=0.06, left=0.08, right=0.97)

    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    ax3 = fig.add_subplot(gs[2])
    ax4 = fig.add_subplot(gs[3])
    ax_slider = fig.add_subplot(gs[4])

    axes = [ax1, ax2, ax3, ax4]
    for ax in axes:
        ax.set_xlim((df.index[0], df.index[-1]))

    fig.suptitle(
        "Market Data Pipeline - {}  |  {} -> {}".format(
            ticker,
            df.index[0].strftime("%d/%m/%Y"),
            df.index[-1].strftime("%d/%m/%Y")
        ),
        color=TEXT_COL, fontsize=12, fontweight="bold", y=0.97
    )

    plot_price(ax1, df, ticker)
    plot_sharpe(ax2, df)
    plot_volatility(ax3, df)
    plot_drawdown(ax4, df)

    _add_crosshair_blit(fig, axes, df)

    # Range slider for zooming into a specific time window
    ax_slider.set_facecolor(GRID_COL)
    total_days = (df.index[-1] - df.index[0]).days
    slider = RangeSlider(ax_slider, "Zoom",
                         valmin=0, valmax=total_days,
                         valinit=(0, total_days),
                         color=ACCENT, track_color=DARK_BG)
    slider.label.set_color(TEXT_COL)
    slider.valtext.set_color(TEXT_COL)

    def update(val):
        s, e = slider.val
        new_start = df.index[0] + pd.Timedelta(days=int(s))
        new_end   = df.index[0] + pd.Timedelta(days=int(e))
        if new_start >= new_end:
            return
        for ax in axes:
            ax.set_xlim(new_start, new_end)
        # Redraw to refresh blit backgrounds after zoom
        fig.canvas.draw()

    slider.on_changed(update)
    fig._slider = slider
    plt.show()
