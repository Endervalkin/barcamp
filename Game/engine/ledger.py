import datetime

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