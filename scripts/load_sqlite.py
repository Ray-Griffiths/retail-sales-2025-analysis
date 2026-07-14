"""
Create a SQLite database (retail.db) and load clean/retail_sales_clean.csv
into a table called `sales`. Confirms the load with a row count and prints
the table schema.

Read-only on the CSV; (re)creates retail.db.

Usage:
    python scripts/load_sqlite.py
"""

import os
import sqlite3
import pandas as pd

CLEAN_PATH = os.path.join("clean", "retail_sales_clean.csv")
DB_PATH = "retail.db"
TABLE = "sales"


def main():
    # ---- Load the cleaned CSV (read-only) ----
    # Parse order_date so it lands in the DB as an ISO date string, not free text.
    df = pd.read_csv(CLEAN_PATH, parse_dates=["order_date"])
    df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")

    # ---- Write into SQLite ----
    # Connect (creates retail.db if it doesn't exist).
    conn = sqlite3.connect(DB_PATH)
    try:
        # if_exists="replace" makes the script re-runnable: a rerun rebuilds the
        # table from scratch rather than appending duplicate rows.
        df.to_sql(TABLE, conn, if_exists="replace", index=False)

        cur = conn.cursor()

        # ---- Confirm the load with a row count ----
        db_rows = cur.execute(f"SELECT COUNT(*) FROM {TABLE};").fetchone()[0]

        print(f"Database : {DB_PATH}")
        print(f"Table    : {TABLE}")
        print(f"Rows in CSV      : {len(df)}")
        print(f"Rows in DB table : {db_rows}")
        print(f"Match            : {len(df) == db_rows}")

        # ---- Show the table schema (column name + type) ----
        print("\n=== SCHEMA (PRAGMA table_info) ===")
        print(f"{'col':<3} {'name':<16} {'type':<10} {'notnull':<7} {'pk'}")
        for cid, name, ctype, notnull, dflt, pk in cur.execute(f"PRAGMA table_info({TABLE});"):
            print(f"{cid:<3} {name:<16} {ctype:<10} {notnull:<7} {pk}")

        # ---- Show the exact CREATE TABLE statement SQLite generated ----
        print("\n=== CREATE STATEMENT ===")
        ddl = cur.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?;", (TABLE,)
        ).fetchone()[0]
        print(ddl)
    finally:
        conn.commit()
        conn.close()


if __name__ == "__main__":
    main()
