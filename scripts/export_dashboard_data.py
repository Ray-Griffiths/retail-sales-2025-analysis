"""
Aggregate clean/retail_sales_clean.csv into a single JSON payload for the
dashboard artifact. Read-only on the data; writes charts/dashboard_data.json.

Usage:
    python scripts/export_dashboard_data.py
"""

import os
import json
import pandas as pd

CLEAN_PATH = os.path.join("clean", "retail_sales_clean.csv")
OUT_PATH = os.path.join("charts", "dashboard_data.json")


def main():
    # ---- Load cleaned data (read-only) ----
    df = pd.read_csv(CLEAN_PATH, parse_dates=["order_date"])

    # ---- Headline KPIs ----
    kpis = {
        "total_revenue": round(float(df["revenue ($)"].sum()), 2),
        "total_orders": int(len(df)),
        "avg_order_value": round(float(df["revenue ($)"].mean()), 2),
        "unique_customers": int(df["customer_id"].nunique()),
        "avg_units_per_order": round(float(df["quantity"].mean()), 2),
    }

    # ---- Revenue by region (descending) ----
    region_rev = df.groupby("region")["revenue ($)"].sum().sort_values(ascending=False)
    region = [{"region": r, "revenue": round(float(v), 2)} for r, v in region_rev.items()]

    # ---- Monthly revenue trend ----
    monthly = df.set_index("order_date")["revenue ($)"].resample("MS").sum()
    trend = [
        {"month": d.strftime("%b"), "revenue": round(float(v), 2)}
        for d, v in monthly.items()
    ]

    # ---- Revenue by category (descending) ----
    cat_rev = df.groupby("category")["revenue ($)"].sum().sort_values(ascending=False)
    category = [{"category": c, "revenue": round(float(v), 2)} for c, v in cat_rev.items()]

    # ---- Region x category matrix (revenue) ----
    matrix = df.groupby(["region", "category"])["revenue ($)"].sum().unstack(fill_value=0)
    matrix = matrix.round(2)
    region_category = {
        "regions": list(matrix.index),
        "categories": list(matrix.columns),
        "values": matrix.values.tolist(),
    }

    # ---- Top category per region ----
    top_cat = {}
    for r in matrix.index:
        row = matrix.loc[r]
        top_cat[r] = {"category": row.idxmax(), "revenue": round(float(row.max()), 2)}

    payload = {
        "kpis": kpis,
        "region": region,
        "trend": trend,
        "category": category,
        "region_category": region_category,
        "top_category_per_region": top_cat,
    }

    os.makedirs("charts", exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(json.dumps(payload, indent=2))
    print(f"\nSaved: {OUT_PATH}")


if __name__ == "__main__":
    main()
