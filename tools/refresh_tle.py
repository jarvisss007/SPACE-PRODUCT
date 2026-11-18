"""Refresh the orbit snapshot inside satellite-watch.html from CelesTrak.

CelesTrak publishes the US Space Force's public element sets for free. This
script downloads the groups the Satellite Watch shows, keeps the same layout
as before ([name, line1, line2, group]) and rewrites the single `const TLE=`
line in the page. It changes nothing if a download fails or looks wrong, so a
bad day at CelesTrak never breaks the site.

Run:  python tools/refresh_tle.py      (then: python build_site.py)
CelesTrak asks that each group is fetched at most once every couple of hours;
the daily GitHub Action stays well inside that.
"""
from pathlib import Path
import json
import re
import sys
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "satellite-watch.html"
BASE = "https://celestrak.org/NORAD/elements/gp.php?FORMAT=tle&"
UA = {"User-Agent": "golapada-satellite-watch/1.0 (daily public snapshot)"}


def fetch(query: str) -> list[list[str]]:
    req = urllib.request.Request(BASE + query, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        text = r.read().decode("utf-8", "replace")
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    out = []
    for i in range(0, len(lines) - 2, 3):
        name, l1, l2 = lines[i], lines[i + 1], lines[i + 2]
        if l1.startswith("1 ") and l2.startswith("2 ") and len(l1) >= 68 and len(l2) >= 68:
            out.append([name.strip(), l1, l2])
    return out


def main() -> int:
    try:
        stations = fetch("GROUP=stations")
        hubble = fetch("CATNR=20580")
        gnss = fetch("GROUP=gnss")
        nvs = fetch("NAME=NVS")
        visual = fetch("GROUP=visual")
    except Exception as e:  # network trouble: keep yesterday's data
        print(f"download failed, page left unchanged: {e}")
        return 0
    sats, seen = [], set()

    def add(rows, group, keep=lambda n: True):
        for name, l1, l2 in rows:
            cat = l1[2:7]
            if cat in seen or not keep(name):
                continue
            seen.add(cat)
            sats.append([name, l1, l2, group])

    add(stations, "station", lambda n: n in ("ISS (ZARYA)", "CSS (TIANHE)"))
    add(hubble, "science")
    add(gnss, "navic", lambda n: n.startswith(("IRNSS", "NVS")))
    add(nvs, "navic", lambda n: n.startswith("NVS"))
    add(visual, "bright")
    must = {"ISS (ZARYA)", "HST"}
    if len(sats) < 50 or not must <= {s[0] for s in sats}:
        print(f"only {len(sats)} satellites, or the ISS or Hubble missing: page left unchanged")
        return 0
    src = PAGE.read_text(encoding="utf-8")
    new_line = "const TLE=" + json.dumps(sats) + ";"
    out, n = re.subn(r"^const TLE=\[.*?\];$", lambda m: new_line, src, count=1, flags=re.M)
    if n != 1:
        print("could not find the orbit data line: page left unchanged")
        return 1
    if out == src:
        print("orbit data unchanged")
        return 0
    PAGE.write_text(out, encoding="utf-8")
    print(f"refreshed {len(sats)} satellites")
    return 0


if __name__ == "__main__":
    sys.exit(main())
