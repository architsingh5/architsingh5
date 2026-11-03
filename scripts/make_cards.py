"""Generate the README cards (dark + light):

  assets/toolbox-{dark,light}.svg  - tech chips with icons
  assets/solving-{dark,light}.svg  - LeetCode + GeeksforGeeks stats

LeetCode numbers come from data/leetcode.json, which scripts/update_leetcode.py
refreshes weekly. GeeksforGeeks has no public API, so its numbers live in GFG below.
Run: python3 scripts/make_cards.py
"""
import json
import os
import re
from xml.sax.saxutils import escape

ROOT = os.path.join(os.path.dirname(__file__), "..")
ASSETS = os.path.join(ROOT, "assets")

GFG = {"solved": 213, "score": 649, "rank": 1002,
       "difficulty": [("Basic", 12), ("Easy", 57), ("Medium", 131), ("Hard", 13)]}

THEMES = {
    "dark": dict(bg="#0d0f12", surface="#171b21", line="#262b33", text="#e8e6e1", muted="#9aa0a8",
                 accent="#f5a524", basic="#6b7280", easy="#199e70", med="#3987e5", hard="#e66767"),
    "light": dict(bg="#f7f5f0", surface="#ffffff", line="#e1ddd2", text="#16181c", muted="#5b616b",
                  accent="#b45f00", basic="#8a8f98", easy="#1baf7a", med="#2a78d6", hard="#e34948"),
}
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"


def load_icons():
    """Icon symbols (Simple Icons CC0 + Lucide ISC), stored as viewBox-24 SVG fragments."""
    s = open(os.path.join(ASSETS, "icons.svg")).read()
    return {m.group(1): m.group(2) for m in re.finditer(r'<symbol id="([^"]+)" viewBox="0 0 24 24">(.*?)</symbol>', s, re.S)}


TOOLS = [
    ("java", "Java"), ("python", "Python"), ("cpp", "C++"), ("kotlin", "Kotlin"),
    ("kafka", "Apache Kafka"), ("spark", "Apache Spark"), ("sql", "SQL"), ("snowflake", "Snowflake"),
    ("db", "IBM DB2"), ("ems", "TIBCO EMS / RV"), ("postgresql", "PostgreSQL"), ("redis", "Redis"),
    ("docker", "Docker"), ("linux", "Linux"), ("bash", "Shell"), ("git", "Git"),
    ("claude", "Claude Code"), ("codex", "OpenAI Codex"), ("copilot", "GitHub Copilot"), ("mcp", "MCP"),
]


