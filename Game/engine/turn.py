from models.settlement import Settlement
from models.structure import Structure
from Game.models.characters import PlayerCharacter
from Game.models.homeward import NPC
from models.homeward import Homeward
from models.barony import Barony
from models.units import Units
from engine.action_handlers.structure_actions import build_structure, upgrade_structure, upgrade_settlement
from engine.action_handlers.settlement_actions import build_settlement



class TurnEngine:
    def __init__(self, baronies, settlements, structures, characters, npcs, homewards,di_map):
        self.baronies = baronies            # list of Barony
        self.settlements = settlements      # list of Settlement
        self.structures = structures        # list of Structure
        self.characters = characters        # list of PlayerCharacter
        self.npcs = npcs                    # list of NPC
        self.homewards = homewards          # list of Homeward
        self.di_map = di_map                # dict of DI ratings per settlement

        self.turn_pool = {}  # Dict to track turns available for each actor
        self.action_enginge = None  # Instance of ActionEngine

    def execute_month(self):
        self.apply_upkeep()
        self.assign_turns()
        self.process_turns()
        self.calculate_domestic_index()
        self.process_resource_production()
        self.update_ledgers_and_taxes()

    def execute_month(self, current_month, target_barony):
            print(f"📅 Executing Turn: {current_month} for Barony: {target_barony.name}")

            # STEP 1: Apply upkeep and ledger flow
            prev_balance = target_barony.ledger.balance.copy()
            engine = TurnLogEngine(previous_balance=prev_balance, tax_exempt=target_barony.tax_exempt)
            engine.apply_inputs(
                production=target_barony.get_production(),      # assumes method exists
                upkeep=target_barony.get_upkeep(),              # assumes method exists
                coin_subs=target_barony.get_coin_subs(),        # optional
                road_cost=target_barony.get_road_upkeep()       # optional
            )
            final, taxes, net = engine.calculate_final()
            target_barony.ledger.submit_month(current_month,
                                            production=target_barony.get_production(),
                                            upkeep=target_barony.get_upkeep(),
                                            coin_subs=target_barony.get_coin_subs(),
                                            road_cost=target_barony.get_road_upkeep())

            # STEP 2: Allocate turns
            allocator = TurnAllocator(
                self.characters, self.settlements,
                self.structures, self.npcs,
                self.homewards, self.di_map
            )
            self.turn_pool = allocator.allocate()

            # STEP 3: Create ActionEngine for tracking actions
            self.action_engine = ActionEngine(target_barony.ledger, self.turn_pool)

            # STEP 4: DI update (optional here, detailed below)
            # DI could be logged per-settlement or stored on each Settlement object

            print("✅ Turn executed. Turns allocated + ledger updated.")
    
    for settlement in self.settlements:
        di_scores = settlement.calculate_domestic_index(
            population=settlement.population,
            needs=settlement.get_needs(),
            structure_lvls=settlement.get_structure_levels(),
            base_unrest=settlement.base_unrest
        )   
        settlement.set_di(di_scores)
        self.di_map[settlement.id] = di_scores
    
    def get_turns_summary(self):
        return {actor_id: turns for actor_id, turns in self.turn_pool.items()}



def get_monthly_turns(self, di_rating):
    turns = 2 if self.name in ["City", "Fortress"] else 0

    # Bonus turn for Stability > 10 and Unrest <= 0
    if di_rating["Stability"] > 10 and di_rating["Unrest"] <= 0:
        turns += 1

    if self.population_base >= self.population_critical:
        turns += 1

    return turns

def is_active(self, available_resources):
    for res, cost in self.upkeep.items():
        if available_resources.get(res, 0) < cost:
            return False
    return True

def get_monthly_turns(self):
    return 1 if self.production else 0  # Some structures just contribute passively

