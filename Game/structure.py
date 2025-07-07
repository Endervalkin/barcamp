class Structure:
    def __init__(
        self,
        name: str,
        level: int,
        build_time: int,
        build_cost: dict,
        upkeep: dict,
        production: dict,
        settlement_needs: dict,
        di_modifiers: dict,
        garrison: int,
        population: int,
        type: str
    ):
        self.name = name
        self.level = level
        self.build_time = build_time
        self.build_cost = build_cost
        self.upkeep = upkeep
        self.production = production
        self.settlement_needs = settlement_needs
        self.di_modifiers = di_modifiers
        self.garrison = garrison
        self.population = population
        self.type = type  # e.g., "basic", "city", "fortress", etc.

import json

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