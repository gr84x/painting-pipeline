# Brush & Paint System Overhaul — Implementation Plan

## Background

The current stroke engine renders every brush mark as a polygon — a center-line offset into left/right boundaries, filled as a quad per segment. This produces rectangular, hard-edged strokes regardless of brush type. The three existing brush types (ROUND, FILBERT, FLAT) differ only in tip taper. There is no bristle texture, no paint depletion model, no pressure variation within a stroke, and no tools other than brushes.

This plan replaces that system with a bristle-simulation engine, a proper paint-load model, a family of oil-painting tools, and documented guidance for when each tool and operation mode should be used.

---

## Architecture Overview

### Core abstraction: PaintingTool

Every tool — brush, knife, finger, sponge, rag — implements a common `PaintingTool` interface with three operation modes:

```
deposit    — adds new paint to the canvas
manipulate — moves or blends existing paint without adding new color
remove     — lifts or subtracts paint to reveal underlying layers
```

A tool may support one, two, or all three modes. The stroke placement engine calls `tool.apply(canvas, path, params)`, which dispatches to the appropriate mode(s).

### New dataclasses

**`BrushProfile`** — defines the physical properties of one tool:
- `name`, `tool_type` (brush | knife | finger | sponge | rag | spatter | sgraffito | comb | squeegee)
- `bristle_count` — 0 for knives/fingers, 8–40 for brushes
- `distribution` — how bristles are arranged across the ferrule: `linear`, `oval`, `radial`, `arc`
- `stiffness` — 0.0 (soft sable) to 1.0 (stiff hog bristle); drives per-bristle deviation
- `spread` — base fan width relative to brush width at neutral pressure
- `pressure_spread` — additional spread at maximum pressure
- `load_capacity` — total paint charge; drives dip frequency and depletion curve
- `edge_sharpness` — for knives: 0.0 (soft scrape) to 1.0 (crisp hard edge)

**`PressureProfile`** — defines how pressure varies within and across strokes:
- `profile_type`: `even | press_lift | lift_press | stab | feather`
- `base_pressure` — 0.0–1.0 default for this pass
- `variance` — per-stroke random variation around base
- `ramp` — optional float; positive = pass starts heavy and lightens, negative = lightens then heavies

**`PaintLoad`** — tracks paint charge on the brush across strokes:
- `current_load` — 0.0–1.0
- `capacity` — maximum charge (from BrushProfile)
- `reload_mode`: `every_stroke | every_n | threshold | never`
- `reload_n` — used when `reload_mode = every_n`
- `reload_threshold` — used when `reload_mode = threshold`; reload when load drops below this value

**`CanvasState`** extensions:
- `thickness_map: np.ndarray` — per-pixel impasto height (0.0–1.0); new, alongside existing color buffer
- `wetness: np.ndarray` — already exists; extended with per-pixel age for drying curve
- `age_map: np.ndarray` — tracks time-since-painted per pixel; drives drying simulation

---

## Phase 1 — Foundation

### 1.1 PaintingTool base class

Replace `BrushTip` with `PaintingTool`. Each concrete tool subclasses it and implements the modes it supports. Unsupported modes raise a clear error rather than silently no-oping.

Tool registry: a module-level dict mapping tool names to instances, so painting passes reference tools by name and the registry is the single source of truth.

### 1.2 Bristle simulation engine

**Replace** `apply_stroke()` polygon fill with a bristle bundle renderer.

**How it works:**
1. Seed the RNG from `(stroke_origin_x, stroke_origin_y, stroke_angle)` — deterministic per stroke, so re-rendering the same image is stable.
2. Sample `bristle_count` bristle positions across the ferrule according to `distribution` (linear spacing for flat, Gaussian for filbert, etc.).
3. For each bristle, compute a deviation path: the bristle's trajectory deviates from the center path by an amount driven by `stiffness` (low stiffness = more flex, more deviation) and the bristle's radial position (outer bristles deviate more than center).
4. Each bristle is a thin Catmull-Rom sub-stroke rendered at 1–2px width with its own opacity drawn from the bristle's local paint load.
5. The aggregate of N bristle sub-strokes produces the emergent stroke shape — ragged edges, visible tracks, natural taper.

