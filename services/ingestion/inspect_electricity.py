
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "raw" / "electricity.csv"

BUILDINGS = [
    "Panther_education_Rosalie",
    "Panther_education_Misty",
    "Panther_education_Mattie",
]


def inspect_electricity():
    with DATA_PATH.open(
        encoding="utf-8-sig", newline=""
    ) as file:

        # Detect an accidental Git LFS pointer
        if file.readline().startswith(
            "version https://git-lfs.github.com/spec/v1"
        ):
            raise ValueError(
                "Git LFS pointer downloaded instead of CSV."
            )

        file.seek(0)
        reader = csv.reader(file)
        header = next(reader)

        timestamp_column = header[0]
        available = [
            building for building in BUILDINGS
            if building in header
        ]

        print("=== AETHERGRID ELECTRICITY AUDIT ===")
        print(f"Timestamp column: {timestamp_column}")
        print(f"Meter columns: {len(header) - 1}")
        print(f"Selected buildings: {available}")

        if not available:
            raise ValueError(
                "No selected buildings found in the dataset."
            )

        indices = {
            building: header.index(building)
            for building in available
        }

        valid = {building: 0 for building in available}
        missing = {building: 0 for building in available}
        first_timestamp = None
        last_timestamp = None
        total = 0

        for row in reader:
            if not row:
                continue

            total += 1
            first_timestamp = first_timestamp or row[0]
            last_timestamp = row[0]

            for building, index in indices.items():
                value = (
                    row[index].strip()
                    if index < len(row) else ""
                )

                if value:
                    valid[building] += 1
                else:
                    missing[building] += 1

        print(f"\nTotal timestamps: {total}")
        print(f"First timestamp: {first_timestamp}")
        print(f"Last timestamp: {last_timestamp}")

        for building in available:
            print(f"\n{building}")
            print(f"  Populated readings: {valid[building]}")
            print(f"  Missing readings: {missing[building]}")


if __name__ == "__main__":
    inspect_electricity()
