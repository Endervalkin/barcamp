import csv
import json
from utils.parsing import parse_int, parse_name_level, parse_structure_requirements

def parse_settlement_row(row):
    row += [""] * (15 - len(row))  # ensure length
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
        next(reader)  # skip header 1
        next(reader)  # skip header 2
        rows = [parse_settlement_row(r) for r in reader if r and r[0].strip()]
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"✅ Parsed {len(rows)} settlements into {json_file}")