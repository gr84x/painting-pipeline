"""
paint_mona_lisa_s111.py -- Session 111 portrait painting.

Warm-start from mona_lisa_s101.png (the latest available base canvas),
then applies sessions 102–111 additions cumulatively.

Session 111 additions:
  - orazio_gentileschi                       -- NEW (session 111)
                                               Orazio Gentileschi
                                               (1563–1639), Italian
                                               Baroque / Caravaggesque /
                                               Courtly Naturalism.
                                               Born in Pisa, trained in
                                               Florence and Rome.  Court
                                               painter to Charles I of
                                               England (1626–1639).
                                               His defining quality:
                                               cool silver north-window
                                               daylight replacing
                                               tenebrism's dramatic
                                               obscurity with clear,
                                               aristocratic, even light.
                                               His highlight flesh tones
                                               are cool silver-grey —
                                               lead white with a trace
                                               of smalt — rather than
                                               the warm ivory of
                                               Raphael or the gold of
                                               Rembrandt.  His fabrics
                                               (gold satin, red damask,
                                               blue silk) are observed
                                               with chromatic precision
                                               that maintains hue
                                               identity from highlight
                                               to shadow.

  SESSION 111 ARTISTIC IMPROVEMENT -- orazio_silver_daylight_pass:

                                               New pass encoding three
                                               defining Orazio qualities:
                                               (1) Silver highlight
                                               coolness — in the upper
                                               highlight zone
                                               (lum > hi_lo ≈ 0.68),
                                               applies a cool shift
                                               (R - silver_r_damp,
                                               B + silver_b_lift) that
                                               renders Orazio's
                                               characteristic cool
                                               north-window daylight
                                               at peak flesh highlights;
                                               (2) Midtone chroma lift —
                                               in the mid-tone band,
                                               applies a gentle
                                               saturation boost away
                                               from grey, encoding
                                               Orazio's chromatic
                                               fabric precision and
                                               the vivid colour identity
                                               of his satin and damask;
                                               (3) Cool shadow control —
                                               in shadow zones, reduces
                                               accumulated warm-amber
                                               deposits (from Guercino,
                                               Ribera, Strozzi passes)
                                               with a gentle R damp and
                                               B lift toward Orazio's
                                               cool atmospheric shadow
                                               quality.

Warm-start base: mona_lisa_s101.png
Applies: s102 (Tissot), s103 (Dolci), s104 (Giordano), s105 (Guercino),
         s106 (Ribera + foreground_warmth), s107 (Boltraffio pearled sfumato),
         s108 (Moroni silver presence), s109 (Strozzi amber impasto),
         s110 (Sassoferrato pure devotion),
         s111 (Orazio Gentileschi silver daylight -- NEW)
"""

import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image, ImageFilter
from stroke_engine import Painter
from scipy.ndimage import gaussian_filter

W, H = 780, 1080

# ── Locate warm-start base ────────────────────────────────────────────────────
S101_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s101.png"),
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "mona_lisa_s101.png"
    ),
    "/c/Source/painting-pipeline/mona_lisa_s101.png",
    "C:/Source/painting-pipeline/mona_lisa_s101.png",
]

base_path = None
for c in S101_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find mona_lisa_s101.png. Searched:\n" +
        "\n".join(f"  {c}" for c in S101_CANDIDATES)
    )

print(f"Loading session-101 base: {base_path}", flush=True)


# ── Utilities ─────────────────────────────────────────────────────────────────

def make_figure_mask() -> np.ndarray:
    """Elliptical figure mask for the standard Mona Lisa composition."""
    mask = np.zeros((H, W), dtype=np.float32)
    cx   = 0.515 * W
    cy   = 0.50  * H
    rx   = 0.26  * W
    ry   = 0.50  * H
    ys, xs = np.ogrid[:H, :W]
    d2 = ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2
    mask[d2 <= 1.0] = 1.0
    mask = gaussian_filter(mask, sigma=18.0)
    mask = np.clip(mask / mask.max(), 0.0, 1.0)
    return mask