**Pressure effect on bristles:**
- High pressure: bristle bundle spreads wider, more bristles contact canvas, individual bristle coverage increases.
- Low pressure: bundle narrows, only center bristles contact, outer bristles lift off entirely (fade to zero opacity beyond a threshold).
- Within-stroke variation driven by `PressureProfile.profile_type`:
  - `even` — constant contact throughout
  - `press_lift` — maximum spread at start, taper off as stroke ends (natural lift)
  - `lift_press` — starts narrow, builds to full contact mid-stroke
  - `stab` — immediate full pressure, released quickly (dab marks)
  - `feather` — very light throughout; only the softest center bristles contact

### 1.3 Paint load and depletion

**Within a stroke:** Each bristle carries a fractional share of the brush's current load. As the bristle travels, its load depletes per unit of distance. Depletion rate scales with pressure (heavy pressure moves more paint). At low load:
- Bristle opacity drops
- Bristle spread *increases* (individual bristles splay as paint runs thin)
- Color picks up a small fraction of the underlying canvas color (brush starts blending rather than depositing cleanly)

**Across strokes:** `PaintLoad` persists across `apply_stroke()` calls. The painter reloads only when `reload_mode` dictates. This means:
- First stroke after a reload: full opacity, tight bundle, strong color
- Subsequent strokes: progressively more transparent, more splayed, dryer texture
- Final strokes before reload: dry-brush character automatically, no special-casing needed

**Reload behavior:** When a reload occurs, load returns to `capacity`. The painter can vary the reload amount (partial dip = half capacity) for controlled gradations.

### 1.4 Brush profiles — oil set

| Name | Bristles | Distribution | Stiffness | Spread | Load capacity | Character |
|---|---|---|---|---|---|---|
| `hog_flat` | 16 | linear | 0.85 | 1.0 | 1.0 | Workhorse — blocking, bold marks |
| `hog_filbert` | 14 | oval | 0.80 | 0.9 | 0.95 | Versatile — most oil form work |
| `round_sable` | 10 | radial | 0.25 | 0.5 | 0.70 | Detail, glazing, fine marks |
| `fan` | 28 | arc | 0.30 | 2.0 | 0.60 | Blending, foliage, skies (loaded) |
| `mop` | 36 | oval | 0.10 | 1.8 | 0.80 | Soft washes, backgrounds |
| `rigger` | 6 | radial | 0.20 | 0.15 | 0.40 | Fine lines, branches, calligraphic |
| `dry_brush` | 18 | linear | 0.90 | 1.3 | 0.25 | Depleted from first stroke; broken drag texture |

**Technique presets** — named combinations of brush + pressure + load settings:

| Preset | Brush | Reload mode | Pressure profile | Character |
|---|---|---|---|---|
| `alla_prima` | hog_filbert | every_stroke | press_lift | Bold, fresh, confident |
| `glazing` | round_sable | every_stroke (thin load) | feather | Thin transparent layers |
| `dry_brush` | dry_brush | threshold=0.1 | even | Broken drag texture |
| `impasto` | hog_flat | every_stroke (full load) | stab | Thick loaded marks |
| `blending` | fan (dry) | never (manipulate only) | feather | Smooth transitions |

### 1.5 Painting knife

No bristles. Completely different model.

**Deposit mode:**
- Rigid flat blade deposits a thick slab of paint
- Stroke body: uniform high opacity with sharp lateral edges (no bristle taper)
- Trailing edge: paint pileup — a slightly darker, thicker ridge where the blade lifted
- Blade texture: faint parallel micro-lines from the metal surface (low-amplitude, high-frequency noise along the stroke direction)
- `edge_sharpness` parameter: 1.0 = razor clean edges; lower values soften the boundary slightly

**Knife shapes** (affect deposit width and tip geometry):
- `trowel` — wide, tapers to a rounded point; versatile
- `diamond` — widest at center, pointed at both ends; precise
- `offset` — cranked blade; wide flat deposit, used for large areas

