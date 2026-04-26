"""
mark_makers.py — Brush motion primitive registry.

Each MarkMaker models a distinct physical brush motion. Uses Pillow (PIL) for
all drawing so no OpenCV dependency is required.

Primitives
----------
StrokeMaker      — directional pulled stroke (foundational)
DabMaker         — loaded-brush touch / impasto dot
DryBrushMaker    — split-bristle under-loaded drag
PaletteKnifeMaker — flat hard-edged scrape
ScrumbleMaker    — broken semi-opaque glaze field
HatchMaker       — parallel / cross-hatch engraving lines
FanMaker         — splayed fan-brush for foliage and hair
"""
from __future__ import annotations

import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw


# ─────────────────────────────────────────────────────────────────────────────
# Shared parameters
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class MarkParams:
    """Shared parameters for all mark makers."""
    width:   float = 8.0    # brush width in pixels
    opacity: float = 0.70
    jitter:  float = 0.05   # position noise fraction [0, 1]
    seed:    int   = 0


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _bgra_to_pil(arr: np.ndarray) -> Image.Image:
    """Convert H×W×4 BGRA uint8 array to PIL RGBA Image."""
    rgba = arr[:, :, [2, 1, 0, 3]]
    return Image.fromarray(rgba, mode="RGBA")


def _pil_to_bgra(img: Image.Image) -> np.ndarray:
    """Convert PIL RGBA Image to H×W×4 BGRA uint8 array."""
    rgba = np.array(img, dtype=np.uint8)
    bgra = rgba[:, :, [2, 1, 0, 3]]
    return bgra


def _color_rgba(color: Tuple[float, float, float], opacity: float) -> Tuple[int, int, int, int]:
    """Convert (r, g, b) float [0,1] + opacity to RGBA uint8 tuple."""
    r, g, b = (int(c * 255) for c in color)
    a = int(opacity * 255)
    return (r, g, b, a)


# ─────────────────────────────────────────────────────────────────────────────
# Abstract base
# ─────────────────────────────────────────────────────────────────────────────

class MarkMaker(ABC):
    """Abstract base for all brush motion primitives."""

    def __init__(self, params: Optional[MarkParams] = None):
        self.params = params or MarkParams()

    @abstractmethod
    def mark(
        self,
        canvas_array: np.ndarray,
        color: Tuple[float, float, float],
        position: Tuple[float, float],
        direction: float = 0.0,
        **kwargs,
    ) -> np.ndarray:
        """Apply one mark to canvas_array; return modified H×W×4 BGRA uint8 array."""
        ...

    def _rng(self) -> random.Random:
        return random.Random(self.params.seed)

    def _draw_on_canvas(self, canvas_array: np.ndarray,
                         draw_fn) -> np.ndarray:
        """Convert to PIL, apply draw_fn(draw, img), return BGRA array."""
        img = _bgra_to_pil(canvas_array)
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw_fn(draw, overlay)
        composite = Image.alpha_composite(img, overlay)
        return _pil_to_bgra(composite)


# ─────────────────────────────────────────────────────────────────────────────
# StrokeMaker — directional pulled stroke
# ─────────────────────────────────────────────────────────────────────────────

class StrokeMaker(MarkMaker):
    """
    Classic pulled brush stroke: an oriented ellipse smeared along a direction.
    The foundational motion — dragging a loaded brush across canvas.
    """

    def __init__(self, params: Optional[MarkParams] = None, length_factor: float = 4.0):
        super().__init__(params)
        self.length_factor = length_factor

    def mark(
        self,
        canvas_array: np.ndarray,
        color: Tuple[float, float, float],
        position: Tuple[float, float],
        direction: float = 0.0,
        **kwargs,
    ) -> np.ndarray:
        cx, cy = float(position[0]), float(position[1])
        w = max(1.0, self.params.width)
        L = max(1.0, w * self.length_factor)
        fill = _color_rgba(color, self.params.opacity)
        angle_deg = math.degrees(direction)

        def draw_fn(draw, img):
            # Draw an unrotated ellipse on a temp layer, then rotate
            ell = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ed  = ImageDraw.Draw(ell)
            ex0 = cx - L / 2
            ey0 = cy - w / 2
            ex1 = cx + L / 2
            ey1 = cy + w / 2
            ed.ellipse([ex0, ey0, ex1, ey1], fill=fill)
            rotated = ell.rotate(-angle_deg, center=(cx, cy), resample=Image.BILINEAR)
            img.paste(rotated, mask=rotated)

        return self._draw_on_canvas(canvas_array, draw_fn)


