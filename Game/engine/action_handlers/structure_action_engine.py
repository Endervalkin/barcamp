import os
import json
from models.settlement import Settlement
from utils.parsing import parse_name_level, parse_int
from utils.di import get_stability_rating, get_economy_rating, get_loyalty_rating, get_unrest_rating
from engine.turn import ActionEngine  # if you need class hints or structure
from models.structure import StructureBuilder


class StructureActionEngine:
    def __init__(self, action_engine, registry):
        self.action_engine = action_engine
        self.registry = registry  # StructureData.json parsed

    def take_turn(self, structure, settlement):
        if structure.turns_remaining < 1:
            return f"⏳ {structure.name} has no turns remaining."

        action_type = structure.get_action_type()  # Defined per entry
        if action_type == "produce":
            return self.produce_resources(structure, settlement)
        elif action_type == "train":
            return self.train_unit(structure, settlement)
        elif action_type == "retrain":
            return self.retrain_unit(structure, settlement)
        elif action_type == "craft":
            return self.produce_items(structure, settlement)
        elif action_type == "specialize":
            return self.specialize_unit(structure, settlement)
        elif action_type == "learn":
            return self.teach_skill(structure, settlement)
        else:
            return f"❌ No valid action for {structure.name}"
        
    def produce_resources(self, structure, settlement):
        prod_type = structure.produces_resource  # e.g. "L"
        base_amount = structure.get_production_amount()  # includes DI or worker boosts

        # Check skilled workers
        attached = structure.get_skilled_workers()
        multiplier = 1 + len(attached)

        total = base_amount * multiplier

        settlement.ledger.add({prod_type: total})
        structure.turns_remaining -= 1

        return self.action_engine.perform_action(
            actor=structure,
            action_type="Produce",
            details=f"{total} {prod_type} produced by {structure.name}",
            cost=None,
            turn_cost=1
        )
        
    def train_unit(self, structure, settlement):
        if structure.turns_remaining < 1:
            return f"❌ {structure.name} has no turns available."

        # Step 1: Determine valid unit types
        allowed_units = structure.can_train
        max_level = structure.level
        selected_unit = self.select_unit_to_train(structure)  # stubbed for now
        if structure.name == "Mage's Tower":
            if unit["type"] != "Caster" or unit["subtype"] != structure.specialization:
                return f"🚫 {unit['subtype']} cannot be trained at {structure.specialization} Mage Tower."
        

        if selected_unit["type"] not in allowed_units:
            return f"🚫 {structure.name} cannot train {selected_unit['type']} units."

        if selected_unit["level"] > max_level:
            return f"📏 {structure.name} can only train up to level {max_level}."

        # Step 2: Calculate cost
        per_level_cost = structure.train_cost_per_level
        train_cost = {
            k: v * selected_unit["level"] for k, v in per_level_cost.items()
        }

        if not settlement.ledger.can_afford(train_cost):
            return f"💰 Insufficient resources to train {selected_unit['name']}."

        # Step 3: Apply training
        settlement.ledger.spend(train_cost, purpose="Train", by=structure.name)
        structure.turns_remaining -= 1
        settlement.units.append(selected_unit)  # or use add_unit()

        return self.action_engine.perform_action(
            actor=structure,
            action_type="Train",
            details=f"{selected_unit['name']} level {selected_unit['level']} trained",
            cost=train_cost,
            turn_cost=1
        )
    
    def retrain_unit(self, structure, settlement):
        if not structure.can_retrain():
            return f"❌ {structure.name} cannot retrain units this turn."

        unit = structure.retrain_unit()
        settlement.units.update(unit)
        structure.decrement_turns()

        return f"✅ {structure.name} retrained unit: {unit.name}"
    
    def produce_items(self, structure, settlement):
        if not structure.can_craft():
            return f"❌ {structure.name} cannot produce items this turn."

        items = structure.craft_items()
        settlement.items.add(items)
        structure.decrement_turns()

        return f"✅ {structure.name} crafted items: {', '.join(item.name for item in items)}"
    
    def specialize_unit(self, structure, settlement):
        if not structure.can_specialize():
            return f"❌ {structure.name} cannot specialize units this turn."

        specialized_unit = structure.specialize_unit()
        settlement.units.update(specialized_unit)
        structure.decrement_turns()

        return f"✅ {structure.name} specialized unit: {specialized_unit.name}" 
    
    def teach_skill(self, structure, settlement):
        if not structure.can_teach():
            return f"❌ {structure.name} cannot teach skills this turn."

        skill = structure.teach_skill()
        settlement.skills.add(skill)
        structure.decrement_turns()

        return f"✅ {structure.name} taught skill: {skill.name}"
    
    def can_build_ship(structure, ship_data):
        ship_class = ship_data["class"]
        ship_level = ship_data["level"]
        return ship_class * ship_level <= structure.level
    
    def can_build_airship(structure, ship_data, approval_registry):
        if ship_data["name"] == "Skycutter" and ship_data["name"] not in approval_registry:
            return False
        return ship_data["class"] == 5 and ship_data["level"] <= structure.level
    
    def is_ship_valid(structure, ship_data, approval_registry):
        if ship_data["type"] != "Ship":
            return False
        if ship_data.get("requires_approval", False) and ship_data["name"] not in approval_registry:
            return False
        return ship_data["class"] * ship_data["level"] <= structure.level