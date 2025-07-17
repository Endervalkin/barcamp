import csv
import json
import re
import os

script_dir = os.path.dirname(__file__)
csv_path = os.path.join(script_dir, "..", "data", "units", "Structure.csv")
output_path = os.path.join(script_dir, "..", "data", "units", "StructureData_refactored.json")



def safe_int(value, default=0):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def parse_roles(row, column="structure_role"):
    value = row.get(column, "")
    return [r.strip() for r in value.split(",") if r.strip()]

def parse_resource_block(row, columns):
    block = {}
    for col in columns:
        raw = row.get(col)
        value = safe_int(raw)
        if value > 0:
            block[col] = value
    return block

def extract_prefixed_block(row, prefix):
    block = {}
    for key, value in row.items():
        if key.startswith(prefix + "_"):
            res_type = key[len(prefix)+1:]
            amount = safe_int(value)
            if amount > 0:
                block[res_type] = amount
    return block

def migrate_row(row, headers):
    name = row.get("name") or row.get("Name")
    
    level = row.get("level") or row.get("Level")
    if not name or not level:
        return None
    

    entry = {
        "name": name.strip(),
        "level": safe_int(level),
        "structure_role": parse_roles(row),
        "limits": {},
        "access_control": {},
        "build_turns": {},
        "build_cost": {},
        "production": {},
        "upkeep": {},
        "settlement_needs": {},
        "domestic_index": {},
        "garrrison": safe_int(row.get("garrison", 0)),
       "population": safe_int(row.get("population", 0)),
       
    }

    entry["build_cost"] = extract_prefixed_block(row, "build_cost")
    entry["production"] = extract_prefixed_block(row, "production")
    entry["upkeep"] = extract_prefixed_block(row, "upkeep")
    entry["settlement_needs"] = extract_prefixed_block(row, "settlement_needs")
    entry["domestic_index"] = extract_prefixed_block(row, "domestic_index")
    entry["building_location"] = extract_prefixed_block(row, "build_location")

    build_turns = safe_int(row.get("build_turns"))
    if build_turns > 0:
        entry["build_turns"] = build_turns


    # Resource blocks
    for block_name in ["build_cost", "production", "upkeep"]:
        block = parse_resource_block(row, headers[block_name])
        if block:
            entry[block_name] = block
    
    print(f"{entry['name']} → {block_name}: {block}")


    return entry
def get_header_indices(headers, target_names):
    return [i for i, h in enumerate(headers) if h.strip() in target_names]

def parse_structure_csv(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        lines = f.readlines()

    # Use line 2 as the real header (row 1 is grouped labels)
    headers_row = [h.strip() for h in lines[1].strip().split(",")]
    reader = csv.DictReader(lines[2:], fieldnames=headers_row)
    print("🔍 CSV headers detected:", reader.fieldnames)

        # Define column slices
    header_map = {
        "build_cost": get_header_indices(headers_row, ["L", "S", "M", "F", "R", "C"]),
        "production": get_header_indices(headers_row, ["L", "S", "M", "F", "R", "C"]),
        "upkeep": get_header_indices(headers_row, ["L", "S", "M", "F", "R", "C"]),
        "settlement_needs": get_header_indices(headers_row, ["Med","Edu","Mor"]),
        "domestic_index": get_header_indices(headers_row, ["Stability", "Economy", "Loyalty", "Unrest"])
    }

    data = []
    for row in reader:
        migrated = migrate_row(row, header_map)
        if migrated:
            data.append(migrated)

    return data

# Example usage
if __name__ == "__main__":
    structures = parse_structure_csv(csv_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(structures, f, indent=2)
    
    print(f"✅ Structure data parsed and saved to → {output_path}")