import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, render_template, request, jsonify
from Game.state.player_factory import create_player
from Game.engine.turn_engine import end_month

app = Flask(__name__)

game_state = {
    "player": create_player("Lee"),
    "hex_registry": {}  # eventually load from file
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create_player", methods=["POST"])
def create():
    name = request.json["name"]
    game_state["player"] = create_player(name)
    return jsonify({"status": "ok", "player": game_state["player"]})

@app.route("/end_month", methods=["POST"])
def end_turn():
    end_month(game_state["player"], game_state["hex_registry"])
    return jsonify({"status": "ok", "resources": game_state["player"]["resources"]})
