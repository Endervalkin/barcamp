import os
def create_caravan():
    """
    Create a caravan for trade.
    """
    # Logic to create a caravan
    pass

def resolve_trade_routes():
    """
    Resolve trade routes for the current turn.
    """
    # Logic to resolve trade routes
    pass


def calculate_trade_value(trade, start_settlement, end_settlement, route_type, infrastructure, player_state):
    base = trade["cargo"]  # Starting value

    # 🏪 Market
    if "Market" in start_settlement.get("structures", []):
        base += 1

    # 🛣 Road bonus (only for Land/Caravan)
    if route_type == "Land":
        road_type = trade.get("road_type")  # "Dirt", "Wooden", "Cobblestone"
        road_bonus = {
            "Dirt": 1, "Wooden-Framed": 2, "Cobblestone": 3
        }.get(road_type, 0)
        base += road_bonus

    # 🧑 Other player destination
    if start_settlement["owner"] != end_settlement["owner"]:
        base += 1

    # 🏰 Capitol bonus
    if start_settlement.get("is_capitol"):
        base += 1
    if end_settlement.get("is_capitol"):
        base += 1

    # 👷 Skilled Worker
    if "Skilled Worker (Coin)" in trade.get("assigned_roles", []):
        base += 1

    # 🧙 Gateway override
    if route_type == "Gateway":
        gateway_lvl = infrastructure.get("Gateway", {}).get("level", 0)
        base += gateway_lvl  # Instead of road bonus

    return base

def get_ship_trade_value(ship, start_settlement):
    cargo = ship["cargo"]
    if ship["type"] != "Merchant":
        cargo = cargo // 2  # Round down
    value = cargo

    # 🚢 Harbor bonus
    if "Harbor" in start_settlement.get("structures", []):
        value += 1

    # 🔭 Lighthouse level
    lighthouse = start_settlement.get("structures", {}).get("Lighthouse", {})
    if lighthouse:
        value += lighthouse.get("level", 0)

    # 👨 Skilled Workers (up to ship level)
    assigned = ship.get("assigned_roles", [])
    allowed = ship.get("level", 1)
    coin_workers = assigned.count("Skilled Worker (Coin)")
    value += min(coin_workers, allowed)

    return value

def get_airship_trade_value(airship, start_settlement):
    cargo = airship["cargo"]
    if airship["type"] != "Merchant":
        cargo = cargo // 2  # Round down
    value = cargo

    # 🚢 Airship Port bonus
    if "Airship Port" in start_settlement.get("structures", []):
        value += 1

    # 🔭 Lighthouse level
    lighthouse = start_settlement.get("structures", {}).get("Lighthouse", {})
    if lighthouse:
        value += lighthouse.get("level", 0)

    # 👨 Skilled Workers (up to ship level)
    assigned = airship.get("assigned_roles", [])
    allowed = airship.get("level", 1)
    coin_workers = assigned.count("Skilled Worker (Coin)")
    value += min(coin_workers, allowed)

    return value