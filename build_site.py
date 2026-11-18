"""Build the Starship Atlas website from the app pages in this folder.

Reads every app page, adds a shared navigation bar, turns links between the
apps into relative links, and writes the result to ./site/. The app files
themselves are left untouched, so each can still be published on its own.

Run:  py build_site.py
"""
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
OUT = HERE / "site"

# page file -> (nav label, published artifact id that other pages link to)
PAGES = [
    ("index.html", "Home", "VEHMzzQ5FUTWq6JxoK3tf3"),
    ("satellite-watch.html", "Live satellites", "HRrym68cV7YcEbuycixy2p"),
    ("starship-catch.html", "Catch", "D2UgmPBXpzcKUxY7qnzQdB"),
    ("rocket-lab.html", "Rockets", "4ZaBFQRVW2jUmBzCpVSHiU"),
    ("navic-lab.html", "NavIC", "DTgnmQzwPso42LJYg5ZR7w"),
    ("space-debris-lab.html", "Debris", "QNYG3ukJSGU1rWvASCXXJx"),
    ("chandrayaan-3.html", "Moon", "XUK9zxrq87WJyK17kfWNLF"),
    ("mangalyaan.html", "Mangalyaan", "Q5T2DFByz6EPAzpzHmgXSE"),
    ("mars-landing-lab.html", "Landing", "7DJKbEScJuDeNiYbadxjZ9"),
    ("mars-campaign.html", "Mars", "T7vLYNDGc7GY4DEWtM2hwF"),
    ("solar-system-lab.html", "Planets", "D6UzQQEY6ngBZNt9xur2q2"),
    ("gravity-assist-lab.html", "Flybys", "PrNazFz9h9iZwcTgoZufjY"),
    ("ion-engine-lab.html", "Ion engines", "3fbbRqFRksvudZPdzmVq4w"),
    ("touch-the-sun.html", "Sun", "PnkK14ys8Py76PPtzFJqjn"),
    ("lagrange-lab.html", "L-points", "21WDJwTNzvBc2rM3Ajv5aH"),
    ("voyager-now.html", "Voyager", "WrQw7GKArg2WtZNMSwZjc8"),
    ("milky-way-atlas.html", "Galaxy", "2z13hH9Do9mCvREK8BHAhz"),
    ("telescope-lab.html", "Telescopes", "WLHTz37drfmw38LnwAXFX9"),
    ("exoplanet-explorer.html", "Exoplanets", "TYsrHB7Nchm1y7yuMq6BfG"),
    ("black-hole-lab.html", "Black holes", "4cEbohQeaFS4ezqs2R8Ahb"),
    ("spacecraft-archive.html", "Missions", "RDxM4WQDNdVSRngpy9R218"),
    ("reentry-lab.html", "Re-entry", "NjXosYNX9sCeCWVThB7VhT"),
    ("planetary-defense-lab.html", "Defense", "UtRh4Wahi2S7pytfcBcXBc"),
    ("aryabhata-lab.html", "Aryabhata", "LaFFtHTwWZh7EiU6gL9F8Z"),
    ("nalanda.html", "Nalanda", "9GzdyyvJ8zRcBAznWXM37B"),
    ("starship-through-time.html", "Through time", "4jbD63EEZBxcEbE7WXseMN"),
    ("clues-in-old-books.html", "Old books", "RHr7yep3A95fUrPY78nS57"),
]

NAV_CSS = """<style>
.sa-nav{position:sticky;top:env(safe-area-inset-top,0px);z-index:50;background:rgba(4,6,11,.92);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);border-bottom:1px solid #1f2a38}
.sa-nav .sa-in{max-width:1200px;margin:0 auto;display:flex;align-items:center;gap:4px;overflow-x:auto;scrollbar-width:none;padding-block:8px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.sa-nav .sa-in::-webkit-scrollbar{display:none}
.sa-nav a{flex:none;font-family:"Saira Condensed","Arial Narrow",sans-serif;font-weight:600;font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:#a9b4c2;text-decoration:none;padding:5px 9px;border-radius:4px;white-space:nowrap}
.sa-nav a:hover{color:#e7edf3;background:#121a25}
.sa-nav a:focus-visible{outline:2px solid #e8c46a;outline-offset:1px}
.sa-nav a[aria-current="page"]{color:#0a0d12;background:#e7edf3}
.sa-nav a.sa-brand{color:#ffa24a;font-weight:700;font-size:15px;margin-right:8px}
.sa-nav a.sa-brand[aria-current="page"]{color:#0a0d12;background:#ffa24a}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:60;background:#04060b}
</style>
"""


def nav_html(current: str) -> str:
    links = []
    for i, (fname, label, _) in enumerate(PAGES):
        cur = ' aria-current="page"' if fname == current else ""
        cls = ' class="sa-brand"' if i == 0 else ""
        text = "Starship Atlas" if i == 0 else label
        links.append(f'<a href="{fname}"{cls}{cur}>{text}</a>')
    return f'<nav class="sa-nav" aria-label="Starship Atlas"><div class="sa-in">{"".join(links)}</div></nav>\n'


def build() -> None:
    OUT.mkdir(exist_ok=True)
    id_to_file = {aid: fname for fname, _, aid in PAGES}
    for fname, _, _ in PAGES:
        src = (HERE / fname).read_text(encoding="utf-8")
        # links between apps become relative, so the site works as one unit
        src = re.sub(r"https://claude\.ai/artifact/([A-Za-z0-9]+)",
                     lambda m: id_to_file.get(m.group(1), m.group(0)), src)
        marker = '<div class="wrap">'
        if marker not in src:
            raise SystemExit(f"{fname}: no {marker} to place the navigation before")
        src = src.replace(marker, NAV_CSS + nav_html(fname) + marker, 1)
        if fname != "index.html" and not src.lstrip().lower().startswith("<!doctype"):
            # extra pages are served without the artifact skeleton, so they need their own doctype
            src = "<!doctype html>\n" + src
        (OUT / fname).write_text(src, encoding="utf-8")
        print(f"built {fname}")


if __name__ == "__main__":
    build()