**Scrape mode (remove):**
- Blade edge-on, dragged across wet paint
- Lifts paint back toward the underlying layer
- Produces a lighter, slightly streaked texture
- Use for: revealing ground color, lightening passages, creating texture contrast

**Usage guidance:**
- Deposit: use for impasto highlights, bold color statements, textured foregrounds
- Scrape: use sparingly — once or twice per passage, not as a broad tool
- Do not use for fine detail; knife marks read as large, confident statements
- A knife stroke should not be followed by a brush stroke on the same area unless the knife layer is dry

### 1.6 Finger tool

No bristles. Gaussian smear of existing canvas color. No new paint deposited.

**Manipulate mode only:**
- Sample existing canvas colors in the smear radius
- Blend toward the weighted average (Gaussian kernel)
- Soft edges: coverage falls off smoothly from center
- Opacity of the smear is low by default (0.3–0.5); heavy use requires many passes

**Usage guidance:**
- Use for softening transitions between two wet areas (sky-to-horizon, shadow-to-light)
- Use after a brush pass to unify adjacent strokes into a smooth field
- Do not use on dry paint (no effect; models real physics)
- Limit to 1–3 passes over any one area — heavy use destroys texture and looks muddy
- Never use on impasto or knife marks; the raised texture is the point

### 1.7 Edge treatment

`edge_treatment` parameter on the `Painter` class:
- `natural_border` — current behavior; ground color visible at canvas edges; appropriate for studies, plein air sketches, academic figure studies
- `full_coverage` — dedicated edge pass ensures the full canvas surface is painted; appropriate for finished works
- `overpainting` — post-pass that samples undersampled edge regions and fills them with outward-biased strokes

---

## Phase 2 — Extended tools

### 2.1 Fan blender (dry)

The fan brush with `current_load = 0.0` throughout. Pure manipulation.

**Manipulate mode:**
- Dragged lightly across adjacent wet strokes
- Merges colors without adding new paint
- Models the real dry fan blend: soft, even, slightly directional

**Usage guidance:**
- Use after placing a brush pass to soften edges between strokes that should not remain distinct
- Apply parallel to the dominant stroke direction for smooth blends; perpendicular for more uniform merging
- 1–2 light passes maximum; more reads as overworked
- Not appropriate after a knife pass or on impasto areas

### 2.2 Rag / cloth

Two submodes driven by pressure:

**Drag (manipulate):**
- Spreads existing paint thinly across a larger area
- Reduces local opacity by ~30–50% per pass
- Adds a faint directional texture (cloth grain)
- Used for: toning large areas quickly, creating atmospheric backgrounds

**Wipe (remove):**
- Lifts paint toward the underlying layer
- Proportional to pressure: light wipe = subtle lightening; heavy wipe = back to near-ground
- Used for: correcting passages, creating soft light areas in a dark ground

**Usage guidance:**
- Drag is effective in the early underpainting and block-in stages for large tonal areas
- Wipe is a correction tool; use it deliberately, not as a habit
- Do not use rag over freshly knifed impasto; rag will flatten and destroy the texture
- Rag followed by a brush pass is a classic sequence for building soft backgrounds

### 2.3 Sponge

Irregular cellular mask (Voronoi-based) stamped along a path.

**Deposit mode:**
- Stamp at intervals along path with slight rotation variance
- Mask produces soft porous edges naturally
- `cell_density` parameter: low = large open holes (sea sponge); high = fine texture (foam sponge)

**Usage guidance:**
- Use for foliage masses, clouds, rough stone, porous surfaces
- Do not use for smooth surfaces, skin, or any area requiring directional structure
- Best applied in passes — light first pass for color, heavier second pass for density
- Sponge + dry brush over top is effective for foliage that still reads as painterly

### 2.4 Spatter

Poisson-distributed dots in a directional cone from source point and angle.

**Deposit mode:**
- Dot size: small near source, larger at distance (inverse of airbrush — coarser spread)
- Density: Poisson spacing prevents clumping
- Color: sampled from the loaded paint color with jitter

**Usage guidance:**
- Use for texture accents: soil, rock, foliage edges, water droplets, sand
- Keep spatter subtle — it reads as a texture accent, not a primary mark
- Use over existing dry passes only, not into wet paint (dots would bleed)
- `density` should be low enough that individual dots are distinguishable at normal viewing distance

