from engine.ledger import ResourceLedger


class PlayerCharacter:
    def __init__(self, name, skills=None, barony=None, role="Member"):
        self.name = name
        self.role = role                 # e.g. "Steward", "Baron", "Court Noble", "Member"
        self.skills = skills or []
        self.barony = barony
        self.ledger = ResourceLedger()
        self.personal_resources = {"L": 0, "S": 0, "M": 0, "F": 0, "R": 0, "C": 0} # Personal resources
        self.personal_settlements = []
        self.personal_troops = []

    def owns_settlement(self, settlement):
        return settlement in self.personal_settlements

    def is_in_barony(self):
        return self.barony is not None
    
    def can_spend_from_barony(self):
        return self.role in ["Baron", "Steward", "Court Noble", "Member"]
    
class NPC:
    def __init__(self, name, npc_type, estate_level=0):
        self.name = name
        self.turns_remaining = 2 if npc_type == "Tier2" else 1
        self.estate_level = estate_level