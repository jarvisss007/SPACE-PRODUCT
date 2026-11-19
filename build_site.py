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
    ("launch-watch.html", "Launches now", "DXjz74y1pXCSzx7CQ1DmWy"),
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
    ("space-startups.html", "Startups", "HhFgwUCGEZ5j2hX9fxbfUw"),
    ("mars-now.html", "Mars Now", "TNHJm7P3s6KexxvzuzMmvC"),
    ("iss-life.html", "ISS life", "NmwH9bRA3aKx2z3ne6ML9a"),
    ("eht-lab.html", "EHT image", "8QPXVMdauJm4FsNHS1E3mJ"),
    ("comets.html", "Comets", "KrfT2qHJ9aqVXTdYxaHVtW"),
    ("moon-sites.html", "Moon sites", "JFxeoytjsLMCNWioRN5c37"),
    ("planetary-defense-lab.html", "Defense", "UtRh4Wahi2S7pytfcBcXBc"),
    ("schools.html", "For schools", "7nffqBM7LHBTznHTZ5fA5M"),
    ("space-day.html", "Space Day", "XFqC8strPfM51DbXvPesFT"),
    ("worksheets.html", "Worksheets", "WL3LspZGoLK2qfmncyT82E"),
    ("kundli.html", "Kundli", "C8ntFThDwqkmPm57vvf5AV"),
    ("know-yourself.html", "Know yourself", "BiWch6C6JQdo3dK5HbAZ2J"),
    ("reading-test.html", "Reading test", "K6rUB5qQc5PdkKot6hzHoQ"),
    ("aryabhata-lab.html", "Aryabhata", "LaFFtHTwWZh7EiU6gL9F8Z"),
    ("indian-astronomy.html", "Indian astronomy", "Ud4noTfngQSDCp9kByDHYY"),
    ("nalanda.html", "Nalanda", "9GzdyyvJ8zRcBAznWXM37B"),
    ("starship-through-time.html", "Through time", "4jbD63EEZBxcEbE7WXseMN"),
    ("clues-in-old-books.html", "Old books", "RHr7yep3A95fUrPY78nS57"),
]

NAV_CSS = """<style>
.sa-nav{position:sticky;top:env(safe-area-inset-top,0px);z-index:50;background:rgba(4,6,11,.94);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);border-bottom:1px solid #1f2a38}
.sa-nav .sa-bar{max-width:1200px;margin:0 auto;display:flex;align-items:center;gap:4px;padding-block:6px;padding-left:max(12px,env(safe-area-inset-left,0px));padding-right:max(12px,env(safe-area-inset-right,0px))}
.sa-nav .sa-in{flex:1 1 auto;min-width:0;display:flex;align-items:center;gap:4px;overflow-x:auto;scrollbar-width:none;scroll-behavior:smooth;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 18px,#000 calc(100% - 18px),transparent 100%);mask-image:linear-gradient(90deg,transparent 0,#000 18px,#000 calc(100% - 18px),transparent 100%);padding:2px 6px}
.sa-nav .sa-in::-webkit-scrollbar{display:none}
.sa-nav a{flex:none;font-family:"Saira Condensed","Arial Narrow",sans-serif;font-weight:600;font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:#a9b4c2;text-decoration:none;padding:5px 9px;border-radius:4px;white-space:nowrap}
.sa-nav a:hover{color:#e7edf3;background:#121a25}
.sa-nav a:focus-visible,.sa-nav button:focus-visible{outline:2px solid #e8c46a;outline-offset:1px}
.sa-nav a[aria-current="page"]{color:#0a0d12;background:#e7edf3}
.sa-nav a.sa-brand{color:#ffa24a;font-weight:700;font-size:15px;margin-right:2px}
.sa-nav a.sa-brand[aria-current="page"]{color:#0a0d12;background:#ffa24a}
.sa-nav button{flex:none;font:600 14px "Saira Condensed","Arial Narrow",sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#e7edf3;background:#121a25;border:1px solid #2c3a4d;border-radius:4px;cursor:pointer;padding:5px 10px;line-height:1.2}
.sa-nav .sa-arr{padding:5px 8px;font-size:16px}.sa-nav .sa-arr[disabled]{opacity:.3;cursor:default}
.sa-nav .sa-all[aria-expanded="true"]{background:#e8c46a;color:#1b1404;border-color:#e8c46a}
.sa-nav .sa-panel{max-width:1200px;margin:0 auto;padding:6px max(12px,env(safe-area-inset-right,0px)) 12px max(12px,env(safe-area-inset-left,0px));display:flex;flex-wrap:wrap;gap:4px;max-height:70vh;overflow:auto}
.sa-nav .sa-panel[hidden]{display:none}
.sa-nav .sa-panel a{background:#0b1017;border:1px solid #1f2a38}.sa-nav .sa-panel a[aria-current="page"]{background:#e7edf3;color:#0a0d12;border-color:#e7edf3}
@media (max-width:560px){.sa-nav .sa-arr{display:none}}
@media print{.sa-nav{display:none}}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:60;background:#04060b}
</style>
"""