def make_reference() -> Image.Image:
    """
    Rebuild the synthetic reference for sfumato_veil_pass.

    Matches the composition established in all prior sessions:
    - Cool blue-grey sky / upper landscape above horizon
    - Warm earth tones below horizon
    - Winding path left, rocky formations upper-right
    - Dark blue-green dress figure, warm ivory flesh
    - Uncanny horizon mismatch: left 8px higher than right (Leonardo's device)
    """
    ref = Image.new("RGB", (W, H), (110, 100, 72))
    px  = ref.load()

    def horizon_y(x: int) -> int:
        """Slight left-right horizon tilt: left side is 8 px higher."""
        return int(0.54 * H - 8 * (x / W - 0.5))

    # Background landscape
    for y in range(H):
        for x in range(W):
            hy = horizon_y(x)
            if y < hy:
                t = (hy - y) / max(hy, 1)
                r = int(130 + 60 * t)
                g = int(140 + 50 * t)
                b = int(155 + 60 * t)
            else:
                t = (y - hy) / max(H - hy, 1)
                r = int(120 - 30 * t)
                g = int(110 - 25 * t)
                b = int(80  - 20 * t)
            px[x, y] = (
                min(255, max(0, r)),
                min(255, max(0, g)),
                min(255, max(0, b)),
            )

    # Winding path on the left side
    for y in range(int(0.52 * H), H):
        t  = (y - 0.52 * H) / (H * 0.48)
        cx = int(0.18 * W + 0.10 * W * t)
        hw = max(2, int(6 * (1 - t * 0.6)))
        for dx in range(-hw, hw + 1):
            xx = cx + dx
            if 0 <= xx < W:
                r, g, b = px[xx, y]
                px[xx, y] = (min(255, r + 18), min(255, g + 14), min(255, b + 8))

    # Rocky formation upper-right
    for y in range(int(0.30 * H), int(0.58 * H)):
        for x in range(int(0.62 * W), W):
            dx = (x - 0.62 * W) / (0.38 * W)
            dy = abs(y / H - 0.44)
            if dx * 0.7 + dy * 0.3 < 0.35:
                r, g, b = px[x, y]
                px[x, y] = (min(255, r - 12), min(255, g - 10), min(255, b - 6))

    # Figure -- dark blue-green dress
    def in_torso(x, y):
        cx_t = 0.515 * W
        top  = 0.38 * H
        bot  = H
        rx_t = 0.16 * W
        rx_b = 0.22 * W
        if y < top or y > bot:
            return False
        t  = (y - top) / (bot - top)
        rx = rx_t + (rx_b - rx_t) * t
        return abs(x - cx_t) <= rx

    for y in range(H):
        for x in range(W):
            if in_torso(x, y):
                px[x, y] = (28, 52, 45)

    # Neckline amber trim
    neck_y = int(0.40 * H)
    for y in range(neck_y - 4, neck_y + 4):
        for x in range(int(0.36 * W), int(0.66 * W)):
            if in_torso(x, y):
                px[x, y] = (180, 145, 72)

    face_cx = int(0.515 * W)
    face_cy = int(0.215 * H)
    face_rx = int(0.105 * W)
    face_ry = int(0.155 * H)

    def paint_skin_ellipse(cx, cy, rx, ry, lit_dir=(0.35, -0.70)):
        for y in range(max(0, cy - ry - 2), min(H, cy + ry + 2)):
            for x in range(max(0, cx - rx - 2), min(W, cx + rx + 2)):
                nx = (x - cx) / rx
                ny = (y - cy) / ry
                d  = math.sqrt(nx * nx + ny * ny)
                if d > 1.0:
                    continue
                dot   = nx * lit_dir[0] + ny * lit_dir[1]
                light = 0.55 + 0.45 * max(dot, 0.0)
                r = int(215 * light)
                g = int(175 * light)
                b = int(130 * light)
                alpha   = min(1.0, (1.0 - d) * 4.0)
                old_r, old_g, old_b = px[x, y]
                px[x, y] = (
                    min(255, max(0, int(old_r * (1 - alpha) + r * alpha))),
                    min(255, max(0, int(old_g * (1 - alpha) + g * alpha))),
                    min(255, max(0, int(old_b * (1 - alpha) + b * alpha))),
                )

    paint_skin_ellipse(face_cx, face_cy, face_rx, face_ry)
    # Neck
    paint_skin_ellipse(
        int(0.515 * W), int(0.355 * H),
        int(0.058 * W), int(0.085 * H),
        lit_dir=(0.30, -0.60),
    )
    # Hands
    paint_skin_ellipse(
        int(0.47 * W), int(0.82 * H),
        int(0.055 * W), int(0.040 * H),
        lit_dir=(0.25, -0.50),
    )
    paint_skin_ellipse(
        int(0.54 * W), int(0.82 * H),
        int(0.050 * W), int(0.038 * H),
        lit_dir=(0.25, -0.50),
    )

    # Dark translucent veil over crown
    for y in range(int(0.08 * H), int(0.20 * H)):
        for x in range(int(0.38 * W), int(0.65 * W)):
            nx = (x - 0.515 * W) / (0.14 * W)
            ny = (y - 0.14 * H) / (0.06 * H)
            if nx * nx + ny * ny < 1.0:
                r, g, b = px[x, y]
                px[x, y] = (
                    max(0, int(r * 0.72)),
                    max(0, int(g * 0.70)),
                    max(0, int(b * 0.68)),
                )

    return ref.filter(ImageFilter.GaussianBlur(radius=3))


