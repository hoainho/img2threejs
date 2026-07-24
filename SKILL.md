---
name: img2threejs
description: Turn an object or character reference image into a quality-gated, animation-ready procedural Three.js model built in code. Use for image-to-3D reconstruction, detail-accurate object rebuilds, stylized/likeness-maximized human characters, sculpt specs, and staged code generation.
license: MIT
version: 1.3.0
---

# img2threejs — Image to procedural Three.js

Rebuild the object visible in a reference image as a **code-only** procedural Three.js model,
gated by a staged sculpting pipeline and an AI-vision self-correction loop. This is
reconstruction-by-code, **not** photogrammetry, mesh extraction, or downloaded art packs.

Agent-agnostic: works under Claude Code, Codex, or OpenCode. Wherever this doc says "agent
vision" or "agent browser tool", use whatever the host provides — native image reading, a
browser MCP (playwright/chrome-devtools), the project preview, or a user-supplied screenshot.

## When To Use

The user attaches/points to an object image and wants a procedural Three.js model, a
reconstruction/animation/destruction plan, a sculpt spec, or code. Also for material studies,
action-ready props, game objects, botanical/mechanical parts, and stylized reconstructions.

## Core Promise

Sculpt from a photo, in order — never one-shot a mesh:
1. **Validate** the image is a suitable 3D target (`grimoire/intake/validation_rubric.md`).
2. **Assess** object class + complexity, then write a `qualityContract` before any code.
3. **Spec** it: component hierarchy, materials, lighting, pivots, sockets, action anchors.
4. **Build pass-by-pass** from blockout → structure → form → material → lighting → interaction → optimization.
5. **Verify** each pass with a screenshot compared against the reference; fail a pass if an identity-defining feature is wrong even when the global score looks fine.

State explicitly when output is approximate/stylized/low-poly. A single image cannot reveal
hidden sides or guarantee exact geometry — say so instead of faking confidence.

## Transparency and Process Debugging (Critical — from Bowie Knife reconstruction)

