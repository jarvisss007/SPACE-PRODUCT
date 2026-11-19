"""Refresh the asteroid snapshot inside asteroid-watch.html from NASA/JPL.

JPL's Small-Body Database APIs are free but do not allow browsers to read them
directly, so, like the satellite orbits, a copy is kept inside the page and
refreshed once a day by the GitHub Action. Three feeds:

  * close approaches within 0.05 au (about 19 lunar distances), the last 30
    days and the next 120 days       (cad.api)
  * the most recent fireballs seen by US government sensors      (fireball.api)
  * asteroids with a non-zero impact probability, Sentry list    (sentry.api)

It rewrites the single `const NEO=` line. If any download fails or looks wrong,
the page is left as it was.

Run:  py -I tools/refresh_neo.py      (then: py -I build_site.py)
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import re
import sys
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "asteroid-watch.html"
API = "https://ssd-api.jpl.nasa.gov/"
UA = {"User-Agent": "golapada-asteroid-watch/1.0 (daily public snapshot)"}


def get(path: str) -> dict:
    req = urllib.request.Request(API + path, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> int:
    try:
        from datetime import timedelta
        today = datetime.now(timezone.utc).date()
        cad = get(f"cad.api?dist-max=0.05&date-min={today - timedelta(days=30)}&date-max={today + timedelta(days=120)}&sort=date&diameter=true")
        fire = get("fireball.api?limit=60")
        sentry = get("sentry.api")
    except Exception as e:  # network trouble: keep yesterday's data
        print(f"download failed, page left unchanged: {e}")
        return 0
    f = cad.get("fields", [])
    need = ["des", "cd", "dist", "v_rel", "h"]
    if not all(k in f for k in need) or int(cad.get("count", 0)) < 5:
        print("close-approach data looks wrong: page left unchanged")
        return 0
    ix = {k: f.index(k) for k in f}
    close = []
    for r in cad["data"]:
        close.append([r[ix["des"]], r[ix["cd"]], round(float(r[ix["dist"]]), 6), round(float(r[ix["v_rel"]]), 2),
                      float(r[ix["h"]]) if r[ix["h"]] else None,
                      float(r[ix["diameter"]]) if "diameter" in ix and r[ix["diameter"]] else None])
    ff = fire.get("fields", [])
    fx = {k: ff.index(k) for k in ff}
    fb = []
    for r in fire.get("data", []):
        try:
            lat = float(r[fx["lat"]]) * (1 if r[fx["lat-dir"]] == "N" else -1) if r[fx["lat"]] else None
            lon = float(r[fx["lon"]]) * (1 if r[fx["lon-dir"]] == "E" else -1) if r[fx["lon"]] else None
            fb.append([r[fx["date"]], lat, lon, float(r[fx["impact-e"]]),
                       float(r[fx["alt"]]) if r[fx["alt"]] else None, float(r[fx["vel"]]) if r[fx["vel"]] else None])
        except (KeyError, ValueError, TypeError):
            continue
    risk = []
    for o in sentry.get("data", []):
        try:
            risk.append([o["des"], float(o["ip"]), float(o["ps_cum"]), float(o["diameter"]) if o.get("diameter") else None,
                         o.get("range", ""), int(o.get("n_imp", 0)), int(o.get("ts_max") or 0)])
        except (KeyError, ValueError):
            continue
    risk.sort(key=lambda r: -r[2])
    snap = {"at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "close": close, "fire": fb,
            "risk": risk[:25], "riskTotal": len(risk)}
    line = "const NEO=" + json.dumps(snap, separators=(",", ":")) + ";"
    src = PAGE.read_text(encoding="utf-8")
    out, n = re.subn(r"^const NEO=\{.*?\};$", lambda m: line, src, count=1, flags=re.M)
    if n != 1:
        print("could not find the NEO data line in asteroid-watch.html: page left unchanged")
        return 1
    if out != src:
        PAGE.write_text(out, encoding="utf-8")
    print(f"{len(close)} close approaches, {len(fb)} fireballs, {len(risk)} on the risk list")
    return 0


if __name__ == "__main__":
    sys.exit(main())
