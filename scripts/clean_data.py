"""
Clean retail_sales_2025.csv and write the result to clean/retail_sales_clean.csv.

The raw file is treated as read-only. All output goes to the clean/ folder.
A running summary of every change is printed at the end.

Usage:
    python scripts/clean_data.py
"""

import os
import pandas as pd

RAW_PATH = r"retail_sales_2025.csv"
CLEAN_DIR = "clean"
CLEAN_PATH = os.path.join(CLEAN_DIR, "retail_sales_clean.csv")


def main():
    # ---- Load the raw data (read-only) ----
    # Parse order_date as a datetime so the saved file keeps a clean date format.
    df = pd.read_csv(RAW_PATH, parse_dates=["order_date"])

    # Capture the starting row count so we can report before/after.
    rows_start = len(df)

    # A dict to accumulate a summary of every change we make.
    summary = {}

    # ---- Rule 1: Drop exact duplicate rows ----
    # duplicated() marks rows whose every column matches an earlier row.
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    summary["exact_duplicate_rows_removed"] = before - len(df)

    # ---- Rule 2: Strip whitespace and title-case the region column ----
    # e.g. " calgary " -> "Calgary". This merges dirty labels into their
    # correct region so totals don't get split across variants.
    regions_before = set(df["region"].unique())
    df["region"] = df["region"].str.strip().str.title()
    regions_after = set(df["region"].unique())
    summary["region_labels_before"] = sorted(regions_before)
    summary["region_labels_after"] = sorted(regions_after)

    # ---- Rule 3: Remove rows where quantity is negative (log how many) ----
    # Negative quantities represent returns/refunds; per the rules we drop them.
    neg_mask = df["quantity"] < 0
    summary["negative_quantity_rows_removed"] = int(neg_mask.sum())
    df = df[~neg_mask].reset_index(drop=True)

    # ---- Rule 4: Fill missing unit_price with the category MEDIAN ----
    # Why median and not mean: unit prices are skewed (a few high-priced items
    # pull the mean upward), and the mean is sensitive to outliers. The median
    # is the robust "typical" price for a category and is not distorted by
    # extreme values, so it is the safer imputation for a missing price.
    missing_price_before = int(df["unit_price ($)"].isna().sum())

    # Median unit price per category, computed only from the rows that HAVE a price.
    category_median_price = df.groupby("category")["unit_price ($)"].transform("median")
    # Fill only the missing cells with their category's median price.
    df["unit_price ($)"] = df["unit_price ($)"].fillna(category_median_price)

    summary["missing_unit_price_filled"] = missing_price_before
    summary["missing_unit_price_remaining"] = int(df["unit_price ($)"].isna().sum())

    # ---- Rule 5: Recalculate revenue after all fixes ----
    # revenue = quantity * unit_price, rounded to 2 decimals (currency).
    # This overwrites any previously missing/stale revenue values so the column
    # is now internally consistent with quantity and the (filled) unit price.
    df["revenue ($)"] = (df["quantity"] * df["unit_price ($)"]).round(2)
    summary["missing_revenue_remaining"] = int(df["revenue ($)"].isna().sum())

    rows_end = len(df)

    # ---- Save cleaned data to clean/ (never touch the raw file) ----
    os.makedirs(CLEAN_DIR, exist_ok=True)
    # Write dates as plain YYYY-MM-DD, no index column.
    df.to_csv(CLEAN_PATH, index=False, date_format="%Y-%m-%d")

    # ---- Report ----
    print("=== CLEANED PREVIEW ===")
    print(df.head())
    print("\nshape:", df.shape)
    print("\ndtypes:")
    print(df.dtypes)

    print("\n=== ROW COUNTS ===")
    print("rows before:", rows_start)
    print("rows after :", rows_end)
    print("net removed:", rows_start - rows_end)

    print("\n=== SUMMARY OF CHANGES ===")
    for key, value in summary.items():
        print(f"{key}: {value}")

    print(f"\nSaved cleaned data to: {CLEAN_PATH}")


if __name__ == "__main__":
    main()
