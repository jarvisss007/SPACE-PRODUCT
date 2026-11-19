"""Refresh this year's launch log inside launch-watch.html from Launch Library 2.

The page loads upcoming and recent launches live from The Space Devs' free
Launch Library 2 API. The totals for the whole year need several requests, so
they are copied into the page once a day by the GitHub Action, kept small:
[time, country code, provider, rocket, status, pad latitude, pad longitude, orbit, name].

It rewrites the single `const YEAR=` line. If a download fails or looks wrong,
the page is left as it was. The free API allows 15 requests an hour; this
script makes one for every 100 launches (about four a year).

Run:  py -I tools/refresh_launches.py      (then: py -I build_site.py)
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import re
import sys
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "launch-watch.html"
API = "https://ll.thespacedevs.com/2.3.0/launches/previous/"
UA = {"User-Agent": "golapada-launch-watch/1.0 (daily public snapshot)"}


def get(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> int:
    year = datetime.now(timezone.utc).year
    url = f"{API}?net__gte={year}-01-01T00:00:00Z&limit=100&mode=normal&ordering=net"
    rows = []
    try:
        for _ in range(8):
            d = get(url)
            for L in d.get("results", []):
                pad = L.get("pad") or {}
                ctry = ((pad.get("country") or {}).get("alpha_3_code")) or ""
                conf = ((L.get("rocket") or {}).get("configuration") or {})
                orbit = (((L.get("mission") or {}).get("orbit")) or {}).get("abbrev", "")
                prov = (L.get("launch_service_provider") or {}).get("name", "")
                rows.append([L.get("net", "")[:16], ctry, prov, conf.get("full_name") or conf.get("name", ""),
                             (L.get("status") or {}).get("abbrev", ""),
                             round(float(pad["latitude"]), 3) if pad.get("latitude") is not None else None,
                             round(float(pad["longitude"]), 3) if pad.get("longitude") is not None else None,
                             orbit, (L.get("name") or "").split(" | ")[-1][:60]])
            url = d.get("next")
            if not url:
                break
    except Exception as e:  # network trouble or rate limit: keep yesterday's data
        print(f"download failed, page left unchanged: {e}")
        return 0
    if len(rows) < 20:
        print(f"only {len(rows)} launches: page left unchanged")
        return 0
    snap = {"at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "year": year, "launches": rows}
    line = "const YEAR=" + json.dumps(snap, ensure_ascii=False, separators=(",", ":")) + ";"
    src = PAGE.read_text(encoding="utf-8")
    out, n = re.subn(r"^const YEAR=\{.*?\};$", lambda m: line, src, count=1, flags=re.M)
    if n != 1:
        print("could not find the YEAR data line in launch-watch.html: page left unchanged")
        return 1
    if out != src:
        PAGE.write_text(out, encoding="utf-8")
    print(f"{len(rows)} launches in {year}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
