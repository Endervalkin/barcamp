import csv
import json
import re

RESOURCE_KEYS = ['L', 'S', 'M', 'F', 'R', 'C']
NEED_KEYS = ['Med', 'Edu', 'Mor']

def parse_int(value):
    try:
        return int(float(value.strip()))
    except:
        return 0

def parse_bool(value):
    return value.strip().upper() == "TRUE"


def parse_structure_requirements(cell):
    result = []
    if not cell.strip():
        return result
    for group in cell.split("|"):
        or_group = []
        for item in group.split(","):
            item = item.strip()
            if ":" in item:
                name, lvl = item.split(":")
                or_group.append({"name": name.strip(), "level": parse_int(lvl)})
            elif item:
                or_group.append({"name": item.strip(), "level": 1})
        if or_group:
            result.append(or_group)
    return result

def parse_row(row):
    # Ensure row has 15 columns (pad if necessary)
    row += [""] * (15 - len(row))
    
    name, level = parse_name_level(row[0])

    return {
        "name": name,
        "level": level,
        "build_turns": parse_int(row[1]),
        "build_cost": {
            "L": parse_int(row[2]),
            "S": parse_int(row[3]),
            "M": parse_int(row[4]),
            "F": parse_int(row[5]),
            "R": parse_int(row[6]),
            "C": parse_int(row[7])
        },
        "garrison": parse_int(row[8]),
        "population_base": parse_int(row[9]),
        "population_critical": parse_int(row[10]),
        "upgrade_requirements": {
            "needs_required": {
                "Medical": parse_int(row[11]),
                "Education": parse_int(row[12]),
                "Morale": parse_int(row[13])
            },
            "structures_required": parse_structure_requirements(row[14])
        }
    }


def parse_csv_to_json(csv_file, json_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # Skip header 1
        next(reader)  # Skip header 2
        data = [parse_row(row) for row in reader if row and row[0].strip()]

    with open(json_file, "w", encoding="utf-8") as out:
        json.dump(data, out, indent=2)
    print(f"✅ Exported {len(data)} settlement tiers into {json_file}")

if __name__ == "__main__":
    parse_csv_to_json("settlement.csv", "SettlementData.json")