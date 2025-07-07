# utils/parsing.py

import re

def parse_int(val):
    try:
        return int(float(val))
    except:
        return 0

def parse_name_level(cell):
    m = re.match(r"(.+?) level (\d+)", cell.strip())
    return (m.group(1), int(m.group(2))) if m else (cell.strip(), 1)

def parse_structure_requirements(cell):
    result = []
    if not cell: return result
    for group in cell.split("|"):
        or_group = []
        for item in group.split(","):
            item = item.strip()
            if ":" in item:
                name, lvl = item.split(":")
                or_group.append({"name": name.strip(),
                                 "level": parse_int(lvl)})
        if or_group:
            result.append(or_group)
    return result