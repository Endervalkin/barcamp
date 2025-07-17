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
            res_type = key[len(prefix)+1:].strip()
            val_str = str(value).strip().lower()

            if val_str == "true":
                block[res_type] = True
            elif val_str == "false":
                block[res_type] = False
            else:
                num = safe_int(value)
                if num > 0:
                    block[res_type] = num

    return block

def extract_boolean_block(row, prefix):
    block = {}
    for key, value in row.items():
        if key.startswith(prefix + "_"):
            loc = key[len(prefix)+1:].replace("_", " ").strip()
            val = str(value).strip().lower()
            if val in ["true", "yes", "1"]:
                block[loc] = True
            elif val in ["false", "no", "0"]:
                block[loc] = False
    return block


def migrate_row(row):
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
        "garrrison": safe_int(row.get("garrison")),
        "population": safe_int(row.get("population")),
       
    }

    entry["build_cost"] = extract_prefixed_block(row, "build_cost")
    entry["production"] = extract_prefixed_block(row, "production")
    entry["upkeep"] = extract_prefixed_block(row, "upkeep")
    entry["settlement_needs"] = extract_prefixed_block(row, "settlement_needs")
    entry["domestic_index"] = extract_prefixed_block(row, "domestic_index")
    entry["building_location"] = extract_boolean_block(row, "building_location")

    build_turns = safe_int(row.get("build_turns"))
    if build_turns > 0:
        entry["build_turns"] = build_turns

# Flat fields to include directly
    flat_fields = [
        "can_train",
        "build_type",
        "max_unit_level",
        "requires_specialization",
        "specialization_options",
        "train_limit_per_turn",
        "produces_items",
        "produce_item_limit_per_turn",
        "can_cast_rituals",
        "max_build_formula",
        "requires_approval"
    ]

    for field in flat_fields:
        raw = row.get(field)
        if raw is None:
            continue

        val = str(raw).strip()

        # Normalize booleans
        if val.lower() in ["true", "yes", "1"]:
            entry[field] = True
        elif val.lower() in ["false", "no", "0"]:
            entry[field] = False
        elif val.isdigit():
            entry[field] = int(val)
        else:
            entry[field] = val  # Keep as string (e.g. formulas or options)

    # Initialize sub-blocks
    entry["limits"] = {}
    entry["access_control"] = {}

    # 🎯 Unit Training Limits
    if row.get("can_train", "").strip().lower() == "true":
        entry["limits"]["unit_training"] = {
            "max_level": safe_int(row.get("max_unit_level"), 1),
            "per_turn": safe_int(row.get("train_limit_per_turn"), 1)
        }

    # 🧪 Item Production Limits
    if row.get("produces_items", "").strip().lower() == "true":
        entry["limits"]["item_production"] = {
            "per_turn": safe_int(row.get("produce_item_limit_per_turn"), 1)
        }

    # 🛠️ Ship Building Formula
    if row.get("max_build_formula"):
        entry["limits"]["ship_building"] = {
            "formula": row["max_build_formula"].strip()
        }

    # 🔐 Requires Approval
    if str(row.get("requires_approval", "")).strip().lower() == "true":
        entry["access_control"]["approval_required"] = True
    return entry
def get_header_indices(headers, target_names):
    return [i for i, h in enumerate(headers) if h.strip() in target_names]

def parse_structure_csv(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        data = []
        for row in reader:
            migrated = migrate_row(row)
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