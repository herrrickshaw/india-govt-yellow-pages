#!/usr/bin/env python3
"""Load the three CSVs into data/yellowpages.duckdb (one table per CSV)."""
import sys
from pathlib import Path

import duckdb

DATA = Path(__file__).resolve().parent.parent / "data"
DB = DATA / "yellowpages.duckdb"

TABLES = {
    "organizations_index": DATA / "organizations_index.csv",
    "org_contacts": DATA / "org_contacts.csv",
    "officials": DATA / "officials.csv",
}


def main():
    con = duckdb.connect(str(DB))
    for table, csv_path in TABLES.items():
        if not csv_path.exists():
            print(f"skip {table}: {csv_path} missing", file=sys.stderr)
            continue
        con.execute(f"CREATE OR REPLACE TABLE {table} AS "
                    f"SELECT * FROM read_csv_auto('{csv_path}', header=true, all_varchar=true)")
        n = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"{table}: {n} rows")
    con.close()
    print(f"-> {DB}")


if __name__ == "__main__":
    main()
