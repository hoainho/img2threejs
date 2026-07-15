# Object Image Validation Rubric

Use this reference when the suitability decision is unclear.

## Pass

- one obvious target object
- object occupies enough of the frame
- at least one strong silhouette
- major materials are visible
- hidden side can be reasonably inferred
- target can be approximated with procedural primitives

## Conditional

- one view only but object has rotational symmetry
- some occlusion but macro shape is clear
- fine surface detail can be represented with procedural texture
- target is organic but user accepts stylization
- exact brand/logo/text fidelity is not required

## Reject

- target object is ambiguous
- photo is a scene, not an object reference
- important shape is hidden, cropped, blurred, or transparent
- request demands exact mesh extraction or manufacturing-grade dimensions
- object relies primarily on hair, smoke, liquid, glass caustics, lace, or complex cloth folds

## Ask For Better Input

Ask for:

- front, side, and back views
- a neutral background
- higher resolution
- close-ups of material/detail
- desired style: realistic, stylized, low-poly, game prop, hero render

## Complex Object Detail Standard

For objects with many details, require:

- macro components for the overall mass
- meso components for visible sub-assemblies
- micro components or local features for repeated/tiny details
- material layer stack for every visually distinct surface
- local overrides for stains, scratches, dirt, color changes, wear, bumps, and roughness shifts
- confidence per component or feature
- evidence refs to image regions

If these cannot be inferred from the image, mark the spec `conditional` and list missing views or close-ups.
