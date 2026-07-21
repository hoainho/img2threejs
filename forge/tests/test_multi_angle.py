#!/usr/bin/env python3
"""Tests for the deterministic Phase-3 §3.2 multi-angle degenerate-view check."""

import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "stage4_review"))
from diagnose_render_multi_angle import analyze_angles, silhouette_area_fraction  # noqa: E402


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def write_rgb_png(path, w, h, pixel_fn):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w):
            raw += bytes(pixel_fn(x, y, w, h))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    path.write_bytes(
        PNG_SIGNATURE
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def _centered_block(x0, y0, x1, y1):
    """Pixel fn: dark block within [x0,x1)x[y0,y1) on a white background."""

    def fn(x, y, w, h):
        if x0 <= x < x1 and y0 <= y < y1:
            return (20, 20, 20)
        return (255, 255, 255)

    return fn


class MultiAngleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_volumetric_object_not_flagged(self):
        ref = self.tmp / "ref.png"
        orbit_a = self.tmp / "orbit_a.png"
        orbit_b = self.tmp / "orbit_b.png"
        # Reference: big centered block. Orbits: similarly large blocks (a real
        # 3D volume keeps a substantial silhouette from other angles).
        write_rgb_png(ref, 200, 200, _centered_block(50, 50, 150, 150))
        write_rgb_png(orbit_a, 200, 200, _centered_block(55, 45, 155, 160))
        write_rgb_png(orbit_b, 200, 200, _centered_block(45, 55, 145, 150))

        result = analyze_angles(ref, [orbit_a, orbit_b])
        self.assertFalse(result["degenerate"])
        for angle in result["angles"]:
            self.assertFalse(angle["degenerate"])

    def test_flat_plane_collapses_flagged(self):
        ref = self.tmp / "ref.png"
        orbit = self.tmp / "orbit_sliver.png"
        # Reference: big block filling most of the frame (~0.64). Orbit: a thin
        # vertical strip, i.e. a billboard seen almost edge-on -> silhouette
        # area collapses (~0.06, ratio ~0.09 < 0.15). The strip is kept wide
        # enough (12px) to stay above the shared segmenter's tiny-mask floor
        # (<3.5% coverage inverts to full-frame), so the collapse is real, not
        # an artifact of the fallback.
        write_rgb_png(ref, 200, 200, _centered_block(20, 20, 180, 180))
        write_rgb_png(orbit, 200, 200, _centered_block(94, 0, 106, 200))

        result = analyze_angles(ref, [orbit])
        self.assertTrue(result["degenerate"])
        self.assertTrue(result["angles"][0]["degenerate"])

    def test_area_fraction_monotonic(self):
        big = self.tmp / "big.png"
        small = self.tmp / "small.png"
        # Full-black frame: the whole frame is foreground -> fraction near 1.0.
        write_rgb_png(big, 100, 100, lambda x, y, w, h: (0, 0, 0))
        # Mostly white with a small dark dot -> much smaller foreground
        # fraction (~0.16). Sized above the segmenter's tiny-mask floor (<3.5%
        # coverage inverts to full-frame) so it reads as a genuine small area.
        write_rgb_png(small, 100, 100, _centered_block(30, 30, 70, 70))

        big_fraction = silhouette_area_fraction(big)
        small_fraction = silhouette_area_fraction(small)
        self.assertGreater(big_fraction, small_fraction)


if __name__ == "__main__":
    unittest.main(verbosity=2)
