"""Write each lab's quiz into its page from quizzes/<page>.json.

Quiz data (one file per lab, named after the page):
    {
      "questions": [
        {"q": "Question text",
         "do": "What to do in the lab to find the answer",
         "a": "The answer, with the number or reasoning",
         "history": false},
        ... exactly five, one or two with "history": true ...
      ]
    }
HTML is allowed in q, do and a (for <b>, <i>, <sub>, <sup>).

The quiz is written between <!-- golapada-quiz:start --> and <!-- golapada-quiz:end -->
just before the page's <footer>, so running this again replaces it. Pages stay
self-contained (the small renderer is inline), so each still works on its own.

Run:  py -I tools/add_quiz.py            (all quizzes)
      py -I tools/add_quiz.py rocket-lab (one page)
"""
from pathlib import Path
import html, json, re, sys

ROOT = Path(__file__).resolve().parent.parent
QDIR = ROOT / "quizzes"
START, END = "<!-- golapada-quiz:start -->", "<!-- golapada-quiz:end -->"

STYLE = """<style>
.gq{background:#0b1017;border:1px solid #1f2a38;border-radius:6px;padding:16px;min-width:0}
.gq h2{font-family:"Saira Condensed","Noto Sans Devanagari","Arial Narrow",sans-serif;font-weight:700;font-size:clamp(20px,3vw,26px);margin:0 0 6px;text-transform:uppercase;color:#e7edf3}
.gq .gq-sub{font-size:13px;color:#8a97a8;margin:0 0 12px;max-width:76ch}
.gq ol{list-style:none;margin:0;padding:0;counter-reset:gq}
.gq li{counter-increment:gq;border-top:1px solid #1f2a38;padding:12px 0 10px 40px;position:relative}
.gq li::before{content:counter(gq);position:absolute;left:0;top:10px;width:28px;height:28px;border-radius:50%;background:#121a25;border:1px solid #2c3a4d;color:#e8c46a;font:700 15px/26px "Saira Condensed",sans-serif;text-align:center}
.gq .gq-q{font-size:15px;color:#e7edf3;margin:0 0 4px}
.gq .gq-do{font-size:13px;color:#8a97a8;margin:0 0 6px}.gq .gq-do b{color:#c3ccd6;font-weight:500}
.gq .gq-h{display:inline-block;font:600 11px/1 "Saira Condensed","Noto Sans Devanagari",sans-serif;letter-spacing:.12em;text-transform:uppercase;color:#1b1404;background:#e8c46a;border-radius:3px;padding:3px 6px;margin-right:6px;vertical-align:2px}
.gq details summary{cursor:pointer;font:600 13px "Saira Condensed","Noto Sans Devanagari",sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#74c7ff;width:max-content}
.gq details summary:focus-visible,.gq button:focus-visible{outline:2px solid #74c7ff;outline-offset:2px}
.gq details p{margin:6px 0 0;padding:8px 10px;background:#121a25;border-left:3px solid #5fd6a0;border-radius:3px;font-size:14px;color:#d5dde6;max-width:76ch}
.gq .gq-bar{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.gq button{font:600 13px "Saira Condensed","Noto Sans Devanagari",sans-serif;letter-spacing:.06em;text-transform:uppercase;color:#e7edf3;background:#121a25;border:1px solid #1f2a38;border-radius:4px;padding:6px 10px;cursor:pointer}
@media print{.gq{background:#fff;border-color:#bbb}.gq h2,.gq .gq-q,.gq details p{color:#000}.gq .gq-sub,.gq .gq-do{color:#333}.gq details p{background:#fff}.gq .gq-bar{display:none}}
</style>"""

# The quiz's own words, by page language: quizzes/<page>.hi.json makes a Hindi block.
TEXT = {
    "en": {"title": "Quiz: five questions", "lang": "",
           "sub": "Answer each one by using the lab above, then check. Good for a class: "
                  "pairs work through them, the teacher reveals the answers.",
           "do": "Use the lab:", "show": "Show answer", "hist": "History",
           "all": "Show all answers", "hide": "Hide all answers"},
    "hi": {"title": "प्रश्नोत्तरी: पाँच प्रश्न", "lang": ' lang="hi"',
           "sub": "हर प्रश्न का उत्तर ऊपर की प्रयोगशाला का उपयोग करके निकालें, फिर जाँचें। "
                  "क्लास के लिए: जोड़ियाँ प्रश्न हल करें, शिक्षक उत्तर दिखाएँ।",
           "do": "प्रयोगशाला में:", "show": "उत्तर देखें", "hist": "इतिहास",
           "all": "सभी उत्तर देखें", "hide": "सभी उत्तर छिपाएँ"},
}

SCRIPT = """<script>
(()=>{const s=document.currentScript.closest('.gq');const b=s.querySelector('.gq-all');b.addEventListener('click',()=>{const d=[...s.querySelectorAll('details')],open=!d.every(x=>x.open);d.forEach(x=>x.open=open);b.textContent=open?'%(hide)s':'%(all)s'})})();
</script>"""


def block(page: str, data: dict) -> str:
    T = TEXT["hi" if page.endswith(".hi") else "en"]
    qs = data["questions"]
    if len(qs) != 5:
        raise SystemExit(f"{page}: needs exactly 5 questions, has {len(qs)}")
    nh = sum(1 for q in qs if q.get("history"))
    if not 1 <= nh <= 2:
        raise SystemExit(f"{page}: needs 1 or 2 history questions, has {nh}")
    items = []
    for q in qs:
        for k in ("q", "do", "a"):
            if not q.get(k, "").strip():
                raise SystemExit(f"{page}: a question is missing '{k}'")
        tag = f'<span class="gq-h">{T["hist"]}</span>' if q.get("history") else ""
        items.append(
            f'<li><p class="gq-q">{tag}{q["q"]}</p>'
            f'<p class="gq-do"><b>{T["do"]}</b> {q["do"]}</p>'
            f'<details><summary>{T["show"]}</summary><p>{q["a"]}</p></details></li>')
    return (f"{START}\n{STYLE}\n<section class=\"gq\"{T['lang']} aria-labelledby=\"gq-title\">"
            f"<h2 id=\"gq-title\">{T['title']}</h2>"
            f"<p class=\"gq-sub\">{T['sub']}</p>"
            f"<ol>{''.join(items)}</ol>"
            f"<div class=\"gq-bar\"><button type=\"button\" class=\"gq-all\">{T['all']}</button></div>"
            f"{SCRIPT % T}</section>\n{END}\n")


def apply(page: str) -> None:
    path = ROOT / f"{page}.html"
    data = json.loads((QDIR / f"{page}.json").read_text(encoding="utf-8"))
    src = path.read_text(encoding="utf-8")
    new = block(page, data)
    if START in src:
        src = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n?", lambda m: new, src, count=1, flags=re.S)
    else:
        i = src.rfind("<footer")
        if i < 0:
            raise SystemExit(f"{page}: no <footer> to put the quiz before")
        line = src.rfind("\n", 0, i) + 1
        src = src[:line] + "  " + new + src[line:]
    path.write_text(src, encoding="utf-8")
    print(f"quiz written: {page}.html")


if __name__ == "__main__":
    pages = sys.argv[1:] or sorted(p.stem for p in QDIR.glob("*.json"))
    for p in pages:
        apply(p)
