

import json
import os

from models.structure import Structure

def load_structures(json_path=None):
    """
    Loads all structure entries from JSON and returns a list of Structure objects.
    """
    if not json_path:
        json_path = os.path.join("data", "units", "structure", "StructureData.json")

    with open(json_path, "r", encoding="utf-8") as f:
        structure_data = json.load(f)

    return [Structure(entry) for entry in structure_data]

def load_structure_by_name(name, level=1, json_path=None):
    """
    Returns a specific structure by name and level.
    """
    if not json_path:
        json_path = os.path.join("data", "structure", "StructureData.json")

    with open(json_path, "r", encoding="utf-8") as f:
        all_structures = json.load(f)

    for entry in all_structures:
        if entry["name"] == name and entry["level"] == level:
            return Structure(entry)

    return None