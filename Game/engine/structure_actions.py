import json
import os

# ────────────────────────────────
# Registry Loader
# ────────────────────────────────

def load_registry(
    path=None
):
    """
    Load structure definitions from StructureData_refactored.json.
    Returns a dict keyed by structure name, with build_cost, upgrade_cost, build_time, etc.
    """
    if path is None:
        # assume this file lives in Game/engine/, adjust relative path
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        path = os.path.join(root, "Game", "data", "structures", "StructureData_refactored.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)

# Load once at module import
STRUCTURES = load_registry()


# ────────────────────────────────
# Utility Validators
# ────────────────────────────────

def _check_resources(entity, cost):
    """
    Ensure entity (player or settlement) has sufficient resources to cover `cost` dict.
    """
    for res, amount in cost.items():
        have = entity["resources"].get(res, 0)
        if have < amount:
            return False, f"Insufficient {res}: have {have}, need {amount}"
    return True, ""


def _deduct_resources(entity, cost):
    """
    Subtracts `cost` resources from entity.
    """
    for res, amount in cost.items():
        entity["resources"][res] -= amount


# ────────────────────────────────
# Core Actions
# ────────────────────────────────

def build_structure(player, settlement, structure_name):
    """
    Build a new structure in `settlement` if player and settlement meet requirements.
    Deducts build_cost, adds to settlement["structures"], and returns True on success.
    """
    if structure_name not in STRUCTURES:
        raise KeyError(f"{structure_name} not in registry")

    meta = STRUCTURES[structure_name]
    cost = meta.get("build_cost", {})
    time = meta.get("build_time", 1)

    ok, msg = _check_resources(player, cost)
    if not ok:
        raise ValueError(f"Cannot build {structure_name}: {msg}")

    # Deduct resources and queue build
    _deduct_resources(player, cost)

    # Initialize settlement structures list if missing
    settlement.setdefault("structures", {})
    settlement["structures"].setdefault(structure_name, {
        "level": 0,
        "turns_until_ready": 0
    })

    slot = settlement["structures"][structure_name]
    # Cannot build if already at or above max level
    if slot["level"] >= meta.get("max_level", 1):
        raise ValueError(f"{structure_name} already at max level")

    # Queue the build as level+1
    slot["turns_until_ready"] = time
    return True


def upgrade_structure(player, settlement, structure_name):
    """
    Upgrade an existing structure (must exist) by one level.
    Deducts upgrade_cost, sets turns_until_ready based on upgrade_time.
    """
    if structure_name not in STRUCTURES:
        raise KeyError(f"{structure_name} not in registry")

    meta = STRUCTURES[structure_name]
    slot = settlement.get("structures", {}).get(structure_name)
    if not slot or slot["level"] == 0:
        raise ValueError(f"{structure_name} does not exist to upgrade")

    current = slot["level"]
    next_lvl = current + 1
    if next_lvl > meta.get("max_level", current):
        raise ValueError(f"{structure_name} is already at max level")

    cost = meta.get("upgrade_cost", {}).get(str(next_lvl), {})
    time = meta.get("upgrade_time", {}).get(str(next_lvl), 1)

    ok, msg = _check_resources(player, cost)
    if not ok:
        raise ValueError(f"Cannot upgrade {structure_name}: {msg}")

    _deduct_resources(player, cost)
    slot["turns_until_ready"] = time
    return True


def finalize_builds(settlement):
    """
    Called at the end of a turn/month to decrement turns_until_ready
    and apply completed builds/upgrades by increasing level.
    """
    for name, slot in settlement.get("structures", {}).items():
        if slot["turns_until_ready"] > 0:
            slot["turns_until_ready"] -= 1
            if slot["turns_until_ready"] == 0:
                slot["level"] += 1


def upgrade_settlement(player, settlement, settlement_type):
    """
    Upgrade the settlement's tier/type (e.g. Village→Town→City).
    Uses settlement_type as key in registry under special "Settlement" entry.
    """
    meta = STRUCTURES.get("Settlement", {})
    # upgrade_cost and upgrade_time keyed by settlement_type
    cost = meta.get("upgrade_cost", {}).get(settlement_type, {})
    time = meta.get("upgrade_time", {}).get(settlement_type, 1)

    ok, msg = _check_resources(player, cost)
    if not ok:
        raise ValueError(f"Cannot upgrade settlement to {settlement_type}: {msg}")

    _deduct_resources(player, cost)
    settlement["upgrade"] = {
        "target_type": settlement_type,
        "turns_until_ready": time
    }
    return True


def finalize_settlement_upgrade(settlement):
    """
    Called end-of-turn to process settlement tier upgrades.
    """
    up = settlement.get("upgrade")
    if not up:
        return

    if up["turns_until_ready"] > 0:
        up["turns_until_ready"] -= 1
        if up["turns_until_ready"] == 0:
            settlement["type"] = up["target_type"]
            del settlement["upgrade"]


# ────────────────────────────────
# Example Hook In Your Turn Engine
# ────────────────────────────────

# In your turn_engine.py end_month(), you would call:
#
# for settlement in player["settlements"].values():
#     finalize_builds(settlement)
#     finalize_settlement_upgrade(settlement)
#
# This applies all queued builds and settlement upgrades.