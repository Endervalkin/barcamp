# models/settlement.py
import json
import os
from Game.utils.parsing import *
from Game.utils.di      import get_stability_rating, get_economy_rating, get_loyalty_rating, get_unrest_rating

class Settlement:
    def __init__(self, data):
        self.name = data["name"]                      # e.g. "City"
        self.level = data["level"]                    # e.g. 3
        self.build_turns = data["build_turns"]
        self.build_cost = data["build_cost"]
        self.garrison = data["garrison"]
        self.population_base = data["population_base"]
        self.population_critical = data["population_critical"]
        self.upgrade_requirements = data.get("upgrade_requirements", {})

    def get_required_needs(self):
        return self.upgrade_requirements.get("needs_required", {})

    def get_required_structures(self):
        return self.upgrade_requirements.get("structures_required", [])

    def can_upgrade(self, player_needs, player_structures):
        # Check needs
        for need, required in self.get_required_needs().items():
            if player_needs.get(need, 0) < required:
                return False

        # Check structure OR-groups
        for group in self.get_required_structures():
            if not any(player_structures.get(s["name"], 0) >= s["level"] for s in group):
                return False

        return True

    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level,
            "build_turns": self.build_turns,
            "build_cost": self.build_cost,
            "garrison": self.garrison,
            "population_base": self.population_base,
            "population_critical": self.population_critical,
            "upgrade_requirements": self.upgrade_requirements
        }

    def calculate_domestic_index(self, population, needs, structure_lvls, base_unrest):
        sr = get_stability_rating(self.level, **structure_lvls)
        er = get_economy_rating(self.level, **structure_lvls)
        avg_needs = sum(needs.values())/len(needs)
        lr = get_loyalty_rating(self.level, avg_needs, structure_lvls.get("Monuments",0))
        ur = get_unrest_rating(population, self.population_critical, base_unrest)
        return {"Stability": sr, "Economy": er, "Loyalty": lr, "Unrest": ur}


    def can_build_structure(self):
        return self.get_turns_remaining() > 0

    def upgrade_structure(self, name, new_level):
        for s in self.structures:
            if s.name == name and s.level < new_level:
                s.level = new_level
                return


    def can_upgrade_self(self):
        if self.get_turns_remaining() < 1:
            return False

        reqs = self.upgrade_reqs
        needs_met = all(
            self.needs.get(need, 0) >= reqs["needs_required"].get(need, 0)
            for need in reqs["needs_required"]
        )

        if not needs_met:
            return False

        # Determine required structure sets based on settlement name/type
        structure_groups = reqs.get("structures_required", [])
        existing_structures = self.get_structure_levels()  # e.g. { "Forge": 2, "Walls": 1 }

        def group_satisfied(group):
            for item in group:
                name = item["name"]
                level = item["level"]
                if existing_structures.get(name, 0) >= level:
                    return True
            return False

        return all(group_satisfied(group) for group in structure_groups)
    
    def has_road_access(self):
        # Must be connected to road network or have adjacent hexes
        return self.location.has_adjacent_hexes()

    def can_research_city_technology(self):
        # Check if settlement has the required structures for research
        required_structure = ["Grand Library"]
        return all(self.get_structure_levels().get(structure, 0) > 0 for structure in required_structure)

