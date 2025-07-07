import csv
import json

def parse_resources(row, start_index):
    keys = ['L', 'S', 'M', 'F', 'R', 'C']
    return {
        key: int(row[start_index + i]) if row[start_index + i].isdigit() else 0
        for i, key in enumerate(keys)
    }

def parse_row(row):
    return {
        "name": row[0].strip(),
        "category": "Siege",
        "armor": int(row[1]),
        "attack": int(row[2]),
        "combat_movement": int(row[3]),
        "range": int(row[4]),
        "damage_reduction": int(row[5]),
        "training_time": int(row[6]),
        "training_cost": parse_resources(row, 7),
        "upkeep": parse_resources(row, 13)
    }

def parse_csv_to_json(csv_file, json_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip header 1
        next(reader)  # skip header 2
        weapons = [parse_row(row) for row in reader if row and row[0].strip()]

    with open(json_file, "w", encoding="utf-8") as out:
        json.dump(weapons, out, indent=2)
    print(f"✅ Parsed {len(weapons)} siege weapons into {json_file}")

if __name__ == "__main__":
    parse_csv_to_json("siege_weapons.csv", "SiegeWeapons.json")