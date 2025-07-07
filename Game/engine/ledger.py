# engine/ledger.py
from datetime import datetime

class ResourceLedger:
    def __init__(self):
        self.resources = {"L": 0, "S": 0, "M": 0, "F": 0, "R": 0, "C": 0}
        self.transaction_log = []  # list of dicts

    def add(self, amount, source="", by="SYSTEM"):
        for key in amount:
            self.resources[key] += amount[key]
        self._log("ADD", amount, source, by)

    def spend(self, cost, purpose="", by="SYSTEM", require_check=True):
        if require_check and any(self.resources.get(k, 0) < cost.get(k, 0) for k in cost):
            return False
        for k in cost:
            self.resources[k] -= cost[k]
        self._log("SPEND", cost, purpose, by)
        return True

    def _log(self, kind, delta, context, actor):
        self.transaction_log.append({
            "type": kind,
            "delta": delta,
            "context": context,
            "by": actor,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })

    def get_log(self, last_n=None):
        return self.transaction_log[-last_n:] if last_n else self.transaction_log

    def get_balance(self):
        return dict(self.resources)

class BaronyLedger:
    def __init__(self, barony_name, tax_exempt=False):
        self.name = barony_name
        self.tax_exempt = tax_exempt
        self.monthly_logs = {}  # e.g., {"062024": TurnLogEngine}
        self.balance = {"L": 0, "S": 0, "M": 0, "F": 0, "R": 0, "C": 0}

    def submit_month(self, month_key, production, upkeep, coin_subs=None, road_cost=None):
        previous = self.balance.copy()
        engine = TurnLogEngine(previous_balance=previous, tax_exempt=self.tax_exempt)
        engine.apply_inputs(production, upkeep, coin_subs, road_cost)

        final, taxes, net = engine.calculate_final()

        self.monthly_logs[month_key] = {
            "engine": engine,
            "final_balance": final,
            "taxes_paid": taxes,
            "net_gain": net
        }

        self.balance = final.copy()

    def get_month_summary(self, month_key):
        if month_key not in self.monthly_logs:
            return f"❌ No data for {month_key}"
        log = self.monthly_logs[month_key]
        return {
            "balance": log["final_balance"],
            "net_gain": log["net_gain"],
            "taxes_paid": log["taxes_paid"]
        }

    def get_ledger_report(self):
        return {
            "barony": self.name,
            "current_balance": self.balance,
            "months_recorded": list(self.monthly_logs.keys())
        }

class TurnLogEngine:
    def __init__(self, previous_balance=None, tax_exempt=False):
        self.previous_balance = previous_balance or {"L": 0, "S": 0, "M": 0, "F": 0, "R": 0, "C": 0}
        self.production = {}
        self.upkeep = {}
        self.coin_substitutions = {}  # coin used to offset upkeep
        self.road_upkeep = {}
        self.tax_exempt = tax_exempt

    def apply_inputs(self, production, upkeep, coin_subs=None, road_cost=None):
        self.production = production
        self.upkeep = upkeep
        self.coin_substitutions = coin_subs or {}
        self.road_upkeep = road_cost or {}

    def calculate_subtotal(self):
        subtotal = {res: self.production.get(res, 0) - self.upkeep.get(res, 0) for res in self.production}
        for res, sub_amount in self.coin_substitutions.items():
            subtotal[res] += sub_amount
            subtotal["C"] -= sub_amount
        subtotal["C"] -= self.road_upkeep.get("C", 0)
        return subtotal

    def calculate_taxes(self, subtotal):
        if self.tax_exempt:
            return {res: 0 for res in subtotal}
        return {
            res: int(subtotal[res] * 0.1) if subtotal[res] >= 10 else 0
            for res in subtotal
        }

    def calculate_final(self):
        subtotal = self.calculate_subtotal()
        taxes = self.calculate_taxes(subtotal)
        net = {res: subtotal[res] - taxes[res] for res in subtotal}
        final = {res: net[res] + self.previous_balance.get(res, 0) for res in net}
        return final, taxes, net