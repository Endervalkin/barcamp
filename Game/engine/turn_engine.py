import os
import json

# map operations (if you need map‐based logic later)
from Game.engine.map_engine import *

# player-driven actions
from Game.engine.character_actions import *

# settlement-scoped actions
from Game.engine.settlement_actions import *

# structure build/upgrade logic
from Game.engine.structure_actions import (
    build_structure,
    upgrade_structure,
    finalize_builds,
    finalize_settlement_upgrade,
    STRUCTURES
)

# trade route logic
from Game.engine.trade_engine import create_caravan, resolve_trade_routes

# optional higher-level wrapper
try:
    from Game.engine.action_engine import ActionEngine
except ImportError:
    ActionEngine = None


class TurnEngine:
    """
    Loads all registries under Game/data and runs:
      1) structure build/upgrades
      2) settlement tier upgrades
      3) trade resolution
      4) Domestic Index bumps
    """

    def __init__(self, player, hex_registry=None, data_root=None):
        self.player = player

        # resolve path to Game/data
        self.data_root = data_root or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data")
        )

        # load JSON registries
        self.hex_registry   = hex_registry or self._load("hex_registry.json")
        self.trade_routes   = self._load("trade_routes.json")
        self.caravan_data   = self._load("caravan_data.json")
        self.creature_data  = self._load(os.path.join("units", "creatures_data.json"))
        # Structure definitions already in STRUCTURES
        self.structure_data = STRUCTURES

        # optional wrapper for combined actions
        if ActionEngine:
            self.action_engine = ActionEngine(
                player=self.player,
                hex_registry=self.hex_registry,
                structures=self.structure_data
            )

    def _load(self, rel_path):
        """Utility: load a JSON file from data_root (handles subfolders)."""
        full = os.path.join(self.data_root, rel_path)
        if not os.path.exists(full):
            raise FileNotFoundError(f"Missing registry at {full}")
        with open(full, "r", encoding="utf-8") as f:
            return json.load(f)

    def end_month(self):
        """
        1) finalize builds/upgrades
        2) resolve trade → coin
        3) bump Domestic Index
        Returns a summary dict.
        """
        # 1) Structures
        for settlement in self.player.get("settlements", {}).values():
            finalize_builds(settlement)
            finalize_settlement_upgrade(settlement)

        # 2) Trade
        income = resolve_trade_routes(self.player, self.hex_registry)
        self.player["resources"]["C"] = self.player["resources"].get("C", 0) + income

        # 3) Domestic Index bonus (+1 Economy per active route)
        domestic = {}
        for name, settlement in self.player.get("settlements", {}).items():
            routes = settlement.get("trade_routes", [])
            di = settlement.setdefault("domestic_index", {})
            di["Economy"] = di.get("Economy", 0) + len(routes)
            domestic[name] = di

        return {
            "resources": self.player["resources"],
            "trade_income": income,
            "domestic_index": domestic
        }