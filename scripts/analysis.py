"""
Exploratory analysis of clean/retail_sales_clean.csv.

Produces three tables (region revenue, monthly trend, top category per region)
and saves two charts as PNGs in charts/:
    - charts/revenue_by_region.png   (bar chart)
    - charts/monthly_revenue_trend.png (line chart)

Colors follow the data-viz reference palette (single blue hue for a single-series
magnitude chart; recessive gray axes/grid; text in ink tokens, not the series
color). Read-only on the data; only writes PNGs.

Usage:
    python scripts/analysis.py
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless backend: render straight to file, no display needed
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator

CLEAN_PATH = os.path.join("clean", "retail_sales_clean.csv")
CHART_DIR = "charts"

# --- Palette tokens (from the data-viz reference palette, light mode) ---
SERIES_BLUE = "#2a78d6"   # single categorical/sequential hue
SURFACE = "#fcfcfb"       # chart surface
INK_PRIMARY = "#0b0b0b"   # titles
INK_SECONDARY = "#52514e" # axis labels
MUTED = "#898781"         # tick labels
GRID = "#e1e0d9"          # hairline gridlines


def money(x, _pos=None):
    """Format a number as a $ amount with thousands separators (for axis ticks)."""
    return f"${x:,.0f}"


def main():
    # ---- Load the CLEANED data (read-only) ----
    df = pd.read_csv(CLEAN_PATH, parse_dates=["order_date"])

    # Required preview after loading.
    print("=== HEAD ===")
    print(df.head())
    print("\nshape:", df.shape)
    print("\ndtypes:")
    print(df.dtypes)

    os.makedirs(CHART_DIR, exist_ok=True)

    # ================================================================
    # 1) Total revenue by region, sorted descending
    # ================================================================
    # Group rows by region and sum their revenue, largest first.
    region_revenue = (
        df.groupby("region")["revenue ($)"].sum().sort_values(ascending=False)
    )
    print("\n=== 1) TOTAL REVENUE BY REGION ===")
    print(region_revenue.round(2))

    # ---- Bar chart: revenue by region ----
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    bars = ax.bar(region_revenue.index, region_revenue.values,
                  color=SERIES_BLUE, width=0.68)

    # Direct value labels on top of each bar (single series -> no legend needed).
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"${height:,.0f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, color=INK_SECONDARY)

    ax.set_title("Total Revenue by Region — 2025", fontsize=14,
                 color=INK_PRIMARY, fontweight="bold", pad=14)
    ax.set_xlabel("Region", fontsize=11, color=INK_SECONDARY)
    ax.set_ylabel("Total Revenue", fontsize=11, color=INK_SECONDARY)
    ax.yaxis.set_major_formatter(FuncFormatter(money))

    # Recessive chrome: light horizontal grid, no top/right spines.
    ax.yaxis.grid(True, color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(GRID)
    ax.tick_params(colors=MUTED)

    fig.tight_layout()
    region_png = os.path.join(CHART_DIR, "revenue_by_region.png")
    fig.savefig(region_png, facecolor=SURFACE)
    plt.close(fig)

    # ================================================================
    # 2) Monthly revenue trend for 2025
    # ================================================================
    # Bucket each order into its calendar month, then sum revenue per month.
    monthly = (
        df.set_index("order_date")["revenue ($)"]
        .resample("MS")  # "MS" = month start; one point per month
        .sum()
    )
    # Nice month labels like "Jan", "Feb", ... for the x-axis.
    month_labels = monthly.index.strftime("%b")
    print("\n=== 2) MONTHLY REVENUE TREND ===")
    print(monthly.round(2))

    # ---- Line chart: monthly revenue ----
    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    ax.plot(month_labels, monthly.values, color=SERIES_BLUE, linewidth=2,
            marker="o", markersize=6, markerfacecolor=SERIES_BLUE,
            markeredgecolor=SURFACE, markeredgewidth=1.2)

    ax.set_title("Monthly Revenue Trend — 2025", fontsize=14,
                 color=INK_PRIMARY, fontweight="bold", pad=14)
    ax.set_xlabel("Month", fontsize=11, color=INK_SECONDARY)
    ax.set_ylabel("Revenue", fontsize=11, color=INK_SECONDARY)
    ax.yaxis.set_major_formatter(FuncFormatter(money))
    # Zoom the y-axis to the data band so month-to-month movement is readable:
    # start at $200,000 with $20,000 gridlines (all months fall between ~203K and ~288K).
    # Note: a non-zero baseline visually amplifies the swings by design.
    ax.set_ylim(200_000, 300_000)
    ax.yaxis.set_major_locator(MultipleLocator(20_000))

    ax.yaxis.grid(True, color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(GRID)
    ax.tick_params(colors=MUTED)

    fig.tight_layout()
    trend_png = os.path.join(CHART_DIR, "monthly_revenue_trend.png")
    fig.savefig(trend_png, facecolor=SURFACE)
    plt.close(fig)

    # ================================================================
    # 3) Top category per region (by revenue)
    # ================================================================
    # Sum revenue for every region+category pair...
    region_cat = df.groupby(["region", "category"])["revenue ($)"].sum()
    # ...then, within each region, pick the category with the highest revenue.
    top_cat = region_cat.groupby(level="region").idxmax().apply(lambda x: x[1])
    top_cat_value = region_cat.groupby(level="region").max()
    top_category = pd.DataFrame({
        "top_category": top_cat,
        "category_revenue": top_cat_value.round(2),
    }).sort_values("category_revenue", ascending=False)
    print("\n=== 3) TOP CATEGORY PER REGION ===")
    print(top_category)

    print(f"\nSaved charts:\n  {region_png}\n  {trend_png}")


if __name__ == "__main__":
    main()