**The problem:** When the user cannot tell what was done or where something went wrong, they cannot debug the process. Over-claiming (reporting success when features still don't match) destroys trust and makes iterative improvement impossible.

**Rule:** Be transparent + don't over-claim. State exactly what changed each pass, with evidence, and name what still doesn't match:
- After each pass, explicitly list what changed: "Updated guard shape to extend left edge from -0.56 to -0.48 for handle overlap"
- Provide evidence: reference the specific values, coordinates, or parameters that changed
- Name what still doesn't match: "Handle silhouette traced but still flat plane (no Z palm-swell), procedural crosshatch not reference's exact dot-grid knurl"
- Explain why a change was made: "Extended guard left edge because handle ends at X=-0.42 and guard ended at X=-0.20, causing visual gap"
- Never claim a feature is "done" when it's only "improved" — use precise language
- When a gate passes but visual inspection shows issues, explain the limitation: "2D gate passed (fidelity 0.83) but three-quarter render shows blade reads as toy (no grind wedge) — 2D gates are blind to 3D realism"

**The user needs to be able to debug the process, not just the output.** If something is wrong, they should be able to trace which decision led to the error and correct it. Opaque processes force restarts; transparent processes enable refinement.

## Required Inputs

- one image path / screenshot / URL / attached image (if missing or unreadable, ask)
- intended use: prop, game object, hero render, playable/destructible object, animation rig
  (default: real-time browser prop with interactive performance)

## The Loop (scripts do enforcement; agent vision does judgment)

Run scripts from the skill root (`forge/...`). Pure Python 3.10+ stdlib, no pip installs.
Full flags: `grimoire/scripts.md`. Never let a script *score* visuals — that is the agent's job.

1. **Analyze the image first** (agent vision, before any script): work the layered observation
   protocol in `grimoire/intake/image_analysis.md` — identify/classify, decompose macro→meso→micro,
   map part relationships, name materials in PBR terms, list identity-defining features, and flag
   what the single view hides. Observation before inference; controlled 3D vocabulary; 3D
   object-space not 2D image-space. This is generic for any subject and feeds every field below.
   Then probe local images: `forge/stage1_intake/probe_image.py <image>` (metadata only, not a visual check).
2. **Pre-Spec Assessment Gate** — classify + score complexity + write the quality contract:
   `forge/stage2_spec/new_pre_spec_assessment.py "Name" --image <img> --complexity <simple|moderate|complex|ultra-complex> --out assessment.json`. Rules: `grimoire/intake/quality_contract.md`.
   Set `objectClass.primaryDomain` (`object` | `character` | `hybrid`) and fill the seeded
   `detailInventory` (its `targetMinDetails` scales with complexity). **CS2 weapon/knife/glove
   skins**: always pass `--cs2`, which defaults the complexity tier to `ultra-complex`
   (`targetMinDetails` 16) — the finish/wear/hardware is the item, so CS2 is held to the top
   fidelity bar; `targetMinDetails` never drops below the 9 floor even if downgraded by hand.
   **Author procedural GEOMETRY (blade/guard/grip profiles) but make the FINISH a de-lit
   reference-crop PROJECTION, not a procedural finish material** — projecting the photo's own
   pixels is what reaches reference fidelity for patterned skins (Doppler/Gamma/Marble/Fade), and
   is what the v1.3 baseline demos do; a procedural finish for a patterned skin reads visibly wrong
   against the reference. Take the projection path in step 2c (it generalizes from characters to
   any reference-matched surface). Procedural finish is the fallback ONLY when live view-dependent
   response matters more than matching this one reference. Finish routes + rulebook:
   `grimoire/build/cs2_finishes.md`; optional exact-texture acquisition:
   `grimoire/intake/cs2_texture_acquisition.md`.
2b. **Detail inventory** (do not skip for detailed subjects) — scan zones and enumerate every
   identity-defining small detail (gloss, bevel, fasteners, linework, contours, stains):
   `forge/stage1_intake/build_detail_inventory.py <image> --mode grid-3x3 --out-dir <dir> --out di.json`.
   Each detail MUST map to a `component.localFeatures` or `material.localOverrides` entry — never
   prose only. Taxonomy + 3D-term recipes: `grimoire/intake/detail_inventory.md`.
2c. **Projection-first fidelity (characters AND reference-matched surfaces — CS2 skins, decals,
   painted patterns)** — when the goal is matching a specific reference's surface, put the photo's
   own pixels on the mesh instead of approximating them procedurally. This is the single biggest
   fidelity lever; a procedural material for a patterned surface is the #1 reconstruction failure.
   Recipe (`grimoire/character/likeness_maximization.md` — its two levers, align-mesh+camera and
   project-the-photo, generalize past characters): solve the camera
   (`stage1_intake/solve_camera_pose.py` → `referenceCamera`), **de-light** the reference so it is
   free of baked lighting (`stage1_intake/delight_albedo.py`, hard requirement — this is what makes
   projection safe, not the flat-lit icon), then project the de-lit crop onto the mesh and bake it
   into UVs (`stage3_build/bake_projected_texture.py --mesh-id <id>`). For a CS2 skin the mesh is the
   procedural blade/guard/grip you author in the spec, and the projected de-lit crop IS the finish
   (front + back from the two views) — no procedural Doppler material. For characters, first capture
   landmarks (`stage1_intake/extract_landmarks.py --out anatomy.json`), fill `preSpecAssessment.anatomy`,
   route `grimoire/character/reconstruction.md`. A single view cannot show hidden sides — report
   per-region confidence and request more views when it matters.
3. Author the spec from the assessment:
   `forge/stage2_spec/new_sculpt_spec.py "Name" --image <img> --assessment assessment.json --out object-sculpt-spec.json`.
   Replace generic starter `featureReviewTargets` with the object's real identity-defining
   systems (≤5 critical, ≤3 important per pass); for characters add `anatomy-proportion`,
   `face-landmark-placement`, `pose-silhouette`, `outfit-and-palette`. Use 3D-graphics terms only
   (`grimoire/glossary/3d_vocabulary.md`), never "nice/smooth/shiny". Classify every component's
   `topologyClass`/`topologyRationale` per `grimoire/intake/surface_topology.md` before picking a
   `primitive` — this is what prevents a continuous organic form from being picked as a box.
4. When material fidelity matters and a source image exists, analyze each material's **finish** then
   extract reference PBR evidence, both per crop (crop the correct region — verify the crop is on the
   part you think it is):
   - `forge/stage1_intake/analyze_texture.py <crop> --spec spec.json --material-id <id> --in-place`
     classifies the finish (`gem-metal | gemstone | painted-metal | worn-composite | brushed-steel |
     plastic`), extracts the gradient palette, and writes doc-grounded MeshPhysicalMaterial scalars
     (metalness/roughness/clearcoat/transmission/ior/anisotropy/envMapIntensity) onto the material.
     Recipes + Three.js texture/PBR rules (colorSpace, CanvasTexture/DataTexture, height→normal) live
     in `grimoire/build/threejs_texture_reference.md`. Rule of thumb: **solid albedo for flat paint,
     real reference crop for patterned finishes** (doppler/quartz/hydro-dip/camo).
   - `forge/stage1_intake/extract_pbr_evidence.py <crop> --out-dir <dir> --material-id <id> --target-threshold 0.7`.
   Confidence < 0.7 is a stop/refine-input signal, not a pass. It is inference, not inverse rendering.
5. Validate, then strict-validate before generating code:
   `forge/stage2_spec/validate_sculpt_spec.py object-sculpt-spec.json` then `--strict-quality`.
   Strict blocks shallow specs (a complex object with one root, no repetition systems, no
   local overrides, no micro groups is NOT implementation-ready even if JSON validates).
6. **Locked build passes** — only touch the currently unlocked pass:
   `forge/stage3_build/orchestrate_passes.py status object-sculpt-spec.json`
   `forge/stage3_build/orchestrate_passes.py check object-sculpt-spec.json --pass-id <pass>`
   `forge/stage3_build/generate_threejs_factory.py object-sculpt-spec.json --out src/createObjectModel.ts`
   (generator is pass-gated: a future `--pass-id` fails until prior passes are reviewed `continue`).
7. Render the current pass in a browser/preview, capture a screenshot at a review viewpoint.
8. Package one side-by-side sheet, then inspect it with agent vision:
   `forge/stage4_review/make_comparison_sheet.py --reference <img> --render <shot> --out cmp.png --json`.
9. Record the review (overall + per-layer + per-feature scores + decision):
   `forge/stage4_review/append_review.py object-sculpt-spec.json --pass-id <pass> --fidelity <0-1> --action <continue|refine-spec|refine-code|request-input|stop> --summary "..." --render-screenshot <shot> --comparison-image cmp.png --ai-vision-score <0-1> --layer-scores-json '{...}' --feature-reviews-json <f.json> --in-place`.
10. Sync pipeline state after manual review edits:
    `forge/stage3_build/orchestrate_passes.py sync object-sculpt-spec.json --in-place`.

## Gates (do not skip)

- **Suitability + reference integrity**: pass / conditional / reject before any planning
  (`grimoire/intake/validation_rubric.md`), AND every reference admitted via
  `forge/stage1_intake/check_reference_admission.py` (rejects empty/fragmented/tiny/duplicate/
  undecodable refs with a reason). Intake understanding cross-checked by
  `forge/stage1_intake/check_intake_correctness.py` (halts on a confident class contradiction).
- **Divine Eye (the harness heart) — deterministic-first, model-last**: the render evaluator is
  `forge/stage4_review/divine_eye.py` — a zero-token multi-signal ensemble (IoU/scale HARD gates;
  proportion/symmetry-parity/pHash/SSIM/edge/blowout/flat/tonal-parity soft) with self-uncertainty
  (`probe` on signal disagreement) and deterministic routing (`continue`/`refine-spec`/`refine-code`/
  `probe`). The VLM (`forge/stage4_review/vlm_gate.py`) is a gated, calibrated, cross-checked
  last layer: **never consulted on a hard-gate failure**, multi-sample-voted, and can rescue a
  soft near-threshold reject but never grant past a hard geometric failure.
- **Multi-angle or it didn't happen**: a non-planar form must hold from ≥2 camera angles.
  `forge/stage4_review/diagnose_render_multi_angle.py` flags `degenerate-view` when an orbited
  silhouette collapses (a flat plane faking a volume). Orbit angles use reference-free
  self-consistency — never scored against a reference angle the photo doesn't cover.
- **Bounded correction loop (token-burn safety)**: `forge/stage4_review/correction_loop.py`
  guarantees termination (success/repeated-defect/oscillation/plateau/hard-ceiling), escalating to
  `request-input` — never a silent infinite burn.
- **Tier 1 (legacy, still valid)**: "Tier 2 (AI-vision) never runs against a render that has not passed Tier 1." Run `forge/stage4_review/diagnose_render.py` (silhouette IoU/proportion/symmetry/per-part color) and record it (`--spec ... --in-place`) before requesting a comparison sheet; `orchestrate_passes.py check` refuses otherwise.
- **Pre-spec / strict-quality**: blocks code gen until the spec is deep enough for its contract.
- **Screenshot feedback**: `continue` is allowed only with a render + comparison sheet + global
  AI-vision score ≥ threshold (default 0.7) AND every critical feature ≥ its own threshold.
  Details + per-layer scorecard: `grimoire/feedback/render_capture.md`.
- **Action-ready**: build a runtime hierarchy (pivots, sockets, colliders, destruction groups),
  never an inert lump; expose `root.userData.sculptRuntime`. `grimoire/readiness/action_rigging.md`.
- **Attachment**: child appendages (branches/limbs/handles/tubes) need `attachment.parentSocket`,
  `localStart`, `localEnd`, `contactType`, `embedDepth`/`overlap`, `gapTolerance` — no mid-air parts.
  `grimoire/readiness/joint_attachment.md`.
- **Material/lighting**: `grimoire/feedback/shading_realism.md` — independent PBR channels
  (never alias albedo into roughness/normal/AO), macro/meso/micro frequency bands, real lights.
- **Detail inventory**: for `moderate`+ subjects strict-quality blocks code gen until the
  `detailInventory` reaches `targetMinDetails` and every detail maps to a real component/material
  entry (gloss needs low-roughness/clearcoat; fasteners need instancing/micro parts).
- **Character track**: when `primaryDomain` is `character`/`hybrid` (or `--character`), the spec
  author auto-builds a stylized humanoid template (head/neck/torso/arms + hair, glasses,
  headphones, face features), flattened to world space under a hidden root, with per-part
  character materials and character build passes (`proportion-lock`, `feature-placement`).
  strict-quality requires a filled `anatomy` block (head-units, proportions, face landmarks) and
  character feature targets. Suitability routing for humans: `grimoire/intake/validation_rubric.md`
  (stylized vs maximum-likeness). Stylized bust, not a face-copy; refine positions per reference.

## Self-Correction

After every pass, decide exactly one: `continue | refine-spec | refine-code | request-input | stop`.
`refine-spec` fixes a wrong/missing/shallow spec (re-validate, don't patch code around it);
`refine-code` fixes geometry/material/lighting that doesn't match a sound spec. Full root-cause
guide + fidelity scale: `grimoire/review/self_correction.md`.

## Implementation Rules (brief)

TypeScript + plain Three.js unless the project uses a wrapper. `Group` factory
`createObjectNameModel(spec, options)`, reconstruction data kept separate from renderer objects,
deterministic seeds for all procedural noise. Prefer primitives / `Shape` extrude / curve+tube /
instancing / displacement / generated canvas textures before any external art. Full geometry &
material recipes + hard-won failure patterns: `grimoire/build/geometry_patterns.md`.

## Output

- **Analysis-only**: suitability verdict + scores, object extraction, macro→micro hierarchy,
  geometry strategy, material/lighting recipe, animation/destruction feasibility, plan + risks.
- **Implementation**: the above briefly, then edit code; verify with typecheck/build + a screenshot.
- **Not feasible**: name the blocker, ask for more views / cleaner image / accepted stylization /
  a narrower target. "This cannot reach the requested fidelity from this image" is a valid result.
