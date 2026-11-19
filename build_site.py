"""Build the Golapada website from the app pages in this folder.

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
    ("tonight.html", "Tonight", "3aUGRPdpk6vgQBkzKSAZWb"),
    ("earth-from-above.html", "Earth", "DgLUJmgCAWUQ5pQsEG9Afj"),
    ("satellite-watch.html", "Live satellites", "HRrym68cV7YcEbuycixy2p"),
    ("space-weather.html", "Space weather", "JPono7cjiSTiPThfrCKzXm"),
    ("meteor-showers.html", "Meteors", "B9gJ3NAKrKPaDJoWTrXMDj"),
    ("asteroid-watch.html", "Asteroids", "GWeaBcDHjRt3WGzY3vBMwH"),
    ("eclipse-lab.html", "Eclipses", "LvmyiUbgkuDqYbgSpd2UcW"),
    ("isro-launches.html", "ISRO launches", "1JsMBgZn6sVaugdKpqyuWz"),
    ("starship-catch.html", "Catch", "D2UgmPBXpzcKUxY7qnzQdB"),
    ("rocket-lab.html", "Rockets", "4ZaBFQRVW2jUmBzCpVSHiU"),
    ("navic-lab.html", "NavIC", "DTgnmQzwPso42LJYg5ZR7w"),
    ("space-debris-lab.html", "Debris", "QNYG3ukJSGU1rWvASCXXJx"),
    ("gaganyaan-lab.html", "Gaganyaan", "6wABpadDbgD2bTpGxGxfFW"),
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
    ("one-sky-lab.html", "One Sky", "8wnKFX4tTwV3Sbd2jBAzWD"),
    ("planetary-defense-lab.html", "Defense", "UtRh4Wahi2S7pytfcBcXBc"),
    ("schools.html", "For schools", "7nffqBM7LHBTznHTZ5fA5M"),
    ("worksheets.html", "Worksheets", "WL3LspZGoLK2qfmncyT82E"),
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
        text = "Golapada" if i == 0 else label
        links.append(f'<a href="{fname}"{cls}{cur}>{text}</a>')
    return f'<nav class="sa-nav" aria-label="Golapada"><div class="sa-in">{"".join(links)}</div></nav>\n'


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
        WEB.mkdir(exist_ok=True)
        (WEB / fname).write_text(web_page(src, fname), encoding="utf-8")
        print(f"built {fname}")
    # GitHub Pages: serve files as they are, without Jekyll processing
    (WEB / ".nojekyll").write_text("", encoding="utf-8")
    (WEB / "404.html").write_text(web_page(
        '<title>Not found · Golapada</title><style>html,body{background:#04060b;color:#e7edf3;font-family:system-ui,sans-serif}'
        '.wrap{max-width:640px;margin:15vh auto;padding:0 16px}a{color:#74c7ff}</style>'
        '<div class="wrap"><h1>Lost in orbit</h1><p>That page is not here. <a href="./">Go to the Golapada home page</a>.</p></div>',
        "404.html"), encoding="utf-8")
    write_offline_zip()
    write_app()


def write_offline_zip() -> None:
    """docs/golapada-offline.zip: every web page, for schools without steady internet.
    Fixed timestamps keep the zip byte-identical unless a page changes."""
    import zipfile
    pages = sorted(p for p in WEB.glob("*.html") if p.name != "404.html")
    readme = "\r\n".join([
        "Golapada offline", "",
        "Unzip this folder and open index.html in any web browser.",
        "Everything is calculated on your own computer. Fonts, the live Earth photographs",
        "and the satellite-tracking library need the internet; satellite positions are from",
        "the day this copy was made, so download a fresh one every week or two.", ""])
    with zipfile.ZipFile(WEB / "golapada-offline.zip", "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        info = zipfile.ZipInfo("golapada/README.txt", (2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, readme)
        for p in pages:
            info = zipfile.ZipInfo("golapada/" + p.name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, p.read_bytes())
    print(f"built golapada-offline.zip ({len(pages)} pages)")


# ---- the public website (docs/), for GitHub Pages or any static host ----
WEB = HERE / "docs"
ICON = ("data:image/svg+xml," "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
        "%3Crect width='64' height='64' rx='14' fill='%2304060b'/%3E"
        "%3Cellipse cx='32' cy='32' rx='26' ry='11' fill='none' stroke='%2374c7ff' stroke-width='3' transform='rotate(-25 32 32)'/%3E"
        "%3Ccircle cx='32' cy='32' r='9' fill='%23ffa24a'/%3E%3Ccircle cx='54' cy='22' r='4' fill='%23e7edf3'/%3E%3C/svg%3E")


def web_page(src: str, fname: str) -> str:
    """A full standalone HTML document: doctype, language, icon and a description for search and link previews."""
    body = re.sub(r"^\s*<!doctype html>\s*", "", src, flags=re.I)
    body = body.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    body = body.replace('<meta charset="utf-8">\n', "", 1)
    title = re.search(r"<title>(.*?)</title>", body, re.S)
    t = title.group(1).strip() if title else "Golapada"
    desc = ("Interactive space-science labs built on real mission data: rockets, satellites, the Moon, Mars, "
            "the Sun and the stars, each checked against what really happened.")
    head = (f'<link rel="icon" href="{ICON}">\n<link rel="manifest" href="manifest.webmanifest">\n'
            f'<link rel="apple-touch-icon" href="icon-192.png">\n<meta name="description" content="{desc}">\n'
            f'<meta property="og:title" content="{t if fname == "index.html" else t + " · Golapada"}">\n'
            f'<meta property="og:description" content="{desc}">\n<meta name="theme-color" content="#04060b">\n')
    # charset first: browsers only look for it in the first 1,024 bytes
    return '<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n' + head + body + APP_JS + "\n</html>\n"


# ---- installable app: manifest, icons, offline service worker ----
APP_JS = """
<style>.ga-install{position:fixed;right:max(14px,env(safe-area-inset-right,0px));bottom:max(14px,env(safe-area-inset-bottom,0px));z-index:80;font:600 14px "Saira Condensed","Arial Narrow",sans-serif;letter-spacing:.08em;text-transform:uppercase;background:#e8c46a;color:#1b1404;border:0;border-radius:999px;padding:10px 16px;box-shadow:0 6px 20px rgba(0,0,0,.5);cursor:pointer}.ga-install[hidden]{display:none}.ga-install:focus-visible{outline:2px solid #74c7ff;outline-offset:2px}@media print{.ga-install{display:none}}</style>
<button type="button" class="ga-install" id="gaInstall" hidden>Install Golapada</button>
<script>
(()=>{if('serviceWorker' in navigator&&location.protocol==='https:')addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));
let ev=null;const b=document.getElementById('gaInstall');addEventListener('beforeinstallprompt',e=>{e.preventDefault();ev=e;b.hidden=false});
b.addEventListener('click',async()=>{if(!ev)return;b.hidden=true;ev.prompt();try{await ev.userChoice}catch(e){}ev=null});addEventListener('appinstalled',()=>{b.hidden=true})})();
</script>"""

SW = r"""// Golapada offline support. The version changes whenever any page changes.
const V='__V__',PAGES=__PAGES__;
const LIBS=/^https:\/\/(cdn\.jsdelivr\.net|fonts\.googleapis\.com|fonts\.gstatic\.com)\//;
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(PAGES)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V&&k.startsWith('golapada-')).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET')return;const u=new URL(r.url);
  if(u.origin===location.origin){ // pages: fresh from the network when online, the saved copy when offline
    e.respondWith(fetch(r).then(res=>{if(res.ok){const cp=res.clone();caches.open(V).then(c=>c.put(r,cp))}return res}).catch(()=>caches.match(r,{ignoreSearch:true}).then(m=>m||caches.match('./'))));return}
  if(LIBS.test(r.url)){ // fonts and code libraries: keep a copy for offline use
    e.respondWith(caches.match(r).then(m=>m||fetch(r).then(res=>{if(res.ok||res.type==='opaque'){const cp=res.clone();caches.open(V).then(c=>c.put(r,cp))}return res})))}
  // live data (NOAA, NASA, CelesTrak) is never cached: it always comes from the network
});
"""


def draw_icon(size: int, maskable: bool = False):
    """The Golapada mark (a sun, a tilted orbit and a planet) as a PNG image."""
    import math
    from PIL import Image, ImageDraw
    S = size * 4  # draw large, then shrink for smooth edges
    im = Image.new("RGBA", (S, S), (4, 6, 11, 255))
    k = 0.78 if maskable else 1.0  # maskable icons keep the art inside the safe circle
    c = S / 2
    orbit = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rx, ry, w = 0.41 * S * k, 0.17 * S * k, max(2, int(0.045 * S * k))
    ImageDraw.Draw(orbit).ellipse([c - rx, c - ry, c + rx, c + ry], outline=(116, 199, 255, 255), width=w)
    im.alpha_composite(orbit.rotate(25, resample=Image.BICUBIC, center=(c, c)))
    d = ImageDraw.Draw(im)
    r = 0.15 * S * k
    d.ellipse([c - r, c - r, c + r, c + r], fill=(255, 162, 74, 255))
    t, rot = math.radians(-20), math.radians(-25)  # a point on the orbit, then the same tilt as the ellipse
    ex, ey = rx * math.cos(t), ry * math.sin(t)
    px, py = c + ex * math.cos(rot) - ey * math.sin(rot), c + ex * math.sin(rot) + ey * math.cos(rot)
    pr = 0.065 * S * k
    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(231, 237, 243, 255))
    return im.resize((size, size), Image.LANCZOS)


def write_app() -> None:
    """Make docs/ an installable app that keeps working offline."""
    import hashlib, json
    for n, m in [(192, False), (512, False), (512, True)]:
        draw_icon(n, m).convert("RGB").save(WEB / (f"icon-maskable-{n}.png" if m else f"icon-{n}.png"), optimize=True)
    manifest = {
        "name": "Golapada: space science you can play with", "short_name": "Golapada",
        "description": "Interactive space-science labs built on real mission data.",
        "start_url": "./", "scope": "./", "display": "standalone",
        "background_color": "#04060b", "theme_color": "#04060b", "lang": "en",
        "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
    (WEB / "manifest.webmanifest").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    pages = sorted(p.name for p in WEB.glob("*.html") if p.name != "404.html")
    h = hashlib.sha256()
    for name in pages:
        h.update((WEB / name).read_bytes())
    files = ["./"] + pages + ["manifest.webmanifest", "icon-192.png", "icon-512.png"]
    (WEB / "sw.js").write_text(SW.replace("__V__", "golapada-" + h.hexdigest()[:12]).replace("__PAGES__", json.dumps(files)), encoding="utf-8")
    print(f"built app: manifest, 3 icons, sw.js caching {len(files)} files")


if __name__ == "__main__":
    build()
