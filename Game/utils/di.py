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