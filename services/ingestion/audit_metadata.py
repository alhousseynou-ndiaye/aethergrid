
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "raw" / "metadata.csv"


def audit_metadata():
    with DATA_PATH.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames or []
        rows = list(reader)

    if not rows:
        raise ValueError("Aucune donnée à analyser.")

    required = {
        "building_id", "site_id",
        "primaryspaceusage", "electricity"
    }

    if not required.issubset(columns):
        raise ValueError("Colonnes obligatoires manquantes.")

    total = len(rows)

    print("=== AETHERGRID DATA QUALITY AUDIT ===")

    # 1. Vérifier les identifiants
    ids = [
        row["building_id"].strip()
        for row in rows
        if row["building_id"].strip()
    ]
    counts = Counter(ids)

    print(f"\nLignes : {total}")
    print(f"Bâtiments uniques : {len(counts)}")
    print(f"Identifiants manquants : {total - len(ids)}")
    print(f"Doublons d'identifiant : {sum(n - 1 for n in counts.values())}")

    # 2. Mesurer les valeurs manquantes
    missing = {
        col: sum(not row[col].strip() for row in rows)
        for col in columns
    }

    print("\nTop 10 colonnes les plus incomplètes :")
    for col, count in sorted(
        missing.items(), key=lambda x: x[1], reverse=True
    )[:10]:
        print(f"{col}: {count / total * 100:.1f}%")

    # 3. Répartition des bâtiments
    usages = Counter(
        row["primaryspaceusage"].strip() or "Non renseigné"
        for row in rows
    )

    print("\nTop 5 types de bâtiments :")
    for usage, count in usages.most_common(5):
        print(f"{usage}: {count}")

    # 4. Informations sur les compteurs électriques
    electricity = Counter(
        row["electricity"].strip() or "Non renseigné"
        for row in rows
    )

    print("\nValeurs du champ electricity :")
    for value, count in electricity.most_common():
        print(f"{value}: {count}")

    # 5. Premiers candidats au prototype
    candidates = [
        row["building_id"]
        for row in rows
        if row["electricity"].strip().lower() == "yes"
    ]

    print("\nTrois premiers bâtiments candidats :")
    for building in candidates[:3]:
        print(f"- {building}")


if __name__ == "__main__":
    audit_metadata()
