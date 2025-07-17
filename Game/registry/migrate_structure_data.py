import json
from data.units import *


def migrate_structure_entry(entry):
    # Start with base fields
    new_entry = {
        "name": entry.get("name"),
        "level": entry.get("level", 1),
        "structure_roles": [],
        "limits": {},
        "access_control": {}
    }

    # Roles
    if entry.get("can_train"):
        new_entry["structure_roles"].append("trainer")
        new_entry["can_train"] = entry["can_train"]

    if entry.get("produces_items"):
        new_entry["structure_roles"].append("item_producer")
        new_entry["produces_items"] = entry["produces_items"]

    if entry.get("produces_resources"):
        new_entry["structure_roles"].append("producer")
        new_entry["produces_resources"] = entry["produces_resources"]

    if entry.get("can_cast_rituals"):
        new_entry["structure_roles"].append("ritual_caster")

    if entry.get("build_type"):
        new_entry["structure_roles"].append("ship_builder")
        new_entry["build_type"] = entry["build_type"]

    # Limits
    if entry.get("max_unit_level") or entry.get("train_limit_per_turn"):
        new_entry["limits"]["unit_training"] = {
            "max_level": entry.get("max_unit_level", 1),
            "per_turn": entry.get("train_limit_per_turn", 1)
        }

    if entry.get("produce_item_limit_per_turn"):
        new_entry["limits"]["item_production"] = {
            "per_turn": entry["produce_item_limit_per_turn"]
        }

    if entry.get("max_build_formula"):
        new_entry["limits"]["ship_building"] = {
            "formula": entry["max_build_formula"]
        }

    # Specialization
    if entry.get("requires_specialization"):
        new_entry["specialization"] = {
            "required": True,
            "options": entry.get("specialization_options", [])
        }

    # Access control
    if entry.get("requires_approval"):
        new_entry["access_control"]["approval_required"] = True

    return new_entry

def migrate_structure_data(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    new_data = [migrate_structure_entry(entry) for entry in old_data]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2)

    print(f"✅ Migration complete. Refactored data saved to {output_path}")

# Example usage
migrate_structure_data("StructureData.json", "StructureData_refactored.json")