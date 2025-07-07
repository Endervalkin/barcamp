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
        "level": int(row[1]),
        "category": "Ground",
        "map_movement": int(row[2]),
        "physical_attack": int(row[3]),
        "spell_attack": int(row[4]),
        "body": int(row[5]),
        "armor": int(row[6]),
        "physical_range": int(row[7]),
        "spell_range": int(row[8]),
        "combat_movement": int(row[9]),
        "damage_reduction": int(row[10]),
        "spell_slot": int(row[11]),
        "training_time": int(row[12]),
        "training_cost": parse_resources(row, 13),
        "upkeep": parse_resources(row, 19)
    }

def parse_csv_to_json(csv_file, json_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip header row
        next(reader)  # skip second header row
        units = [parse_row(row) for row in reader if row and row[0].strip()]

    with open(json_file, "w", encoding="utf-8") as out:
        json.dump(units, out, indent=2)
    print(f"✅ Parsed {len(units)} ground units into {json_file}")

if __name__ == "__main__":
    parse_csv_to_json("ground_units.csv", "GroundUnits.json")

