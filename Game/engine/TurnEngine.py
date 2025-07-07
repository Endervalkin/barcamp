class TurnEngine:
    def __init__(self, baronies, settlements, structures, characters, npcs, homewards):
        self.baronies = baronies            # list of Barony
        self.settlements = settlements      # list of Settlement
        self.structures = structures        # list of Structure
        self.characters = characters        # list of PlayerCharacter
        self.npcs = npcs                    # list of NPC
        self.homewards = homewards          # list of Homeward

    def execute_month(self):
        self.apply_upkeep()
        self.assign_turns()
        self.process_turns()
        self.calculate_domestic_index()
        self.process_resource_production()



def get_monthly_turns(self, di_rating):
    turns = 2 if self.name in ["City", "Fortress"] else 0

    # Bonus turn for Stability > 10 and Unrest <= 0
    if di_rating["Stability"] > 10 and di_rating["Unrest"] <= 0:
        turns += 1

    if self.population_base >= self.population_critical:
        turns += 1

    return turns

def is_active(self, available_resources):
    for res, cost in self.upkeep.items():
        if available_resources.get(res, 0) < cost:
            return False
    return True

def get_monthly_turns(self):
    return 1 if self.production else 0  # Some structures just contribute passively

def get_turns(self):
    total_levels = sum(c.level for c in self.magical_creatures)
    turns = (total_levels // 7) * self.level
    return max(turns, 0)

class TurnLogEngine:
    def __init__(self, previous_balance=None, tax_exempt=False):
        self.previous_balance = previous_balance or {"L": 0, "S": 0, "M": 0, "F": 0, "R": 0, "C": 0}
        self.production = {}
        self.upkeep = {}
        self.coin_substitutions = {}  # coin used to offset upkeep
        self.road_upkeep = {}
        self.tax_exempt = tax_exempt

    def apply_inputs(self, production, upkeep, coin_subs=None, road_cost=None):
        self.production = production
        self.upkeep = upkeep
        self.coin_substitutions = coin_subs or {}
        self.road_upkeep = road_cost or {}

    def calculate_subtotal(self):
        subtotal = {res: self.production.get(res, 0) - self.upkeep.get(res, 0) for res in self.production}
        for res, sub_amount in self.coin_substitutions.items():
            subtotal[res] += sub_amount
            subtotal["C"] -= sub_amount
        subtotal["C"] -= self.road_upkeep.get("C", 0)
        return subtotal

    def calculate_taxes(self, subtotal):
        if self.tax_exempt:
            return {res: 0 for res in subtotal}
        return {
            res: int(subtotal[res] * 0.1) if subtotal[res] >= 10 else 0
            for res in subtotal
        }

    def calculate_final(self):
        subtotal = self.calculate_subtotal()
        taxes = self.calculate_taxes(subtotal)
        net = {res: subtotal[res] - taxes[res] for res in subtotal}
        final = {res: net[res] + self.previous_balance.get(res, 0) for res in net}
        return final, taxes, net