# img2threejs

Rebuild the object in a reference image as a **code-only, procedural Three.js model** — quality-gated, animation-ready, and deliberately token-efficient. This is reconstruction-by-code, not photogrammetry, mesh extraction, or downloaded art packs.

![img2threejs demo — a reference loot-chest image reconstructed as a procedural Three.js model](assets/demo.gif)

*Above: a single reference image reconstructed in code — correct proportions, colours, bevels, gold trim, and an emissive emblem — running live in the browser.*

---

## What it does

You give it one reference image of an object. It produces a `THREE.Group` factory written in TypeScript that recreates that object from primitives, procedural shaders, and generated geometry — with a runtime hierarchy (pivots, sockets, colliders) so the result is ready to animate, not an inert lump.

It works under Claude Code, Codex, or OpenCode. It is agent-agnostic: wherever the docs say "agent vision" or "agent browser tool", it uses whatever the host provides (native image reading, a browser MCP, the project preview, or a user-supplied screenshot).

---

## Why it is token-efficient

Most image-to-3D agent loops burn tokens by asking the model to do mechanical work — re-reading the whole model every pass, scoring pixels, validating JSON by hand, re-running steps it already did. img2threejs pushes all of that into deterministic scripts and spends model tokens only where judgment is actually required.

- **Scripts enforce, the model judges.** Ten Python scripts handle validation, gating, spec authoring, PBR extraction, comparison-sheet packaging, and pipeline state. They never score visuals. The model's tokens go to one thing: looking at a single side-by-side sheet and deciding pass or fail.
- **Zero dependencies, zero install churn.** Every script is pure Python 3.10+ standard library. No pip, no PIL, no numpy, no Playwright. PNG read/write is done with `struct` and `zlib`. Nothing to install means nothing to debug in-context.
- **Pass-gated generation.** The code generator emits only the currently unlocked build pass. The model does not regenerate or re-read the entire model on every iteration — each step is small and scoped.
- **Fail fast, before codegen.** A strict-quality gate blocks shallow specs before a single line of Three.js is generated, so you never spend tokens rendering and re-doing a model that was underspecified from the start.
- **One image per review.** Each pass is judged from exactly one packaged comparison sheet (reference beside render), not a scattering of screenshots.
- **Text output, not binaries.** The result is diffable TypeScript plus a JSON spec — small, reviewable, and version-controllable, instead of multi-megabyte mesh files.

The net effect: you still get a faithful 3D model from an image, but the expensive model context is reserved for visual judgment and code, not bookkeeping.

---

## How it works

The skill runs a staged sculpting pipeline. Scripts gate each stage; the agent's vision is the only thing that can approve a pass.

```mermaid
flowchart TD
    A[Reference image] --> B[Probe and suitability gate]
    B --> C[Pre-Spec Assessment<br/>class, complexity, quality contract]
    C --> D[Author ObjectSculptSpec<br/>components, materials, sockets]
    D --> E{Validate and strict-quality}
    E -- too shallow --> D
    E -- ok --> F[Locked build passes]
    F --> G[Generate Three.js factory<br/>current pass only]
    G --> H[Render in browser and screenshot]
    H --> I[Package one side-by-side sheet]
    I --> J{Agent vision review}
    J -- score below threshold --> K[Self-correct:<br/>refine-spec or refine-code]
    K --> F
    J -- pass --> L{More passes?}
    L -- yes --> F
    L -- no --> M[Animation-ready Three.js model]
```

### The build passes

The model is sculpted in a fixed order, and a pass only unlocks after the previous one is reviewed and accepted:

`blockout` to `structural-pass` to `form-refinement` to `material-pass` to `surface-pass` to `lighting-pass` to `interaction-pass` to `optimization-pass`

Each pass has its own acceptance criteria. A pass can be marked `continue` only with a real render, a comparison sheet, an agent-vision score at or above threshold, and every identity-defining feature at or above its own threshold.

### The gates

