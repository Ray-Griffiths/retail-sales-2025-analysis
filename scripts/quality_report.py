"""
Data quality report for retail_sales_2025.csv.
Read-only: this script never writes to or modifies the raw file.

Usage:
    python scripts/quality_report.py
"""

import pandas as pd

# Path to the raw data file, relative to the project root.
RAW_PATH = r"retail_sales_2025.csv"


def main():
    # ---- Load the raw data (read-only) ----
    # Parse order_date as a real datetime so we can spot bad/out-of-range dates.
    df = pd.read_csv(RAW_PATH, parse_dates=["order_date"])

    # ---- Required preview: head, shape, dtypes ----
    print("=== HEAD ===")
    print(df.head())
    print("\n=== SHAPE (rows, columns) ===")
    print(df.shape)
    print("\n=== DTYPES ===")
    print(df.dtypes)

    # ---- 1) Row count ----
    print("\n=== ROW COUNT ===")
    print(len(df))

    # ---- 2) Missing values per column ----
    # isna() flags empty/NaN cells; .sum() counts them per column.
    print("\n=== MISSING VALUES PER COLUMN ===")
    print(df.isna().sum())

    # ---- 3) Duplicates ----
    # Fully duplicated rows (every column identical):
    full_dupes = df.duplicated().sum()
    # Duplicated order_id (the intended unique key), regardless of other columns:
    id_dupes = df.duplicated(subset=["order_id"]).sum()
    print("\n=== DUPLICATES ===")
    print("Fully duplicated rows:", full_dupes)
    print("Duplicate order_id values:", id_dupes)

    # ---- 4) Invalid / suspicious values ----
    print("\n=== INVALID / SUSPICIOUS VALUES ===")

    # Negative or zero quantities (returns or data errors):
    print("quantity <= 0 :", (df["quantity"] <= 0).sum())
    print("  of which negative:", (df["quantity"] < 0).sum())

    # Negative or zero unit price (a price should be positive):
    print("unit_price <= 0 :", (df["unit_price ($)"] <= 0).sum())

    # Negative revenue (usually pairs with negative quantity = returns):
    print("revenue < 0 :", (df["revenue ($)"] < 0).sum())

    # Consistency check: does revenue equal quantity * unit_price (within rounding)?
    # We allow a 1-cent tolerance for floating-point / rounding differences.
    # NOTE: rows with a missing unit_price/revenue produce NaN and are skipped here.
    expected_revenue = df["quantity"] * df["unit_price ($)"]
    revenue_mismatch = (df["revenue ($)"] - expected_revenue).abs() > 0.01
    print("revenue != quantity * unit_price (>1c off):", revenue_mismatch.sum())

    # Dates outside calendar year 2025 (dataset is meant to be 2025 only):
    out_of_range_dates = (df["order_date"] < "2025-01-01") | (df["order_date"] > "2025-12-31")
    print("order_date outside 2025:", out_of_range_dates.sum())

    # Value ranges for context:
    print("\norder_date range:", df["order_date"].min(), "->", df["order_date"].max())
    print("quantity range:", df["quantity"].min(), "->", df["quantity"].max())
    print("unit_price range:", df["unit_price ($)"].min(), "->", df["unit_price ($)"].max())
    print("revenue range:", df["revenue ($)"].min(), "->", df["revenue ($)"].max())

    # Category / region value sets (spot typos or unexpected labels):
    print("\nregions:", sorted(df["region"].unique()))
    print("categories:", sorted(df["category"].unique()))


if __name__ == "__main__":
    main()
