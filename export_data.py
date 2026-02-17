"""
Export the anonymized health data to a CSV file you can open in Excel or Google Sheets.

Usage:
    python export_data.py

This creates a file called "health_data.csv" in the current folder.
It contains ONLY anonymized data - no phone numbers or names.
"""
import csv
import os
import sqlite3

from dotenv import load_dotenv
load_dotenv()

HEALTH_DB = os.environ.get("HEALTH_DB_PATH", "data/health.db")
IDENTITY_DB = os.environ.get("IDENTITY_DB_PATH", "data/identity.db")

OUTPUT_FILE = "health_data.csv"


def export():
    if not os.path.exists(HEALTH_DB):
        print("No health data found yet. Run the study for a bit first!")
        return

    # Get anonymized participant info (UV exposure, zip, household - no phone numbers)
    participants = {}
    if os.path.exists(IDENTITY_DB):
        conn = sqlite3.connect(IDENTITY_DB)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, uv_exposure, uv_hours_per_week, zip_code, household_size FROM participants"
        ).fetchall()
        conn.close()
        for r in rows:
            participants[r["id"]] = {
                "uv_exposure": "Yes" if r["uv_exposure"] else "No",
                "uv_hours_per_week": r["uv_hours_per_week"] or "",
                "zip_code": r["zip_code"] or "",
                "household_size": r["household_size"] or "",
            }

    # Get health responses
    conn = sqlite3.connect(HEALTH_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT participant_id, week_start, sick, severity, symptoms, responded_at "
        "FROM responses ORDER BY week_start, participant_id"
    ).fetchall()
    conn.close()

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "participant_id", "week_start", "sick", "severity", "symptoms",
            "responded_at", "uv_exposure", "uv_hours_per_week", "zip_code", "household_size"
        ])
        for r in rows:
            p = participants.get(r["participant_id"], {})
            writer.writerow([
                r["participant_id"],
                r["week_start"],
                "Yes" if r["sick"] else "No",
                r["severity"] or "",
                r["symptoms"] or "",
                r["responded_at"],
                p.get("uv_exposure", ""),
                p.get("uv_hours_per_week", ""),
                p.get("zip_code", ""),
                p.get("household_size", ""),
            ])

    print(f"Exported {len(rows)} responses to {OUTPUT_FILE}")
    print("You can open this file in Excel or Google Sheets.")
    print("NOTE: This file contains NO phone numbers or names - it's fully anonymized.")


if __name__ == "__main__":
    export()
