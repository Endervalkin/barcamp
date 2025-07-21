import os
import json
import csv



class Homeward:
    def __init__(self, level):
        self.level = level
        self.assigned_creatures = []  # Each entry is {"name": str, "level": int}
        self.turns_available = 0

    def add_creature(self, name, level):
        self.assigned_creatures.append({ "name": name, "level": level })

    def creature_total(self):
        return sum(c["level"] for c in self.assigned_creatures)

    def update_turns(self):
        threshold = self.level * 7
        if self.creature_total() >= threshold:
            self.turns_available = self.level
        else:
            self.turns_available = 0