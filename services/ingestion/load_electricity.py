
import csv
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import psycopg
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

DATA_PATH = ROOT / "data" / "raw" / "electricity.csv"

BUILDINGS = [
    "Panther_education_Rosalie",
    "Panther_education_Misty",
    "Panther_education_Mattie",
]

BATCH_SIZE = 1000

INSERT_SQL = """
    INSERT INTO electricity_readings (
        building_id,
        timestamp_local,
        consumption_kwh
    )
    VALUES (%s, %s, %s)
    ON CONFLICT (building_id, timestamp_local)
    DO NOTHING
"""


def insert_batch(cursor, records):
    if not records:
        return 0

    cursor.executemany(INSERT_SQL, records)
    return cursor.rowcount


def load_electricity():
    password = os.getenv("POSTGRES_PASSWORD")

    if not password:
        raise ValueError("POSTGRES_PASSWORD is missing")

    hours = 0
    valid = 0
    missing = 0
    rejected = 0
    inserted = 0
    batch = []

    with psycopg.connect(
        host="127.0.0.1",
        port=5433,
        dbname="aethergrid",
        user="aethergrid",
        password=password,
    ) as conn:

        with conn.cursor() as cursor:

            with DATA_PATH.open(
                encoding="utf-8-sig",
                newline=""
            ) as file:

                reader = csv.reader(file)
                header = next(reader)

                if not header or header[0] != "timestamp":
                    raise ValueError("Invalid CSV header")

                if not all(b in header for b in BUILDINGS):
                    raise ValueError("Building columns missing")

                indices = {
                    building: header.index(building)
                    for building in BUILDINGS
                }

                for row in reader:
                    if not row:
                        continue

                    if len(row) != len(header):
                        raise ValueError(
                            f"Invalid row at hour {hours + 1}"
                        )

                    timestamp = datetime.fromisoformat(
                        row[0].strip()
                    )

                    if timestamp.tzinfo is not None:
                        raise ValueError(
                            "Expected a local naive timestamp"
                        )

                    hours += 1

                    for building, index in indices.items():
                        raw = row[index].strip()

                        if not raw:
                            missing += 1
                            continue

                        try:
                            kwh = Decimal(raw)
                        except InvalidOperation:
                            rejected += 1
                            continue

                        if not kwh.is_finite() or kwh < 0:
                            rejected += 1
                            continue

                        valid += 1
                        batch.append(
                            (building, timestamp, kwh)
                        )

                        if len(batch) >= BATCH_SIZE:
                            inserted += insert_batch(
                                cursor, batch
                            )
                            batch.clear()

                # Insert any remaining records
                if batch:
                    inserted += insert_batch(
                        cursor, batch
                    )
                    batch.clear()

    # The transaction has committed successfully.
    print("=== AETHERGRID FULL INGESTION ===")
    print(f"Hours processed: {hours}")
    print(f"Valid readings: {valid}")
    print(f"Missing readings: {missing}")
    print(f"Rejected readings: {rejected}")
    print(f"Rows inserted: {inserted}")


if __name__ == "__main__":
    load_electricity()
