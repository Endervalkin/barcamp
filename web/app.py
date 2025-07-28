import sys
import os
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from math import sqrt, radians, cos, sin
from flask import Flask, render_template, request, jsonify
from Game.state.player_factory import create_player
from Game.engine.map_engine import generate_centered_axial_hexes
from Game.engine.hex_renderer import hex_points, axial_to_pixel
from Game.engine.turn_engine import TurnEngine

app = Flask(__name__, static_folder="static", template_folder="templates")




# Calculate the proper hex “size” so your grid spans the 2686px width
def build_hex_overlay(cols, rows, map_w, map_h):
    size = 20
    #min( map_w / (1.5 * (cols - 1) + 1),map_h / (math.sqrt(3) * (rows + cols/2)))

    offset_x = 20  # small left margin
    offset_y = 20  # small top margin

    x0, y0 = axial_to_pixel(0, 0, size, offset_x, offset_y)
    print(f"Hex (0,0) pixel = ({x0:.1f}, {y0:.1f})")

    axial_map = generate_centered_axial_hexes(cols, rows)
    hexes = [
        {
            "id": hex_id,
            "points": hex_points(q, r, size, offset_x, offset_y)
        }
        for hex_id, (q, r) in axial_map.items()
    ]
    
    return hexes





app = Flask(__name__)

# Create your game_state at startup
game_state = {
    "player": {},
    "hex_registry": generate_centered_axial_hexes(217, 184),
    "hexes": build_hex_overlay(
    cols=217,  # number of q values
    rows=184,  # number of r values
    map_w=2686,
    map_h=4096
)

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

