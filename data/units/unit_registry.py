import json
import os

class UnitRegistry:
    def __init__(self, directory="data/units"):
        self.units = []
        self.index_by_name = {}
        self.index_by_category = {"Ground": [], "Ship": [], "Airship": [], "Siege": []}

        self.load_all_units(directory)

    def load_all_units(self, path):
        filenames = ["GroundUnits.json", "ShipsAndAirships.json", "SiegeWeapons.json"]
        for filename in filenames:
            full_path = os.path.join(path, filename)
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for unit in data:
                    self.units.append(unit)
                    key = unit["name"].lower()
                    self.index_by_name[key] = unit
                    self.index_by_category.setdefault(unit["category"], []).append(unit)

    def get_unit(self, name: str):
        return self.index_by_name.get(name.lower())

    def get_all_by_category(self, category: str):
        return self.index_by_category.get(category, [])

    def get_all(self):
        return self.units