NAV_JS = """<script>
(()=>{const n=document.currentScript.previousElementSibling,s=n.querySelector('.sa-in'),[l,r]=n.querySelectorAll('.sa-arr'),b=n.querySelector('.sa-all'),p=n.querySelector('.sa-panel');
const upd=()=>{l.disabled=s.scrollLeft<=2;r.disabled=s.scrollLeft+s.clientWidth>=s.scrollWidth-2};
l.onclick=()=>{s.scrollLeft-=s.clientWidth*0.7};r.onclick=()=>{s.scrollLeft+=s.clientWidth*0.7};
s.addEventListener('scroll',upd,{passive:true});addEventListener('resize',upd);
s.addEventListener('wheel',e=>{if(Math.abs(e.deltaY)>Math.abs(e.deltaX)&&s.scrollWidth>s.clientWidth){s.scrollLeft+=e.deltaY;e.preventDefault()}},{passive:false});
const c=s.querySelector('[aria-current]');if(c)s.scrollLeft=c.offsetLeft-s.clientWidth/2+c.offsetWidth/2;upd();
const close=()=>{p.hidden=true;b.setAttribute('aria-expanded','false')};
b.onclick=()=>{const o=p.hidden;p.hidden=!o;b.setAttribute('aria-expanded',String(o));if(o){const a=p.querySelector('a');if(a)a.focus()}};
addEventListener('keydown',e=>{if(e.key==='Escape'&&!p.hidden){close();b.focus()}});
addEventListener('click',e=>{if(!p.hidden&&!n.contains(e.target))close()})})();
</script>
"""


def nav_html(current: str) -> str:
    links, brand = [], ""
    for i, (fname, label, _) in enumerate(PAGES):
        cur = ' aria-current="page"' if fname == current else ""
        if i == 0:
            brand = f'<a href="{fname}" class="sa-brand"{cur}>Golapada</a>'
            continue
        links.append(f'<a href="{fname}"{cur}>{label}</a>')
    tabs = "".join(links)
    return ('<nav class="sa-nav" aria-label="Golapada">'
            f'<div class="sa-bar">{brand}<button type="button" class="sa-arr" aria-label="Scroll the lab list left">‹</button>'
            f'<div class="sa-in">{tabs}</div>'
            '<button type="button" class="sa-arr" aria-label="Scroll the lab list right">›</button>'
            '<button type="button" class="sa-all" aria-expanded="false">All labs</button></div>'
            f'<div class="sa-panel" hidden>{tabs}</div></nav>\n' + NAV_JS)


# Hindi versions: <page>.hi.html, built when present, reached from a switch on the English page
# (not in the navigation bar). Machine-assisted translations; each says so at the top.
HINDI = ["gaganyaan-lab", "chandrayaan-3", "launch-watch", "eclipse-lab", "tonight"]
LANG_SWITCH = ('<p style="max-width:1200px;margin:10px auto 0;padding:0 max(16px,env(safe-area-inset-left,0px));'
               'font:500 14px/1.4 \'IBM Plex Sans\',system-ui,sans-serif;text-align:right">'
               '<a href="{href}" lang="hi" style="color:#74c7ff">हिन्दी में पढ़ें</a></p>')


def build() -> None:
    OUT.mkdir(exist_ok=True)
    id_to_file = {aid: fname for fname, _, aid in PAGES}
    hindi = [f"{p}.hi.html" for p in HINDI if (HERE / f"{p}.hi.html").exists()]
    for fname in [f for f, _, _ in PAGES] + hindi:
        src = (HERE / fname).read_text(encoding="utf-8")
        hi = fname.replace(".html", ".hi.html")
        if hi in hindi:
            # the English page offers its Hindi version just under the navigation
            src = src.replace('<div class="wrap">', LANG_SWITCH.format(href=hi) + '<div class="wrap">', 1)
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
    icons = [(192, False), (512, False), (512, True)]
    try:
        import PIL  # noqa: F401  (drawing the icons needs Pillow)
        for n, m in icons:
            draw_icon(n, m).convert("RGB").save(WEB / (f"icon-maskable-{n}.png" if m else f"icon-{n}.png"), optimize=True)
    except ImportError:
        # The daily GitHub Action has no Pillow. The icons never change, so the committed ones are kept.
        missing = [f"icon-maskable-{n}.png" if m else f"icon-{n}.png" for n, m in icons
                   if not (WEB / (f"icon-maskable-{n}.png" if m else f"icon-{n}.png")).exists()]
        if missing:
            raise SystemExit(f"Pillow is needed to draw the missing app icons: {', '.join(missing)}")
        print("Pillow not installed: keeping the existing app icons")
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
