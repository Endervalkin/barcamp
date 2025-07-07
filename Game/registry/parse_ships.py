import csv
import json

def parse_resources(fields):
    keys = ['L', 'S', 'M', 'F', 'R', 'C']
    return {k: int(fields[i]) if fields[i].isdigit() else 0 for i, k in enumerate(keys)}

def parse_row(row):
    return {
        "name": row[0].strip(),
        "level": int(row[1]),
        "class": int(row[2]),
        "type": row[3].strip(),
        "armor": int(row[4]),
        "weapon_mount": int(row[5]),
        "attack": int(row[6]),
        "combat_movement": int(row[7]),
        "range": int(row[8]),
        "damage_reduction": int(row[9]),
        "cargo": int(row[10]),
        "map_movement": int(row[11]),
        "training_time": int(row[12]),

        "training_cost": parse_resources(row[13:19]),
        "upkeep":        parse_resources(row[19:25]),
        "production":    parse_resources(row[25:31])
    }

def parse_csv_to_json(csv_file, json_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip first header row
        next(reader)  # skip second header row
        ships = [parse_row(row) for row in reader if row and row[0].strip()]

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(ships, f, indent=2)
    print(f"✅ Parsed {len(ships)} entries into {json_file}")

if __name__ == "__main__":
    parse_csv_to_json("ships.csv", "ShipsAndAirships.json")