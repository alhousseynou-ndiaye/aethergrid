
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "metadata.csv"


def inspect_metadata():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset introuvable : {DATA_PATH}"
        )

    with DATA_PATH.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames
        rows = list(reader)

    if not columns or not rows:
        raise ValueError("Le fichier CSV est vide ou invalide.")

    print("=== AETHERGRID DATA INSPECTION ===")
    print(f"Nombre de bâtiments : {len(rows)}")
    print(f"Nombre de colonnes : {len(columns)}")

    print("\nColonnes disponibles :")
    for column in columns:
        print(f"- {column}")

    print("\nPremier enregistrement :")
    print(rows[0])


if __name__ == "__main__":
    inspect_metadata()
