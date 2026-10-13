
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "raw" / "electricity.csv"

BUILDINGS = [
    "Panther_education_Rosalie",
    "Panther_education_Misty",
    "Panther_education_Mattie",
]


def audit():
    with DATA_PATH.open(
        encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.reader(file)
        header = next(reader)

        indices = {
            building: header.index(building)
            for building in BUILDINGS
        }

        for building, index in indices.items():
            zeros = 0
            positives = 0
            missing = 0
            invalid = 0
            first_positive = None

            # Restart the reader for each building
            file.seek(0)
            next(reader)

            for row in reader:
                raw = row[index].strip()

                if not raw:
                    missing += 1
                    continue

                try:
                    value = Decimal(raw)
                except InvalidOperation:
                    invalid += 1
                    continue

                if not value.is_finite() or value < 0:
                    invalid += 1
                elif value == 0:
                    zeros += 1
                else:
                    positives += 1
                    if first_positive is None:
                        first_positive = row[0]

            print(f"\n=== {building} ===")
            print(f"Zero readings: {zeros}")
            print(f"Positive readings: {positives}")
            print(f"Missing readings: {missing}")
            print(f"Invalid readings: {invalid}")
            print(f"First positive: {first_positive}")


if __name__ == "__main__":
    audit()
