import os
import json

# Load caravan data
def load_caravan_data(path="data/caravan_data.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Build a caravan unit
def create_caravan(player, origin_hex, caravan_type="Caravan"):
    data = load_caravan_data()
    caravan = data[caravan_type]
    for res, amt in caravan["build_cost"].items():
        if player["resources"].get(res, 0) < amt:
            raise ValueError(f"Not enough {res}")
        player["resources"][res] -= amt

    new_caravan = {
        "id": f"{player['name']}-caravan-{len(player['caravans'])}",
        "location": origin_hex,
        "owner": player["name"],
        "turns_until_ready": caravan["build_time"],
        "active": False,
        "stats": caravan["stats"],
        "route": [],
        "assigned_roles": []
    }
    player["caravans"].append(new_caravan)
    return new_caravan



def resolve_trade_routes(player, hex_registry):
    income = 0
    for caravan in player["caravans"]:
        if not caravan["active"]: continue
        start_hex = hex_registry.get(caravan["location"])
        end_hex_id = caravan["route"][-1] if caravan["route"] else None
        end_hex = hex_registry.get(end_hex_id) if end_hex_id else {}
        coin = calculate_trade_value(
            trade=caravan,
            start_settlement=start_hex.get("settlement", {}),
            end_settlement=end_hex.get("settlement", {}),
            route_type="Land",
            infrastructure=start_hex.get("settlement", {}).get("structures", {}),
            player_state=player
        )
        income += coin
    player["resources"]["C"] += income
    return income



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