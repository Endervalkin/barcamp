# Game/engine/hex_renderer.py
import math
from math import sqrt, radians, cos, sin
from typing import Dict, List, Tuple

# Game/engine/hex_render.py
import math

def axial_to_pixel(q, r, size, offset_x=0, offset_y=0):
    x = size * sqrt(3) * (q + r/2) + offset_x
    y = size * 3/2 * r + offset_y
    return x, y


def hex_corner(cx, cy, size, i):
    angle_rad = math.radians(60 * i - 30)
    return (
        cx + size * math.cos(angle_rad),
        cy + size * math.sin(angle_rad)
    )

def hex_points(q, r, size, offset_x=0, offset_y=0):
    cx, cy = axial_to_pixel(q, r, size, offset_x, offset_y)
    return [
        (
            cx + size * cos(radians(60 * i - 30)),
            cy + size * sin(radians(60 * i - 30))
        )
        for i in range(6)
        
    ]

# hex_renderer.py
def hex_to_svg_polygon(q, r):
    cx, cy = axial_to_pixel(q, r)
    points = hex_points(cx, cy)
    points_str = ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)
    return f'<polygon data-q="{q}" data-r="{r}" points="{points_str}" ... />'

def render_hex_grid_to_svg(q_range, r_range, width, height):
    elements = [hex_to_svg_polygon(q, r)
                for q in q_range for r in r_range
                if in_bounds(axial_to_pixel(q, r), width, height)]
    return wrap_svg(elements, width, height)
