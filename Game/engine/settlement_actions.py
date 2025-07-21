def build_settlement(character, location_data, action_engine, template_path=None):
    import json, os
    from Game.models.settlement import Settlement

    # Default template path
    if not template_path:
        template_path = os.path.join("data", "settlement", "SettlementData.json")

    # Check turn availability
    if character.get_turns_remaining() < 1:
        return f"❌ {character.name} lacks turns to build a settlement."

    # Check location is valid (stub for now)
    if not location_data.get("valid", False):
        return f"📍 Chosen location is not valid for settlement."

    # Select settlement type (stub: City vs Fortress)
    chosen_type = location_data.get("type", "City")  # or "Fortress"

    # Load settlement template
    with open(template_path, "r", encoding="utf-8") as f:
        templates = json.load(f)

    template = next((t for t in templates if t["name"] == chosen_type and t["level"] == 1), None)
    if not template:
        return f"🚫 No settlement template found for {chosen_type} level 1."

    build_cost = template.get("build_cost", {})
    if not character.ledger.can_afford(build_cost):
        return f"💰 {character.name} lacks resources to found a {chosen_type}."

    # Create and register settlement
    new_settlement = Settlement(template)
    new_settlement.location = location_data.get("coords")
    new_settlement.founder_id = character.id

    # Spend resources and turn
    character.ledger.spend(build_cost, purpose="Found Settlement", by=character.name)
    character.decrement_turns()

    # Log action
    result = action_engine.perform_action(
        actor=character,
        action_type="Found Settlement",
        details=f"{chosen_type} at {new_settlement.location}",
        cost=build_cost,
        turn_cost=1
    )

    # Optional: add to character-owned list
    character.owned_settlements.append(new_settlement)

    return f"🌆 {character.name} founded a {chosen_type} at {new_settlement.location}.\n{result}"

def place_structure(settlement, structure_data, action_engine):
    """
    Place a structure in the settlement.
    """
    name = structure_data["name"]
    level = structure_data["level"]
    build_cost = structure_data["build_cost"]

    # Check if settlement can build this structure
    if not settlement.can_build_structure(name):
        return f"⛔ {settlement.name} cannot build {name}."

    # Check resource availability
    if not settlement.ledger.can_afford(build_cost):
        return f"💰 {settlement.name} lacks resources to build {name}."

    # Spend resources and turn
    settlement.ledger.spend(build_cost, purpose="Build Structure", by=settlement.name)
    settlement.decrement_turns()

    # Log action
    result = action_engine.perform_action(
        actor=settlement,
        action_type="Place Structure",
        details=f"{name} level {level}",
        cost=build_cost,
        turn_cost=1
    )

    # Add structure to settlement
    settlement.add_structure(structure_data)

    return f"✅ {settlement.name} placed {name} level {level}.\n{result}"