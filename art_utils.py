"""
art_utils.py — Reusable art toolkit for Claude.

Pipeline:
  ArtCanvas (pycairo) → SVG/PNG → Inkscape (render/display)

Usage:
  from art_utils import ArtCanvas, Palette, Lighting, Composition, open_in_inkscape
  c = ArtCanvas(800, 1000)
  c.background(Palette.SKY_GRADIENT)
  c.ellipse(400, 300, 100, 130, fill=Palette.SKIN, stroke=Palette.SKIN_SHD)
  c.save("out.svg")
  open_in_inkscape("out.svg")
"""

import math
import colorsys
import subprocess
import os
import io
from typing import Tuple, List, Optional, Union
import cairo

# ── Type aliases ─────────────────────────────────────────────────────────────
Color  = Tuple[float, float, float]          # RGB 0-1
ColorA = Tuple[float, float, float, float]   # RGBA 0-1
Point  = Tuple[float, float]

INKSCAPE = r"C:\Program Files\Inkscape\bin\inkscape.exe"

# ─────────────────────────────────────────────────────────────────────────────
# Palette — colours as (R, G, B) floats 0-1
# ─────────────────────────────────────────────────────────────────────────────
class Palette:
    """Named colours and colour-manipulation helpers."""

    # Skin tones
    SKIN       = (0.80, 0.67, 0.51)
    SKIN_SHD   = (0.69, 0.55, 0.39)
    SKIN_HLT   = (0.88, 0.76, 0.63)
    SKIN_DARK  = (0.55, 0.38, 0.25)

    # Hair
    HAIR_BRN   = (0.20, 0.14, 0.08)
    HAIR_LT    = (0.45, 0.32, 0.18)
    HAIR_BLK   = (0.08, 0.06, 0.04)

    # Landscape
    SKY_TOP    = (0.47, 0.63, 0.75)
    SKY_MID    = (0.59, 0.74, 0.84)
    SKY_HAZE   = (0.76, 0.84, 0.88)
    HILL_FAR   = (0.40, 0.55, 0.60)
    HILL_MID   = (0.30, 0.47, 0.42)
    HILL_NEAR  = (0.22, 0.38, 0.28)
    WATER      = (0.36, 0.55, 0.67)

    # Stone / architecture
    STONE      = (0.55, 0.49, 0.40)
    STONE_HLT  = (0.72, 0.67, 0.57)
    STONE_SHD  = (0.35, 0.30, 0.24)

    # Fabric
    DRESS_GRN  = (0.22, 0.27, 0.18)
    DRESS_BRN  = (0.38, 0.28, 0.18)
    VEIL_GRY   = (0.55, 0.51, 0.44)

    # Face features
    LIP_RED    = (0.63, 0.35, 0.30)
    LIP_MED    = (0.71, 0.43, 0.35)
    EYE_BRN    = (0.22, 0.18, 0.12)
    EYE_WHITE  = (0.90, 0.84, 0.77)
    BROW_BRN   = (0.24, 0.18, 0.10)

    # Neutral
    BLACK      = (0.0,  0.0,  0.0)
    WHITE      = (1.0,  1.0,  1.0)
    SHADOW     = (0.12, 0.10, 0.07)

    @staticmethod
    def lerp(c1: Color, c2: Color, t: float) -> Color:
        """Linear interpolate between two colours."""
        t = max(0.0, min(1.0, t))
        return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(3))

    @staticmethod
    def with_alpha(c: Color, a: float) -> ColorA:
        return (*c, a)

    @staticmethod
    def darken(c: Color, amount: float = 0.2) -> Color:
        return Palette.lerp(c, Palette.BLACK, amount)

    @staticmethod
    def lighten(c: Color, amount: float = 0.2) -> Color:
        return Palette.lerp(c, Palette.WHITE, amount)

    @staticmethod
    def from_hex(h: str) -> Color:
        """Parse '#RRGGBB' or 'RRGGBB'."""
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

    @staticmethod
    def harmony(base: Color, scheme: str = "complementary",
                value_spread: float = 0.0) -> List[Color]:
        """
        Generate a harmonious palette from a base colour using colour-wheel theory.

        Painters from Delacroix to Bonnard built their palettes on relationships
        between hues rather than picking colours independently.  This method
        applies the standard schemes from the colour wheel to a base hue,
        preserving saturation and value so the returned colours form a true
        family rather than an arbitrary collection.

        Parameters
        ----------
        base         : (R, G, B) base colour in [0, 1].
        scheme       : One of:
                         'complementary'       — base + hue opposite (2 colours)
                         'analogous'           — base ± 30° and ± 60° (5 colours)
                         'triadic'             — base, +120°, +240° (3 colours)
                         'split_complementary' — base, +150°, +210° (3 colours)
                         'tetradic'            — base, +90°, +180°, +270° (4 colours)
                         'double_split'        — base ± 30° + complement ± 30°
                                                 (4 colours; also called 'rectangle')
        value_spread : Optional value variation applied across the returned colours.
                       0.0 = all colours have identical value (V in HSV).
                       0.10 = each step shifts value by ±10%, spreading the palette
                       from slightly darker to slightly lighter around the base value.
                       Useful for ensuring the palette has tonal variety as well as
                       hue variety.

        Returns
        -------
        List of (R, G, B) colour tuples in [0, 1].  The base colour is always
        the first element.

        Examples
        --------
        >>> Palette.harmony((0.72, 0.28, 0.10), 'triadic')
        [(0.72, 0.28, 0.10), (0.10, 0.72, 0.28), (0.28, 0.10, 0.72)]

        >>> Palette.harmony((0.85, 0.65, 0.30), 'analogous')
        # 5 colours at 0°, ±30°, ±60° from the warm amber base
        """
        scheme = scheme.lower().replace("-", "_").replace(" ", "_")

        # Hue offsets (in [0, 1] fractions of the full hue circle) for each scheme
        _SCHEMES: dict = {
            "complementary":       [0.0, 0.5],
            "analogous":           [0.0, -1/12, 1/12, -1/6, 1/6],
            "triadic":             [0.0, 1/3, 2/3],
            "split_complementary": [0.0, 5/12, 7/12],
            "tetradic":            [0.0, 1/4, 1/2, 3/4],
            "double_split":        [0.0, -1/12, 1/12, 5/12, 7/12],
        }
        if scheme not in _SCHEMES:
            raise ValueError(
                f"Unknown harmony scheme {scheme!r}. "
                f"Available: {', '.join(sorted(_SCHEMES))}"
            )
        offsets = _SCHEMES[scheme]

        h_base, s_base, v_base = colorsys.rgb_to_hsv(*base)
        n = len(offsets)

        result = []
        for i, offset in enumerate(offsets):
            h_new = (h_base + offset) % 1.0
            # Value spread: spread values from slightly darker to slightly lighter
            # across the colour family, centred on the base value.
            if value_spread > 0.0 and n > 1:
                t = i / (n - 1)               # 0 at first, 1 at last colour
                v_delta = value_spread * (t - 0.5)
            else:
                v_delta = 0.0
            v_new = max(0.0, min(1.0, v_base + v_delta))
            result.append(colorsys.hsv_to_rgb(h_new, s_base, v_new))

        return result

    @staticmethod
    def gradient_stops(colors: List[Color], steps: int) -> List[Color]:
        """Expand a list of key colours into `steps` interpolated colours."""
        result = []
        segments = len(colors) - 1
        for i in range(steps):
            t_global = i / max(steps - 1, 1)
            seg = min(int(t_global * segments), segments - 1)
            t_local = t_global * segments - seg
            result.append(Palette.lerp(colors[seg], colors[seg + 1], t_local))
        return result


