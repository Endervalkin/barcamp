import json
import os

structure_path = os.path.join("data", "structure", "StructureData.json")

with open(structure_path, "r", encoding="utf-8") as f:
    structure_data = json.load(f)


class Structure:
    def __init__(self, data):
        self.name = data["name"]
        self.level = data["level"]
        self.build_time = data.get("build_time", 0)
        self.build_cost = data.get("build_cost", {})
        self.production = data.get("production", {})
        self.upkeep = data.get("upkeep", {})
        self.settlement_needs = data.get("settlement_needs", {})
        self.di_modifiers = data.get("di_modifiers", {})
        self.garrison = data.get("garrison", 0)
        self.population = data.get("population", 0)
        self.buildable_in = data.get("buildable_in", {})

    def is_buildable_in(self, settlement_type):
        """Check if the structure can be built in a given settlement type"""
        return self.buildable_in.get(settlement_type, False)

    def get_di_impact(self):
        """Return a summary of what this structure contributes to DI"""
        return self.di_modifiers

    def get_needs_contribution(self):
        """Return Morale, Education, Medical boosts if any"""
        return self.settlement_needs

    def describe(self):
        return f"{self.name} (Lvl {self.level}) — Garrison: {self.garrison}, Pop: {self.population}"

    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level,
            "build_time": self.build_time,
            "build_cost": self.build_cost,
            "production": self.production,
            "upkeep": self.upkeep,
            "settlement_needs": self.settlement_needs,
            "di_modifiers": self.di_modifiers,
            "garrison": self.garrison,
            "population": self.population,
            "buildable_in": self.buildable_in
        }

class StructureBuilder:
    def __init__(self, json_file: str):
        with open(json_file, "r") as f:
            self.structure_data = json.load(f)

    def get_all(self):
        return [self._build_struct(s) for s in self.structure_data]

    def get_structure(self, name: str, level: int):
        for s in self.structure_data:
            if s["name"].lower() == name.lower() and s["level"] == level:
                return self._build_struct(s)
        raise ValueError(f"Structure '{name}' level {level} not found.")

    def _build_struct(self, s: dict) -> Structure:
        return Structure(
            name=s["name"],
            level=s["level"],
            build_time=s["build_time"],
            build_cost=s.get("build_cost", {}),
            upkeep=s.get("upkeep", {}),
            production=s.get("production", {}),
            settlement_needs=s.get("settlement_needs", {}),
            di_modifiers=s.get("di_modifiers", {}),
            garrison=s.get("garrison", 0),
            population=s.get("population", 0)
        )