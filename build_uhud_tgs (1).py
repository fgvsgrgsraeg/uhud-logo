import math
from lottie.objects.animation import Animation
from lottie.objects.layers import ShapeLayer
from lottie.objects.shapes import (
    Group, Ellipse, Path, Fill, Stroke, GradientFill, Trim, TransformShape
)
from lottie.objects.helpers import Transform
from lottie.objects.bezier import Bezier
from lottie.objects import easing
from lottie.nvector import NVector
from lottie.utils.font import RawFontRenderer
from lottie.exporters.core import export_tgs
from lottie.exporters.tgs_validator import TgsValidator, Severity

W, H = 512, 512
FPS = 30
DURATION = 2.7
N_FRAMES = int(FPS * DURATION)

anim = Animation(N_FRAMES, FPS)
anim.width = W
anim.height = H
anim.in_point = 0
anim.out_point = N_FRAMES

GOLD_LIGHT = NVector(0.965, 0.780, 0.396)   # light gold
GOLD_DARK = NVector(0.702, 0.451, 0.145)    # dark amber
WHITE = NVector(1, 1, 1)

# ---------------------------------------------------------------
# DISC ICON (brake-rotor mark), centered at local origin, radius ~95
# ---------------------------------------------------------------
disc_group = Group()
disc_group.name = "disc_icon"

RADIUS = 85
STROKE_W = 22

def add_gradient_stroke(shape_group, ellipse, start_deg, end_deg, width, colors):
    """Attach an elliptical arc (via Trim) with a gradient stroke."""
    grp = Group()
    grp.add_shape(ellipse)
    trim = Trim()
    trim.start.value = start_deg / 360 * 100
    trim.end.value = end_deg / 360 * 100
    grp.add_shape(trim)
    grad = GradientFill(colors)
    # placeholder; caller replaces with stroke instead if needed
    return grp

# Main ring: ~78% of a full circle (leaves a gap at the top for the accent swoosh)
ring_ellipse = Ellipse(position=NVector(0, 0), size=NVector(RADIUS * 2, RADIUS * 2))
ring_group = Group()
ring_group.name = "ring"
ring_group.add_shape(ring_ellipse)

ring_trim = Trim()
ring_trim.start.value = 8
ring_trim.end.value = 84
ring_trim.offset.value = -90
ring_group.add_shape(ring_trim)

ring_stroke = Stroke(GOLD_DARK, STROKE_W)
ring_stroke.line_cap = ring_stroke.line_cap.__class__.Round
from lottie.objects.shapes import GradientStroke
ring_gstroke = GradientStroke([
    0.0, GOLD_LIGHT.x, GOLD_LIGHT.y, GOLD_LIGHT.z,
    1.0, GOLD_DARK.x, GOLD_DARK.y, GOLD_DARK.z,
], )
ring_gstroke.width.value = STROKE_W
ring_gstroke.start_point.value = NVector(-RADIUS, -RADIUS)
ring_gstroke.end_point.value = NVector(RADIUS, RADIUS)
ring_gstroke.line_cap = ring_gstroke.line_cap.__class__.Round
ring_group.add_shape(ring_gstroke)
disc_group.add_shape(ring_group)

# Accent swoosh: short arc near the gap, brighter, suggesting motion/speed
accent_ellipse = Ellipse(position=NVector(0, 0), size=NVector(RADIUS * 2, RADIUS * 2))
accent_group = Group()
accent_group.name = "accent"
accent_group.add_shape(accent_ellipse)
accent_trim = Trim()
accent_trim.start.value = 86
accent_trim.end.value = 100
accent_trim.offset.value = -90
accent_group.add_shape(accent_trim)
accent_stroke = Stroke(WHITE, STROKE_W * 0.9)
accent_stroke.line_cap = accent_stroke.line_cap.__class__.Round
accent_group.add_shape(accent_stroke)
disc_group.add_shape(accent_group)

# Bolt holes: 5 small dots around a smaller inner circle
N_HOLES = 5
HOLE_R = 7
HOLE_ORBIT = 41
for i in range(N_HOLES):
    ang = math.radians(-90 + i * (360 / N_HOLES))
    cx = math.cos(ang) * HOLE_ORBIT
    cy = math.sin(ang) * HOLE_ORBIT
    hole = Ellipse(position=NVector(cx, cy), size=NVector(HOLE_R * 2, HOLE_R * 2))
    hole_group = Group()
    hole_group.name = "hole_%d" % i
    hole_group.add_shape(hole)
    hole_fill = Fill(GOLD_DARK)
    hole_group.add_shape(hole_fill)
    disc_group.add_shape(hole_group)

