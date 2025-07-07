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

