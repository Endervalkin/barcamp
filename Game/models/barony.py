
from Game.engine.resource_ledger import ResourceLedger

from Game.models.player_character import PlayerCharacter

class Barony:
    def __init__(self, name, baron=None):
        self.name = name
        self.baron = baron              # PlayerCharacter object
        self.members = set()            # PlayerCharacter objects
        self.ledger = ResourceLedger()  # ResourceLedger object for shared resources
        self.resources = {"L": 0, "S": 0, "M": 0, "F": 0, "R": 0, "C": 0} # Shared resources
        self.settlements = []           # Shared settlements
        self.troops = []                # Shared troop units
        self.structures = []            # Shared structures

    def add_member(self, character):
        self.members.add(character)
        character.barony = self  # attach reference

    def add_resources(self, resources):
        for key, value in resources.items():
            self.resources[key] += value

    def spend_resources(self, cost):
        for key, value in cost.items():
            if self.resources.get(key, 0) < value:
                return False
        for key, value in cost.items():
            self.resources[key] -= value
        return True

    def describe(self):
        return f"🏰 {self.name} — Baron: {self.baron.name if self.baron else 'None'} | Members: {len(self.members)}"