# Center hub: filled circle + thin ring
hub_fill_ellipse = Ellipse(position=NVector(0, 0), size=NVector(27, 27))
hub_group = Group()
hub_group.name = "hub"
hub_group.add_shape(hub_fill_ellipse)
hub_fill = Fill(GOLD_LIGHT)
hub_group.add_shape(hub_fill)
disc_group.add_shape(hub_group)

hub_ring_ellipse = Ellipse(position=NVector(0, 0), size=NVector(41, 41))
hub_ring_group = Group()
hub_ring_group.name = "hub_ring"
hub_ring_group.add_shape(hub_ring_ellipse)
hub_ring_stroke = Stroke(GOLD_DARK, 6)
hub_ring_group.add_shape(hub_ring_stroke)
disc_group.add_shape(hub_ring_group)

# Two small radial tick marks (like tread marks) near the bottom of the ring
for sign in (-1, 1):
    ang = math.radians(60 * sign + 90)
    x1, y1 = math.cos(ang) * (RADIUS - STROKE_W * 0.7), math.sin(ang) * (RADIUS - STROKE_W * 0.7)
    x2, y2 = math.cos(ang) * (RADIUS + STROKE_W * 0.7), math.sin(ang) * (RADIUS + STROKE_W * 0.7)
    bez = Bezier()
    bez.add_point(NVector(x1, y1))
    bez.add_point(NVector(x2, y2))
    tick_path = Path(bez)
    tick_group = Group()
    tick_group.name = "tick"
    tick_group.add_shape(tick_path)
    tick_stroke = Stroke(GOLD_LIGHT, 8)
    tick_group.add_shape(tick_stroke)
    disc_group.add_shape(tick_group)

# --- Disc layer: place disc icon, animate continuous rotation ---
disc_layer = ShapeLayer()
disc_layer.name = "disc"
disc_layer.shapes.append(disc_group)
disc_layer.in_point = 0
disc_layer.out_point = N_FRAMES
DISC_CX = 140
DISC_CY = 256
disc_layer.transform.position.value = NVector(DISC_CX, DISC_CY)
disc_layer.transform.rotation.add_keyframe(0, 0, easing.Linear())
disc_layer.transform.rotation.add_keyframe(N_FRAMES, 360, easing.Linear())
anim.add_layer(disc_layer)

# ---------------------------------------------------------------
# TEXT "UHUD"
# ---------------------------------------------------------------
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # istalgan bold shrift faylini shu yerga qo'ying
font = RawFontRenderer(FONT_PATH)
TEXT_SIZE = 130
text_group = font.render("UHUD", TEXT_SIZE, pos=NVector(0, 0))
text_group.name = "UHUD"
text_fill = Fill(WHITE)
text_group.add_shape(text_fill)

# Precise bounding box of the glyphs, used to center the text block exactly
bb = text_group.bounding_box(0)
text_layer = ShapeLayer()
text_layer.name = "UHUD_text"
text_layer.shapes.append(text_group)
text_layer.in_point = 0
text_layer.out_point = N_FRAMES

TEXT_LEFT = 256   # just to the right of the disc icon
TEXT_CENTER_Y = DISC_CY

# Anchor at the bbox's left edge / vertical center so scaling/position math is exact
anchor_x = bb.x1
anchor_y = (bb.y1 + bb.y2) / 2
text_layer.transform.anchor_point.value = NVector(anchor_x, anchor_y)
text_layer.transform.position.value = NVector(TEXT_LEFT, TEXT_CENTER_Y)

# Bounce-in scale/opacity animation for the text (frames 0 -> 20)
s = text_layer.transform.scale
s.add_keyframe(0, NVector(0, 0), easing.EaseOut())
s.add_keyframe(12, NVector(112, 112), easing.EaseOut())
s.add_keyframe(20, NVector(100, 100), easing.EaseOut())

o = text_layer.transform.opacity
o.add_keyframe(0, 0, easing.Linear())
o.add_keyframe(10, 100, easing.Linear())

anim.add_layer(text_layer)

# ---------------------------------------------------------------
# Export
# ---------------------------------------------------------------
out_path = "/home/claude/uhud_emoji.tgs"
export_tgs(anim, out_path, sanitize=True)

validator = TgsValidator(Severity.Warning)
validator.check_size(__import__("os").path.getsize(out_path))
for e in validator.errors:
    print(e)

import os
print("Size (KB):", os.path.getsize(out_path) / 1024)
print("Done ->", out_path)