### 2.5 Sgraffito

Scratch line through wet paint to reveal the layer beneath.

**Remove mode:**
- Thin path that pulls paint opacity toward 0 along the scratch
- Reveals the color of the layer directly below
- `scratch_depth` parameter: 0.0 = light scratch (slight lightening); 1.0 = full reveal of lower layer
- Edge hardness: scratches are sharp by default (simulates a hard tool point)

**Usage guidance:**
- Use for bright highlights in dark passages (scratch to reveal a light ground)
- Use for fine texture: grasses in a dark foreground, branches against sky, fur highlights
- Use sparingly — sgraffito is a finishing technique, not a building technique
- Only effective when paint below is wet; on dry paint no reveal is possible
- 3–5 scratches per passage maximum; more becomes decorative rather than structural

### 2.6 Comb / texture drag

Rigid comb dragged through wet paint, leaving parallel grooves.

**Manipulate mode:**
- `tine_count` and `tine_spacing` define the comb geometry
- Grooves pull paint aside and partially expose the lower layer at the groove center
- Result: parallel light/dark alternating lines in the direction of drag

**Usage guidance:**
- Use for: wood grain, hair masses, calm water reflections, grass fields
- Drag in one consistent direction per passage; crossing directions produces a crosshatch that reads as fabric rather than organic texture
- Works only in wet paint; apply immediately after a brush or knife pass
- Use coarse combs (wide spacing) for large features; fine combs (tight spacing) for hair, fur

---

## Phase 3 — Paint properties

### 3.1 Impasto thickness map

`thickness_map` is a float32 array the same size as the canvas, initialized to 0.

Each stroke contributes thickness proportional to:
- Current paint load at time of deposit
- Pressure at each point along the stroke
- Tool type: knife deposits maximum thickness; brush deposits moderate; sponge/rag deposit near-zero

Thickness decays slightly between passes (paint settles, canvas dries) via a small exponential decay factor.

### 3.2 Sheen / wet paint highlight pass

After each painting pass, a sheen compositing step:
1. Compute the gradient magnitude of `thickness_map`
2. At high-gradient regions (raised edges of thick marks), add a directional highlight
3. Highlight color: slightly desaturated, brightened version of the local paint color
4. Highlight intensity scales with `thickness_map` value at that location
5. Light angle is a painter-level parameter (`sheen_angle`); defaults to 45° upper-left

Result: thick impasto edges catch light, thin glazes remain matte. Reproduces the visual quality of oil paint under raking light.

### 3.3 Wetness gradient within strokes

The existing `wetness` map is updated per-stroke. Additionally:
- The start of a stroke has slightly higher wet-blend (softer edges, more blending)
- The end of a stroke has lower wet-blend as paint and canvas both dry slightly
- This is driven by `PaintLoad.current_load` at each point along the path

---

## Phase 4 — Watercolor specifics

### 4.1 Diffusion / bleeding

After placing strokes on a wet area, apply one round of 2D Gaussian diffusion to the wet region. Radius proportional to `wetness` at that point. Produces realistic color bleeding at wet-into-wet boundaries.

### 4.2 Hard drying edges

As wet areas dry (between painting passes), the perimeter of formerly wet regions accumulates pigment. Implementation: find the boundary pixels of each wet region, darken them slightly (multiply value by 0.85–0.92). The classic watercolor cauliflower and hard-edge effects emerge naturally.

### 4.3 Granulation

Pigment settling into paper texture: modulate stroke opacity with the existing `cold_press_texture` map. High-frequency texture variation means paint settles into paper valleys (darker, denser) and skims over peaks (lighter, thinner). Pigment granulation factor is paint-color-dependent — earth tones granulate more than synthetic pigments.

---

## Tool usage guidance — reference

This section documents the intended balance of deposit / manipulate / remove across painting stages. It serves as both documentation and as the basis for automated stage validation.

### Operation modes defined

**Deposit** — adds new paint; changes both color and opacity of the canvas. Primary mode for building the painting.