# ─────────────────────────────────────────────────────────────────────────────
# Lighting — simple diffuse + ambient shading
# ─────────────────────────────────────────────────────────────────────────────
class Lighting:
    """
    Directional light model.
    light_dir: normalised (x, y, z) pointing TOWARD the surface from the light.
    """

    def __init__(self,
                 light_dir: Tuple[float, float, float] = (-0.5, -0.8, 0.3),
                 ambient: float = 0.35,
                 diffuse: float = 0.65):
        mag = math.sqrt(sum(v**2 for v in light_dir))
        self.light = tuple(v / mag for v in light_dir)
        self.ambient = ambient
        self.diffuse = diffuse

    def shade(self, base: Color, normal: Tuple[float, float, float]) -> Color:
        """Return a shaded version of `base` given a surface normal."""
        mag = math.sqrt(sum(v**2 for v in normal))
        if mag == 0:
            return base
        n = tuple(v / mag for v in normal)
        # dot product of normal with negated light direction (light hitting surface)
        ndotl = max(0.0, sum(n[i] * (-self.light[i]) for i in range(3)))
        factor = self.ambient + self.diffuse * ndotl
        factor = min(factor, 1.0)
        return tuple(min(1.0, c * factor) for c in base)

    def shade_by_y(self, base: Color, y_norm: float,
                   top_factor: float = 1.1, bot_factor: float = 0.75) -> Color:
        """
        Simple top-lit shading: y_norm 0=top, 1=bottom.
        Great for faces, bodies, hills.
        """
        factor = top_factor + (bot_factor - top_factor) * y_norm
        return tuple(min(1.0, max(0.0, c * factor)) for c in base)


