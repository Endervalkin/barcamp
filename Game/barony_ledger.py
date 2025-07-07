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