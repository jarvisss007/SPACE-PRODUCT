"""Build the Golapada website from the app pages in this folder.

Reads every app page, adds a shared navigation bar, turns links between the
apps into relative links, and writes the result to ./site/. The app files
themselves are left untouched, so each can still be published on its own.

Run:  py build_site.py
"""
from pathlib import Path
import json
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
    ("about.html", "About", "Sr4HjpkwPpx5d1mojsoH2v"),
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


# "Keep exploring": three related labs at the foot of every lab, so no page is a dead end.
# Titles and one-line descriptions come from the home page's list in tools/make_index.py.
RELATED = {
    "tonight.html": ["satellite-watch.html", "meteor-showers.html", "kundli.html"],
    "earth-from-above.html": ["satellite-watch.html", "space-weather.html", "iss-life.html"],
    "satellite-watch.html": ["iss-life.html", "navic-lab.html", "space-debris-lab.html"],
    "space-weather.html": ["touch-the-sun.html", "lagrange-lab.html", "earth-from-above.html"],
    "meteor-showers.html": ["comets.html", "tonight.html", "asteroid-watch.html"],
    "asteroid-watch.html": ["planetary-defense-lab.html", "comets.html", "meteor-showers.html"],
    "eclipse-lab.html": ["tonight.html", "indian-astronomy.html", "clues-in-old-books.html"],
    "isro-launches.html": ["launch-watch.html", "rocket-lab.html", "space-startups.html"],
    "launch-watch.html": ["isro-launches.html", "space-startups.html", "rocket-lab.html"],
    "starship-catch.html": ["rocket-lab.html", "reentry-lab.html", "mars-campaign.html"],
    "rocket-lab.html": ["isro-launches.html", "starship-catch.html", "ion-engine-lab.html"],
    "navic-lab.html": ["satellite-watch.html", "space-startups.html", "isro-launches.html"],
    "space-debris-lab.html": ["satellite-watch.html", "reentry-lab.html", "space-startups.html"],
    "gaganyaan-lab.html": ["iss-life.html", "reentry-lab.html", "isro-launches.html"],
    "chandrayaan-3.html": ["moon-sites.html", "mangalyaan.html", "gaganyaan-lab.html"],
    "mangalyaan.html": ["mars-now.html", "gravity-assist-lab.html", "chandrayaan-3.html"],
    "mars-landing-lab.html": ["mars-now.html", "reentry-lab.html", "mars-campaign.html"],
    "mars-campaign.html": ["mars-now.html", "mars-landing-lab.html", "starship-catch.html"],
    "solar-system-lab.html": ["gravity-assist-lab.html", "comets.html", "exoplanet-explorer.html"],
    "gravity-assist-lab.html": ["voyager-now.html", "touch-the-sun.html", "solar-system-lab.html"],
    "ion-engine-lab.html": ["rocket-lab.html", "gravity-assist-lab.html", "space-startups.html"],
    "touch-the-sun.html": ["space-weather.html", "lagrange-lab.html", "gravity-assist-lab.html"],
    "lagrange-lab.html": ["touch-the-sun.html", "telescope-lab.html", "space-weather.html"],
    "voyager-now.html": ["gravity-assist-lab.html", "spacecraft-archive.html", "milky-way-atlas.html"],
    "milky-way-atlas.html": ["exoplanet-explorer.html", "black-hole-lab.html", "telescope-lab.html"],
    "telescope-lab.html": ["eht-lab.html", "exoplanet-explorer.html", "lagrange-lab.html"],
    "exoplanet-explorer.html": ["telescope-lab.html", "milky-way-atlas.html", "solar-system-lab.html"],
    "black-hole-lab.html": ["eht-lab.html", "milky-way-atlas.html", "telescope-lab.html"],
    "spacecraft-archive.html": ["voyager-now.html", "isro-launches.html", "moon-sites.html"],
    "reentry-lab.html": ["gaganyaan-lab.html", "mars-landing-lab.html", "space-debris-lab.html"],
    "one-sky-lab.html": ["space-startups.html", "moon-sites.html", "navic-lab.html"],
    "space-startups.html": ["launch-watch.html", "isro-launches.html", "one-sky-lab.html"],
    "mars-now.html": ["mars-landing-lab.html", "mangalyaan.html", "mars-campaign.html"],
    "iss-life.html": ["gaganyaan-lab.html", "satellite-watch.html", "reentry-lab.html"],
    "eht-lab.html": ["black-hole-lab.html", "telescope-lab.html", "milky-way-atlas.html"],
    "comets.html": ["meteor-showers.html", "asteroid-watch.html", "solar-system-lab.html"],
    "moon-sites.html": ["chandrayaan-3.html", "one-sky-lab.html", "eclipse-lab.html"],
    "planetary-defense-lab.html": ["asteroid-watch.html", "comets.html", "space-debris-lab.html"],
    "kundli.html": ["tonight.html", "reading-test.html", "indian-astronomy.html"],
    "know-yourself.html": ["reading-test.html", "kundli.html", "tonight.html"],
    "reading-test.html": ["know-yourself.html", "kundli.html", "clues-in-old-books.html"],
    "aryabhata-lab.html": ["indian-astronomy.html", "starship-through-time.html", "nalanda.html"],
    "indian-astronomy.html": ["aryabhata-lab.html", "clues-in-old-books.html", "eclipse-lab.html"],
    "nalanda.html": ["aryabhata-lab.html", "indian-astronomy.html", "clues-in-old-books.html"],
    "starship-through-time.html": ["aryabhata-lab.html", "mars-campaign.html", "indian-astronomy.html"],
    "clues-in-old-books.html": ["indian-astronomy.html", "eclipse-lab.html", "comets.html"],
}
EXPLORE_CSS = ("<style>.gk{min-width:0;margin-top:8px}"
               ".gk h2{font:700 clamp(20px,3vw,26px) 'Saira Condensed','Arial Narrow',sans-serif;text-transform:uppercase;color:#e7edf3;margin:0 0 10px}"
               ".gk .gk-g{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}"
               ".gk a{display:flex;flex-direction:column;gap:4px;text-decoration:none;background:#0b1017;border:1px solid #1f2a38;border-left:4px solid var(--k,#74c7ff);border-radius:6px;padding:12px 14px;min-width:0}"
               ".gk a:hover,.gk a:focus-visible{border-color:var(--k,#74c7ff);outline:none}"
               ".gk b{font:700 20px 'Saira Condensed','Arial Narrow',sans-serif;text-transform:uppercase;color:#e7edf3}"
               ".gk span{font:400 13.5px/1.45 'IBM Plex Sans',system-ui,sans-serif;color:#aeb9c6}"
               "@media print{.gk{display:none}}</style>")