def load_png_into_painter(p: Painter, path: str) -> None:
    """Load a PNG file into a Painter canvas (BGRA Cairo format)."""
    img = Image.open(path).convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    rgb  = np.array(img, dtype=np.uint8)
    bgra = np.zeros((H, W, 4), dtype=np.uint8)
    bgra[:, :, 0] = rgb[:, :, 2]   # B
    bgra[:, :, 1] = rgb[:, :, 1]   # G
    bgra[:, :, 2] = rgb[:, :, 0]   # R
    bgra[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = bgra.tobytes()


# ── Main paint function ───────────────────────────────────────────────────────

def paint(out_dir: str = ".") -> str:
    """
    Apply sessions 102–111 passes on top of the session-101 base canvas.

    Returns the output PNG path.
    """
    print("=" * 68, flush=True)
    print("Session 111 warm-start from mona_lisa_s101.png", flush=True)
    print("Applying: Tissot(102) + Dolci(103) + Giordano(104) +", flush=True)
    print("          Guercino(105) + Ribera(106) + Boltraffio(107) +", flush=True)
    print("          Moroni silver presence (108) +", flush=True)
    print("          Strozzi amber impasto (109) +", flush=True)
    print("          Sassoferrato pure devotion (110) +", flush=True)
    print("          Orazio Gentileschi silver daylight (111 -- NEW)", flush=True)
    print("=" * 68, flush=True)
    print(flush=True)

    # Load session-101 base canvas
    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # Rebuild reference for passes that need it
    ref = make_reference()

    # ── Session 102: James Tissot fashionable gloss pass ─────────────────────
    print("Tissot fashionable gloss pass (session 102)...", flush=True)
    p.tissot_fashionable_gloss_pass(
        clarity_str    = 0.11,
        sheen_thresh   = 0.72,
        sheen_strength = 0.07,
        chroma_boost   = 0.06,
        mid_lo         = 0.28,
        mid_hi         = 0.72,
        highlight_cool = 0.04,
        blur_radius    = 4.0,
        opacity        = 0.27,
    )

    # ── Session 103: Carlo Dolci Florentine enamel pass ───────────────────────
    print("Dolci Florentine enamel pass (session 103)...", flush=True)
    p.dolci_florentine_enamel_pass(
        smooth_sigma      = 2.8,
        smooth_strength   = 0.55,
        flesh_lo          = 0.38,
        flesh_hi          = 0.84,
        shadow_lo         = 0.05,
        shadow_hi         = 0.32,
        shadow_depth_str  = 0.08,
        shadow_warm_r     = 0.040,
        shadow_warm_g     = 0.012,
        highlight_lo      = 0.80,
        highlight_lift    = 0.05,
        highlight_ivory_r = 0.018,
        highlight_ivory_g = 0.010,
        penumbra_lo       = 0.30,
        penumbra_hi       = 0.55,
        penumbra_amber_r  = 0.022,
        penumbra_amber_g  = 0.008,
        penumbra_amber_b  = 0.012,
        blur_radius       = 4.0,
        opacity           = 0.30,
    )

    # Session 103 IMPROVED: subsurface_scatter_pass with penumbra_warmth_depth
    print("Subsurface scatter pass (s92 improved, s103 penumbra_warmth_depth=0.07)...", flush=True)
    p.subsurface_scatter_pass(
        scatter_strength      = 0.14,
        scatter_radius        = 8.0,
        scatter_low           = 0.42,
        scatter_high          = 0.82,
        penumbra_warm         = 0.06,
        shadow_cool           = 0.04,
        shadow_pellucidity    = 0.05,
        penumbra_warmth_depth = 0.07,
        opacity               = 0.52,
    )

    # ── Session 104: Luca Giordano rapidità luminosa pass ────────────────────
    print("Giordano rapidità luminosa pass (session 104)...", flush=True)
    p.giordano_rapidita_luminosa_pass(
        aureole_cx      = 0.88,
        aureole_cy      = 0.06,
        aureole_radius  = 0.72,
        aureole_r       = 0.052,
        aureole_g       = 0.028,
        aureole_b       = 0.007,
        rim_strength    = 0.040,
        rim_sigma       = 3.0,
        shadow_hi       = 0.30,
        shadow_violet_b = 0.013,
        shadow_violet_r = 0.005,
        blur_radius     = 5.0,
        opacity         = 0.30,
    )

    # ── Session 105: il Guercino penumbra warmth pass ────────────────────────
    print("Guercino penumbra warmth pass (session 105)...", flush=True)
    p.guercino_penumbra_warmth_pass(
        penumbra_lo      = 0.28,
        penumbra_hi      = 0.62,
        amber_r          = 0.038,
        amber_g          = 0.018,
        amber_b          = 0.008,
        light_cx         = 0.18,
        light_cy         = 0.08,
        light_radius     = 0.85,
        directional_str  = 0.018,
        shadow_lo        = 0.05,
        shadow_hi        = 0.28,
        shadow_warm_r    = 0.022,
        shadow_warm_g    = 0.008,
        blur_radius      = 4.5,
        opacity          = 0.28,
    )

    # ── Session 105 IMPROVED: sfumato_veil_pass with penumbra_bloom ───────────
    print("Sfumato veil pass (s82 improved, s105 penumbra_bloom=0.06)...", flush=True)
    p.sfumato_veil_pass(
        reference              = ref,
        n_veils                = 4,
        veil_opacity           = 0.14,
        warmth                 = 0.35,
        shadow_warm_recovery   = 0.10,
        chroma_gate            = 0.42,
        highlight_ivory_lift   = 0.06,
        highlight_ivory_thresh = 0.82,
        atmospheric_blue_shift = 0.35,
        penumbra_bloom         = 0.06,
        penumbra_bloom_lo      = 0.30,
        penumbra_bloom_hi      = 0.60,
    )

    # ── SESSION 106: Jusepe de Ribera gritty tenebrism pass ──────────────────
    print("Ribera gritty tenebrism pass (session 106)...", flush=True)
    p.ribera_gritty_tenebrism_pass(
        shadow_hi        = 0.22,
        shadow_warm_r    = 0.015,
        shadow_warm_g    = 0.006,
        grain_strength   = 0.020,
        penumbra_lo      = 0.22,
        penumbra_hi      = 0.45,
        penumbra_grain   = 0.018,
        light_cx         = 0.15,
        light_cy         = 0.08,
        light_radius     = 0.70,
        amber_r          = 0.028,
        amber_g          = 0.012,
        blur_radius      = 3.5,
        opacity          = 0.12,
    )

    # ── SESSION 106 IMPROVEMENT: atmospheric_depth_pass with foreground_warmth ─
    print("Atmospheric depth pass (s106 improvement -- foreground_warmth=0.08)...", flush=True)
    p.atmospheric_depth_pass(
        haze_color            = (0.68, 0.74, 0.84),
        desaturation          = 0.62,
        lightening            = 0.46,
        depth_gamma           = 1.6,
        background_only       = True,
        horizon_glow_band     = 0.12,
        horizon_y_frac        = 0.55,
        horizon_band_sigma    = 0.06,
        zenith_luminance_boost = 0.06,
        zenith_band_sigma     = 0.10,
        foreground_warmth     = 0.08,
        foreground_band_sigma = 0.18,
    )

    # ── SESSION 107: Giovanni Antonio Boltraffio pearled sfumato pass ─────────
    print("Boltraffio pearled sfumato pass (session 107)...", flush=True)
    p.boltraffio_pearled_sfumato_pass(
        pearl_lo          = 0.72,
        pearl_r           = 0.010,
        pearl_g           = 0.015,
        pearl_b           = 0.022,
        shadow_hi         = 0.28,
        shadow_b          = 0.018,
        shadow_g          = 0.006,
        shadow_r          = 0.004,
        flesh_lo          = 0.40,
        flesh_hi          = 0.72,
        clarity_sigma     = 0.8,
        clarity_strength  = 0.14,
        blur_radius       = 4.0,
        opacity           = 0.32,
    )

    # ── SESSION 108: Giovanni Battista Moroni silver presence pass ────────────
    print("Moroni silver presence pass (session 108)...", flush=True)
    p.moroni_silver_presence_pass(
        hi_lo         = 0.70,
        silver_r      = 0.006,
        silver_g      = 0.010,
        silver_b      = 0.016,
        shadow_hi     = 0.35,
        warm_r        = 0.016,
        warm_g        = 0.008,
        warm_b        = 0.005,
        mid_lo        = 0.35,
        mid_hi        = 0.70,
        mid_gamma_lo  = 0.95,
        mid_gamma_hi  = 1.05,
        blur_radius   = 3.5,
        opacity       = 0.34,
    )

    # ── SESSION 109: Bernardo Strozzi amber impasto pass ─────────────────────
    print("Strozzi amber impasto pass (session 109)...", flush=True)
    p.strozzi_amber_impasto_pass(
        shadow_hi    = 0.36,
        amber_r      = 0.028,
        amber_g      = 0.014,
        amber_b      = 0.020,
        hi_lo        = 0.74,
        cream_r      = 0.012,
        cream_g      = 0.008,
        cream_b      = 0.010,
        hi_boost     = 1.035,
        mid_lo       = 0.36,
        mid_hi       = 0.74,
        rose_r       = 0.014,
        rose_b       = 0.007,
        blur_radius  = 4.0,
        opacity      = 0.38,
    )

    # ── SESSION 110: Sassoferrato pure devotion pass ──────────────────────────
    print("Sassoferrato pure devotion pass (session 110)...", flush=True)
    p.sassoferrato_pure_devotion_pass(
        ultra_thresh  = 0.04,
        ultra_b_lift  = 0.022,
        ultra_r_damp  = 0.016,
        pearl_lo      = 0.76,
        pearl_b_lift  = 0.010,
        pearl_r_damp  = 0.007,
        shadow_hi     = 0.30,
        shadow_b_lift = 0.016,
        shadow_r_damp = 0.008,
        blur_radius   = 3.5,
        opacity       = 0.30,
    )

    # ── SESSION 111: Orazio Gentileschi silver daylight pass (NEW) ────────────
    # "Silver daylight" — Orazio Gentileschi's cool Caravaggesque courtly naturalism.
    # Three-stage effect applied after the accumulated warm and devotional passes:
    #
    # (1) Silver highlight coolness — the Strozzi amber impasto and Dolci enamel
    #     passes have built rich warmth in the upper flesh tones.  Orazio's
    #     distinguishing quality is that his highlights — particularly the forehead,
    #     cheekbone, and nose bridge — are cool silver rather than warm ivory.  This
    #     is the quality of lead white with a trace of smalt under north-facing
    #     daylight.  Applied gently (silver_r_damp=0.010, silver_b_lift=0.016) so
    #     as to refine the Sassoferrato porcelain without removing it.
    #
    # (2) Midtone chroma lift — The accumulated glazing passes (Tissot, Dolci,
    #     Guercino, Strozzi) have harmonised the palette toward warm amber unity.
    #     Orazio's fabrics insist on chromatic distinctness: his golds are golden,
    #     his reds are red, his blues are blue — each hue more itself, not subsumed
    #     into the warm common ground.  A gentle chroma lift in the mid-tone zone
    #     restores this chromatic precision without disrupting the tonal harmony.
    #
    # (3) Cool shadow control — Orazio's shadows are cool and atmospheric.  After
    #     the warm shadow deposits of Guercino, Ribera, and Strozzi, a gentle cool
    #     correction (cool_r_damp=0.008, cool_b_lift=0.012) restores the Orazio
    #     quality in the deep tones without inverting the warmth entirely.
    print("Orazio Gentileschi silver daylight pass (session 111 -- NEW)...", flush=True)
    p.orazio_silver_daylight_pass(
        hi_lo          = 0.68,
        silver_r_damp  = 0.010,
        silver_b_lift  = 0.016,
        mid_lo         = 0.32,
        mid_hi         = 0.68,
        chroma_lift    = 0.018,
        shadow_hi      = 0.34,
        cool_r_damp    = 0.008,
        cool_b_lift    = 0.012,
        blur_radius    = 3.0,
        opacity        = 0.30,
    )

    # ── Finishing passes ──────────────────────────────────────────────────────

    # Edge lost-and-found (s81 improved, s91)
    print("Edge lost-and-found pass (s81/s91)...", flush=True)
    p.edge_lost_and_found_pass(
        focal_xy             = (0.515, 0.195),
        found_radius         = 0.28,
        found_sharpness      = 0.48,
        lost_blur            = 2.0,
        strength             = 0.34,
        figure_only          = True,
        gradient_selectivity = 0.65,
        soft_halo_strength   = 0.14,
    )

    # Old-master varnish
    print("Old-master varnish pass (s63)...", flush=True)
    p.old_master_varnish_pass(
        amber_strength  = 0.12,
        edge_darken     = 0.10,
        highlight_desat = 0.06,
        opacity         = 0.28,
    )

    # Final glaze — slightly cooler than s110 to reflect Orazio's silver balance
    print("Final glaze (cool-warm balance for Orazio silver daylight)...", flush=True)
    p.glaze((0.58, 0.44, 0.16), opacity=0.032)

    # Vignette and crackle
    print("Finishing (vignette + crackle)...", flush=True)
    p.finish(vignette=0.50, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s111.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