# ─────────────────────────────────────────────────────────────────────────────
# Composition — layout helpers
# ─────────────────────────────────────────────────────────────────────────────
class Composition:
    """Proportional layout helpers."""

    def __init__(self, width: int, height: int):
        self.w = width
        self.h = height

    def thirds(self) -> dict:
        """Return x/y positions of the rule-of-thirds grid."""
        return {
            'x1': self.w / 3, 'x2': 2 * self.w / 3,
            'y1': self.h / 3, 'y2': 2 * self.h / 3,
        }

    def golden(self) -> dict:
        """Golden ratio split points."""
        phi = (1 + math.sqrt(5)) / 2
        return {
            'x': self.w / phi,
            'y': self.h / phi,
        }

    def portrait_guides(self) -> dict:
        """Classic portrait proportions (face centered, hands at ~70% height)."""
        return {
            'horizon':    self.h * 0.38,
            'shoulder':   self.h * 0.58,
            'eye_line':   self.h * 0.40,
            'nose_line':  self.h * 0.52,
            'mouth_line': self.h * 0.59,
            'chin_line':  self.h * 0.66,
            'face_cx':    self.w * 0.50,
            'hands_y':    self.h * 0.72,
        }

    def px(self, norm_x: float) -> float:
        return norm_x * self.w

    def py(self, norm_y: float) -> float:
        return norm_y * self.h


