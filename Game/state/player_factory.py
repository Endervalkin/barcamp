def create_player(name):
    return {
        "name": name,
        "resources": { "L": 20, "S": 20, "M": 20, "F": 20, "R": 20, "C": 20 },
        "turn_log": [],
        "settlements": {},
        "caravans": []
    }