def get_turns(self):
    total_levels = sum(c.level for c in self.magical_creatures)
    turns = (total_levels // 7) * self.level
    return max(turns, 0)

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

class TurnAllocator:
    def __init__(self, characters, settlements, structures, npcs, homewards, di_map):
        self.characters = characters
        self.settlements = settlements
        self.structures = structures
        self.npcs = npcs
        self.homewards = homewards
        self.di_map = di_map  # Dict of DI ratings per settlement

    def allocate(self):
        turn_pool = {}

        # Player Characters → 2 base turns
        for pc in self.characters:
            turn_pool[pc.id] = 2

        # NPCs → 1 or 2 turns if housed in active Estate
        for npc in self.npcs:
            estate = npc.estate
            if estate and estate.is_active():
                turn_pool[npc.id] = npc.get_monthly_turns()

        # Settlements → variable turns
        for settlement in self.settlements:
            di = self.di_map.get(settlement.id, {})
            turns = settlement.get_monthly_turns(di)
            turn_pool[settlement.id] = turns

        # Structures → typically 1 turn if active
        for structure in self.structures:
            if structure.is_active():
                turn_pool[structure.id] = structure.get_monthly_turns()

        # Homewards → depends on creature power + level
        for hw in self.homewards:
            turn_pool[hw.id] = hw.get_turns()

        return turn_pool
    
class TurnPlanner:
    def __init__(self, action_engine, turn_pool):
        self.action_engine = action_engine
        self.turn_pool = turn_pool

    def plan_turn(self, actor):
        if chosen_action == "Build Structure":
            structure_data = select_structure_to_build(actor)
            if structure_data:
                result = build_structure(actor, structure_data, self.action_engine)
            else:
                result = f"⚠️ No valid structures to build for {actor.name}."

        elif chosen_action == "Upgrade Structure":
            result = upgrade_structure(actor, self.action_engine)
        
        elif chosen_action == "Upgrade Settlement":
            result = upgrade_settlement(actor, self.action_engine)
            print(result)

        elif chosen_action == "Build Settlement":
            location_data = {
                "valid": True,
                "type": "City",
                "coords": (4, 6)
            }
            result = build_settlement(actor, location_data, self.action_engine)
            print(result)
        else:
            result = f"🔧 {actor.name} performed {chosen_action} (stubbed)."
        
        

    def spend_turn(self, actor, action_type, details, cost=None, turn_cost=1):
        turns = self.turn_pool.get(actor.id, 0)
        if turns < turn_cost:
            return f"❌ {actor.name} has no turns left."

        result = self.action_engine.perform_action(actor, action_type, details, cost, turn_cost)
        return result

    def plan_turn(self, actor):
        actions = self.get_available_actions(actor)
        print(f"\n🎯 {actor.name} has {self.turn_pool.get(actor.id, 0)} turn(s). Available actions:")
        for i, action in enumerate(actions):
            print(f"  {i+1}. {action}")

        # This can later be replaced by GUI input, CLI prompt, or AI automation
        # For now, stub in a default action
        chosen = actions[0] if actions else None
        if chosen:
            result = self.spend_turn(actor, chosen, "Default Detail")
            print(result)

    def get_available_actions(self, actor):
        # PLAYER CHARACTERS
        if isinstance(actor, PlayerCharacter):
            return [
                "Build Structure",
                "Upgrade Structure",
                "Build Settlement",
                "Upgrade Settlement",
                "Cast Leyline Spell",
                "Gather Resources",
                "Train Units",
                "Research City Techonology",
                "Build Road",
                "Upgrade Road",
                "Travel"
            ]

        # NON-PLAYER CHARACTERS (NPCs)
        elif isinstance(actor, PC_npc):
            available = [
                "Build Structure",
                "Upgrade Structure",
                "Upgrade Settlement",
                "Cast Leyline Spell",
                "Gather Resources",
                "Train Units",
                "Research City Techonology",
                "Build Road",
                "Upgrade Road",
                "Travel"
            ]
            return available

        # SETTLEMENTS
        elif isinstance(actor, Settlement):
            actions = []
            if actor.can_build_structure():
                actions.append("Build Structure")
            if actor.can_upgrade_structure():
                actions.append("Upgrade Structure")
            if actor.can_upgrade_self():
                actions.append("Upgrade Settlement")
            if actor.can_research_city_technology():
                actions.append("Research City Technology")
            if actor.has_road_access():
                actions.append("Build Road")
                actions.append("Upgrade Road")
            return actions            

        # STRUCTURES
        elif isinstance(actor, Structure):
            options = []
            if actor.can_train_units:
                options.append("Train Units")
            if actor.can_train_ships:
                options.append("Build Ship")
            if actor.can_train_siege_weapons:
                options.append("Build Siege Weapon")    
            if actor.can_produce_resources:
                options.append("Initiate Production")
            return options

        # HOMEWARDS
        elif isinstance(actor, Homeward):
            return [
                "Build Structure",
                "Upgrade Structure",
                "Upgrade Settlement"
            ]

        # TROOPS
        elif isinstance(actor, Troops):
            return [
                "Scout",
                "Engage in Combat",
                "Defend Settlement",
                "Garrison Settlement"
            ]
        # SHIPS
        elif isinstance(actor, Ship):
            return [
                "Sail",
                "Engage in Naval Combat",
                "Trade with Port"
            ]
        # DEFAULT
        else:
            return []