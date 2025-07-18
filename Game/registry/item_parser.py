import os
import json



def safe_int(value, default=0):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def parse_produce_items(raw_string):
    """
    Parses produce_items from CSV format:
    "Item Name | cost | tag1, tag2 || Item Name 2 | cost | tag3 || ..."
    Returns a list of dictionaries with name, cost, and groups.
    """
    entries = []
    if not raw_string:
        return entries

    for block in raw_string.split("||"):
        parts = [p.strip() for p in block.strip().split("|")]
        if len(parts) < 3:
            continue  # Skip malformed blocks

        name = parts[0]
        cost = safe_int(parts[1], 0)
        tags = [tag.strip() for tag in parts[2].split(",") if tag.strip()]
        entries.append({"name": name, "cost": cost, "groups": tags})

    return entries

def validate_produce_items(item_list, structure_name=None):
    """
    Checks for missing fields, malformed costs, or duplicate items.
    """
    seen_names = set()
    for item in item_list:
        name = item.get("name")
        cost = item.get("cost")

        if not name or cost is None:
            print(f"⚠️ Missing fields in item: {item}")
        elif name in seen_names:
            print(f"⚠️ Duplicate item '{name}' in structure '{structure_name}'")
        elif cost <= 0:
            print(f"⚠️ Invalid cost for item '{name}' in '{structure_name}': {cost}")
        seen_names.add(name)

def get_valid_recipes(structure, turn_points=None):
    """
    Returns a list of items that the structure can produce this turn,
    based on its level, per-turn limit, and item costs.
    """
    recipes = structure.get("produce_items", [])
    level = structure.get("level", 1)
    limits = structure.get("limits", {}).get("item_production", {})
    per_turn_limit = limits.get("per_turn", 1)

    # Default to level-based point pool if not overridden
    available_points = turn_points if turn_points is not None else level

    # Filter recipes by cost
    valid = [r for r in recipes if r.get("cost", 0) <= available_points]

    # Enforce per-turn cap
    return valid[:per_turn_limit]