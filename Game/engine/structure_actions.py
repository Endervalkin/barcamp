import json
import os

from Game.models.structure import Structure
from Game.utils.parsing import parse_name_level, parse_int
from Game.utils.di import get_stability_rating, get_economy_rating, get_loyalty_rating, get_unrest_rating
from Game.models.settlement import Settlement
from Game.models.structure import StructureBuilder
from Game.engine.action_engine import ActionEngine  # if you need class hints or structure
from Game.engine.structure_action_engine import StructureActionEngine
from Game.registry.parse_structure import *

# Initialize registry once
STRUCTURES = load_registry()

def train(struct_name, game_state, unit, qty=1, specialization=None):
    struct = STRUCTURES[struct_name]
    valid = get_trainable_units(struct, specialization)
    if unit not in valid:
        raise ValueError(f"{struct_name} cannot train {unit}")
    return apply_training(struct, game_state, unit, qty)

def produce(struct_name, game_state, item_name):
    struct = STRUCTURES[struct_name]
    valid = [r["name"] for r in get_producible_items(struct, game_state)]
    if item_name not in valid:
        raise ValueError(f"{item_name} not producible this turn")
    return apply_production(struct, game_state, item_name)

def convert(struct_name, game_state, from_unit, to_unit):
    struct = STRUCTURES[struct_name]
    conv = {c["from"]: c["to"] for c in get_conversions(struct)}
    if conv.get(from_unit) != to_unit:
        raise ValueError("Invalid conversion")
    return apply_conversion(struct, game_state, from_unit, to_unit)

def build(struct_name, game_state, unit_name, catalog, **kwargs):
    struct = STRUCTURES[struct_name]
    valid = [c["name"] for c in get_buildable(struct, catalog, game_state)]
    if unit_name not in valid:
        raise ValueError(f"{unit_name} cannot be built here")
    return apply_build(struct, game_state, unit_name, **kwargs)

def build_structure(settlement, structure_data, action_engine):
    name = structure_data["name"]
    level = structure_data["level"]
    build_cost = structure_data["build_cost"]
    buildable_in = structure_data["buildable_in"]

    # 1. Check turns
    if settlement.get_turns_remaining() < 1:
        return f"❌ {settlement.name} has no turns left."

    # 2. Check buildable location
    if not buildable_in.get(settlement.name, False):
        return f"⛔ {name} cannot be built in a {settlement.name}."

    # 3. Check resource availability
    if not settlement.ledger.can_afford(build_cost):
        return f"💰 {settlement.name} lacks resources to build {name}."

    # 4. Spend resources and turn
    structure = Structure(structure_data)  # Create instance
    settlement.add_structure(structure)    # Attach to settlement
    settlement.ledger.spend(build_cost, purpose="Build", by=settlement.name)

    # 5. Submit to action engine
    result = action_engine.perform_action(
        actor=settlement,
        action_type="Build Structure",
        details=f"{name} level {level}",
        cost=build_cost,
        turn_cost=1
    )

    return f"✅ {settlement.name} built {name} level {level}.\n{result}"

def select_structure_to_build(settlement, registry_path=None):
    """
    Returns a valid structure_data dict that the settlement can build.
    You can later replace this with a menu or AI logic.
    """
    if not registry_path:
        registry_path = os.path.join("data", "structure", "StructureData.json")

    with open(registry_path, "r", encoding="utf-8") as f:
        all_structures = json.load(f)

    # Filter by buildable_in
    buildable = [
        s for s in all_structures
        if s.get("buildable_in", {}).get(settlement.name, False)
    ]

    # Optional: filter out structures already built
    existing = settlement.get_structure_levels()  # e.g. { "Forge": 1, "Walls": 2 }
    buildable = [
        s for s in buildable
        if existing.get(s["name"], 0) < s["level"]
    ]

    # Optional: sort by DI impact or cost
    buildable.sort(key=lambda s: sum(s.get("di_modifiers", {}).values()), reverse=True)

    # Return first valid option (stub for now)
    return buildable[0] if buildable else None

