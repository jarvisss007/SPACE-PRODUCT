"""Fill the Space Day kit's quiz rounds from the labs' own quizzes.

Each round takes questions from quizzes/<lab>.json in the order listed, so the
rounds stay in step with the labs. Writes the JSON between
<!-- space-day-rounds:start --> and <!-- space-day-rounds:end --> in space-day.html.

Run:  py -I tools/make_space_day.py
"""
from pathlib import Path
import html, json, re

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "space-day.html"
START, END = "<!-- space-day-rounds:start -->", "<!-- space-day-rounds:end -->"

# (round title, [(lab, which questions: "plain" = not history, "history", or a list of indexes)])
ROUNDS = [
    ("India in space", [("chandrayaan-3", [0, 1]), ("gaganyaan-lab", [0, 1]), ("isro-launches", [0]), ("navic-lab", [0])]),
    ("Sky and Sun", [("space-weather", [0, 1]), ("tonight", [2]), ("eclipse-lab", [0, 1]), ("meteor-showers", [0])]),
    ("From Aryabhata to Aditya-L1", [(lab, "history") for lab in
        ("aryabhata-lab", "nalanda", "eclipse-lab", "clues-in-old-books", "gaganyaan-lab", "voyager-now", "lagrange-lab")]),
]


def lab_title(lab: str) -> str:
    m = re.search(r"<title>(.*?)</title>", (ROOT / f"{lab}.html").read_text(encoding="utf-8"), re.S)
    return html.unescape(m.group(1).strip()) if m else lab


def main() -> None:
    out = []
    for title, picks in ROUNDS:
        qs, used = [], []
        for lab, which in picks:
            data = json.loads((ROOT / "quizzes" / f"{lab}.json").read_text(encoding="utf-8"))["questions"]
            if which == "history":
                chosen = [q for q in data if q.get("history")][:1]
            else:
                chosen = [data[i] for i in which]
            name = lab_title(lab)
            for q in chosen:
                qs.append({"q": q["q"], "a": q["a"], "history": bool(q.get("history")), "lab": name})
            used.append(name)
        out.append({"title": title, "from": used, "questions": qs})
    block = (f'{START}\n<script type="application/json" id="rounds">'
             + json.dumps(out, ensure_ascii=False).replace("</", "<\\/") + f"</script>\n{END}")
    src = PAGE.read_text(encoding="utf-8")
    src = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: block, src, count=1, flags=re.S)
    PAGE.write_text(src, encoding="utf-8")
    print("space-day rounds:", ", ".join(f"{r['title']} ({len(r['questions'])})" for r in out))


if __name__ == "__main__":
    main()
