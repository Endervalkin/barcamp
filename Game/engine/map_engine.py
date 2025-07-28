import os
import json
import math
from math import sqrt
from flask import Flask, render_template, request, jsonify
from Game.engine.hex_renderer import axial_to_pixel, hex_points

from typing import Dict, List, Tuple

# ─────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────

# Compute the path to your Game/data folder
DATA_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data")
)

# Load road definitions
_ROAD_PATH = os.path.join(DATA_ROOT, "roads", "road_data.json")
with open(_ROAD_PATH, "r", encoding="utf-8") as f:
    road_data: Dict[str, dict] = json.load(f)

# Load hex registry
_HEX_PATH = os.path.join(DATA_ROOT, "roads", "hex_registry.json")
with open(_HEX_PATH, "r", encoding="utf-8") as f:
    hex_registry: Dict[str, dict] = json.load(f)


# ─────────────────────────────────────────────────
# Core Functions
# ─────────────────────────────────────────────────



def generate_axial_hexes(cols, rows):
    return {
        f"{q},{r}": (q, r)
        for q in range(cols)
        for r in range(rows)
    }

def generate_centered_axial_hexes(cols, rows):
    q_min = -cols // 2
    r_min = -rows // 2
    return {
        f"{q},{r}": (q, r)
        for q in range(q_min, q_min + cols)
        for r in range(r_min, r_min + rows)
    }




def get_neighbors(coord: Tuple[int, int]) -> List[Tuple[int, int]]:
    """
    Given an axial coordinate (q, r), return the six neighbor coords.
    """
    q, r = coord
    directions = [(+1, 0), (0, +1), (-1, +1), (-1, 0), (0, -1), (+1, -1)]
    return [(q + dq, r + dr) for dq, dr in directions]


# Width and height of your hex grid, matching your map layout
axial_map = generate_centered_axial_hexes(217, 184)  # example
hex_list = []

for hex_id, (q, r) in axial_map.items():
    hex_list.append({
        "id": hex_id,
        "points": hex_points(q, r, size=20)
    })



def place_road(settlement: dict, from_hex: str, to_hex: str) -> bool:
    """
    Adds a road between two hex IDs in the settlement’s road network.
    """
    settlement.setdefault("roads", [])
    road_key = tuple(sorted([from_hex, to_hex]))
    if road_key in settlement["roads"]:
        return False  # already built
    settlement["roads"].append(road_key)
    return True


def move_troop(player: dict, from_hex: str, to_hex: str) -> bool:
    """
    Moves one troop marker from one hex to another, if valid.
    """
    troops = player.setdefault("troops", {})
    if troops.get(from_hex, 0) < 1:
        return False
    troops[from_hex] -= 1
    troops[to_hex] = troops.get(to_hex, 0) + 1
    return True

def place_settlement(player: dict, hex_id: str, settlement_data: dict) -> bool:
    """ Place a settlement on the specified hex if valid."""
    if hex_id not in hex_registry:
        return False  # Invalid hex

    settlement = {
        "id": settlement_data["id"],
        "name": settlement_data["name"],
        "type": settlement_data["type"],
        "location": hex_id,
        "owner": player["id"],
        "resources": settlement_data.get("resources", {}),
        "structures": {}
    }

    # Register the settlement
    player.setdefault("settlements", {})[hex_id] = settlement
    hex_registry[hex_id]["settlement"] = settlement
    return True