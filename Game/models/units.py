import json
import os
from utils.parsing import parse_name_level, parse_int, parse_structure_requirements
from utils.di      import get_stability_rating, get_economy_rating, get_loyalty_rating, get_unrest_rating

# Ensure relative import works if running from another location
UNIT_PATH = os.path.abspath(os.path.join("data", "units"))
if UNIT_PATH not in sys.path:
    sys.path.append(UNIT_PATH)

from unit_registry import UnitRegistry


class Units:
    def __init__(self, data_dir="data/units"):
        self.registry = UnitRegistry(data_dir)

    def get_unit(self, name):
        """Retrieve a unit by name (case-insensitive)"""
        return self.registry.get_unit(name)

    def get_units_by_category(self, category):
        """Return units by category: 'Ground', 'Ship', 'Airship', 'Siege'"""
        return self.registry.get_all_by_category(category)

    def get_all_units(self):
        return self.registry.get_all()

    def list_all_names(self):
        return sorted([u["name"] for u in self.get_all_units()])

    def describe_unit(self, name):
        unit = self.get_unit(name)
        if not unit:
            return f"❌ Unit '{name}' not found."
        return (
            f"{unit['name']} (Lvl {unit.get('level', 1)}): "
            f"ATK {unit.get('attack', 0)} | Range {unit.get('range', 0)} | "
            f"Move {unit.get('combat_movement', 0)} | HP {unit.get('health', '?')}"
        )