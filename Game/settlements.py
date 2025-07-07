import json
import os

structure_path = os.path.join("data", "settlements", "SettlementData.json")

with open(structure_path, "r", encoding="utf-8") as f:
    structure_data = json.load(f)

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

    def can_upgrade(self, current_population, player_needs, player_structures):
        # Check needs
        for need, required in self.get_required_needs().items():
            if player_needs.get(need, 0) < required:
                return False

        # Check structure OR-groups
        for group in self.get_required_structures():
            if not any(player_structures.get(s["name"], 0) >= s["level"] for s in group):
                return False

        return True

    def get_stability_rating(self, contributors):
        """
        contributors: dict with keys like Towers, Garrisons, Troops, Defenses (levels as ints)
        """
        points = sum(contributors.get(k, 0) for k in ["Towers", "Garrisons", "Troops", "Defenses"])
        return round(points / max(self.level, 1), 2)

    def get_economy_rating(self, contributors):
        points = sum(contributors.get(k, 0) for k in ["Markets", "Harbors", "TradeRoutes"])
        return round(points / max(self.level, 1), 2)

    def get_loyalty_rating(self, needs, monument_points):
        avg_needs = sum(needs.get(k, 0) for k in ["Morale", "Education", "Medical"]) / 3
        return round((avg_needs + monument_points) / max(self.level, 1), 2)

    def get_unrest_rating(self, unrest_sources, pop, critical):
        base_unrest = sum(unrest_sources.values())
        overpop_ratio = max((pop - critical) / critical, 0)
        overpop_unrest = int(overpop_ratio * 5)  # 1 unrest per 20% over cap
        return base_unrest + overpop_unrest

    def calculate_domestic_index(self, population, needs, structure_levels, unrest_sources, monument_points):
        return {
            "Stability": self.get_stability_rating(structure_levels),
            "Economy": self.get_economy_rating(structure_levels),
            "Loyalty": self.get_loyalty_rating(needs, monument_points),
            "Unrest": self.get_unrest_rating(unrest_sources, population, self.population_critical)
        }

    def describe_di(self, population, needs, structures, unrest_sources, monument_points):
        di = self.calculate_domestic_index(population, needs, structures, unrest_sources, monument_points)
        return (
            f"🛡️ Stability: {di['Stability']}, 💰 Economy: {di['Economy']}, "
            f"🏛️ Loyalty: {di['Loyalty']}, 🔥 Unrest: {di['Unrest']}"
        )

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