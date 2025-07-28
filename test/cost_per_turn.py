#DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Game", "data"))

#def load_json(path):
#    with open(path, "r", encoding="utf-8") as f:
#        return json.load(f)

# Load data
#settlements = load_json(os.path.join(DATA_DIR, "settlements", "SettlementData.json"))
#structures = load_json(os.path.join(DATA_DIR, "structures", "StructureData.json"))
#units = load_json(os.path.join(DATA_DIR, "units", "UnitData.json"))
#roads = load_json(os.path.join(DATA_DIR, "roads", "road_data.json"))


def round_lumber(build_cost_L: int, build_turns: int, current_turn: int) -> int:
    """
    Round the lumber cost based on the build cost and turns.
    """
    return round(build_cost_L / build_turns) * current_turn
    

def lumber_per_turn():
    build_cost_L = 65
    build_turns = 20
    current_turn = 1
    if(round_lumber(65,20,1) < build_cost_L and round_lumber(65,20,1) - build_cost_L) == (build_cost_L/ build_turns):
        return 0
    elif round_lumber(65,20,1) - build_cost_L < build_cost_L:
        return 0
    elif build_turns == 2 and round_lumber(65,20,1) < build_cost_L:
        return build_cost_L - round(build_cost_L / build_turns)
    elif round_lumber(65,20,1) < build_cost_L:
        return build_cost_L - round_lumber(65,20, current_turn - 1)
    elif round_lumber(65,20,1) > build_cost_L or round_lumber(65,20,1) == build_cost_L:
        return round(build_cost_L / build_turns)
    elif (round_lumber(65,20,1) - build_cost_L) < 0:
        return 0
    
    

    
