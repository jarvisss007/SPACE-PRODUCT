"""Make a lab easy for anyone: plain words first, details one click away.

For each page with a file simple/<page>.json, this tool
  1. writes an "In simple words" card right after the page's header
     (between <!-- golapada-simple:start --> and <!-- golapada-simple:end -->,
     so running it again replaces it), and
  2. folds the technical sections ("How far to trust it", "Checks",
     "What the model leaves out" and similar) into "For experts" buttons.

simple/<page>.json looks like:
    {
      "lead":   "One or two short sentences: what this page shows, in everyday words.",
      "try":    "The first thing to do on the page.",
      "points": ["Three short takeaways", "in plain words", "no jargon"]
    }
Write for a curious 12-year-old: short sentences, everyday words, no symbols or
units without explaining them. Simple HTML (<b>, <i>) is allowed.

Hindi pages: simple/<page>.hi.json (for <page>.hi.html) gets the card's labels
in Hindi too, and the technical sections fold under "विशेषज्ञों के लिए".

Run:  py -I tools/simplify.py              (every page that has a simple/*.json)
      py -I tools/simplify.py rocket-lab   (one page)
"""
from pathlib import Path
import html
import json
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SDIR = ROOT / "simple"
START, END = "<!-- golapada-simple:start -->", "<!-- golapada-simple:end -->"
EXPERT = re.compile(r"^(How far to trust|Checks|What (the|this) (model|page) leaves out|What the sources say"
                    r"|इस पर कितना भरोसा|(यह )?(मॉडल|पृष्ठ) (क्या|किन बातों को) छोड़)", re.I)

STYLE = """<style>
.gs{background:linear-gradient(180deg,#14202c,#0e1620);border:1px solid #2c3a4d;border-left:5px solid #e8c46a;border-radius:8px;padding:16px 18px;min-width:0}
.gs .gs-k{font:700 13px/1 "Saira Condensed","Arial Narrow",sans-serif;letter-spacing:.16em;text-transform:uppercase;color:#e8c46a;margin-bottom:8px}
.gs .gs-lead{font-size:17.5px;line-height:1.5;color:#f1f5f9;margin:0 0 10px;max-width:70ch}
.gs .gs-try{font-size:15.5px;color:#e7edf3;background:#0b1017;border-radius:6px;padding:10px 12px;margin:0 0 10px}.gs .gs-try b{color:#5fd6a0}
.gs ul{margin:0;padding-left:20px}.gs li{font-size:15.5px;line-height:1.5;color:#d6dde5;margin:5px 0}
details.gx>summary{cursor:pointer;font:700 19px "Saira Condensed","Arial Narrow",sans-serif;text-transform:uppercase;color:#74c7ff;list-style:none}
details.gx>summary::before{content:"▸ ";color:#e8c46a}details.gx[open]>summary::before{content:"▾ "}
details.gx>summary:focus-visible{outline:2px solid #74c7ff;outline-offset:2px}
@media print{.gs{background:#fff;border-color:#999}.gs .gs-lead,.gs li,.gs .gs-try{color:#000;background:#fff}}
</style>"""


# The card's own words, by page language: simple/<page>.hi.json makes a Hindi card.
TEXT = {
    "en": {"k": "In simple words", "try": "Try this first:", "exp": "For experts:", "lang": ""},
    "hi": {"k": "आसान शब्दों में", "try": "पहले यह करके देखें:", "exp": "विशेषज्ञों के लिए:", "lang": ' lang="hi"'},
}


def card(d: dict, T: dict) -> str:
    pts = "".join(f"<li>{p}</li>" for p in d["points"])
    return (f"{START}\n{STYLE}\n<section class=\"gs\"{T['lang']} aria-label=\"{T['k']}\"><div class=\"gs-k\">{T['k']}</div>"
            f"<p class=\"gs-lead\">{d['lead']}</p><p class=\"gs-try\"><b>{T['try']}</b> {d['try']}</p><ul>{pts}</ul></section>\n{END}")


def fold_expert(src: str, label: str = "For experts:") -> str:
    """Turn technical <section class="card"> blocks into <details> 'For experts' buttons."""
    out, i = [], 0
    # any <section> whose class list holds "card", whatever the attribute order
    pat = re.compile(r'<section\b([^>]*)>(\s*)<h2>([^<]*)</h2>', re.S)
    while True:
        m = pat.search(src, i)
        if not m:
            out.append(src[i:])
            break
        title = html.unescape(m.group(3)).strip()
        end = src.find("</section>", m.end())
        nxt = src.find("<section", m.end())
        cls = re.search(r'\bclass="([^"]*)"', m.group(1))
        if (not cls or "card" not in cls.group(1).split() or not EXPERT.match(title)
                or end < 0 or (0 <= nxt < end)):
            out.append(src[i:m.end()])
            i = m.end()
            continue
        out.append(src[i:m.start()])
        attrs = m.group(1)[:cls.start()] + f'class="{cls.group(1)} gx"' + m.group(1)[cls.end():]
        out.append(f'<details{attrs}><summary>{label} {m.group(3)}</summary>{src[m.end():end]}</details>')
        i = end + len("</section>")
    return "".join(out)


def apply(name: str) -> bool:
    page, data = ROOT / f"{name}.html", SDIR / f"{name}.json"
    if not page.exists() or not data.exists():
        print(f"skipped {name}: page or simple/{name}.json missing")
        return False
    d = json.loads(data.read_text(encoding="utf-8"))
    assert d.get("lead") and d.get("try") and len(d.get("points", [])) >= 2, f"{name}: lead, try and 2+ points needed"
    T = TEXT["hi" if name.endswith(".hi") else "en"]
    src = page.read_text(encoding="utf-8")
    # remove the old card together with the spacing that was added with it, so a re-run changes nothing
    src = re.sub(r"(?:\n\n  )?" + re.escape(START) + r".*?" + re.escape(END) + r"\n?(?:  (?=<section))?", "", src, flags=re.S)
    block = card(d, T) + "\n"
    if "</header>" in src:
        src = src.replace("</header>", "</header>\n\n  " + block, 1)
    else:  # pages without a header: before the first section
        k = src.find("<section", src.find('<div class="wrap">'))
        src = src[:k] + block + "  " + src[k:]
    src = fold_expert(src, T["exp"])
    page.write_text(src, encoding="utf-8")
    print(f"simplified {name}")
    return True


def main(argv: list[str]) -> int:
    names = argv or sorted(p.stem for p in SDIR.glob("*.json"))
    ok = sum(apply(n) for n in names)
    print(f"{ok} page(s) done")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