**Manipulate** — moves, blends, or softens existing wet paint; does not add new color. Used to unify and refine. Should always follow deposit, never precede it (nothing to manipulate on a blank canvas).

**Remove** — lifts or subtracts paint; reveals lower layers. Corrective and textural. Should be used deliberately and sparingly.

### By painting stage

| Stage | Primary operation | Secondary | Remove | Notes |
|---|---|---|---|---|
| Tone ground | deposit | — | — | One rag pass to even the ground is appropriate |
| Underpainting | deposit | manipulate (light) | remove (correction only) | Establish values; rag drag for large tonal areas |
| Block in | deposit | — | — | Bold strokes; do not blend yet; let marks read |
| Build form | deposit | manipulate | — | Fan blender or finger after each brush pass to soften form edges |
| Detail pass | deposit | — | remove (sgraffito for highlights) | Small brushes; high pressure; minimal blending |
| Impasto / lights | deposit | — | — | Knife or heavy loaded brush; no manipulation after |
| Final glazing | deposit (transparent) | — | — | Very low opacity; round sable or mop; no manipulation |
| Finish / correction | remove | manipulate | — | Sgraffito for highlights; rag wipe for overworked areas |

### Balance ratios by style

| Style | Deposit | Manipulate | Remove |
|---|---|---|---|
| Alla prima (Sargent/Sorolla) | 90% | 5% | 5% |
| Classical layered (Rembrandt) | 70% | 20% | 10% |
| Impressionist (Monet) | 85% | 10% | 5% |
| Impasto / textural (van Gogh) | 95% | 2% | 3% |
| Soft portrait (Bouguereau) | 60% | 35% | 5% |
| Watercolor | 65% | 25% | 10% |

### Warning conditions (guide for automated validation)

These indicate a painting that has been overworked or tool-sequenced incorrectly:

- **Manipulation before deposit** on a blank or near-blank area — nothing to blend
- **Heavy manipulation ratio > 40%** for an oil mode — will produce muddy, overworked result
- **Remove on dry paint** — sgraffito/rag wipe has no effect; likely a stage-ordering error
- **Knife pass followed immediately by brush in the same area** — brush will flatten impasto
- **Fan blender used more than 2 passes over the same area** — destroys texture
- **Finger tool used on impasto areas** — flattens the thickness map, destroys raised texture
- **Spatter into wet paint** — dots bleed; spatter is for dry or near-dry surfaces only

---

## Implementation sequence

```
Phase 1 (foundation — must ship together as one cohesive change):
  1.1  PaintingTool base class + tool registry
  1.2  BrushProfile, PressureProfile, PaintLoad dataclasses
  1.3  Bristle simulation engine (replaces apply_stroke polygon)
  1.4  Seeded per-bristle deviation
  1.5  Paint load + depletion model (within-stroke and cross-stroke)
  1.6  Pressure profiles (within-stroke variation)
  1.7  Oil brush profiles + technique presets
  1.8  Painting knife (deposit + scrape modes)
  1.9  Finger tool (manipulate only)
  1.10 Edge treatment options on Painter

Phase 2 (extended tools — can ship incrementally):
  2.1  Fan blender (dry manipulation)
  2.2  Rag (drag + wipe)
  2.3  Sponge
  2.4  Spatter
  2.5  Sgraffito
  2.6  Comb / texture drag

Phase 3 (paint properties — depends on Phase 1 canvas state extensions):
  3.1  Thickness map
  3.2  Sheen / wet highlight pass
  3.3  Wetness gradient within strokes

Phase 4 (watercolor — self-contained, can run parallel to Phase 3):
  4.1  Diffusion / bleeding
  4.2  Hard drying edges
  4.3  Granulation
```

---

## Files affected

- `stroke_engine.py` — primary change; most of the above lives here
- New module (or section within stroke_engine.py): tool definitions and profiles
- Per-mode painting functions (e.g. `impressionist_pass`, `sargent_pass`) will need to be updated to use tool names and technique presets rather than raw BrushTip parameters
- All 135 artist modes should be audited post-Phase 1 to confirm their brush/tool choices still produce correct results; the technique preset names provide a stable mapping

---

*Plan compiled from design discussion — 2026-04-28*
