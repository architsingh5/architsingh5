"""Generate the animated profile banner (dark + light) as self-contained SVGs.

The banner mirrors the portfolio hero: messages flowing through partitions,
with three highlighted lanes (orders, executions, clearing).
Run: python3 scripts/make_banner.py
"""
import os
import random

W, H = 1200, 300
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

THEMES = {
    "dark": dict(bg="#0d0f12", line="#262b33", text="#e8e6e1", muted="#9aa0a8",
                 accent="#f5a524", lane="rgba(255,255,255,0.06)", dim="#9aa0a8"),
    "light": dict(bg="#f7f5f0", line="#e1ddd2", text="#16181c", muted="#5b616b",
                  accent="#9a5000", lane="rgba(0,0,0,0.06)", dim="#8a8f98"),
}

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"


def build(t):
    rnd = random.Random(7)  # deterministic output, so regenerating gives a clean diff
    n_lanes = 9
    top, bottom = 46, H - 46
    lanes = [top + (bottom - top) * i / (n_lanes - 1) for i in range(n_lanes)]
    hot = {2, 4, 6}

    msgs = []
    for li, y in enumerate(lanes):
        count = 5 if li in hot else 3
        base = rnd.uniform(9, 16)
        for _ in range(count):
            w = rnd.uniform(10, 34)
            dur = base * rnd.uniform(0.85, 1.2)
            delay = -rnd.uniform(0, dur)
            if li in hot:
                op = rnd.uniform(0.6, 1.0)
                fill = t["accent"]
            else:
                op = rnd.uniform(0.18, 0.35)
                fill = t["dim"]
            msgs.append(
                f'<rect class="m" x="0" y="{y - 2.5:.1f}" width="{w:.1f}" height="5" rx="2.5" '
                f'fill="{fill}" opacity="{op:.2f}" style="animation-duration:{dur:.2f}s;animation-delay:{delay:.2f}s"/>'
            )

    lane_lines = "\n    ".join(
        f'<line x1="0" y1="{y:.1f}" x2="{W}" y2="{y:.1f}" stroke="{t["lane"]}" stroke-width="1"/>' for y in lanes
    )
    labels = "".join(
        f'<text x="{W - 28}" y="{lanes[i] - 8:.1f}" text-anchor="end" class="lbl">{name}</text>'
        for i, name in zip(sorted(hot), ["p0 · orders", "p1 · executions", "p2 · clearing"])
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">Archit Singh</title>
  <desc id="d">Software Engineer at Goldman Sachs building high-throughput Java services and Kafka pipelines. Animated banner of messages flowing through partitions.</desc>
  <style>
    .m {{ animation-name: flow; animation-timing-function: linear; animation-iteration-count: infinite; }}
    @keyframes flow {{ from {{ transform: translateX(-60px); }} to {{ transform: translateX({W + 20}px); }} }}
    @media (prefers-reduced-motion: reduce) {{ .m {{ animation: none; }} }}
    .name {{ font: 700 64px {SANS}; letter-spacing: -2px; fill: {t["text"]}; }}
    .sub {{ font: 400 23px {SANS}; fill: {t["muted"]}; }}
    .sub b {{ font-weight: 600; fill: {t["text"]}; }}
    .eyebrow {{ font: 500 17px {MONO}; fill: {t["muted"]}; letter-spacing: 0.5px; }}
    .lbl {{ font: 400 13px {MONO}; fill: {t["muted"]}; opacity: 0.8; }}
    .pulse {{ animation: pulse 2s ease-out infinite; transform-origin: 63px 83px; }}
    @keyframes pulse {{ 0% {{ opacity: .9; transform: scale(1); }} 100% {{ opacity: 0; transform: scale(2.6); }} }}
    @media (prefers-reduced-motion: reduce) {{ .pulse {{ animation: none; opacity: 0; }} }}
  </style>
  <defs>
    <clipPath id="frame"><rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16"/></clipPath>
    <linearGradient id="fade" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="{t["bg"]}" stop-opacity="1"/>
      <stop offset="0.42" stop-color="{t["bg"]}" stop-opacity="0.92"/>
      <stop offset="0.7" stop-color="{t["bg"]}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="{t["bg"]}"/>
    {lane_lines}
    {"".join(msgs)}
    {labels}
    <rect width="{W}" height="{H}" fill="url(#fade)"/>
    <circle class="pulse" cx="63" cy="83" r="5" fill="{t["accent"]}"/>
    <circle cx="63" cy="83" r="5" fill="{t["accent"]}"/>
    <text x="80" y="89" class="eyebrow">Software Engineer · Goldman Sachs · Bengaluru</text>
    <text x="54" y="160" class="name">Archit Singh</text>
    <text x="56" y="205" class="sub">I build high-throughput <tspan font-weight="600" fill="{t["text"]}">Java</tspan> services and <tspan font-weight="600" fill="{t["text"]}">Kafka</tspan> pipelines</text>
    <text x="56" y="237" class="sub">that carry trades through orders, executions and clearing.</text>
  </g>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{t["line"]}"/>
</svg>
'''


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, theme in THEMES.items():
        with open(os.path.join(OUT, f"banner-{name}.svg"), "w") as f:
            f.write(build(theme))
    print("wrote banner-dark.svg, banner-light.svg")