# ─────────────────────────────────────────────────────────────────────────────
# DabMaker — loaded-brush dab / touch
# ─────────────────────────────────────────────────────────────────────────────

class DabMaker(MarkMaker):
    """
    Single bristle-load deposit. A round or slightly oval spot — like touching
    a fully-loaded brush to the surface without dragging. Used for impasto
    highlights and Pointillist dots.
    """

    def __init__(self, params: Optional[MarkParams] = None, aspect: float = 1.0):
        super().__init__(params)
        self.aspect = aspect

    def mark(
        self,
        canvas_array: np.ndarray,
        color: Tuple[float, float, float],
        position: Tuple[float, float],
        direction: float = 0.0,
        **kwargs,
    ) -> np.ndarray:
        cx, cy = float(position[0]), float(position[1])
        rx = max(1.0, self.params.width / 2)
        ry = max(1.0, rx * self.aspect)
        fill = _color_rgba(color, self.params.opacity)

        def draw_fn(draw, img):
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill)

        return self._draw_on_canvas(canvas_array, draw_fn)


# ─────────────────────────────────────────────────────────────────────────────
# DryBrushMaker — split-bristle dry-drag
# ─────────────────────────────────────────────────────────────────────────────

class DryBrushMaker(MarkMaker):
    """
    Under-loaded brush dragged fast: paint deposits on texture peaks leaving
    gaps. Multiple thin parallel strokes with random gaps.
    Used for hair, fur underlayers, aged/weathered surfaces.
    """

    def __init__(self, params: Optional[MarkParams] = None,
                 bristle_count: int = 12, coverage: float = 0.55):
        super().__init__(params)
        self.bristle_count = bristle_count
        self.coverage = coverage

    def mark(
        self,
        canvas_array: np.ndarray,
        color: Tuple[float, float, float],
        position: Tuple[float, float],
        direction: float = 0.0,
        **kwargs,
    ) -> np.ndarray:
        cx, cy = float(position[0]), float(position[1])
        w = self.params.width
        L = w * 4.0
        rng = self._rng()
        cos_d, sin_d = math.cos(direction), math.sin(direction)
        perp = (-sin_d, cos_d)

        lines = []
        alphas = []
        for i in range(self.bristle_count):
            if rng.random() > self.coverage:
                continue
            offset = (i / self.bristle_count - 0.5) * w
            bx = cx + perp[0] * offset
            by = cy + perp[1] * offset
            x1 = bx - cos_d * L / 2
            y1 = by - sin_d * L / 2
            x2 = bx + cos_d * L / 2
            y2 = by + sin_d * L / 2
            lines.append(((x1, y1), (x2, y2)))
            alphas.append(rng.uniform(0.4, 1.0))

        def draw_fn(draw, img):
            for (pt1, pt2), alpha in zip(lines, alphas):
                fill = _color_rgba(color, self.params.opacity * alpha)
                draw.line([pt1, pt2], fill=fill, width=1)

        return self._draw_on_canvas(canvas_array, draw_fn)


# ─────────────────────────────────────────────────────────────────────────────
# PaletteKnifeMaker — flat-scrape knife stroke
# ─────────────────────────────────────────────────────────────────────────────

