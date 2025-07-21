import os
import sys



class ActionEngine:
    def __init__(self, ledger, turn_tracker):
        self.ledger = ledger              # Instance of BaronyLedger or PlayerLedger
        self.turn_tracker = turn_tracker # Dict {actor_id: turns_remaining}
        self.action_log = []             # Each entry: dict with actor, action, cost, timestamp

    def perform_action(self, actor, action_type, details, cost=None, turn_cost=1):
        # Check turn availability
        if self.turn_tracker.get(actor.id, 0) < turn_cost:
            return f"❌ {actor.name} has no turns remaining."

        # Validate resources
        if cost and not self.ledger.ledger.spend(cost, purpose=action_type, by=actor.name):
            return f"💰 {actor.name} lacks resources for {action_type}."

        # Spend turn(s)
        self.turn_tracker[actor.id] -= turn_cost

        # Log it
        self.action_log.append({
            "actor": actor.name,
            "type": action_type,
            "details": details,
            "cost": cost or {},
            "turns_spent": turn_cost
        })

        return f"✅ {actor.name} performed {action_type}: {details}"