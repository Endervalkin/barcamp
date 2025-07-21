from map_engine import generate_axial_hexes, place_settlement, place_road, move_troops, is_valid_hex

def build_roads(player, selected_hexes, road_type):
    return place_road(selected_hexes, road_type, player)

def start_caravan(player, origin_hex, cargo, assigned_roles=None):
    raise NotImplementedError  # Wrapper for trade_engine.create_caravan()