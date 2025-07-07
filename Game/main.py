from fastapi import FastAPI
import json
from fastapi.responses import JSONResponse

app = FastAPI()

with open("parse/StructureData.json") as f:
    structure_data = json.load(f)

@app.get("/structures")
def get_all_structures():
    return structure_data