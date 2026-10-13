
import csv
import os
from decimal import Decimal
from pathlib import Path

import psycopg
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[2]

load_dotenv(ROOT / ".env")

METADATA_PATH = ROOT / "data" / "raw" / "metadata.csv"

BUILDINGS = {
    "Panther_education_Rosalie",
    "Panther_education_Misty",
    "Panther_education_Mattie",
}


def load_buildings():
    with METADATA_PATH.open(
        encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        selected = {
            row["building_id"]: row
            for row in reader
            if row["building_id"] in BUILDINGS
        }

    missing = BUILDINGS - selected.keys()

    if missing:
        raise ValueError(f"Missing buildings: {missing}")

    password = os.getenv("POSTGRES_PASSWORD")

    if not password:
        raise ValueError("POSTGRES_PASSWORD is missing")

    with psycopg.connect(
        host="localhost",
        port=5433,
        dbname="aethergrid",
        user="aethergrid",
        password=password,
    ) as conn:

        with conn.cursor() as cursor:
            inserted = 0

            for building_id, row in sorted(selected.items()):
                sqm = (
                    Decimal(row["sqm"])
                    if row["sqm"].strip()
                    else None
                )

                cursor.execute(
                    """
                    INSERT INTO buildings (
                        building_id,
                        site_id,
                        primary_space_usage,
                        sqm,
                        timezone
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (building_id) DO NOTHING
                    """,
                    (
                        building_id,
                        row["site_id"],
                        row["primaryspaceusage"],
                        sqm,
                        row["timezone"],
                    ),
                )

                inserted += cursor.rowcount

    print(f"Buildings selected: {len(selected)}")
    print(f"Buildings inserted: {inserted}")


if __name__ == "__main__":
    load_buildings()
