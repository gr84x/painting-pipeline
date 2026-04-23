"""
paint_mona_lisa_s146.py -- Session 146 portrait painting.

Warm-start from mona_lisa_s145.png (latest accumulated canvas),
then applies session 146 additions.

Session 146 additions:
  - gossaert                            -- NEW (session 146)
                                           Jan Gossaert (Mabuse)
                                           (c. 1478–1532),
                                           Flemish Italianate
                                           Renaissance.
                                           The first Flemish painter
                                           to visit Rome (1508),
                                           absorbing Italian Renaissance
                                           classicism and fusing it with
                                           the Northern oil glazing
                                           tradition inherited from Jan
                                           van Eyck.  His flesh has a
                                           distinctive crystalline quality
                                           — highlights are cool pearl-
                                           white (unlike warm Venetian
                                           gold), shadows glow with warm
                                           umber, midtones carry vivid
                                           local colour.  Forms are
                                           resolved with Flemish precision
                                           across multiple transparent
                                           glaze layers.

  SESSION 146 MAIN PASS -- gossaert_pearl_crystalline_pass:

                                           Twenty-fourth distinct mode:
                                           MULTI-THRESHOLD LUMINANCE
                                           STRIATION WITH COOL-PEARL
                                           HIGHLIGHT ISOLATION.

                                           Three-stratum decomposition:
                                           shadow zone (luma < 0.38)
                                           → warm umber tint (R boost,
                                           B reduction);
                                           highlight zone (luma > 0.68)
                                           → cool pearl (desaturate +
                                           blue boost);
                                           midtone zone (residual)
                                           → saturation lift.
                                           At stratum boundaries: USM
                                           sharpening for crystalline
                                           edge clarity.

                                           Distinct from all 23 prior
                                           modes: three-stratum
                                           DIFFERENTIAL chromatic
                                           treatment.  Cools highlights
                                           (unlike Crivelli's gold-
                                           gilding warmth); three explicit
                                           strata (unlike Giorgione's two
                                           smooth gradient zones).

  SESSION 146 ARTISTIC IMPROVEMENT -- shadow_transparency_pass:

                                           General-purpose pass enriching
                                           shadows with the chromatic
                                           transparency of Old Master oil
                                           glazing. Deep shadows receive
                                           a cool-violet accent (simulating
                                           the underpaint visible through
                                           transparent glaze layers);
                                           penumbra zones receive a
                                           saturation boost for richness.

Warm-start base: mona_lisa_s145.png
Applies: s145 accumulated base + s146 (Gossaert crystalline -- NEW)
                                  + s146 (shadow transparency -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# -- Locate warm-start base ---------------------------------------------------
S145_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s145.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mona_lisa_s145.png"),
    "C:/Source/painting-pipeline/mona_lisa_s145.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s144.png"),
    "C:/Source/painting-pipeline/mona_lisa_s144.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s143.png"),
    "C:/Source/painting-pipeline/mona_lisa_s143.png",
]

base_path = None
for c in S145_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find warm-start base. Searched:\n" +
        "\n".join(f"  {c}" for c in S145_CANDIDATES)
    )

print(f"Loading warm-start base: {base_path}", flush=True)


# -- Utilities ----------------------------------------------------------------

def make_figure_mask() -> np.ndarray:
    mask = np.zeros((H, W), dtype=np.float32)
    cx, cy = W * 0.50, H * 0.46
    rx, ry = W * 0.38, H * 0.46
    y_idx, x_idx = np.ogrid[:H, :W]
    ellipse = ((x_idx - cx) / rx) ** 2 + ((y_idx - cy) / ry) ** 2
    mask[ellipse <= 1.0] = 1.0
    from scipy.ndimage import gaussian_filter
    mask = gaussian_filter(mask, sigma=30)
    return np.clip(mask, 0.0, 1.0)


def load_png_into_painter(p: Painter, path: str) -> None:
    img = Image.open(path).convert("RGBA").resize((W, H), Image.LANCZOS)
    import cairo
    import array as arr
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surface)
    img_data = img.tobytes("raw", "BGRA")
    src = cairo.ImageSurface.create_for_data(
        arr.array("B", img_data), cairo.FORMAT_ARGB32, W, H
    )
    ctx.set_source_surface(src, 0, 0)
    ctx.paint()
    p.canvas.surface.get_data()[:] = surface.get_data()[:]
    p.canvas.surface.mark_dirty()


def paint(out_dir: str = ".") -> str:
    print("=" * 68, flush=True)
    print("Session 146 warm-start from accumulated canvas", flush=True)
    print("Applying: Gossaert crystalline (146 -- NEW)", flush=True)
    print("Applying: Shadow transparency (146 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 146 (NEW): Gossaert pearl-crystalline pass -------------------
    # Twenty-fourth distinct mode: MULTI-THRESHOLD LUMINANCE STRIATION.
    # Applies cool-pearl highlight isolation + warm umber shadow enrichment
    # + midtone saturation lift + crystalline boundary clarity.
    #
    # Design intent for the accumulated Leonardo canvas:
    #
    # 1. Pearl highlights: The sfumato portrait has warm amber highlights
    #    (from the repeated velatura and glazing passes).  A gentle cool-pearl
    #    treatment (pearl_desat=0.12, pearl_cool_b=0.04) introduces the
    #    Flemish crystalline quality without overriding the Leonardo warmth.
    #    The luminance threshold highlight_lo=0.70 targets only the brightest
    #    pixels — the forehead catch-light, the nose ridge, the hands — so the
    #    broad warm mid-tones are untouched.
    #
    # 2. Warm umber shadows: The deep shadow zones of the sfumato portrait
    #    already have warm umber quality from the Leonardo glazing.  A gentle
    #    shadow_warm_r=0.025 boost reinforces this without creating
    #    any noticeable shift.  shadow_hi=0.36 targets only the deepest pixels.
    #
    # 3. Midtone saturation lift: mid_sat_boost=0.05 is very conservative.
    #    The sfumato portraits are intentionally desaturated; we lift gently
    #    to add subtle presence without departing from the Leonardo palette.
    #
    # 4. Crystalline boundaries: crystal_sigma=2.0 (slightly enlarged for the
    #    full 780×1080 canvas), crystal_amount=0.08 (gentle). The USM sharpening
    #    at stratum transitions adds micro-edge definition compatible with
    #    Leonardo's sfumato — sharpening occurs ONLY at the luminance-zone
    #    boundaries, not at every fine-detail edge.
    #
    # opacity=0.30: moderate; respects the 23-pass accumulated surface.
    print("Gossaert pearl-crystalline pass (session 146 -- NEW)...", flush=True)
    p.gossaert_pearl_crystalline_pass(
        shadow_hi       = 0.36,
        highlight_lo    = 0.70,
        pearl_cool_b    = 0.04,
        pearl_desat     = 0.12,
        shadow_warm_r   = 0.025,
        shadow_warm_b   = 0.020,
        mid_sat_boost   = 0.05,
        crystal_sigma   = 2.0,
        crystal_amount  = 0.08,
        opacity         = 0.30,
    )

    # -- Session 146 (NEW): Shadow transparency pass --------------------------
    # Artistic improvement: enriches shadows with chromatic transparency.
    # Injects a cool violet accent into deep shadows (simulating the underpaint
    # visible through transparent oil glaze layers) and boosts saturation in
    # the penumbra zone.
    #
    # Design intent:
    # The Gossaert pass warmed the deep shadows with umber; this pass then
    # introduces a subtle cool-violet underpaint character at low opacity,
    # creating the complex chromatic depth of the shadow interior that is
    # characteristic of multi-layer Flemish oil glazing — where multiple
    # pigment layers of different hue all contribute simultaneously.
    #
    # shadow_hi=0.38: targets pixels up to 38% luminance.
    # penumbra range [0.28, 0.55]: the transition zone around the shadow edge.
    # violet_r=0.38, violet_g=0.30, violet_b=0.68: warm violet (not pure blue)
    #   — appropriate for the Leonardo palette; pure cool blue would clash.
    # shadow_tint=0.03: very subtle — just a whisper of violet in the deepest
    #   shadow cores.
    # penumbra_chroma=0.06: gentle saturation lift in the penumbra for richness.
    # opacity=0.22: low; this is a subtle enrichment, not a transformation.
    print("Shadow transparency pass (session 146 artistic improvement -- NEW)...", flush=True)
    p.shadow_transparency_pass(
        shadow_hi       = 0.38,
        penumbra_lo     = 0.28,
        penumbra_hi     = 0.55,
        violet_r        = 0.38,
        violet_g        = 0.30,
        violet_b        = 0.68,
        shadow_tint     = 0.03,
        penumbra_chroma = 0.06,
        opacity         = 0.22,
    )

    # -- Carry-forward passes from session 145 --------------------------------

    # Cambiaso geometric planes (from s145 -- carry forward)
    print("Cambiaso geometric planes pass (session 145 carry-forward)...", flush=True)
    p.cambiaso_geometric_planes_pass(
        sigma_coarse   = 22.0,
        sigma_medium   = 5.0,
        flatten_amount = 0.50,
        edge_boost     = 0.22,
        sigma_edge     = 2.0,
        terra_r        = 0.68,
        terra_g        = 0.45,
        terra_b        = 0.18,
        terra_lo       = 0.08,
        terra_hi       = 0.38,
        terra_amount   = 0.055,
        opacity        = 0.15,
    )

    # Guardi atmospheric shimmer (from s144 -- carry forward)
    print("Guardi atmospheric shimmer pass (session 144 carry-forward)...", flush=True)
    p.guardi_atmospheric_shimmer_pass(
        shimmer_sigma = 2.0,
        n_trembles    = 5,
        tremble_px    = 2,
        cool_r        = 0.72,
        cool_g        = 0.74,
        cool_b        = 0.78,
        cool_lo       = 0.28,
        cool_hi       = 0.72,
        cool_amount   = 0.040,
        sat_dampen    = 0.07,
        opacity       = 0.16,
    )

    # Magnasco nervous brilliance (from s143 -- carry forward)
    print("Magnasco nervous brilliance pass (session 143 carry-forward)...", flush=True)
    p.magnasco_nervous_brilliance_pass(
        hf_sigma      = 3.0,
        scatter_px    = 2,
        bright_thresh = 0.04,
        dark_gate_lo  = 0.08,
        dark_gate_hi  = 0.55,
        warm_tint     = 0.04,
        opacity       = 0.12,
    )

    # Focal vignette (from s142 -- carry forward)
    print("Focal vignette pass (session 142 carry-forward)...", flush=True)
    p.focal_vignette_pass(
        focal_x           = 0.50,
        focal_y           = 0.35,
        vignette_strength = 0.25,
        vignette_power    = 2.2,
        cool_shift        = 0.018,
        opacity           = 0.30,
    )

    # Glazing depth pass (from session 141 -- carry forward)
    print("Glazing depth pass (session 141 carry-forward)...", flush=True)
    p.glazing_depth_pass(
        glaze_sigma = 3.5,
        warm_r      = 0.07,
        warm_g      = 0.025,
        depth_low   = 0.28,
        depth_high  = 0.72,
        opacity     = 0.12,
    )

    # Velatura: warm amber unifying glaze
    print("Velatura warm amber glaze (Leonardo sfumato finish)...", flush=True)
    p.velatura_pass(midtone_tint=(0.80, 0.65, 0.38), midtone_opacity=0.04)

    # Vignette finish
    print("Finishing (vignette)...", flush=True)
    p.finish(vignette=0.48, crackle=False)

    out_path = os.path.join(out_dir, "mona_lisa_s146.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
