#!/usr/bin/env python3
"""The Divine Eye (đôi mắt thần) — deterministic multi-signal render↔reference evaluator.

Plan 1.3 Phase 3 core (§3.1 ensemble, §3.3 combination + self-uncertainty). This is
the single authority the correction loop asks "how close is this render to the
reference, and what's wrong?". It is DETERMINISTIC and ZERO-TOKEN: pure Python +
pixel math, reusing the Tier-1 primitives (diagnose_render) + the shared pHash. No
LLM/VLM call lives here — the VLM layer (§3.4) is a separate, gated, subordinate step.

Signals (each → normalized [0,1] agreement + a defect tag when it fails):
  HARD gates (a fail cannot be averaged away):
    - silhouette IoU        (< 0.85 ⇒ reject)
    - scale delta           (> 0.08 ⇒ reject)
  SOFT signals (ensemble-weighted):
    - proportion / aspect ratio
    - bilateral symmetry
    - pHash structural similarity
    - global SSIM (luma)
    - edge-map overlap (Sobel linework)
    - blowout parity (QA: blown-highlight fraction vs reference)
    - flat-region ratio (QA: material reacting to light, not a dead flat fill)
    - tonal/contrast parity (QA: luma-histogram match)

Deferred to later Phase-3 increments (documented, not silently missing):
  Directional Chamfer Distance, OSIM objectness (numpy+weights, R-DEP/R-OSIM-EFFORT),
  multi-angle browser capture (diagnose_render_multi_angle.py), CIE-Lab per-region ΔE
  wiring (available via extract_part_color_recipe; folded in with per-feature §3.8).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_render import (  # noqa: E402
    bbox_of,
    bilateral_symmetry_error,
    load_mask,
    proportion_delta,
    silhouette_iou,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "stage1_intake"))
from extract_pbr_evidence import load_image  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_shared"))
from image_hash import normalized_similarity, phash_from_image  # noqa: E402

# Hard-gate thresholds (shared with diagnose_render; calibratable in Phase 5).
IOU_HARD_MIN = 0.85
SCALE_HARD_MAX = 0.08
# Ensemble: fidelity target + disagreement (self-uncertainty) spread.
FIDELITY_TARGET = 0.85
DISAGREEMENT_SPREAD = 0.35  # if soft-signal spread exceeds this ⇒ low-confidence → probe
LUMA_SIZE = 64   # SSIM / tonal / blowout / flat work on this downsampled luma grid
EDGE_SIZE = 96   # edge overlap grid


def load_luma(png_path: Path, size: int) -> list[float]:
    """Box-average downsample of Rec.709 luma to size×size, normalized 0..1."""
    width, height, pixels, _warn = load_image(png_path)
    acc = [0.0] * (size * size)
    cnt = [0] * (size * size)
    for idx, (r, g, b, _a) in enumerate(pixels):
        x = idx % width
        y = idx // width
        if y >= height:
            break
        cell = min(size - 1, y * size // height) * size + min(size - 1, x * size // width)
        acc[cell] += (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
        cnt[cell] += 1
    return [acc[i] / cnt[i] if cnt[i] else 0.0 for i in range(size * size)]


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def global_ssim(a: list[float], b: list[float]) -> float:
    """Single-window SSIM over the whole downsampled luma image (structure signal)."""
    n = len(a)
    if n == 0 or len(b) != n:
        return 0.0
    mu_a, mu_b = _mean(a), _mean(b)
    var_a = _mean([(x - mu_a) ** 2 for x in a])
    var_b = _mean([(x - mu_b) ** 2 for x in b])
    cov = _mean([(a[i] - mu_a) * (b[i] - mu_b) for i in range(n)])
    c1, c2 = 0.01 ** 2, 0.03 ** 2
    ssim = ((2 * mu_a * mu_b + c1) * (2 * cov + c2)) / (
        (mu_a ** 2 + mu_b ** 2 + c1) * (var_a + var_b + c2)
    )
    return max(0.0, min(1.0, ssim))


def _sobel_edges(luma: list[float], size: int, thresh: float = 0.12) -> list[bool]:
    edges = [False] * (size * size)
    for y in range(1, size - 1):
        for x in range(1, size - 1):
            def g(dx, dy):
                return luma[(y + dy) * size + (x + dx)]
            gx = (g(-1, -1) + 2 * g(-1, 0) + g(-1, 1)) - (g(1, -1) + 2 * g(1, 0) + g(1, 1))
            gy = (g(-1, -1) + 2 * g(0, -1) + g(1, -1)) - (g(-1, 1) + 2 * g(0, 1) + g(1, 1))
            if math.hypot(gx, gy) > thresh:
                edges[y * size + x] = True
    return edges


def edge_overlap(a: list[float], b: list[float], size: int) -> float:
    ea, eb = _sobel_edges(a, size), _sobel_edges(b, size)
    inter = union = 0
    for i in range(len(ea)):
        if ea[i] or eb[i]:
            union += 1
            if ea[i] and eb[i]:
                inter += 1
    return inter / union if union else 1.0


def _blown_fraction(luma: list[float], hi: float = 0.95) -> float:
    return sum(1 for v in luma if v >= hi) / max(1, len(luma))


def blowout_parity(ref: list[float], ren: list[float]) -> float:
    diff = abs(_blown_fraction(ren) - _blown_fraction(ref))
    return max(0.0, 1.0 - diff * 4.0)  # 25% extra blown pixels ⇒ score 0


def flat_fraction(luma: list[float], size: int, eps: float = 0.02) -> float:
    """Fraction of pixels whose local gradient is ~0 (a dead flat fill)."""
    flat = 0
    total = 0
    for y in range(1, size - 1):
        for x in range(1, size - 1):
            c = luma[y * size + x]
            grad = abs(c - luma[y * size + x - 1]) + abs(c - luma[(y - 1) * size + x])
            total += 1
            if grad < eps:
                flat += 1
    return flat / total if total else 0.0


def tonal_parity(ref: list[float], ren: list[float], bins: int = 16) -> float:
    def hist(xs):
        h = [0] * bins
        for v in xs:
            h[min(bins - 1, int(v * bins))] += 1
        tot = sum(h) or 1
        return [c / tot for c in h]
    ha, hb = hist(ref), hist(ren)
    l1 = sum(abs(ha[i] - hb[i]) for i in range(bins))
    return max(0.0, 1.0 - l1 / 2.0)  # L1 over two distributions ∈ [0,2]


def evaluate(reference_png: Path, render_png: Path) -> dict[str, Any]:
    """Run all deterministic signals and combine into a verdict + routing action."""
    ref_mask = load_mask(reference_png)
    ren_mask = load_mask(render_png)
    ref_luma = load_luma(reference_png, LUMA_SIZE)
    ren_luma = load_luma(render_png, LUMA_SIZE)
    ref_edge = load_luma(reference_png, EDGE_SIZE)
    ren_edge = load_luma(render_png, EDGE_SIZE)
    rw, rh, rpx, _ = load_image(reference_png)
    vw, vh, vpx, _ = load_image(render_png)

    iou = silhouette_iou(ref_mask, ren_mask)
    prop = proportion_delta(bbox_of(ref_mask), bbox_of(ren_mask))
    scale_delta = prop.get("scaleDelta", 0.0)
    aspect_delta = prop.get("aspectRatioDelta", 0.0)
    # symmetry + flat-region are PARITY signals (render vs reference), NOT absolute —
    # a legitimately asymmetric or flat-lit subject must not be penalized when the
    # render matches the reference. score = 1 when render is as (a)symmetric / as flat
    # as the reference; drops when the render diverges (e.g. render flatter ⇒ material
    # not reacting to light).
    sym_ref = bilateral_symmetry_error(ref_mask)
    sym_ren = bilateral_symmetry_error(ren_mask)
    sym = max(0.0, 1.0 - abs(sym_ren - sym_ref) / 0.10)
    flat_ref = flat_fraction(ref_luma, LUMA_SIZE)
    flat_ren = flat_fraction(ren_luma, LUMA_SIZE)
    flat = max(0.0, 1.0 - abs(flat_ren - flat_ref) * 4.0)
    phash_sim = normalized_similarity(phash_from_image(rw, rh, rpx), phash_from_image(vw, vh, vpx))
    ssim = global_ssim(ref_luma, ren_luma)
    edges = edge_overlap(ref_edge, ren_edge, EDGE_SIZE)
    blow = blowout_parity(ref_luma, ren_luma)
    tonal = tonal_parity(ref_luma, ren_luma)

    # HARD gates: a fail is an immediate reject with a specific numeric reason.
    hard_failures: list[str] = []
    if iou < IOU_HARD_MIN:
        hard_failures.append(f"silhouette IoU {iou:.3f} < {IOU_HARD_MIN}")
    if scale_delta > SCALE_HARD_MAX:
        hard_failures.append(f"scale delta {scale_delta:.3f} > {SCALE_HARD_MAX}")

    # SOFT signals → weighted ensemble fidelity. Weights are provisional (Phase 5
    # calibrates them on the known-good/known-bad corpus); recorded here so they are
    # auditable, not magic.
    soft = {
        "proportion": (max(0.0, 1.0 - aspect_delta / 0.05), 1.0),
        "symmetry": (sym, 0.5),
        "phash": (phash_sim, 1.0),
        "ssim": (ssim, 1.5),
        "edgeOverlap": (edges, 1.0),
        "blowoutParity": (blow, 0.8),
        "flatRegion": (flat, 0.8),
        "tonalParity": (tonal, 1.0),
    }
    weighted = sum(s * w for s, w in soft.values())
    total_w = sum(w for _s, w in soft.values())
    fidelity = weighted / total_w if total_w else 0.0

    soft_scores = [s for s, _w in soft.values()]
    spread = max(soft_scores) - min(soft_scores) if soft_scores else 0.0

    # Verdict + routing (deterministic function of which signal failed — §3.5).
    if hard_failures:
        verdict, action = "reject", "refine-code"
    elif spread > DISAGREEMENT_SPREAD and fidelity < FIDELITY_TARGET:
        verdict, action = "low-confidence", "probe"
    elif fidelity >= FIDELITY_TARGET:
        verdict, action = "pass", "continue"
    else:
        verdict, action = "reject", "refine-code"

    return {
        "verdict": verdict,
        "action": action,
        "fidelity": round(fidelity, 4),
        "fidelityTarget": FIDELITY_TARGET,
        "hardGateFailures": hard_failures,
        "disagreementSpread": round(spread, 4),
        "signals": {
            "silhouetteIoU": round(iou, 4),
            "scaleDelta": round(scale_delta, 4),
            "aspectRatioDelta": round(aspect_delta, 4),
            "symmetryParity": round(sym, 4),
            "phashSimilarity": round(phash_sim, 4),
            "ssim": round(ssim, 4),
            "edgeOverlap": round(edges, 4),
            "blowoutParity": round(blow, 4),
            "flatRegionScore": round(flat, 4),
            "tonalParity": round(tonal, 4),
        },
        "weights": {k: w for k, (_s, w) in soft.items()},
        "reference": str(reference_png.resolve()),
        "render": str(render_png.resolve()),
        "note": "deterministic ensemble; zero VLM/token. VLM layer (§3.4) runs only if this passes.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--render", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = evaluate(args.reference.expanduser().resolve(), args.render.expanduser().resolve())
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"{result['verdict'].upper()} → {result['action']}  fidelity={result['fidelity']} "
              f"(target {result['fidelityTarget']})")
        for f in result["hardGateFailures"]:
            print(f"  HARD: {f}")
    # exit 0 only on a clean pass; non-zero otherwise so a pipeline can gate on it.
    return 0 if result["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
