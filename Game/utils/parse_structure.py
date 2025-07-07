import csv
import json
import re

RESOURCE_KEYS = ['L', 'S', 'M', 'F', 'R', 'C']
DI_KEYS = ['Stability', 'Economy', 'Loyalty', 'Unrest']
NEED_KEYS = ['Mor', 'Edu', 'Med']
LOCATION_KEYS = ['Village Inn', 'Outpost', 'City', 'Fortress']

def parse_name_level(value):
    match = re.match(r"(.+?) lvl (\d+)", value)
    if match:
        return match.group(1).strip(), int(match.group(2))
    return value.strip(), 1

def parse_int(val):
    try:
        return int(float(val))
    except:
        return 0

def parse_bool(val):
    return val.strip().upper() == 'TRUE'

def parse_cost(row, start_idx):
    return {
        key: parse_int(row[start_idx + i])
        for i, key in enumerate(RESOURCE_KEYS)
        if row[start_idx + i].strip() and parse_int(row[start_idx + i]) > 0
    }

def parse_structure_row(row):
    name, level = parse_name_level(row[0])
    return {
        "name": name,
        "level": level,
        "build_time": parse_int(row[1]),
        "build_cost": parse_cost(row, 2),
        "production": parse_cost(row, 8),
        "upkeep": parse_cost(row, 14),
        "settlement_needs": {
            "Morale": parse_int(row[20]),
            "Education": parse_int(row[21]),
            "Medical": parse_int(row[22])
        },
        "di_modifiers": {
            "Stability": parse_int(row[23]),
            "Economy": parse_int(row[24]),
            "Loyalty": parse_int(row[25]),
            "Unrest": parse_int(row[26])
        },
        "garrison": parse_int(row[27]),
        "population": parse_int(row[28]),
        "buildable_in": {
            "Village Inn": parse_bool(row[29]),
            "Outpost": parse_bool(row[30]),
            "City": parse_bool(row[31]),
            "Fortress": parse_bool(row[32])
        }
    }

def parse_structure_csv(csv_file, json_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip header 1
        next(reader)  # skip header 2
        structures = [parse_structure_row(row) for row in reader if row and row[0].strip()]

    with open(json_file, 'w', encoding='utf-8') as out:
        json.dump(structures, out, indent=2)
    print(f"✅ Parsed {len(structures)} structures into {json_file}")

if __name__ == "__main__":
    parse_structure_csv("Structure.csv", "StructureData.json")