class PaletteKnifeMaker(MarkMaker):
    """
    Palette knife: a wide, thin, hard-edged flat deposit. Creates impasto
    texture with straight, sharp edges — characteristic of Richter, de Stael,
    Turner's sky passages. Modelled as a filled rotated quadrilateral.
    """

    def __init__(self, params: Optional[MarkParams] = None,
                 length_factor: float = 5.0, taper: float = 0.85):
        super().__init__(params)
        self.length_factor = length_factor
        self.taper = taper

    def mark(
        self,
        canvas_array: np.ndarray,
        color: Tuple[float, float, float],
        position: Tuple[float, float],
        direction: float = 0.0,
        **kwargs,
    ) -> np.ndarray:
        cx, cy = float(position[0]), float(position[1])
        w = self.params.width
        L = w * self.length_factor
        fill = _color_rgba(color, self.params.opacity)
        cos_d, sin_d = math.cos(direction), math.sin(direction)
        perp = (-sin_d, cos_d)
        hw, hL = w / 2, L / 2
        t = self.taper

        corners = [
            (cx - cos_d * hL - perp[0] * hw,      cy - sin_d * hL - perp[1] * hw),
            (cx + cos_d * hL - perp[0] * hw * t,  cy + sin_d * hL - perp[1] * hw * t),
            (cx + cos_d * hL + perp[0] * hw * t,  cy + sin_d * hL + perp[1] * hw * t),
            (cx - cos_d * hL + perp[0] * hw,      cy - sin_d * hL + perp[1] * hw),
        ]

        def draw_fn(draw, img):
            draw.polygon(corners, fill=fill)

        return self._draw_on_canvas(canvas_array, draw_fn)


# ─────────────────────────────────────────────────────────────────────────────
# ScrumbleMaker — scumbled semi-transparent glaze field
# ─────────────────────────────────────────────────────────────────────────────

class ScrumbleMaker(MarkMaker):
    """
    Scumbling: a broken, semi-opaque layer of lighter paint over darker —
    a field of small random dabs at reduced opacity.
    Used for atmospheric haze and glowing light passages.
    """

    def __init__(self, params: Optional[MarkParams] = None,
                 dab_count: int = 40, size_spread: float = 0.5):
        super().__init__(params)
        self.dab_count = dab_count
        self.size_spread = size_spread

    def mark(
        self,
        canvas_array: np.ndarray,
        color: Tuple[float, float, float],
        position: Tuple[float, float],
        direction: float = 0.0,
        **kwargs,
    ) -> np.ndarray:
        cx, cy = float(position[0]), float(position[1])
        w = self.params.width
        rng = self._rng()

        dabs = []
        for _ in range(self.dab_count):
            jx = rng.uniform(-w, w)
            jy = rng.uniform(-w, w)
            r = max(1.0, w * rng.uniform(1.0 - self.size_spread, 1.0 + self.size_spread) / 2)
            alpha = self.params.opacity * rng.uniform(0.2, 0.6)
            dabs.append((cx + jx, cy + jy, r, alpha))

        def draw_fn(draw, img):
            for (dx, dy, r, alpha) in dabs:
                fill = _color_rgba(color, alpha)
                draw.ellipse([dx - r, dy - r, dx + r, dy + r], fill=fill)

        return self._draw_on_canvas(canvas_array, draw_fn)


# ─────────────────────────────────────────────────────────────────────────────
# HatchMaker — parallel / cross-hatch lines
# ─────────────────────────────────────────────────────────────────────────────