def frame(t, w, h, body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
  <title>{escape(title)}</title>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="16" fill="{t["bg"]}" stroke="{t["line"]}"/>
{body}
</svg>
'''


def toolbox(t, icons):
    cols, cw, ch, gx, gy, pad = 4, 196, 46, 12, 12, 24
    rows = (len(TOOLS) + cols - 1) // cols
    w = pad * 2 + cols * cw + (cols - 1) * gx
    h = pad * 2 + rows * ch + (rows - 1) * gy
    out = []
    for i, (ic, label) in enumerate(TOOLS):
        r, c = divmod(i, cols)
        x, y = pad + c * (cw + gx), pad + r * (ch + gy)
        frag = icons[ic].replace("currentColor", t["muted"])
        out.append(
            f'  <g transform="translate({x} {y})">'
            f'<rect width="{cw}" height="{ch}" rx="23" fill="{t["surface"]}" stroke="{t["line"]}"/>'
            f'<g transform="translate(15 12) scale(0.9167)">{frag}</g>'
            f'<text x="46" y="28.5" font-family="{SANS}" font-size="15" fill="{t["text"]}">{escape(label)}</text></g>'
        )
    return frame(t, w, h, "\n".join(out), "Toolbox: " + ", ".join(l for _, l in TOOLS))


def seg_bar(t, x, y, w, parts):
    total = sum(v for _, v in parts) or 1
    colors = {"Basic": t["basic"], "Easy": t["easy"], "Medium": t["med"], "Hard": t["hard"]}
    gap, out, cx = 2, [], x
    avail = w - gap * (len([p for p in parts if p[1]]) - 1)
    for name, v in parts:
        if not v:
            continue
        pw = max(4, avail * v / total)
        out.append(f'<rect x="{cx:.1f}" y="{y}" width="{pw:.1f}" height="12" rx="4" fill="{colors[name]}"><title>{name}: {v}</title></rect>')
        cx += pw + gap
    return "".join(out)


def legend(t, x, y, parts, colw):
    colors = {"Basic": t["basic"], "Easy": t["easy"], "Medium": t["med"], "Hard": t["hard"]}
    out = []
    for i, (name, v) in enumerate(parts):
        cx = x + (i % 2) * colw
        cy = y + (i // 2) * 22
        out.append(
            f'<rect x="{cx}" y="{cy - 10}" width="11" height="11" rx="3" fill="{colors[name]}"/>'
            f'<text x="{cx + 18}" y="{cy}" font-family="{SANS}" font-size="14" fill="{t["muted"]}">{name} '
            f'<tspan font-family="{MONO}" fill="{t["text"]}" font-weight="600">{v:,}</tspan></text>'
        )
    return "".join(out)


def panel(t, x, title, big, sub, parts, stats):
    bw = 360
    num = f"{big:,}"
    tx = x + 10 + len(num) * 33
    out = [
        f'<text x="{x}" y="46" font-family="{MONO}" font-size="13" letter-spacing="1" fill="{t["accent"]}">{escape(title.upper())}</text>',
        f'<text x="{x}" y="110" font-family="{SANS}" font-size="58" font-weight="700" letter-spacing="-2" fill="{t["text"]}">{num}</text>',
        f'<text x="{tx}" y="94" font-family="{SANS}" font-size="15" fill="{t["muted"]}">problems solved</text>',
        f'<text x="{tx}" y="112" font-family="{MONO}" font-size="12.5" fill="{t["muted"]}">{escape(sub)}</text>',
        seg_bar(t, x, 134, bw, parts),
        legend(t, x, 176, parts, 150),
    ]
    for i, (lbl, val) in enumerate(stats):
        sx = x + i * 128
        out.append(
            f'<text x="{sx}" y="244" font-family="{SANS}" font-size="13" fill="{t["muted"]}">{escape(lbl)}</text>'
            f'<text x="{sx}" y="270" font-family="{SANS}" font-size="21" font-weight="700" fill="{t["text"]}">{escape(val)}</text>'
        )
    return "\n  ".join(out)


def solving(t, lc):
    w, h = 880, 312
    lc_parts = [(d["name"], d["solved"]) for d in lc["difficulty"]]
    top = lc["languages"][0]
    lc_stats = [("Global rank", f'{lc["ranking"]:,}'), ("Badges", str(lc["badges"])), (f"in {top['name']}", f'{top["solved"]:,}')]
    gfg_stats = [("Coding score", f'{GFG["score"]:,}'), ("Institute rank", f'{GFG["rank"]:,}')]
    acc = f'{lc["acceptance"]}% acceptance' if lc.get("acceptance") is not None else ""
    hard = dict(GFG["difficulty"])
    body = "\n  ".join([
        panel(t, 32, "LeetCode", lc["solved"], acc, lc_parts, lc_stats),
        f'<line x1="440" y1="32" x2="440" y2="{h - 32}" stroke="{t["line"]}"/>',
        panel(t, 476, "GeeksforGeeks", GFG["solved"], f'{hard["Hard"]} hard · {hard["Medium"]} medium', GFG["difficulty"], gfg_stats),
        f'<text x="{w - 24}" y="{h - 14}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{t["muted"]}">LeetCode refreshed {escape(lc["updated"])}</text>',
    ])
    total = lc["solved"] + GFG["solved"]
    return frame(t, w, h, "  " + body, f"Problem solving: {total:,} problems; LeetCode {lc['solved']}, GeeksforGeeks {GFG['solved']}")


def main():
    icons = load_icons()
    lc = json.load(open(os.path.join(ROOT, "data", "leetcode.json")))
    for name, t in THEMES.items():
        open(os.path.join(ASSETS, f"toolbox-{name}.svg"), "w").write(toolbox(t, icons))
        open(os.path.join(ASSETS, f"solving-{name}.svg"), "w").write(solving(t, lc))
    print("wrote toolbox-*.svg, solving-*.svg")


if __name__ == "__main__":
    main()
