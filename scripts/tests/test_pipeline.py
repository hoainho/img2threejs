#!/usr/bin/env python3
"""End-to-end integration tests for the Three.js Object Sculptor pipeline.

Pure stdlib. Runs each CLI script as a subprocess and asserts the gate behavior
described in SKILL.md / references. Also generates a tiny real PNG (struct+zlib)
to exercise the image-consuming scripts without any third-party deps.

Run: python3 scripts/tests/test_pipeline.py   (from skill root)
  or: python3 -m unittest discover -s scripts/tests
"""
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
SCRIPTS = SKILL / "scripts"


def run(script, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        capture_output=True, text=True,
    )


def write_png(path, w=64, h=64):
    """Write a minimal valid RGB PNG with a simple gradient (no PIL)."""
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter type 0 per scanline
        for x in range(w):
            raw += bytes(((x * 4) % 256, (y * 4) % 256, ((x + y) * 2) % 256))

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    Path(path).write_bytes(png)


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.assessment = self.dir / "assessment.json"
        self.spec = self.dir / "object-sculpt-spec.json"
        self.ref = self.dir / "ref.png"
        self.render = self.dir / "render.png"
        write_png(self.ref)
        write_png(self.render)

    def test_probe_image(self):
        r = run("probe_reference_image.py", self.ref)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("64", r.stdout)  # reports dimensions

    def test_assessment_and_spec(self):
        r = run("new_pre_spec_assessment.py", "Oak", "--complexity", "complex",
                "--out", self.assessment)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self.assessment.exists())
        self.assertIn("qualityContract", json.loads(self.assessment.read_text()))

        r = run("new_sculpt_spec.py", "Oak", "--assessment", self.assessment,
                "--out", self.spec)
        self.assertEqual(r.returncode, 0, r.stderr)
        spec = json.loads(self.spec.read_text())
        self.assertEqual(spec["schemaVersion"], "2.0")
        self.assertEqual(spec["targetName"], "Oak")

    def test_normal_validate_passes_strict_fails_on_shallow(self):
        run("new_pre_spec_assessment.py", "Oak", "--complexity", "complex",
            "--out", self.assessment)
        run("new_sculpt_spec.py", "Oak", "--assessment", self.assessment,
            "--out", self.spec)
        # normal validation of a structurally-sound starter succeeds
        self.assertEqual(run("validate_sculpt_spec.py", self.spec).returncode, 0)
        # strict quality gate must BLOCK a shallow starter spec
        strict = run("validate_sculpt_spec.py", self.spec, "--strict-quality")
        self.assertNotEqual(strict.returncode, 0)
        self.assertIn("strict quality failure", strict.stdout + strict.stderr)

    def test_orchestrator_starts_at_blockout(self):
        run("new_sculpt_spec.py", "Oak", "--out", self.spec)
        r = run("sculpt_pass_orchestrator.py", "status", self.spec)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("blockout", r.stdout)
        # a future pass must be locked
        locked = run("sculpt_pass_orchestrator.py", "check", self.spec,
                     "--pass-id", "material-pass")
        self.assertNotEqual(locked.returncode, 0)

    def test_generate_factory_emits_typescript(self):
        run("new_sculpt_spec.py", "Oak", "--out", self.spec)
        out = self.dir / "createObjectModel.ts"
        r = run("generate_threejs_factory.py", self.spec, "--out", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        ts = out.read_text()
        self.assertIn("import * as THREE from 'three'", ts)
        self.assertIn("sculptRuntime", ts)
        # generating a locked future pass must fail
        locked = run("generate_threejs_factory.py", self.spec, "--out", out,
                     "--pass-id", "lighting-pass")
        self.assertNotEqual(locked.returncode, 0)

    def test_comparison_sheet_packages_without_scoring(self):
        cmp = self.dir / "cmp.png"
        r = run("make_visual_comparison_sheet.py", "--reference", self.ref,
                "--render", self.render, "--out", cmp, "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(cmp.exists() and cmp.stat().st_size > 0)

    def test_append_review_gate_and_record(self):
        run("new_sculpt_spec.py", "Oak", "--out", self.spec)
        # GATE: continue on a visual pass WITHOUT screenshot evidence must be refused.
        no_evidence = run("append_sculpt_review.py", self.spec, "--pass-id", "blockout",
                          "--fidelity", "0.8", "--action", "continue",
                          "--summary", "no evidence", "--ai-vision-score", "0.8",
                          "--in-place")
        self.assertNotEqual(no_evidence.returncode, 0)
        self.assertIn("render-screenshot", no_evidence.stdout + no_evidence.stderr)
        # WITH evidence: the review is recorded.
        cmp = self.dir / "cmp.png"
        run("make_visual_comparison_sheet.py", "--reference", self.ref,
            "--render", self.render, "--out", cmp)
        layers = json.dumps({
            "silhouetteProportion": 0.82, "componentStructure": 0.78,
            "formDetail": 0.75, "materialSurface": 0.7, "lightingCamera": 0.8,
        })
        # every critical feature target of this pass needs an AI-vision review entry
        spec = json.loads(self.spec.read_text())
        targets = spec.get("selfCorrectLoop", {}).get("featureReviewTargets", [])
        reviews = [
            {"id": t.get("id"), "score": 0.8, "visible": True, "notes": "acceptable"}
            for t in targets if t.get("tier") == "critical"
        ] or [{"id": "overall-silhouette", "score": 0.8, "visible": True, "notes": "ok"}]
        freviews = self.dir / "features.json"
        freviews.write_text(json.dumps(reviews))
        r = run("append_sculpt_review.py", self.spec, "--pass-id", "blockout",
                "--fidelity", "0.8", "--action", "continue",
                "--summary", "Blockout silhouette acceptable.",
                "--render-screenshot", self.render, "--comparison-image", cmp,
                "--ai-vision-score", "0.8", "--layer-scores-json", layers,
                "--feature-reviews-json", freviews,
                "--camera-view", "front", "--in-place")
        self.assertEqual(r.returncode, 0, r.stderr)
        spec = json.loads(self.spec.read_text())
        self.assertTrue(len(spec.get("reviewHistory", [])) >= 1)

    def test_pbr_extraction_runs(self):
        # low-detail synthetic image: either passes or refuses (non-zero) — both are valid,
        # but it must not crash and must respect the confidence gate.
        r = run("extract_reference_pbr.py", self.ref, "--out-dir", self.dir / "pbr",
                "--material-id", "bark", "--target-threshold", "0.7",
                "--report", self.dir / "pbr-report.json")
        self.assertIn(r.returncode, (0, 1), r.stderr)
        self.assertTrue((self.dir / "pbr-report.json").exists() or r.returncode == 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
