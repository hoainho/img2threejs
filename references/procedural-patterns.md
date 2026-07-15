# Procedural Three.js Object Patterns

Use this reference only when implementing a model.

## Geometry Choices

- box: flat machinery, furniture, panels, blockout masses
- sphere/ellipsoid: fruit, knobs, organic joints, rounded stones
- cylinder/cone/capsule: trunks, pipes, limbs, handles, bottles, rockets
- torus: rings, tires, loops, trim, cable coils
- shape extrude: logos, flat ornamental plates, blades, keys, leaves
- lathe: vases, bottles, bowls, lamps, wheels
- tube along curve: cables, roots, branches, straps, hoses
- instanced mesh: screws, rivets, leaves, needles, scales, pebbles, repeated ornaments
- plane cards: thin leaves, feathers, labels, cloth strips, decals

## Material Recipes

- wood: brown base, vertical grain normal, roughness variation, darker creases, lighter worn edges
- stone: mottled albedo, high roughness, bump/normal noise, lichen/dirt patches
- metal: lower roughness, metalness, edge scratches, anisotropic-looking streaks via texture
- plastic: controlled roughness, subtle color variation, bevels to catch highlights
- leaf/plant: alpha cards or thin shape geometry, green hue variation, central vein, translucent-ish bright rim
- water/glass: transparent material only if needed; add environment/reflection cues or it reads as a flat sheet

## Material Layer Fields

For each material, prefer a layered description:

- `baseColor`: dominant sampled color.
- `colorVariation`: palette, mottling pattern, amplitude, regional masks.
- `roughness`: base value, variation amount, map/pattern source.
- `metalness`: base value and local changes.
- `normal`: procedural pattern, strength, scale.
- `bump`: amplitude and scale for small tactile relief.
- `displacement`: only for silhouette-visible or close-up relief.
- `wear`: edge wear, scratches, chips, polish, exposed underlayer.
- `dirt`: amount, cavity bias, color, vertical streaking, contact staining.
- `localOverrides`: named regions where color/roughness/bump differs from the base.

Local overrides should answer: where, what changes, how strong, and which image evidence supports it.

## Local Feature Types

Use `component.localFeatures` for details that matter to recognizability:

- raised ridge
- recessed groove
- seam line
- screw or rivet
- chip or dent
- scratch cluster
- stain or dirt patch
- decal or label area
- hole or socket
- bevel highlight
- fabric stitch
- leaf vein or serrated edge

Each feature should include placement, approximate size, orientation, material effect, geometry effect, and confidence.

## Verification Cues

A procedural object is usually failing when:

- silhouette reads wrong even before material
- every edge is perfectly sharp or perfectly smooth
- material has one flat color and no roughness variation
- lighting hides the form instead of explaining it
- repeated details are too evenly spaced
- close-up details add triangles but not recognizability
