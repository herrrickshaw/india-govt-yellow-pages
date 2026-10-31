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
    "ministry_officials": DATA / "ministry_officials.csv",
    "policy_contacts": DATA / "policy_contacts.csv",
    "pib_ministry_contacts": DATA / "pib_ministry_contacts.csv",
    "ias_officers": DATA / "ias_officers.csv",
    "ips_officers": DATA / "ips_officers.csv",
    # who signed what (scripts/signatory_matrix.py)
    "notification_signatories": DATA / "signatories/notification_signatories.csv",
    "officer_topic_matrix": DATA / "signatories/officer_topic_matrix.csv",
    "officer_documents": DATA / "signatories/officer_documents.csv",
    "signatory_directory": DATA / "signatories/signatory_directory.csv",
    "state_signatory_directory": DATA / "states/signatory_directory_all_states.csv",
    "career_events": DATA / "career/career_events.csv",
    "state_officials": DATA / "states/state_officials.csv",
    "state_notification_signatories": DATA / "states/notification_signatories_all_states.csv",
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