# ─────────────────────────────────────────────────────────────────────────────
# Bezier helpers
# ─────────────────────────────────────────────────────────────────────────────
def cubic_bezier_points(p0: Point, p1: Point, p2: Point, p3: Point,
                        steps: int = 40) -> List[Point]:
    """Evaluate a cubic Bézier curve and return `steps` points."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u**3*p0[0] + 3*u**2*t*p1[0] + 3*u*t**2*p2[0] + t**3*p3[0]
        y = u**3*p0[1] + 3*u**2*t*p1[1] + 3*u*t**2*p2[1] + t**3*p3[1]
        pts.append((x, y))
    return pts


def smooth_path(points: List[Point], tension: float = 0.3) -> List[Point]:
    """
    Generate a smooth Catmull-Rom spline through the given points.
    Returns many interpolated points suitable for drawing.
    """
    if len(points) < 2:
        return points
    result = []
    n = len(points)
    for i in range(n - 1):
        p0 = points[max(i - 1, 0)]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[min(i + 2, n - 1)]
        for t_step in range(20):
            t = t_step / 20
            t2, t3 = t*t, t*t*t
            x = 0.5 * ((2*p1[0]) +
                        (-p0[0]+p2[0])*t +
                        (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 +
                        (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            y = 0.5 * ((2*p1[1]) +
                        (-p0[1]+p2[1])*t +
                        (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 +
                        (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            result.append((x, y))
    result.append(points[-1])
    return result


# ─────────────────────────────────────────────────────────────────────────────
# ArtCanvas — main drawing surface
# ─────────────────────────────────────────────────────────────────────────────
class ArtCanvas:
    """
    Wraps a pycairo ImageSurface with high-level drawing primitives.

    Coordinate system: pixels from top-left (same as PIL).
    All colors: (R, G, B) or (R, G, B, A) floats 0-1.
    """

    def __init__(self, width: int, height: int, bg: Optional[Color] = None):
        self.w = width
        self.h = height
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.ctx = cairo.Context(self.surface)
        # pycairo default is top-left origin, y increases downward — matches PIL
        self.ctx.set_antialias(cairo.ANTIALIAS_BEST)
        self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        self.ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        self.comp = Composition(width, height)
        if bg is not None:
            self.fill_background(bg)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _set_color(self, color: Union[Color, ColorA]):
        if len(color) == 4:
            self.ctx.set_source_rgba(*color)
        else:
            self.ctx.set_source_rgb(*color)

    def _apply(self, fill: Optional[Union[Color, ColorA]],
               stroke: Optional[Union[Color, ColorA]],
               stroke_width: float = 1.5):
        if fill is not None and stroke is not None:
            self._set_color(fill)
            self.ctx.fill_preserve()
            self._set_color(stroke)
            self.ctx.set_line_width(stroke_width)
            self.ctx.stroke()
        elif fill is not None:
            self._set_color(fill)
            self.ctx.fill()
        elif stroke is not None:
            self._set_color(stroke)
            self.ctx.set_line_width(stroke_width)
            self.ctx.stroke()
        else:
            self.ctx.new_path()

    # ── Background ────────────────────────────────────────────────────────────

    def fill_background(self, color: Color):
        self.ctx.rectangle(0, 0, self.w, self.h)
        self._set_color(color)
        self.ctx.fill()

    def gradient_background(self, top: Color, bottom: Color):
        """Vertical linear gradient background."""
        grad = cairo.LinearGradient(0, 0, 0, self.h)
        grad.add_color_stop_rgb(0, *top)
        grad.add_color_stop_rgb(1, *bottom)
        self.ctx.rectangle(0, 0, self.w, self.h)
        self.ctx.set_source(grad)
        self.ctx.fill()

    def gradient_rect(self, x: float, y: float, w: float, h: float,
                      top: Union[Color, ColorA], bottom: Union[Color, ColorA]):
        """Vertical gradient rectangle. Supports RGB or RGBA stops."""
        grad = cairo.LinearGradient(x, y, x, y + h)
        t = (*top, 1.0) if len(top) == 3 else top
        b = (*bottom, 1.0) if len(bottom) == 3 else bottom
        grad.add_color_stop_rgba(0, *t)
        grad.add_color_stop_rgba(1, *b)
        self.ctx.rectangle(x, y, w, h)
        self.ctx.set_source(grad)
        self.ctx.fill()

    # ── Basic shapes ──────────────────────────────────────────────────────────

    def rect(self, x: float, y: float, w: float, h: float,
             fill: Optional[Color] = None,
             stroke: Optional[Color] = None,
             stroke_width: float = 1.5,
             radius: float = 0):
        """Rectangle with optional rounded corners."""
        if radius > 0:
            self.ctx.arc(x + radius, y + radius, radius, math.pi, 3*math.pi/2)
            self.ctx.arc(x + w - radius, y + radius, radius, 3*math.pi/2, 0)
            self.ctx.arc(x + w - radius, y + h - radius, radius, 0, math.pi/2)
            self.ctx.arc(x + radius, y + h - radius, radius, math.pi/2, math.pi)
            self.ctx.close_path()
        else:
            self.ctx.rectangle(x, y, w, h)
        self._apply(fill, stroke, stroke_width)

    def ellipse(self, cx: float, cy: float, rx: float, ry: float,
                fill: Optional[Color] = None,
                stroke: Optional[Color] = None,
                stroke_width: float = 1.5,
                rotation: float = 0):
        """Axis-aligned (or rotated) ellipse."""
        self.ctx.save()
        self.ctx.translate(cx, cy)
        if rotation:
            self.ctx.rotate(rotation)
        self.ctx.scale(rx, ry)
        self.ctx.arc(0, 0, 1, 0, 2 * math.pi)
        self.ctx.restore()
        self._apply(fill, stroke, stroke_width)

    def circle(self, cx: float, cy: float, r: float,
               fill: Optional[Color] = None,
               stroke: Optional[Color] = None,
               stroke_width: float = 1.5):
        self.ellipse(cx, cy, r, r, fill=fill, stroke=stroke, stroke_width=stroke_width)

    def polygon(self, points: List[Point],
                fill: Optional[Color] = None,
                stroke: Optional[Color] = None,
                stroke_width: float = 1.5):
        if not points:
            return
        self.ctx.move_to(*points[0])
        for p in points[1:]:
            self.ctx.line_to(*p)
        self.ctx.close_path()
        self._apply(fill, stroke, stroke_width)

    def line(self, x1: float, y1: float, x2: float, y2: float,
             color: Color = (0, 0, 0),
             width: float = 1.5):
        self.ctx.move_to(x1, y1)
        self.ctx.line_to(x2, y2)
        self._set_color(color)
        self.ctx.set_line_width(width)
        self.ctx.stroke()

    # ── Curves ────────────────────────────────────────────────────────────────

    def smooth_curve(self, points: List[Point],
                     color: Color = (0, 0, 0),
                     width: float = 2.0,
                     fill: Optional[Color] = None,
                     closed: bool = False):
        """Draw a smooth Catmull-Rom spline through `points`."""
        smooth = smooth_path(points)
        if not smooth:
            return
        self.ctx.move_to(*smooth[0])
        for p in smooth[1:]:
            self.ctx.line_to(*p)
        if closed:
            self.ctx.close_path()
        if fill and closed:
            self._set_color(fill)
            self.ctx.fill_preserve()
        self._set_color(color)
        self.ctx.set_line_width(width)
        self.ctx.stroke()

    def bezier(self, p0: Point, p1: Point, p2: Point, p3: Point,
               color: Color = (0, 0, 0),
               width: float = 2.0):
        """Single cubic Bézier stroke."""
        self.ctx.move_to(*p0)
        self.ctx.curve_to(*p1, *p2, *p3)
        self._set_color(color)
        self.ctx.set_line_width(width)
        self.ctx.stroke()

    # ── Gradients ─────────────────────────────────────────────────────────────

    def radial_gradient(self, cx: float, cy: float, r: float,
                        inner: Color, outer: Color, alpha_outer: float = 0.0):
        """Soft spotlight / vignette effect."""
        grad = cairo.RadialGradient(cx, cy, 0, cx, cy, r)
        grad.add_color_stop_rgba(0, *inner, 1.0)
        grad.add_color_stop_rgba(1, *outer, alpha_outer)
        self.ctx.arc(cx, cy, r, 0, 2 * math.pi)
        self.ctx.set_source(grad)
        self.ctx.fill()

    def vignette(self, strength: float = 0.6):
        """Dark vignette around the canvas edges."""
        grad = cairo.RadialGradient(
            self.w/2, self.h/2, min(self.w, self.h) * 0.35,
            self.w/2, self.h/2, max(self.w, self.h) * 0.75,
        )
        grad.add_color_stop_rgba(0, 0, 0, 0, 0)
        grad.add_color_stop_rgba(1, 0, 0, 0, strength)
        self.ctx.rectangle(0, 0, self.w, self.h)
        self.ctx.set_source(grad)
        self.ctx.fill()

    # ── Shaded faces / ovals ─────────────────────────────────────────────────

    def shaded_ellipse(self, cx: float, cy: float, rx: float, ry: float,
                       base_color: Color,
                       light: Lighting,
                       highlight_offset: Tuple[float, float] = (-0.3, -0.5)):
        """
        Fill an ellipse with a radial gradient simulating spherical lighting.
        `highlight_offset` is (dx, dy) in normalised ellipse coords (-1 to 1).
        """
        # Highlight centre in canvas coords
        hx = cx + highlight_offset[0] * rx
        hy = cy + highlight_offset[1] * ry
        hl_color = Palette.lighten(base_color, 0.25)
        shd_color = Palette.darken(base_color, 0.35)

        grad = cairo.RadialGradient(hx, hy, 0, cx, cy, max(rx, ry) * 1.1)
        grad.add_color_stop_rgb(0, *hl_color)
        grad.add_color_stop_rgb(0.55, *base_color)
        grad.add_color_stop_rgb(1.0, *shd_color)

        self.ctx.save()
        self.ctx.translate(cx, cy)
        self.ctx.scale(rx, ry)
        self.ctx.arc(0, 0, 1, 0, 2 * math.pi)
        self.ctx.restore()
        self.ctx.set_source(grad)
        self.ctx.fill()

    # ── Text ──────────────────────────────────────────────────────────────────

    def text(self, x: float, y: float, content: str,
             color: Color = (0, 0, 0),
             size: float = 16,
             font: str = "Palatino",
             bold: bool = False,
             italic: bool = False,
             center: bool = False):
        self.ctx.select_font_face(
            font,
            cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_BOLD  if bold   else cairo.FONT_WEIGHT_NORMAL,
        )
        self.ctx.set_font_size(size)
        if center:
            ext = self.ctx.text_extents(content)
            x -= ext.width / 2
        self._set_color(color)
        self.ctx.move_to(x, y)
        self.ctx.show_text(content)

    # ── Layers / compositing ──────────────────────────────────────────────────

    def push_layer(self, alpha: float = 1.0):
        """Start a new compositing group (like a Photoshop layer)."""
        self.ctx.push_group()

    def pop_layer(self, alpha: float = 1.0,
                  blend: cairo.Operator = cairo.OPERATOR_OVER):
        """Merge the current group onto the canvas."""
        self.ctx.pop_group_to_source()
        self.ctx.set_operator(blend)
        self.ctx.paint_with_alpha(alpha)
        self.ctx.set_operator(cairo.OPERATOR_OVER)

    def save_state(self):
        self.ctx.save()

    def restore_state(self):
        self.ctx.restore()

    def clip_ellipse(self, cx: float, cy: float, rx: float, ry: float):
        """Set an elliptical clip region."""
        self.ctx.save()
        self.ctx.translate(cx, cy)
        self.ctx.scale(rx, ry)
        self.ctx.arc(0, 0, 1, 0, 2 * math.pi)
        self.ctx.restore()
        self.ctx.clip()

    def reset_clip(self):
        self.ctx.reset_clip()

    # ── Output ────────────────────────────────────────────────────────────────

    def save(self, path: str):
        """Save as PNG (from ImageSurface)."""
        self.surface.write_to_png(path)
        print(f"Saved: {path}")

    def to_pil(self):
        """Convert to a PIL Image for further processing."""
        from PIL import Image
        buf = io.BytesIO()
        self.surface.write_to_png(buf)
        buf.seek(0)
        return Image.open(buf).convert("RGBA")


# ─────────────────────────────────────────────────────────────────────────────
# Inkscape integration
# ─────────────────────────────────────────────────────────────────────────────

def render_svg(svg_path: str, png_path: str, dpi: int = 96) -> bool:
    """Use Inkscape CLI to render an SVG to PNG."""
    result = subprocess.run(
        [INKSCAPE, svg_path, f"--export-filename={png_path}", f"--export-dpi={dpi}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Inkscape error:", result.stderr)
        return False
    return True


def open_in_inkscape(path: str, wait: bool = False):
    """Open a file in the Inkscape GUI."""
    proc = subprocess.Popen([INKSCAPE, path])
    if wait:
        proc.wait()
    return proc


def open_in_paint(path: str):
    """Open a file in MS Paint."""
    subprocess.Popen(["mspaint", path])


# ─────────────────────────────────────────────────────────────────────────────
# Subject mask + direction field builders
# ─────────────────────────────────────────────────────────────────────────────

def build_subject_mask(
    reference: "np.ndarray",
    method: str = "luminance_threshold",
    threshold: float = 0.35,
    sigma: float = 2.0,
    center: Optional[Tuple[float, float]] = None,
    radius_frac: float = 0.45,
) -> "np.ndarray":
    """
    Build a binary subject mask (H×W float32 in [0,1]) from a synthetic reference.

    Parameters
    ----------
    reference    : H×W×3 float32 numpy array in [0, 1]
    method       : 'convex_region'       — soft ellipse centred on center/radius_frac
                   'luminance_threshold' — pixels whose smoothed luma > threshold
                   'gradient_watershed'  — largest connected bright region
    threshold    : luma cutoff for threshold and watershed methods
    sigma        : Gaussian pre-blur sigma (also softens final mask edges)
    center       : (row_frac, col_frac) fractional centre for convex_region
    radius_frac  : fraction of min(H,W) for convex_region radius

    Returns H×W float32 in [0,1].
    """
    import numpy as np
    from scipy.ndimage import gaussian_filter, label

    ref = np.asarray(reference, dtype=np.float32)
    H, W = ref.shape[:2]

    if method == "convex_region":
        cy, cx = center or (0.5, 0.5)
        r = min(H, W) * radius_frac
        ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
        dist = np.sqrt(((ys - cy * H) / (r + 1e-6)) ** 2 +
                       ((xs - cx * W) / (r + 1e-6)) ** 2)
        mask = np.clip(1.0 - dist, 0.0, 1.0).astype(np.float32)

    elif method == "luminance_threshold":
        luma   = 0.2126 * ref[:, :, 0] + 0.7152 * ref[:, :, 1] + 0.0722 * ref[:, :, 2]
        luma_s = gaussian_filter(luma, sigma=sigma)
        mask   = (luma_s > threshold).astype(np.float32)

    elif method == "gradient_watershed":
        luma    = 0.2126 * ref[:, :, 0] + 0.7152 * ref[:, :, 1] + 0.0722 * ref[:, :, 2]
        luma_s  = gaussian_filter(luma, sigma=sigma)
        labeled, n = label(luma_s > threshold)
        if n == 0:
            mask = np.zeros((H, W), dtype=np.float32)
        else:
            sizes    = [(labeled == i).sum() for i in range(1, n + 1)]
            dominant = int(np.argmax(sizes)) + 1
            mask     = (labeled == dominant).astype(np.float32)

    else:
        raise ValueError(
            f"Unknown subject mask method {method!r}. "
            "Available: 'convex_region', 'luminance_threshold', 'gradient_watershed'"
        )

    if sigma > 0.0:
        mask = gaussian_filter(mask, sigma=sigma * 0.5)

    return np.clip(mask, 0.0, 1.0).astype(np.float32)


def build_direction_field(
    reference: "np.ndarray",
    sigma: float = 3.0,
) -> "np.ndarray":
    """
    Build a direction field (H×W×2 float32) from a synthetic reference array.

    Each pixel holds a unit vector [dy, dx] tangent to the local luminance
    gradient — the direction a brush would follow to paint *along* the form
    rather than across it.

    Returns H×W×2 float32 with component values in [-1, 1].
    """
    import numpy as np
    from scipy.ndimage import gaussian_filter

    ref    = np.asarray(reference, dtype=np.float32)
    luma   = 0.2126 * ref[:, :, 0] + 0.7152 * ref[:, :, 1] + 0.0722 * ref[:, :, 2]
    luma_s = gaussian_filter(luma, sigma=sigma)

    gy, gx = np.gradient(luma_s)
    # Tangent direction = rotate gradient 90° (perpendicular to isophotes)
    ty, tx = -gx, gy
    mag    = np.sqrt(ty ** 2 + tx ** 2) + 1e-8
    ty    /= mag
    tx    /= mag

    return np.stack([ty, tx], axis=-1).astype(np.float32)


def show(canvas: ArtCanvas, viewer: str = "inkscape"):
    """
    Save the canvas to a temp PNG and open it.
    viewer: 'inkscape' | 'paint'
    """
    import tempfile
    tmp = tempfile.mktemp(suffix=".png", prefix="art_")
    canvas.save(tmp)
    if viewer == "inkscape":
        open_in_inkscape(tmp)
    else:
        open_in_paint(tmp)
    return tmp
