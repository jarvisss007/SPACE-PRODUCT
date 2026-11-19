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


ALPHA5 = "ABCDEFGHJKLMNPQRSTUVWXYZ"  # Alpha-5: I and O are skipped


def catnr5(n: int) -> str:
    """Five-character catalogue number; above 99999 use the Alpha-5 letter scheme."""
    if n <= 99999:
        return f"{n:05d}"
    return ALPHA5[n // 10000 - 10] + f"{n % 10000:04d}"


def _exp(v: float) -> str:
    """TLE implied-decimal exponent field, e.g. -0.11606e-4 -> '-11606-4'."""
    if v == 0:
        return " 00000+0"
    sign = "-" if v < 0 else " "
    m, e = f"{abs(v):.4e}".split("e")
    mant = int(round(float(m) * 10000))
    ex = int(e) + 1
    if mant >= 100000:
        mant //= 10
        ex += 1
    return f"{sign}{mant:05d}{'-' if ex < 0 else '+'}{abs(ex)}"


def _check(line: str) -> str:
    return str(sum(int(c) if c.isdigit() else (1 if c == "-" else 0) for c in line[:68]) % 10)


def omm_to_tle(o: dict) -> list[str]:
    """Turn one CelesTrak OMM (JSON) record into [name, line1, line2]. Newer objects
    have six-digit catalogue numbers that the classic TLE text download leaves out."""
    from datetime import datetime
    ep = datetime.fromisoformat(o["EPOCH"])
    doy = ep.timetuple().tm_yday + (ep.hour + (ep.minute + (ep.second + ep.microsecond / 1e6) / 60) / 60) / 24
    sat = catnr5(int(o["NORAD_CAT_ID"]))
    yr, rest = o["OBJECT_ID"].split("-", 1)
    intl = (yr[2:] + rest).ljust(8)[:8]
    nd = float(o.get("MEAN_MOTION_DOT", 0))
    ndot = ("-" if nd < 0 else " ") + f"{abs(nd):.8f}"[1:]
    l1 = (f"1 {sat}{o.get('CLASSIFICATION_TYPE', 'U')} {intl} {ep.year % 100:02d}{doy:012.8f} {ndot} "
          f"{_exp(float(o.get('MEAN_MOTION_DDOT', 0)))} {_exp(float(o.get('BSTAR', 0)))} 0 {int(o.get('ELEMENT_SET_NO', 999)) % 10000:4d}")
    l1 = l1[:68] + _check(l1)
    ecc = f"{float(o['ECCENTRICITY']):.7f}"[2:]
    l2 = (f"2 {sat} {float(o['INCLINATION']):8.4f} {float(o['RA_OF_ASC_NODE']):8.4f} {ecc} "
          f"{float(o['ARG_OF_PERICENTER']):8.4f} {float(o['MEAN_ANOMALY']):8.4f} {float(o['MEAN_MOTION']):11.8f}{int(o.get('REV_AT_EPOCH', 0)) % 100000:5d}")
    l2 = l2[:68] + _check(l2)
    return [o["OBJECT_NAME"].strip(), l1, l2]


def fetch_new(query: str) -> list[list[str]]:
    """Objects with six-digit catalogue numbers, from the JSON (OMM) download, as TLE lines."""
    req = urllib.request.Request(BASE.replace("FORMAT=tle&", "FORMAT=json&") + query, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode("utf-8", "replace") or "[]")
    return [omm_to_tle(o) for o in data if int(o.get("NORAD_CAT_ID", 0)) > 99999]


def gnss_system(name: str):
    """Which navigation system a CelesTrak 'gnss' entry belongs to (None for augmentation satellites)."""
    n = name.upper()
    if n.startswith("GPS"):
        return "GPS"
    if n.startswith("COSMOS"):
        return "GLONASS"
    if "GALILEO" in n:
        return "Galileo"
    if n.startswith("BEIDOU"):
        return "BeiDou"
    if n.startswith("QZS"):
        return "QZSS"
    if n.startswith(("IRNSS", "NVS")):
        return "NavIC"
    return None


def write_gnss(gnss: list, nvs: list) -> None:
    """Rewrite the `const GNSS=` line in every page that has one (the One Sky Lab)."""
    rows, seen = [], set()
    for name, l1, l2 in gnss + nvs:
        sys_ = gnss_system(name)
        if sys_ and l1[2:7] not in seen:
            seen.add(l1[2:7])
            rows.append([name, l1, l2, sys_])
    if len(rows) < 80 or not {"GPS", "GLONASS", "Galileo", "BeiDou"} <= {r[3] for r in rows}:
        print(f"only {len(rows)} navigation satellites: navigation data left unchanged")
        return
    line = "const GNSS=" + json.dumps(rows) + ";"
    for page in sorted(ROOT.glob("*.html")):
        src = page.read_text(encoding="utf-8")
        out, n = re.subn(r"^const GNSS=\[.*?\];$", lambda m: line, src, count=1, flags=re.M)
        if n == 1 and out != src:
            page.write_text(out, encoding="utf-8")
            print(f"{len(rows)} navigation satellites written to {page.name}")


def main() -> int:
    try:
        stations = fetch("GROUP=stations")
        hubble = fetch("CATNR=20580")
        gnss = fetch("GROUP=gnss")
        nvs = fetch("NAME=NVS")
        try:  # six-digit catalogue numbers (e.g. NVS-03, 101228) only come as JSON
            gnss += fetch_new("GROUP=gnss")
            nvs += fetch_new("NAME=NVS")
        except Exception as e:
            print(f"newer objects skipped: {e}")
        visual = fetch("GROUP=visual")
    except Exception as e:  # network trouble: keep yesterday's data
        print(f"download failed, page left unchanged: {e}")
        return 0
    write_gnss(gnss, nvs)
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
    new_line = "const TLE=" + json.dumps(sats) + ";"
    pages = [p for p in sorted(ROOT.glob("*.html"))
             if re.search(r"^const TLE=\[", p.read_text(encoding="utf-8"), re.M)]
    if PAGE not in pages:
        print("could not find the orbit data line in satellite-watch.html: pages left unchanged")
        return 1
    changed = 0
    for page in pages:  # every page that carries the snapshot (Satellite Watch, Tonight's Sky, ...)
        src = page.read_text(encoding="utf-8")
        out, n = re.subn(r"^const TLE=\[.*?\];$", lambda m: new_line, src, count=1, flags=re.M)
        if n == 1 and out != src:
            page.write_text(out, encoding="utf-8")
            changed += 1
    print(f"{len(sats)} satellites; updated {changed} of {len(pages)} pages" if changed else "orbit data unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