- **Suitability** — is the image a viable 3D target at all.
- **Pre-spec and strict-quality** — blocks code generation until the spec is deep enough for the object's complexity (no single-root spec for a compound object).
- **Screenshot feedback** — `continue` requires a render plus a comparison sheet plus a passing vision score.
- **Action-ready** — the model must expose a runtime hierarchy (pivots, sockets, colliders, destruction groups) via `root.userData.sculptRuntime`.
- **Attachment correctness** — child parts (handles, limbs, tubes) must declare how they join their parent, so nothing floats in mid-air.
- **Material and lighting realism** — independent PBR channels and real lights, never albedo aliased into roughness.

### Self-correction

After every pass the agent chooses exactly one action: `continue`, `refine-spec`, `refine-code`, `request-input`, or `stop`. `refine-spec` fixes a wrong or shallow spec and re-validates; `refine-code` fixes geometry, material, or lighting that does not match a sound spec.

---

## Quick start

1. **Install** — place this folder in your skills directory:

   ```bash
   git clone https://github.com/hoainho/img2threejs.git ~/.claude/skills/img2threejs
   ```

2. **Invoke** — in Claude Code, attach or point to an object image and run:

   ```
   /img2threejs Rebuild this object as a Three.js model, keep the proportions, angles, and colours.
   ```

3. **Follow the pipeline** — the skill validates the image, writes an assessment and spec, generates the factory pass by pass, and shows you a side-by-side comparison at each step until the render matches.

The scripts run from the skill root. They need only Python 3.10+ — nothing to install.

```bash
python3 scripts/probe_reference_image.py <image>
python3 scripts/new_pre_spec_assessment.py "Name" --image <image> --out assessment.json
python3 scripts/new_sculpt_spec.py "Name" --image <image> --assessment assessment.json --out spec.json
python3 scripts/validate_sculpt_spec.py spec.json --strict-quality
python3 scripts/generate_threejs_factory.py spec.json --out src/createObjectModel.ts
```

---

## Scripts

| Script | Role |
| --- | --- |
| `probe_reference_image.py` | Image metadata and obvious technical issues (not a visual check). |
| `new_pre_spec_assessment.py` | Classify the object, score complexity, emit a quality contract. |
| `new_sculpt_spec.py` | Author the ObjectSculptSpec from the assessment. |
| `validate_sculpt_spec.py` | Validate the spec; `--strict-quality` blocks shallow specs before codegen. |
| `extract_reference_pbr.py` | Reference-derived PBR evidence per crop (inference, not inverse rendering). |
| `sculpt_pass_orchestrator.py` | Locked pass state: status, check, sync. |
| `generate_threejs_factory.py` | Emit the Three.js `Group` factory for the current unlocked pass. |
| `make_visual_comparison_sheet.py` | Package one reference-vs-render sheet for review. |
| `append_sculpt_review.py` | Record a per-pass review: scores, decision, evidence. |
| `visual_feature_gate.py` | Internal helper enforcing per-feature score thresholds. |

The `references/` folder holds the detailed rubrics each gate applies (validation, pre-spec assessment, procedural patterns, material and lighting realism, attachment correctness, action-ready models, self-correction).

---

## What you get

- An `ObjectSculptSpec` JSON: the full component tree, materials, repetition systems, sockets, and a recorded review history for every pass.
- A TypeScript `createObjectNameModel(spec, options)` factory returning a `THREE.Group`, with `root.userData.sculptRuntime` exposing nodes, sockets, colliders, and destruction groups.
- A render plus comparison sheets documenting the fidelity at each pass.

---

## Requirements

- Python 3.10+ (standard library only).
- A Three.js project or preview to render into (any modern bundler).
- A host that can read images and capture a browser screenshot (Claude Code, Codex, or OpenCode with a browser tool or user-supplied screenshots).

---

## Honesty about limits

A single image cannot reveal hidden sides or guarantee exact geometry. The skill states plainly when output is approximate, stylized, or low-poly, and infers unseen faces by mirroring visible ones rather than faking confidence. "This cannot reach the requested fidelity from this image" is a valid, expected result.

---

## License

MIT.
