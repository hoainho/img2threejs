# CS2 Texture Acquisition (optional exactness upgrade)

This is **not** part of the default image-first path. It is an optional Tier-3 upgrade for exact
texture likeness, driven autonomously by the host agent from the **user's own legal CS2 install**.
The user performs no manual step beyond, at most, pointing at the install / VPK path. If nothing is
found the agent falls back to the image-only reconstruction — it never fabricates a wrong render.

**IP boundary (hard rule):** extracted textures are Valve IP. They stay in the local, gitignored
`cs2_textures/` workspace and are **never** committed or redistributed. The MIT repo ships code
only. `.gitignore` excludes `cs2_textures/`; a test asserts nothing under it is
tracked.

## Steps

### 1. Metadata (optional, no install needed) — `forge/stage1_intake/fetch_cs2_metadata.py`

Resolve the skin's paint index, float range, rarity, and CDN image URL from the public CSGO-API
skins index (`--index-file` local, or `--index-url` live):

```
fetch_cs2_metadata.py --weapon Karambit --skin Doppler --phase "Phase 2" \
    --index-file skins.json --out metadata.json
```

A no-match or an ambiguous multi-match is an **error** (nonzero exit), never a silent guess — add
`--phase` to disambiguate. This gives the precise paint index for a Tier-2 descriptor even without
extracting textures.

### 2. Locate the VPK — `forge/stage1_intake/locate_cs2_vpk.py`

```
locate_cs2_vpk.py --json          # or --root <steam-root> (repeatable) to override
```

Searches per-OS default Steam roots plus any libraries declared in `steamapps/libraryfolders.vdf`,
for `.../Counter-Strike Global Offensive/game/csgo/pak01_dir.vpk`. Best-effort and non-fatal:
prints `{"found": false, ...}` and exits 1 when nothing is located (never raises). `--root` is
dependency-injectable for offline testing.

### 3. Extract + classify — `forge/stage1_intake/extract_cs2_textures.py`

Requires `Source2Viewer-CLI` on `PATH` (which needs the .NET runtime). Assert availability first,
then extract into the gitignored workspace and bucket the output maps by filename convention
(`color` / `normal` / `roughness_metalness` / `mask` / `other`):

```
extract_cs2_textures.py --out cs2_textures --json     # --vpk <path> to skip locating
```

On any failure — no VPK, missing binary, subprocess error, or non-zero exit — it returns
`{"status": "fallback", "reason": ...}` and exits 1, so the pipeline degrades to the image-only
path with an explicit notice that exact texture likeness is unavailable. On `Source2Viewer-CLI`
flag drift, consult its `--help` and adapt the wrapped call in `run_source2viewer()`; if it still
fails, report and fall back rather than guessing.

## Using the result

Feed the classified maps into the finish material's PBR channels (color → albedo, normal → normal,
packed → roughness/metalness, mask → wear/pattern) to raise fidelity above the procedural
image-only recipe. The finish-style machinery (PBR ranges, environment, wear) in
`grimoire/build/cs2_finishes.md` still applies — it drives *realism* independent of whether exact
textures were acquired.