def upgrade_structure(settlement, action_engine, registry_path=None):
    import json, os
    from models.structure import Structure

    if not registry_path:
        registry_path = os.path.join("data", "structure", "StructureData.json")

    with open(registry_path, "r", encoding="utf-8") as f:
        all_structures = json.load(f)

    current_levels = settlement.get_structure_levels()  # e.g. { "Forge": 1, "Walls": 2 }

    # Find all structures in settlement that have a higher level entry in the registry
    upgradable = []
    for s_name, s_lvl in current_levels.items():
        for entry in all_structures:
            if entry["name"] == s_name and entry["level"] == s_lvl + 1:
                upgradable.append(entry)
                break

    if not upgradable:
        return f"🔒 No upgradable structures available for {settlement.name}."

    # Stub: pick first one (later use menu/AI logic)
    upgrade_data = upgradable[0]
    name = upgrade_data["name"]
    new_lvl = upgrade_data["level"]
    cost = upgrade_data.get("build_cost", {})

    if settlement.get_turns_remaining() < 1:
        return f"❌ {settlement.name} lacks turns to upgrade {name}."

    if not settlement.ledger.can_afford(cost):
        return f"💰 {settlement.name} lacks resources to upgrade {name}."

    # Apply upgrade
    settlement.upgrade_structure(name, new_lvl)
    settlement.ledger.spend(cost, purpose="Upgrade", by=settlement.name)

    result = action_engine.perform_action(
        actor=settlement,
        action_type="Upgrade Structure",
        details=f"{name} to level {new_lvl}",
        cost=cost,
        turn_cost=1
    )

    return f"✅ {settlement.name} upgraded {name} to level {new_lvl}.\n{result}"

def upgrade_settlement(settlement, action_engine):
    if settlement.get_turns_remaining() < 1:
        return f"❌ {settlement.name} lacks turns to upgrade itself."

    upgrade_data = settlement.upgrade_reqs
    if not upgrade_data:
        return f"🚫 No upgrade path defined for {settlement.name}."

    unmet_needs = []
    for need, required in upgrade_data["needs_required"].items():
        actual = settlement.needs.get(need, 0)
        if actual < required:
            unmet_needs.append(f"{need}: {actual}/{required}")

    if unmet_needs:
        need_report = "\n📉 Unmet Needs:\n" + "\n".join(f"  - {n}" for n in unmet_needs)
    else:
        need_report = ""

    structure_groups = upgrade_data.get("structures_required", [])
    owned_structures = settlement.get_structure_levels()

    failed_groups = []
    for group in structure_groups:
        satisfied = False
        missing_entries = []
        for item in group:
            name, level = item["name"], item["level"]
            owned_level = owned_structures.get(name, 0)
            if owned_level >= level:
                satisfied = True
                break
            else:
                missing_entries.append(f"{name} (lv {owned_level}/{level})")
        if not satisfied:
            failed_groups.append(missing_entries)

    if failed_groups:
        structure_report = "\n🏗️ Missing Structure Requirements:"
        for i, group in enumerate(failed_groups, 1):
            structure_report += f"\n  OR Group {i}:\n    - " + "\n    - ".join(group)
    else:
        structure_report = ""

    if unmet_needs or failed_groups:
        return f"⚠️ {settlement.name} cannot upgrade yet." + need_report + structure_report

    # Upgrade settlement
    settlement.level += 1
    settlement.reset_unrest_on_upgrade()
    settlement.recalculate_di()

    result = action_engine.perform_action(
        actor=settlement,
        action_type="Upgrade Settlement",
        details=f"Upgraded to level {settlement.level}",
        cost=None,
        turn_cost=1
    )

    return f"🏛️ {settlement.name} successfully upgraded to level {settlement.level}.\n{result}"

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
        

    def load_registry(path="Game/data/StructureData_refactored.json"):
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