def parse_trainable_units(raw):
    return [u.strip() for u in raw.split(",") if u.strip()]

def parse_unit_conversions(raw):
    conv = []
    for pair in raw.split(","):
        if "→" not in pair: continue
        src, dst = [p.strip() for p in pair.split("→")]
        conv.append({"from": src, "to": dst})
    return conv