class HatchMaker(MarkMaker):
    """
    Parallel hatch lines — the mark of pen-and-ink, engraving, and old-master
    chalk drawings. cross_hatch=True adds a second layer at 45° for tonal depth.
    """

    def __init__(self, params: Optional[MarkParams] = None,
                 line_count: int = 8, line_spacing: float = 1.2,
                 cross_hatch: bool = False):
        super().__init__(params)
        self.line_count = line_count
        self.line_spacing = line_spacing
        self.cross_hatch = cross_hatch

    def _build_lines(self, cx: float, cy: float,
                     direction: float) -> list:
        w = self.params.width
        L = w * 3.0
        cos_d, sin_d = math.cos(direction), math.sin(direction)
        perp = (-sin_d, cos_d)
        spacing = w / max(1, self.line_count) * self.line_spacing
        lines = []
        for i in range(self.line_count):
            offset = (i - self.line_count / 2.0) * spacing
            lx = cx + perp[0] * offset
            ly = cy + perp[1] * offset
            lines.append((
                (lx - cos_d * L / 2, ly - sin_d * L / 2),
                (lx + cos_d * L / 2, ly + sin_d * L / 2),
            ))
        return lines

    def mark(
        self,
        canvas_array: np.ndarray,
        color: Tuple[float, float, float],
        position: Tuple[float, float],
        direction: float = 0.0,
        **kwargs,
    ) -> np.ndarray:
        cx, cy = float(position[0]), float(position[1])
        fill = _color_rgba(color, self.params.opacity)
        lines = self._build_lines(cx, cy, direction)
        if self.cross_hatch:
            lines += self._build_lines(cx, cy, direction + math.pi / 4)

        def draw_fn(draw, img):
            for (pt1, pt2) in lines:
                draw.line([pt1, pt2], fill=fill, width=1)

        return self._draw_on_canvas(canvas_array, draw_fn)


# ─────────────────────────────────────────────────────────────────────────────
# FanMaker — fan-brush spread for foliage and hair
# ─────────────────────────────────────────────────────────────────────────────

class FanMaker(MarkMaker):
    """
    Fan brush: splayed bristles making a fan-shaped radiating stroke.
    The mark of foliage, tall grass, hair highlights, and water ripples.
    """

    def __init__(self, params: Optional[MarkParams] = None,
                 bristle_count: int = 20,
                 fan_angle: float = math.pi / 3,
                 length_factor: float = 3.5):
        super().__init__(params)
        self.bristle_count = bristle_count
        self.fan_angle = fan_angle
        self.length_factor = length_factor

    def mark(
        self,
        canvas_array: np.ndarray,
        color: Tuple[float, float, float],
        position: Tuple[float, float],
        direction: float = 0.0,
        **kwargs,
    ) -> np.ndarray:
        cx, cy = float(position[0]), float(position[1])
        L = self.params.width * self.length_factor
        rng = self._rng()

        bristles = []
        for i in range(self.bristle_count):
            t = i / max(1, self.bristle_count - 1) - 0.5
            angle = direction + t * self.fan_angle
            bl = L * rng.uniform(0.7, 1.0)
            alpha = self.params.opacity * rng.uniform(0.5, 1.0)
            x2 = cx + math.cos(angle) * bl
            y2 = cy + math.sin(angle) * bl
            bristles.append(((cx, cy), (x2, y2), alpha))

        def draw_fn(draw, img):
            for (pt1, pt2, alpha) in bristles:
                fill = _color_rgba(color, alpha)
                draw.line([pt1, pt2], fill=fill, width=1)

        return self._draw_on_canvas(canvas_array, draw_fn)


# ─────────────────────────────────────────────────────────────────────────────
# Registry
# ─────────────────────────────────────────────────────────────────────────────

_MARK_MAKERS = {
    "stroke":        StrokeMaker,
    "dab":           DabMaker,
    "dry_brush":     DryBrushMaker,
    "palette_knife": PaletteKnifeMaker,
    "scumble":       ScrumbleMaker,
    "hatch":         HatchMaker,
    "fan":           FanMaker,
}


def get_mark_maker(name: str, params: Optional[MarkParams] = None,
                   **kwargs) -> MarkMaker:
    """
    Instantiate a MarkMaker by name.

    Parameters
    ----------
    name   : 'stroke' | 'dab' | 'dry_brush' | 'palette_knife' | 'scumble' | 'hatch' | 'fan'
    params : shared MarkParams; uses defaults if not provided
    kwargs : extra keyword arguments forwarded to the MarkMaker subclass __init__
    """
    if name not in _MARK_MAKERS:
        raise ValueError(
            f"Unknown mark maker {name!r}. Available: {sorted(_MARK_MAKERS)}"
        )
    return _MARK_MAKERS[name](params=params, **kwargs)
