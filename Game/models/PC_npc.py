from barony import Barony
from player_character import PlayerCharacter

class NPC:
    def __init__(self, name, npc_type, barony, estate_level=0):
        self.name = name
        self.turns_remaining = 2 if npc_type == "Tier2" else 1
        self.estate_level = estate_level