def lab_cards() -> dict:
    """Title, description and colour of every lab, read from the home page's list."""
    src = (HERE / "tools" / "make_index.py").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'\(\s*"([a-z0-9\-]+\.html)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*,\s*"[^"]*"\s*,\s*"[^"]*"\s*,\s*\'(#[0-9a-fA-F]{3,6})\'\s*\)', src):
        out[m.group(1)] = (m.group(2).replace('\\"', '"'), m.group(3).replace('\\"', '"'), m.group(4))
    return out


def explore_html(fname: str, cards: dict) -> str:
    import html as h
    picks = [p for p in RELATED.get(fname, []) if p in cards and (HERE / p).exists()]
    if not picks:
        return ""
    items = "".join(f'<a href="{p}" style="--k:{cards[p][2]}"><b>{h.escape(cards[p][0])}</b><span>{h.escape(cards[p][1])}</span></a>'
                    for p in picks)
    return f'{EXPLORE_CSS}<section class="gk" aria-label="Keep exploring"><h2>Keep exploring</h2><div class="gk-g">{items}</div></section>\n'


# A thin strip at the very foot of every page: About, Privacy and a "Report a mistake" link that opens
# the GitHub issue form (.github/ISSUE_TEMPLATE/mistake.yml) with the page name filled in.
REPORT_URL = "https://github.com/jarvisss007/SPACE-PRODUCT/issues/new?template=mistake.yml&amp;page={page}&amp;title=Mistake%20on%20{page}"


def trust_strip(fname: str) -> str:
    hi = fname.endswith(".hi.html")
    about, priv, rep = ("परिचय", "निजता", "गलती बताएँ") if hi else ("About Golapada", "Privacy", "Report a mistake on this page")
    a = ' lang="hi"' if hi else ""
    return ('<p class="gt"' + a + ' style="max-width:1200px;margin:6px auto 0;padding:10px max(16px,env(safe-area-inset-left,0px)) 28px;'
            'border-top:1px solid #1f2a38;font:400 13px/1.6 \'IBM Plex Sans\',system-ui,sans-serif;color:#8a97a8">'
            f'<a href="about.html" style="color:#74c7ff">{about}</a> · <a href="about.html#privacy" style="color:#74c7ff">{priv}</a> · '
            f'<a href="{REPORT_URL.format(page=fname)}" rel="noopener" style="color:#74c7ff">{rep}</a></p>\n'
            # remember, in this browser only, that this lab was opened (ticks the guided paths on the home page)
            "<script>try{const k='golapada-seen',f=(location.pathname.split('/').pop()||'index.html').replace('.hi.html','.html'),"
            "a=JSON.parse(localStorage.getItem(k)||'[]');if(!a.includes(f)){a.push(f);localStorage.setItem(k,JSON.stringify(a.slice(-300)))}}catch(e){}</script>\n")


