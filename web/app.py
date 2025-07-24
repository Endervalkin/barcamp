import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, render_template, request, jsonify
from Game.state.player_factory import create_player


app = Flask(__name__, static_folder="static", template_folder="templates")


game_state = {
    "player": create_player("Lee"),
    "hex_registry": {}  # eventually load from file
}

@app.route("/")
def index():
    return render_template("index.html", game_state=game_state)
@app.route("/game_state")
def get_game_state():
    return jsonify(game_state)

@app.route("/select_hex", methods=["POST"])
def select_hex():
    hex_id = request.json["hex"]
    # Update game_state, log action, etc.
    return jsonify({ "selected": hex_id })

@app.route("/create_player", methods=["POST"])
def create():
    name = request.json["name"]
    game_state["player"] = create_player(name)
    return jsonify({"status": "ok", "player": game_state["player"]})

from Game.engine.turn_engine import TurnEngine

@app.route("/end_month", methods=["POST"])
def end_month_route():
    engine = TurnEngine(game_state["player"])
    result = engine.end_month()
    return jsonify(result)

if __name__ == "__main__":
    # debug=True shows errors in-console; host='0.0.0.0' exposes to WSL network
    app.run(debug=True, host="0.0.0.0", port=5000)

@app.route("/check_hex", methods=["POST"])
def check_hex():
    hex_id = request.json["hex"]
    settlements = game_state["player"].get("settlements", {})
    for s in settlements.values():
        if s.get("hex") == hex_id:
            return jsonify({ "has_settlement": True })
    return jsonify({ "has_settlement": False })

@app.route("/build_settlement", methods=["POST"])
def build_settlement():
    hex_id = request.json["hex"]
    settlement_type = request.json["type"]

    # Use your engine logic
    from Game.engine.settlement_actions import build_settlement
    build_settlement(game_state["player"], hex_id, settlement_type)

    return jsonify({ "status": "ok", "built": settlement_type, "hex": hex_id })

from Game.engine.map_engine import generate_axial_hexes, hex_points


def build_hex_overlay():
    axial_map = generate_axial_hexes(width=184, height=106)
    hex_list = []

    for hex_id, (q, r) in axial_map.items():
        hex_list.append({
            "id": hex_id,
            "points": hex_points(q, r, size=20)
        })

    return hex_list

# Create your game state early in the app:
game_state = {
    "player": {},
    "hex_registry": generate_axial_hexes(184, 106),
    "hexes": build_hex_overlay()
}
