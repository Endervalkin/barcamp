from fastapi import FastAPI
import os

import json
from fastapi.responses import JSONResponse

app = FastAPI()

with open("Game/data/units/StructureData_refactored.json") as f:
    structure_data = json.load(f)

@app.get("/structures")
def get_all_structures():
    return structure_data