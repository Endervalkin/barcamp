import json
import os

from models.structure import Structure
from utils.parsing import parse_name_level, parse_int
from utils.di import get_stability_rating, get_economy_rating, get_loyalty_rating, get_unrest_rating
from models.settlement import Settlement
from models.structure import StructureBuilder
from engine.turn import ActionEngine  # if you need class hints or structure

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