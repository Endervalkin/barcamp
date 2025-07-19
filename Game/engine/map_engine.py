import os
import json
from data.roads import road_data, hex_registry

def generate_axial_hexes(q_range, r_range):
    hex_map = {}
    for q in range(*q_range):
        for r in range(*r_range):
            hex_map[f"{q},{r}"] = {
                "terrain": "Unassigned",
                "settlement": None,
                "roads": [],
                "troops": [],
                "waterway": False,
                "special_zone": None
            }
    return hex_map

# Example call:
hexes = generate_axial_hexes((-53, 53), (-92, 92))

def get_neighboring_hexes(q, r):
    neighbors = [
        (q + 1, r), (q - 1, r), (q, r + 1), (q, r - 1),
        (q + 1, r - 1), (q - 1, r + 1)
    ]
    return [f"{n[0]},{n[1]}" for n in neighbors if f"{n[0]},{n[1]}" in hexes]

def is_valid_hex(q, r):
    return f"{q},{r}" in hexes

def place_settlement(q, r, settlement):
    hex_key = f"{q},{r}"
    if is_valid_hex(q, r):
        hexes[hex_key]["settlement"] = settlement
        return True
    return False

def place_road(q1, r1, q2, r2):
    hex_key1 = f"{q1},{r1}"
    hex_key2 = f"{q2},{r2}"
    if is_valid_hex(q1, r1) and is_valid_hex(q2, r2):
        hexes[hex_key1]["roads"].append(hex_key2)
        hexes[hex_key2]["roads"].append(hex_key1)
        return True
    return False

def move_troops(stack_id, from_hex, to_hex):
    if is_valid_hex(*from_hex) and is_valid_hex(*to_hex):
        from_key = f"{from_hex[0]},{from_hex[1]}"
        to_key = f"{to_hex[0]},{to_hex[1]}"
        if stack_id in hexes[from_key]["troops"]:
            hexes[from_key]["troops"].remove(stack_id)
            hexes[to_key]["troops"].append(stack_id)
            return True
    return False

def place_road(hexes, road_type, player):
    road = road_data[road_type]
    if len(hexes) > road["batch_size"]:
        raise ValueError("Too many hexes in one batch")

    # Deduct full batch cost even for < 10 hexes
    for res, amt in road["build_cost_per_batch"].items():
        if player["resources"].get(res, 0) < amt:
            raise ValueError(f"Insufficient {res}")
        player["resources"][res] -= amt

    # Tag hexes
    for hex_id in hexes:
        hex_registry[hex_id]["roads"].append(road_type)

    return {"built": hexes, "type": road_type, "cost": dict(road["build_cost_per_batch"])}