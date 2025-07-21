# utils/parsing.py

import re
from Game.registry import *


def parse_int(val: str) -> int:
    """
    Safely parse any string/number to int.
    Returns 0 on failure.
    """
    try:
        return int(float(val.strip()))
    except:
        return 0


def parse_bool(val: str) -> bool:
    """
    Parses a truthy string (e.g. "TRUE") into True, else False.
    """
    return bool(val and val.strip().upper() == "TRUE")


def parse_name_level(cell: str) -> tuple[str,int]:
    """
    Splits strings like "Market level 3" into ("Market", 3).
    Falls back to (cell, 1) if no match.
    Case‐insensitive on "level".
    """
    m = re.match(r"(.+?)\s+level\s+(\d+)", cell.strip(), re.IGNORECASE)
    if m:
        return m.group(1).strip(), int(m.group(2))
    return cell.strip(), 1


def parse_structure_requirements(cell: str) -> list[list[dict]]:
    """
    Transforms strings like "Walls:1|Market:1|Forge:1,Refinery:1"
    into a list of OR‐groups:
      [
        [ {"name":"Walls","level":1} ],
        [ {"name":"Market","level":1} ],
        [ {"name":"Forge","level":1},
          {"name":"Refinery","level":1} ]
      ]
    """
    groups = []
    if not cell or not cell.strip():
        return groups

    for or_chunk in cell.split("|"):
        or_group = []
        for item in or_chunk.split(","):
            item = item.strip()
            if not item:
                continue
            if ":" in item:
                name, lvl = item.split(":", 1)
                or_group.append({
                    "name": name.strip(),
                    "level": parse_int(lvl)
                })
            else:
                # no level specified → default to 1
                or_group.append({"name": item, "level": 1})

        if or_group:
            groups.append(or_group)

    return groups