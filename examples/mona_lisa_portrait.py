"""
mona_lisa_portrait.py — Render the Mona Lisa description through the Leonardo pipeline.

Synthesises a compositional reference that captures the essential layout described
in the prompt:
  - Half-length female figure, slightly right of centre, three-quarter pose
  - Dark hair parted at centre with veil, dark dress with gauze wrap
  - Dreamy atmospheric landscape background (left higher than right)
  - Winding path visible on the left, body of water in middle-distance

Then applies the HIGH_RENAISSANCE pipeline:
  tone_ground -> underpainting -> block_in -> build_form -> sfumato_veil_pass ->
  tonal_envelope_pass -> place_lights -> glaze -> finish

No Blender required — the stroke engine runs directly on the synthetic reference.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter
from art_catalog import get_style


# ── Canvas dimensions (close to Mona Lisa's proportions: 53 × 77 cm) ────────
W, H = 530, 770


# ── Build a synthetic compositional reference ─────────────────────────────────

def build_reference(w: int, h: int) -> Image.Image:
    """
    Construct a tonal reference image capturing the Mona Lisa composition:
    - Upper register: cool atmospheric haze (aerial perspective / sfumato sky)
    - Middle ground: rocky geological landscape dissolving into mist
    - Figure: warm flesh oval, torso slightly right of centre
    - Head: small bright oval, slightly left of figure centre (3/4 pose)
    - Hair: dark warm-brown cap over head, veiled
    - Dress: dark forest-green occupying the lower torso
    - Hands: warm flesh region at the base of the composition
    - Background asymmetry: left side sits slightly higher than right (as noted in the prompt)
    """
    # (H, W) coordinate grids, values in [0, 1]
    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None] * np.ones((1, w), dtype=np.float32)
    xx = np.ones((h, 1), dtype=np.float32) * np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]
    # yy, xx — both shape (H, W)

    def _blend(base, colour, alpha):
        """Alpha-blend `colour` (shape (3,)) over `base` (H,W,3) with `alpha` (H,W)."""
        a = alpha[:, :, None]   # (H, W, 1)
        return base * (1.0 - a) + colour[None, None, :] * a

    # ── Background: atmospheric landscape with sfumato recession ─────────────
    sky   = np.array([0.66, 0.68, 0.70], dtype=np.float32)  # pale cool haze
    rocks = np.array([0.48, 0.53, 0.52], dtype=np.float32)  # grey-green middle
    earth = np.array([0.32, 0.38, 0.34], dtype=np.float32)  # near ground

    t_sky   = np.clip(1.0 - yy * 4.5,        0.0, 1.0)   # (H, W)
    t_earth = np.clip((yy - 0.68) * 5.0,     0.0, 1.0)
    t_mid   = np.clip(1.0 - t_sky - t_earth, 0.0, 1.0)

    # Compose background into (H, W, 3)
    arr = (sky[None, None, :]   * t_sky[:, :, None]
         + rocks[None, None, :] * t_mid[:, :, None]
         + earth[None, None, :] * t_earth[:, :, None])

    # Left-side background slightly lighter (prompt: horizon mismatch)
    left_tint = np.clip(0.55 - xx, 0.0, 0.55) * 0.10   # (H, W)
    arr += left_tint[:, :, None] * np.array([0.02, 0.06, 0.12], dtype=np.float32)

    # Winding path on the left — diagonal stripe slightly lighter than bg
    path_x_centre = 0.25 + (yy - 0.30) * 0.18   # (H, W) — shifts right as y rises
    path_dist = np.abs(xx - path_x_centre) / 0.04
    path_mask = (np.clip(1.0 - path_dist, 0.0, 1.0)
                 * np.clip((yy - 0.25) / 0.40, 0.0, 1.0))
    arr += path_mask[:, :, None] * np.array([0.05, 0.06, 0.04], dtype=np.float32)

    # Water glint in middle-distance (right of centre, horizontal)
    water_d = (((xx - 0.70) / 0.20)**2 + ((yy - 0.48) / 0.04)**2)
    water_mask = np.clip(1.0 - water_d, 0.0, 1.0) ** 2 * 0.35
    arr += water_mask[:, :, None] * np.array([0.18, 0.22, 0.28], dtype=np.float32)

    arr = np.clip(arr, 0.0, 1.0)

    # ── Figure: torso / lap — warm flesh oval ────────────────────────────────
    fig_cx, fig_cy = 0.505, 0.62
    fig_rx, fig_ry = 0.30, 0.44
    fx = (xx - fig_cx) / fig_rx
    fy = (yy - fig_cy) / fig_ry
    fig_d = fx**2 + fy**2   # (H, W)

    flesh = np.array([0.76, 0.62, 0.47], dtype=np.float32)
    fig_alpha = np.clip(1.55 - fig_d, 0.0, 1.0) ** 0.60
    arr = _blend(arr, flesh, fig_alpha)

    # Dark dress: lower torso and lap
    dress = np.array([0.14, 0.20, 0.17], dtype=np.float32)
    d_alpha = np.clip(1.2 - fig_d, 0.0, 1.0) * (yy > 0.58) * 0.72
    arr = _blend(arr, dress, d_alpha)

    # Semi-transparent gauze wrap over chest
    gauze = np.array([0.38, 0.42, 0.40], dtype=np.float32)
    g_alpha = (np.clip(0.90 - fig_d, 0.0, 1.0)
               * ((yy > 0.50) & (yy < 0.66) & (fig_d < 0.90)) * 0.30)
    arr = _blend(arr, gauze, g_alpha)

    # ── Head: bright oval, slightly left of torso centre ─────────────────────
    head_cx, head_cy = 0.488, 0.265
    head_rx, head_ry = 0.125, 0.158
    hx = (xx - head_cx) / head_rx
    hy = (yy - head_cy) / head_ry
    head_d = hx**2 + hy**2   # (H, W)

    face = np.array([0.84, 0.72, 0.56], dtype=np.float32)
    head_alpha = np.clip(1.45 - head_d, 0.0, 1.0) ** 0.52
    arr = _blend(arr, face, head_alpha)

    # Light on left side of face (upper-left source)
    lit_d = (hx + 0.30)**2 + (hy + 0.15)**2
    lit_alpha = np.clip(1.0 - lit_d, 0.0, 1.0) ** 1.8 * 0.55 * head_alpha
    arr = _blend(arr, np.array([0.91, 0.82, 0.68], dtype=np.float32), lit_alpha)

    # Shadow on right side
    shad_d = (-hx + 0.25)**2 + (hy - 0.10)**2
    shad_alpha = np.clip(1.0 - shad_d, 0.0, 1.0) ** 2.2 * 0.45 * head_alpha
    arr = _blend(arr, np.array([0.52, 0.40, 0.28], dtype=np.float32), shad_alpha)

    # ── Hair: dark warm brown, centre-parted with veil ───────────────────────
    hair_d = (((xx - head_cx) / (head_rx * 1.55))**2
              + ((yy - head_cy) / (head_ry * 1.42))**2)
    face_zone = (np.abs(hx) < 0.50) & (hy > -0.62) & (hy < 0.72)
    hair_mask = (hair_d < 1.0) & ~face_zone & (hy < 0.52)
    h_alpha = np.where(hair_mask, np.clip(1.0 - hair_d, 0.0, 1.0) * 0.88, 0.0)
    arr = _blend(arr, np.array([0.19, 0.14, 0.09], dtype=np.float32), h_alpha)

    # Veil: dark translucent film over the crown
    veil_zone = (hair_d < 0.70) & (hy < -0.10) & (yy < 0.28)
    v_alpha = np.clip(0.70 - hair_d, 0.0, 1.0) * 0.55 * veil_zone
    arr = _blend(arr, np.array([0.12, 0.10, 0.08], dtype=np.float32), v_alpha)

    # ── Hands: warm flesh at base of composition ──────────────────────────────
    hndx = (xx - 0.504) / 0.175
    hndy = (yy - 0.845) / 0.085
    hands_d = hndx**2 + hndy**2
    hand_alpha = np.clip(1.25 - hands_d, 0.0, 1.0) ** 0.72 * 0.78
    arr = _blend(arr, np.array([0.74, 0.60, 0.45], dtype=np.float32), hand_alpha)

    # ── Final clip, convert, and smooth ──────────────────────────────────────
    arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
    ref = Image.fromarray(arr, "RGB")
    ref = ref.filter(ImageFilter.GaussianBlur(5))
    return ref


# ── Build painter and apply the Leonardo HIGH_RENAISSANCE pipeline ────────────

def paint_mona_lisa(output_path: str = "mona_lisa_portrait.png") -> str:
    """Run the full Leonardo sfumato pipeline on the synthetic reference."""

    print("=" * 64)
    print("  Mona Lisa — Leonardo da Vinci style")
    print("  HIGH_RENAISSANCE / Sfumato pipeline")
    print("=" * 64)

    ref = build_reference(W, H)
    ref.save("mona_lisa_reference.png")
    print(f"\n  Reference saved -> mona_lisa_reference.png  ({W}×{H})")

    # Load Leonardo's style from the catalog
    leo = get_style("leonardo")

    # Initialise the stroke engine
    p = Painter(W, H)

    # ── Step 1: Warm ochre imprimatura (toned ground) ─────────────────────────
    # Leonardo worked on a mid-toned ochre imprimatura that eliminates the cold
    # white of raw canvas and provides a warm unified undertone.
    p.tone_ground(leo.ground_color, texture_strength=0.06)
    print("\n  [1/10] Tone ground complete")

    # ── Step 2: Underpainting — dead-colour value structure ───────────────────
    # Value composition only: no colour yet.  Leonardo established his tonal
    # structure in desaturated umber before introducing colour glazes.
    p.underpainting(ref, stroke_size=48, n_strokes=160)
    print("  [2/10] Underpainting complete")

    # ── Step 3: Block-in — main colour masses ─────────────────────────────────
    # Large confident strokes establishing the warm flesh vs cool background
    # colour relationship across the composition.
    p.block_in(ref, stroke_size=32, n_strokes=340)
    print("  [3/10] Block-in complete")

    # ── Step 4: Build form — directional medium strokes ───────────────────────
    # Medium strokes following surface topology: face, neck, hands, drapery.
    # Leonardo was extraordinarily patient here — hundreds of small, deliberate
    # marks building the three-dimensional form.
    p.build_form(ref, stroke_size=10, n_strokes=1400)
    print("  [4/10] Build form complete")

    # ── Step 5: Sfumato veil pass — imperceptible edge dissolution ────────────
    # The defining Leonardo technique: multiple thin, warm semi-transparent
    # glazes composited over the edge zones, built up to 30-40 layers in the
    # original paintings (here approximated by n_veils=10).
    # The chroma_dampen replicates the subtle desaturation visible under X-ray
    # at the corners of the Mona Lisa's mouth and eyes.
    p.sfumato_veil_pass(
        ref,
        n_veils       = 10,
        blur_radius   = 14.0,
        warmth        = 0.38,
        veil_opacity  = 0.07,
        edge_only     = True,
        chroma_dampen = 0.20,
    )
    print("  [5/10] Sfumato veil pass complete")

    # ── Step 6: Tonal envelope — portrait luminosity gradient ─────────────────
    # Brightens the composition centre (face/hands area) with a warm amber
    # glow, slightly deepens the peripheral corners.  Simulates the tonal
    # management Leonardo applied to guide the eye to the sitter's face.
    p.tonal_envelope_pass(
        center_x      = 0.488,   # head position (slightly left of centre)
        center_y      = 0.32,
        radius        = 0.48,
        lift_strength = 0.09,
        lift_warmth   = 0.35,
        edge_darken   = 0.07,
        gamma         = 1.9,
    )
    print("  [6/10] Tonal envelope pass complete")

    # ── Step 7: Selective focus — face sharp, background softens ─────────────
    # NEW (session 34): radial peripheral blur + desaturation that keeps the
    # sitter's face and hands at maximum sharpness while the landscape
    # background and clothing areas soften gradually — the natural quality
    # difference between a carefully wrought face and a broadly indicated
    # environment that Leonardo instinctively applied.
    p.selective_focus_pass(
        center_x        = 0.488,   # face position (matches tonal envelope)
        center_y        = 0.29,
        focus_radius    = 0.34,    # covers the face and immediate neckline
        max_blur_radius = 2.8,     # subtle — not a photographic effect
        desaturation    = 0.10,    # slight peripheral chroma reduction
        gamma           = 2.2,
    )
    print("  [7/10] Selective focus pass complete")

    # ── Step 8: Place lights — impasto highlights ─────────────────────────────
    # Warm ivory highlights concentrated in the lit upper-left face zone,
    # hands, and the brightest passages of the atmospheric background.
    p.place_lights(ref, stroke_size=5, n_strokes=320)
    print("  [8/10] Place lights complete")

    # ── Step 9: Warm amber unifying glaze ─────────────────────────────────────
    # Leonardo's characteristic final glaze: a thin transparent warm amber wash
    # that unifies the entire picture plane with a golden warmth and eliminates
    # any remaining coolness in the shadow passages.
    p.glaze((0.72, 0.52, 0.22), opacity=0.06)
    print("  [9/10] Final glaze complete")

    # ── Step 10: Finish — subtle vignette + crackle ───────────────────────────
    # Gentle vignette (Louvre lighting reproduces a slight peripheral darkening).
    # Crackle: the original Mona Lisa has extensive craquelure.
    p.finish(vignette=0.28, crackle=True)
    print("  [10/10] Finish complete")

    # ── Save output ───────────────────────────────────────────────────────────
    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Painting saved -> {output_path}  ({W}×{H})")
    print("=" * 64)

    return output_path


if __name__ == "__main__":
    out = "mona_lisa_portrait.png"
    if len(sys.argv) > 1:
        out = sys.argv[1]
    paint_mona_lisa(out)
