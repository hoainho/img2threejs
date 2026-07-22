# img2threejs Roadmap

This roadmap outlines the planned evolution of img2threejs from its initial release through major feature additions. For the full technical specification, requirements, and acceptance criteria, see [docs/UPGRADE_PLAN.md](docs/UPGRADE_PLAN.md).

## Version status

| Version | Theme | Status | Highlights |
|---|---|---|---|
| v1.0 | Object pipeline | Shipped | Staged sculpt pipeline (blockout through optimization), render-vs-reference review loop, action-ready runtime hierarchy |
| v1.1 | Detail-first analysis | Shipped | Required detailInventory artifact (gloss, bevel, fasteners, linework, stains), strict-quality gate blocking shallow specs before codegen |
| v1.2 | Humanoid character generator | Shipped | Character/hybrid domain detection, anatomy and facial landmarks, proportion-lock and feature-placement build passes, per-part character materials |
| v1.3 | Likeness maximization | Planned | Projection-first path wired into character rendering (camera solve, de-lighting, texture projection), opt-in generativeAssist mode with confidence reporting, high-likeness character demo |
| v1.4 | Animation-ready rigs | Planned | True humanoid rig and pivot hierarchy (replacing current world-space flatten), SkinnedMesh with morph targets, glTF export |
| v1.5 | Ecosystem | Planned | Expanded live demo gallery accepting community demos via pull request, broader host and agent coverage, measured token-cost benchmark replacing current estimates |

## Version details

### v1.0 - Object pipeline
The foundational release introduces the staged reconstruction pipeline for hard-surface objects. Images are analyzed for suitability, authored into an ObjectSculptSpec describing components and materials, then generated pass by pass as Three.js code. Each pass gates on a visual review using side-by-side comparison sheets. The result exposes a runtime hierarchy (pivots, sockets, colliders) ready for animation.

### v1.1 - Detail-first analysis
Micro-detail capture becomes a required, evidence-linked artifact with its own validation gate. A detail inventory enumerates identity-defining small features (gloss zones, bevels, screws and rivets, engraved or painted lines, contours, stains and wear). Every detail must map to a real component or material entry, and the strict-quality gate blocks code generation until the inventory is complete and linked. This prevents shallow specs from reaching the renderer.

### v1.2 - Humanoid character generator
Characters and hybrid subjects are now first-class. The pipeline detects character-like form language and routes the reconstruction through an anatomy-aware track. A humanoid component template with measured head-unit proportions, facial landmark placement, and pose alignment emerges from the assessment. Build passes for proportion-locking and feature-placement gate on anatomical correctness. Per-part character materials (skin, hair, cloth, accessories) integrate with the Track A detail machinery, producing stylized human figures with correct proportions and recognizable likeness.

### v1.3 - Likeness maximization
The projection-first path maximizes likeness for specific people or characters. A parametric humanoid template is fitted to image landmarks, the reference photo is de-lit and camera-matched, then projected onto the fitted mesh as texture. This achieves significantly higher visual fidelity than hand-authored primitives. An optional, clearly flagged generativeAssist mode allows import of a base mesh from external image-to-3D generators, then applies the same projection and material pipeline. Per-region confidence reporting acknowledges unobservable areas (back, sides, occluded geometry) and requests additional views when fidelity matters. A high-likeness character demo showcases the technique.

### v1.4 - Animation-ready rigs
The character rig moves from a flattened world-space hierarchy to a proper animated skeleton with named joints (neck, shoulders, elbows, hips, knees, ankles). SkinnedMesh deformation and morph targets enable facial expression and body deformation. Clean, predictable mesh topology supports blendshape deformation without artifacts. The rig and morph channels export as glTF and integrate with industry-standard animation tools and game engines. Model-level GLB export from the viewer (`export/glbExporter.js`) ships ahead of the rig work, so any current model can already be exported to `.glb` for Blender.

### v1.5 - Ecosystem
The project expands beyond a single skill into a broader ecosystem. A live demo gallery on the project site showcases community reconstructions accepted via pull request, lowering the barrier to sharing results. Coverage extends to more Claude hosts (Codex, OpenCode) and browser automation MCPs. Token costs are measured empirically across real reconstructions rather than estimated, replacing the current engineering-estimate model with a reproducible benchmark. This version solidifies the pipeline as a reference implementation for single-image 3D reconstruction by code.

## Contributing

img2threejs welcomes contributions. For planning or submitting work on v1.3 and later features, see [CONTRIBUTING.md](CONTRIBUTING.md). Feature requests and bug reports help prioritize future releases. The roadmap is responsive to real-world usage and feedback from the open-source community.