MONTHS = {m: i + 1 for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July",
                                           "August", "September", "October", "November", "December"])}


def today_data() -> str:
    """Data for the home page's "Today in space", rebuilt every day:
    onthis: {"MM-DD": [[year, title, page], ...]} from every "Then and now" entry that names a full date;
    neo: the coming week's asteroid passes [name, ISO time, Moon distances, size km] from Asteroid Watch."""
    import html as h, json, math
    from datetime import datetime, timedelta, timezone
    onthis = {}
    item = re.compile(r'<li[^>]*>\s*<details[^>]*>\s*<summary>(.*?)</summary>(.*?)</details>', re.S)
    date = re.compile(r'\b(\d{1,2}) (' + "|".join(MONTHS) + r') (\d{4})\b')
    for fname, _, _ in PAGES:
        src = (HERE / fname).read_text(encoding="utf-8")
        k = src.find("<h2>Then and now</h2>")
        if k < 0:
            continue
        end = src.find("</section>", k)
        for m in item.finditer(src[k:end]):
            summary = m.group(1)
            ylab = re.search(r'<span class="y[^"]*">(.*?)</span>', summary, re.S)
            label = h.unescape(ylab.group(1)) if ylab else re.sub(r"<[^>]+>", " ", summary)[:12]
            # the entry's own year(s): "1978", "2023–24" -> 2023, 2024; only dates in those years count
            years = set(re.findall(r"\d{4}", label))
            for a, b in re.findall(r"(\d{4})\s*[–-]\s*(\d{2})\b", label):
                years.add(a[:2] + b)
            title = h.unescape(re.sub(r"<[^>]+>", " ", re.sub(r'<span class="(y|tag)[^"]*">.*?</span>', "", summary, flags=re.S)))
            title = re.sub(r"\s+", " ", title).replace("+", "").strip()
            title = re.sub(r"^(\d{4}(\s*[–-]\s*\d{2,4})?|~?\d{3,4}s?)\s+", "", title)  # drop a repeated year
            text = re.sub(r"<[^>]+>", " ", m.group(0))
            for d in date.finditer(text):
                day, mon, yr = int(d.group(1)), MONTHS[d.group(2)], d.group(3)
                before = text[max(0, d.start() - 12):d.start()].lower()
                if not 1 <= day <= 31 or (years and yr not in years) or "as of" in before or "until" in before:
                    continue
                row = [yr, title, fname]
                lst = onthis.setdefault(f"{mon:02d}-{day:02d}", [])
                if not any(r[1] == title for r in lst):
                    lst.append(row)
    for lst in onthis.values():
        lst.sort(key=lambda r: r[0])
    neo = []
    aw = (HERE / "asteroid-watch.html").read_text(encoding="utf-8")
    m = re.search(r"^const NEO=(\{.*?\});$", aw, re.M)
    if m:
        now = datetime.now(timezone.utc)
        for des, cd, dist, _v, hmag, diam in json.loads(m.group(1)).get("close", []):
            t = datetime.strptime(cd, "%Y-%b-%d %H:%M").replace(tzinfo=timezone.utc)
            if now - timedelta(days=1) <= t <= now + timedelta(days=8):
                size = diam if diam else (1329 / math.sqrt(0.14) * 10 ** (-hmag / 5) if hmag else None)
                neo.append([des, t.strftime("%Y-%m-%dT%H:%MZ"), round(dist / 0.00256956, 2), round(size, 3) if size else None])
    # question of the day: every English lab quiz question, with its answer and lab
    quiz = []
    for f in sorted((HERE / "quizzes").glob("*.json")):
        if f.stem.endswith(".hi") or not (HERE / f"{f.stem}.html").exists():
            continue
        for q in json.loads(f.read_text(encoding="utf-8")).get("questions", []):
            quiz.append([q["q"], q["a"], f"{f.stem}.html"])
    # coming up in the sky: meteor shower peaks (Meteor Showers' own list) and the total solar eclipses in the Eclipse Lab
    showers = []
    ms = (HERE / "meteor-showers.html").read_text(encoding="utf-8")
    for nm, mo, dy, zhr in re.findall(r"\['[A-Z]{3}','([^']+)',(\d+),(\d+),[^,]+,[^,]+,[^,]+,(null|\d+),", ms):
        showers.append([nm, int(mo), int(dy), None if zhr == "null" else int(zhr)])
    ecl = (HERE / "eclipse-lab.html").read_text(encoding="utf-8")
    mon3 = {m[:3]: i for m, i in MONTHS.items()}
    eclipses = sorted({(f"{y}-{mon3[mo]:02d}-{d}", label) for y, mo, d, label in
                       re.findall(r"'(\d{4})([A-Z][a-z]{2})(\d{2})T':'(\d{1,2} [A-Za-z]+ \d{4} · total · [^']+)'", ecl)})
    return json.dumps({"onthis": onthis, "neo": neo, "quiz": quiz, "showers": showers, "eclipses": [list(e) for e in eclipses]},
                      ensure_ascii=False, separators=(",", ":"))


