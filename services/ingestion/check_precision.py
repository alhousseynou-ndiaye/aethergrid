
import csv
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "raw" / "electricity.csv"

BUILDINGS = [
    "Panther_education_Rosalie",
    "Panther_education_Misty",
    "Panther_education_Mattie",
]

PRECISION = Decimal("0.00001")


def check_precision():
    total = 0
    affected = 0
    rounded_to_zero = 0
    max_error = Decimal("0")

    with DATA_PATH.open(
        encoding="utf-8-sig", newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            for building in BUILDINGS:
                raw = row[building].strip()

                if not raw:
                    continue

                value = Decimal(raw)

                if not value.is_finite() or value < 0:
                    continue

                total += 1

                rounded = value.quantize(PRECISION)
                error = abs(value - rounded)

                if error > 0:
                    affected += 1
                    max_error = max(max_error, error)

                if value > 0 and rounded == 0:
                    rounded_to_zero += 1

    print("=== AETHERGRID PRECISION AUDIT ===")
    print(f"Valid readings: {total}")
    print(f"Readings requiring rounding: {affected}")
    print(f"Positive values rounded to zero: {rounded_to_zero}")
    print(f"Maximum absolute rounding error: {max_error}")


if __name__ == "__main__":
    check_precision()
