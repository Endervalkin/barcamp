# Game/engine/hex_renderer.py
import math
from math import sqrt, radians, cos, sin
from typing import Dict, List, Tuple

import math

HEX_SIZE = 50  # Default radius

def axial_to_pixel(q, r, size=HEX_SIZE):
    x = size * 3/2 * q
    y = size * math.sqrt(3) * (r + q / 2)
    return x, y

def hex_points(cx, cy, size=HEX_SIZE):
    return [
        (cx + size * math.cos(math.radians(angle)),
         cy + size * math.sin(math.radians(angle)))
        for angle in range(30, 390, 60)
    ]

def format_polygon(q, r, points, stroke="rgba(0,0,0,0.2)", fill="none"):
    points_str = ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)
    return (f'<polygon class="hex" data-q="{q}" data-r="{r}" '
            f'points="{points_str}" stroke="{stroke}" stroke-width="1" fill="{fill}" />')

def wrap_svg(elements, width, height):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width} {height}" width="{width}" height="{height}">\n'
            + '\n'.join(elements) +
            '\n</svg>')


def render_hex_grid(q_range, r_range, width, height, size=50):
    elements = []
    for q in q_range:
        for r in r_range:
            cx, cy = axial_to_pixel(q, r, size)
            if 0 <= cx <= width and 0 <= cy <= height:
                points = hex_points(cx, cy, size)
                elements.append(format_polygon(q, r, points))
    return wrap_svg(elements, width, height)