def build() -> None:
    cards = lab_cards()
    today = today_data()
    missing = [f for f in RELATED if f not in cards] + [p for v in RELATED.values() for p in v if p not in cards]
    if missing:
        print(f"note: no home-page card for {sorted(set(missing))}")
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
        if fname == "index.html":
            src = src.replace("/*golapada-today*/null", today, 1)
        if fname in RELATED:  # English labs only; the Hindi pages keep their own endings
            k = src.rfind("<footer")
            block = explore_html(fname, cards)
            if k > 0 and block:
                src = src[:k] + block + src[k:]  # inside the page's own column, just above its sources
        # tables in side-scrolling boxes: reachable and scrollable with the keyboard (WCAG), named for screen readers
        src = re.sub(r'<div class="scroll"(?![^>]*tabindex)',
                     '<div class="scroll" tabindex="0" role="region" aria-label="Table (scrolls sideways on small screens)"', src)
        src = src.rstrip() + "\n" + trust_strip(fname)  # after the page's own column, at the very foot
        if fname != "index.html" and not src.lstrip().lower().startswith("<!doctype"):
            # extra pages are served without the artifact skeleton, so they need their own doctype
            src = "<!doctype html>\n" + src
        # claude.ai copies cannot fetch side files, so their data goes back inside the page
        (OUT / fname).write_text(inline_data(src), encoding="utf-8")
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
    copy_data()
    write_offline_zip()
    write_app()


# ---- big catalogues live in data/ and load after the page appears ----
# A page marks where its data goes with /*golapada-data:NAME*/null (NAME = data/NAME.json).
# The website (docs/) fetches data/NAME.json; claude.ai copies (site/) and the offline zip,
# which cannot fetch side files, get the data written straight into the page.
DATA = HERE / "data"
DATA_MARK = re.compile(r"/\*golapada-data:([a-z0-9-]+)\*/null")


def inline_data(src: str) -> str:
    import base64

    def fill(m):
        d = json.loads((DATA / f"{m.group(1)}.json").read_text(encoding="utf-8"))
        if isinstance(d, dict):  # image lists point at files in data/; embed them
            for v in d.values():
                if isinstance(v, dict) and str(v.get("src", "")).startswith("data/"):
                    f = HERE / v["src"]
                    mime = "image/jpeg" if f.suffix.lower() in (".jpg", ".jpeg") else f"image/{f.suffix[1:].lower()}"
                    v["src"] = f"data:{mime};base64," + base64.b64encode(f.read_bytes()).decode()
        return json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return DATA_MARK.sub(fill, src)


def copy_data() -> None:
    """Mirror data/ into docs/data/ (removing files that are gone from data/)."""
    import shutil
    dst = WEB / "data"
    if dst.exists():
        shutil.rmtree(dst)
    if DATA.exists():
        shutil.copytree(DATA, dst)
        n = sum(1 for p in dst.rglob("*") if p.is_file())
        print(f"copied data/ ({n} files)")


def data_files() -> list:
    d = WEB / "data"
    return sorted(p.relative_to(WEB).as_posix() for p in d.rglob("*") if p.is_file()) if d.exists() else []


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
            # opened from a folder, a page cannot fetch data/; give it its data inline
            z.writestr(info, inline_data(p.read_text(encoding="utf-8")).encode("utf-8"))
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
    data = data_files()
    for name in pages + data:
        h.update((WEB / name).read_bytes())
    # data/ catalogues (about 1.4 MB) are not downloaded on install: phones on mobile data fetch them
    # only when that lab is opened, and the fetch handler then keeps a copy for offline use
    files = ["./"] + pages + ["manifest.webmanifest", "icon-192.png", "icon-512.png"]
    (WEB / "sw.js").write_text(SW.replace("__V__", "golapada-" + h.hexdigest()[:12]).replace("__PAGES__", json.dumps(files)), encoding="utf-8")
    print(f"built app: manifest, 3 icons, sw.js caching {len(files)} files")


if __name__ == "__main__":
    build()
