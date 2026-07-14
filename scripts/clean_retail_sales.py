"""
Clean the raw 2025 retail sales data and write an analysis-ready copy plus an
audit trail of every cleaning action.

Source (READ-ONLY, never modified): retail_sales_2025.xlsx
Outputs:
    clean/retail_sales_2025_clean.csv   — cleaned, analysis-ready data
    clean/cleaning_audit.csv            — one row per cleaning action, with the
                                          row counts affected (feeds the workbook's
                                          "Data Quality" sheet so an auditor can
                                          trace every number)

Cleaning rules (as agreed):
    1. Dedupe            — drop duplicate orders (same order_id).
    2. Fix regions       — strip whitespace + title-case so " calgary" -> "Calgary".
    3. Drop returns      — remove rows with negative quantity.
    4. Median-impute     — fill missing unit_price ($) with the median unit price.
    5. Recalc revenue    — revenue ($) = quantity * unit_price ($) for every row,
                           so revenue is internally consistent after imputation.

Usage:
    python scripts/clean_retail_sales.py
"""

import os
import pandas as pd

RAW_PATH = "retail_sales_2025.xlsx"          # source of truth — read only
CLEAN_DIR = "clean"
CLEAN_PATH = os.path.join(CLEAN_DIR, "retail_sales_2025_clean.csv")
AUDIT_PATH = os.path.join(CLEAN_DIR, "cleaning_audit.csv")

PRICE_COL = "unit_price ($)"
REV_COL = "revenue ($)"

# Column order for the audit trail (kept stable so the report can rely on it).
AUDIT_COLUMNS = ["step", "action", "basis", "rows_in", "rows_affected",
                 "rows_out", "detail"]


def clean_with_audit(df_raw: pd.DataFrame):
    """Apply the cleaning rules in order, recording an audit entry per step.

    Returns (df_clean, audit_records). Row-count columns:
      rows_in       = dataset size entering the step ("" when N/A)
      rows_affected = rows removed or values modified by the step ("" when N/A)
      rows_out      = dataset size leaving the step
    Index is preserved throughout so 'before' values stay aligned to survivors.
    """
    df = df_raw.copy()
    audit: list[dict] = []

    def log(action, basis, rows_in, rows_affected, rows_out, detail):
        audit.append({
            "step": len(audit) + 1,
            "action": action,
            "basis": basis,
            "rows_in": rows_in,
            "rows_affected": rows_affected,
            "rows_out": rows_out,
            "detail": detail,
        })

    # ── 0. Baseline: raw dataset as loaded ───────────────────────────────────
    raw_rows = len(df)
    log("Load raw dataset", "source", "", "", raw_rows,
        f"Read {RAW_PATH} (sheet 'sales')")

    # ── 1. Dedupe: drop repeated orders, keeping the first occurrence ─────────
    before = len(df)
    df = df.drop_duplicates(subset="order_id", keep="first")
    log("Remove duplicate orders", "dedupe", before, before - len(df), len(df),
        "Dropped rows with a repeated order_id; kept first occurrence")

    # ── 2. Fix regions: trim stray spaces and normalise casing ───────────────
    #    Count rows whose label actually changed (e.g. " calgary" -> "Calgary").
    fixed_region = df["region"].str.strip().str.title()
    region_changed = int((df["region"] != fixed_region).sum())
    df["region"] = fixed_region
    log("Standardize region labels", "fix regions", len(df), region_changed, len(df),
        "Trim whitespace + Title Case; ' calgary' -> 'Calgary' (row count unchanged)")

    # ── 3. Drop returns: remove rows where quantity is negative ──────────────
    before = len(df)
    df = df[df["quantity"] >= 0].copy()
    log("Remove return rows", "drop negative quantities", before, before - len(df), len(df),
        "Removed rows with quantity < 0 (product returns)")

    # ── 4. Median-impute missing unit prices ─────────────────────────────────
    n_missing_price = int(df[PRICE_COL].isna().sum())
    median_price = df[PRICE_COL].median()
    df[PRICE_COL] = df[PRICE_COL].fillna(median_price)
    log("Impute missing unit prices", "median-impute prices", len(df),
        n_missing_price, len(df),
        f"Filled {n_missing_price} null {PRICE_COL} with median = {median_price:.2f}")

    # ── 5. Recalculate revenue = quantity * unit price ───────────────────────
    #    Applied to all rows; count how many actually changed (incl. previously null).
    orig_rev = df[REV_COL]
    new_rev = (df["quantity"] * df[PRICE_COL]).round(2)
    rev_changed = int((orig_rev.isna() | ((orig_rev - new_rev).abs() > 0.01)).sum())
    df[REV_COL] = new_rev
    log("Recalculate revenue", "recalc revenue", len(df), rev_changed, len(df),
        f"revenue = quantity x unit_price; {rev_changed} rows changed (incl. previously null)")

    # ── Formatting: normalise order_date to YYYY-MM-DD (no value change) ──────
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.strftime("%Y-%m-%d")

    # ── Final validation snapshot ────────────────────────────────────────────
    nulls_remaining = int(df.isna().sum().sum())
    log("Final validated dataset", "output", len(df), "", len(df),
        f"{len(df)} clean rows; nulls remaining = {nulls_remaining}; "
        f"regions = {sorted(df['region'].unique())}")

    return df, audit


def main() -> None:
    # ── Load raw data ────────────────────────────────────────────────────────
    df_raw = pd.read_excel(RAW_PATH)

    # Required preview per CLAUDE.md: head / shape / dtypes before any analysis.
    print("=== RAW PREVIEW ===")
    print(df_raw.head())
    print("\nshape:", df_raw.shape)
    print("\ndtypes:\n", df_raw.dtypes)

    # ── Clean + capture audit trail ──────────────────────────────────────────
    df, audit = clean_with_audit(df_raw)
    audit_df = pd.DataFrame(audit, columns=AUDIT_COLUMNS)

    # ── Write outputs to clean/ (never overwrite the raw source) ─────────────
    os.makedirs(CLEAN_DIR, exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    audit_df.to_csv(AUDIT_PATH, index=False)

    # ── Cleaning report (echo the audit trail) ───────────────────────────────
    print("\n=== CLEANING AUDIT ===")
    for rec in audit:
        print(f"  [{rec['step']}] {rec['action']:<28} "
              f"in={rec['rows_in']!s:>5}  affected={rec['rows_affected']!s:>5}  "
              f"out={rec['rows_out']!s:>5}")
    print(f"\nclean data written to: {CLEAN_PATH}")
    print(f"audit trail written to: {AUDIT_PATH}")


if __name__ == "__main__":
    main()
