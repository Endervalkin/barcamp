import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../Game")))  # Add this if your models folder is under Game/
import json
from models.settlement import Settlement
from models.structure import Structure
from models.barony import Barony, BaronyLedger
from registry.settlement_loader import parse_csv_to_json
from registry.unit_registry import UnitRegistry
from engine.ledger import TurnLogEngine
from engine.turn import TurnEngine

def test_settlement_load():
    data = json.load(open("Game/data/settlements/SettlementData.json"))
    city2 = Settlement(next(s for s in data if s["name"]=="City" and s["level"]==2))
    assert city2.name=="City" and city2.level==2

def test_structure_load():
    data = json.load(open("Game/data/settlements/StructureData.json"))
    s = Structure(data[0])
    assert hasattr(s, "di_modifiers") and isinstance(s.di_modifiers, dict)

def test_barony_ledger_flow():
    bl = BaronyLedger("Test", tax_exempt=True)
    bl.submit_month("0000", production={"L":10}, upkeep={"L":5}, coin_subs=None, road_cost=None)
    summary = bl.get_month_summary("0000")
    assert summary["net_gain"]["L"]==5 and summary["taxes_paid"]["L"]==0

def test_unit_registry():
    ur = UnitRegistry("Game/data/units")
    all_units = ur.get_all()
    assert isinstance(all_units, list) and len(all_units)>0