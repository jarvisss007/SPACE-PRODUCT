"""Stitch one day of NASA EPIC photographs into a single map of the whole Earth.

EPIC (on DSCOVR, near L1) photographs the sunlit Earth about 13 times a day,
each picture centred about 27 degrees further west. This script projects every
picture back onto latitude and longitude and blends them, giving the
equirectangular map that the globe on earth-from-above.html wraps round a
sphere. Browsers cannot do this themselves: NASA's archive does not let web
pages read the pixels of its photographs, so the GitHub Action runs this daily
and publishes the result next to the page.

Geometry, per picture (all from NASA's own metadata):
  * the camera looks at Earth's centre from DSCOVR's distance, so a point on the
    globe lands on the picture by a true perspective projection;
  * the disk's radius in pixels is measured from the picture itself;
  * NASA publishes the pictures north-up, centred on the point under the camera.
Each picture is trusted most at its centre: weight = cos(angle from centre)^8,
so seams fall halfway between pictures. Clouds still move between pictures
taken two hours apart, so a seam can show a small jump; that is real.

Writes docs/earth-globe.jpg (2048 x 1024) and docs/earth-globe.json.
If anything fails, the files already published are left as they were.

Run:  python3 -I tools/stitch_epic.py [YYYY-MM-DD]
"""
from pathlib import Path
import io
import json
import sys
import urllib.request

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"
API = "https://epic.gsfc.nasa.gov/api/natural"
ARC = "https://epic.gsfc.nasa.gov/archive/natural/"
UA = {"User-Agent": "golapada-earth-globe/1.0 (daily public mosaic)"}
W, H = 2048, 1024
R_EARTH = 6371.0


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def disk(img: np.ndarray):
    """Centre and radius of Earth's disk, measured from the picture."""
    lum = img.mean(axis=2)
    m = lum > 12
    rows, cols = np.where(m.any(1))[0], np.where(m.any(0))[0]
    cy, cx = (rows[0] + rows[-1]) / 2, (cols[0] + cols[-1]) / 2
    r = ((rows[-1] - rows[0]) + (cols[-1] - cols[0])) / 4
    return cx, cy, r


def bilinear(img: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    x = np.clip(x, 0, w - 1.001)
    y = np.clip(y, 0, h - 1.001)
    x0, y0 = x.astype(np.int32), y.astype(np.int32)
    fx, fy = (x - x0)[:, None], (y - y0)[:, None]
    a, b = img[y0, x0], img[y0, x0 + 1]
    c, d = img[y0 + 1, x0], img[y0 + 1, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def main() -> int:
    date = sys.argv[1] if len(sys.argv) > 1 else None
    meta = json.loads(get(f"{API}/date/{date}" if date else API))
    if len(meta) < 6:
        print(f"only {len(meta)} pictures; leaving the published globe as it is")
        return 0
    meta.sort(key=lambda e: e["date"])
    day = meta[0]["date"][:10]

    lat = np.radians(90 - (np.arange(H) + 0.5) * 180 / H)[:, None] * np.ones((1, W))
    lon = np.radians(-180 + (np.arange(W) + 0.5) * 360 / W)[None, :] * np.ones((H, 1))
    lat, lon = lat.ravel(), lon.ravel()
    # unit vectors of every map pixel, Earth-fixed (x to 0E, y to 90E, z north)
    P = np.stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)], 1)

    acc = np.zeros((H * W, 3))
    wsum = np.zeros(H * W)
    best = np.zeros(H * W)  # how squarely the best picture saw each spot
    used = []
    for e in meta:
        url = f"{ARC}{e['date'][:10].replace('-', '/')}/jpg/{e['image']}.jpg"
        try:
            img = np.asarray(Image.open(io.BytesIO(get(url))).convert("RGB"), dtype=np.float32)
        except Exception as err:  # one missing picture is not fatal
            print("skip", e["image"], err)
            continue
        cx, cy, rpx = disk(img)
        c = e["centroid_coordinates"]
        la0, lo0 = np.radians(c["lat"]), np.radians(c["lon"])
        v = np.array([np.cos(la0) * np.cos(lo0), np.cos(la0) * np.sin(lo0), np.sin(la0)])  # towards camera
        east = np.array([-np.sin(lo0), np.cos(lo0), 0.0])
        north = np.cross(v, east)
        d = np.linalg.norm([e["dscovr_j2000_position"][k] for k in "xyz"]) / R_EARTH
        f = rpx / np.tan(np.arcsin(1 / d))  # focal length in pixels, from the measured disk
        cosc = P @ v
        ok = cosc > max(0.12, 1 / d)
        Q = P[ok]
        depth = d - Q @ v
        px = cx + f * (Q @ east) / depth
        py = cy - f * (Q @ north) / depth
        wgt = cosc[ok] ** 8
        acc[ok] += bilinear(img, px, py) * wgt[:, None]
        wsum[ok] += wgt
        best[ok] = np.maximum(best[ok], cosc[ok])
        used.append({"image": e["image"], "time": e["date"][11:16], "lat": round(c["lat"], 2), "lon": round(c["lon"], 2)})

    if len(used) < 6:
        print("too few pictures downloaded; leaving the published globe as it is")
        return 0
    seen = wsum > 1e-6
    rgb = np.zeros((H * W, 3))
    rgb[seen] = acc[seen] / wsum[seen][:, None]
    # never in view of the camera that day (polar night): dark, with a soft edge
    a = np.clip((best - 0.12) / 0.18, 0, 1)[:, None]
    rgb = rgb * a + np.array([10, 16, 28]) * (1 - a)
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8).reshape(H, W, 3))
    OUT.mkdir(exist_ok=True)
    im.save(OUT / "earth-globe.jpg", quality=86, optimize=True, progressive=True)
    lat_deg = 90 - (np.arange(H) + 0.5) * 180 / H
    rows_seen = seen.reshape(H, W).mean(1) > 0.5
    info = {"date": day, "pictures": used, "width": W, "height": H,
            "seen_north": round(float(lat_deg[rows_seen].max()), 1),
            "seen_south": round(float(lat_deg[rows_seen].min()), 1),
            "source": "NASA EPIC natural-colour images, DSCOVR (epic.gsfc.nasa.gov)"}
    (OUT / "earth-globe.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(f"stitched {len(used)} pictures from {day}; seen {info['seen_south']} to {info['seen_north']} latitude")
    return 0


if __name__ == "__main__":
    sys.exit(main())
