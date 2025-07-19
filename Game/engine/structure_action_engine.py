import os
import json
from models.settlement import Settlement
from utils.parsing import parse_name_level, parse_int
from utils.di import get_stability_rating, get_economy_rating, get_loyalty_rating, get_unrest_rating
from engine.turn import ActionEngine  # if you need class hints or structure
from models.structure import StructureBuilder
from registry.item_parser import get_valid_recipes, validate_produce_items



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
        



    def load_registry(path="StructureData_refactored.json"):
        with open(path, "r", encoding="utf-8") as f:
            return {s["name"]: s for s in json.load(f)}

    # 1. TRAINING LOGIC
    def get_trainable_units(struct, player_specialization=None):
        # e.g. ["Archer"], ["Commando","Footman","Guardsman"], ["Celestial Generalist","Earth Generalist"]
        units = struct.get("trainable_units", [])
        # If Mage's Tower, filter by chosen spec
        if struct.get("requires_specialization") and player_specialization:
            return [u for u in units if player_specialization in u]
        return units

    def can_train(struct, game_state):
        """Return how many units can be trained this turn (per-turn limit)."""
        lim = struct.get("limits", {}).get("unit_training", {})
        return lim.get("per_turn", 0)

    def apply_training(struct, game_state, unit, quantity=1):
        pts_left = game_state["structures"][struct["name"]].get("train_points", struct["level"])
        per_turn = can_train(struct, game_state)
        if quantity > per_turn or quantity > pts_left:
            raise ValueError("Too many units requested")
        # Deduct your turn‐based “points” or whatever currency you use
        game_state["structures"][struct["name"]]["train_points"] = pts_left - quantity
        # Add units to player’s roster
        game_state["player_units"].append({ "type": unit, "count": quantity })
        return True

    # 2. ITEM PRODUCTION LOGIC
    def get_producible_items(struct, game_state):
        # Reads structured produce_items + per-turn limit + level points
        return get_valid_recipes(struct)

    def apply_production(struct, game_state, item_name):
        recipes = {r["name"]: r for r in struct.get("produce_items", [])}
        recipe = recipes.get(item_name)
        if not recipe:
            raise ValueError(f"{item_name} not in catalog")
        # check points & per-turn
        pts_left = game_state["structures"][struct["name"]].get("prod_points", struct["level"])
        if recipe["cost"] > pts_left:
            raise ValueError("Insufficient points")
        per_turn = struct.get("limits", {}).get("item_production", {}).get("per_turn", 1)
        used = game_state["structures"][struct["name"]].get("produced_this_turn", 0)
        if used >= per_turn:
            raise ValueError("Production limit reached")
        # Apply
        game_state["structures"][struct["name"]]["prod_points"] = pts_left - recipe["cost"]
        game_state["structures"][struct["name"]]["produced_this_turn"] = used + 1
        game_state["player_items"].append({ "name": item_name })
        return True

    # 3. UNIT CONVERSION LOGIC
    def get_conversions(struct):
        return struct.get("unit_conversions", [])

    def apply_conversion(struct, game_state, from_unit, to_unit):
        # Remove one from_unit, add one to_unit
        inv = game_state["player_units"]
        # find and decrement
        for u in inv:
            if u["type"] == from_unit and u["count"] > 0:
                u["count"] -= 1
                break
        else:
            raise ValueError("No unit to convert")
        # add the new
        game_state["player_units"].append({ "type": to_unit, "count": 1 })
        return True

    # 4. SHIP / AIRSHIP BUILDING
    def get_buildable(struct, catalog, game_state):
        # catalog: list of {"name","class"} for ships/airships loaded separately
        lvl = struct["level"]
        if struct["build_type"] == "ships":
            # formula: class * level
            max_power = lvl * lvl  # or whatever your formula means
            return [c for c in catalog if c["class"] * lvl <= max_power]
        else:
            return [c for c in catalog if c["class"] <= struct.get("build_rules", {}).get("max_class", 0)]

    def apply_build(struct, game_state, unit_name):
        # similar pattern: check build points, per-turn, deduct, add to queue
        raise NotImplementedError