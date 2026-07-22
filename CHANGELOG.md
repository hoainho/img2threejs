# Changelog

All notable changes to the **img2threejs** skill. Versions follow the `SKILL.md` frontmatter.

## [1.3.0] — 2026-07-22

The "quality & efficiency" line: a deterministic-first review harness (Divine Eye), stronger
input integrity, geometry-truth gates, and reference-grounded texture/material analysis.

### Added — Plan 1.3 (Phases 1–7)
- **Input integrity** — reference admission (`check_reference_admission.py`), intake-correctness
  cross-check (`check_intake_correctness.py`), property auto-binding, shared pHash.
- **Geometry truth** — curve-sweep (F.6), flatness gate (G.1), Blum lathe-profile derivation.
- **Divine Eye** — deterministic multi-signal ensemble (`divine_eye.py`): IoU/scale hard gates;
  proportion / symmetry-parity / pHash / SSIM / edge / blowout / flat / tonal-parity soft signals;
  self-uncertainty `probe` routing.
- **Multi-angle** — degenerate-view detection (`diagnose_render_multi_angle.py`) with reference-free
  self-consistency; auto-framing.
- **Eye judgment layers** — gated VLM gate (`vlm_gate.py`), per-feature verification (§3.8),
  bounded stop policy (§3.6), calibration harness (report-only + separation check).
- **Efficiency** — per-module codegen cache (§3.7 neighbor invalidation).
- **Presentation** — reference-conditional post-fx (DOF/bloom) strictly off the evaluation path.

### Added — session capability work (folded into 1.3)
- **Texture-finish analysis** — `stage1_intake/analyze_texture.py`: classifies finish
  (gem-metal / gemstone / painted-metal / worn-composite / brushed-steel / plastic) and writes
  doc-grounded MeshPhysicalMaterial scalars; `grimoire/build/threejs_texture_reference.md`.
- **Objectness (OSIM-lite)** — `stage4_review/objectness.py`: pure-stdlib HOG-like descriptor +
  cosine similarity; wired into Divine Eye as a soft signal + reconstruction-mode rescue.
- **`ground-blade` primitive** — lofted beveled cross-section (primary bevel + swedge/false edge)
  in the generator + validator whitelist.
- **Color-gate fix** — `diagnose_render.py` `color_is_gated(pass_id)` (color hard-fail only from
  the material pass onward, so clay blockouts don't false-fail).

### Notes
- Pure Python 3.10+ stdlib in `forge/` (no pip installs). 16/16 forge test suites green at tag.
- Grimoire lessons updated: shading realism (hue-survival under tone-mapping; reference beats prose),
  geometry patterns, self-correction.

## [1.2.0] — prior
- Staged sculpting pipeline (blockout → structure → form → material → lighting → interaction →
  optimization), pass-gated generator, Tier-1 diagnostics, comparison-sheet review loop.
