"""Regenerates the coloured eXor404 wordmark in assets/.

Run manually after a palette change; not part of CI.
    pip install pyfiglet && python3 .github/scripts/wordmark.py

The ANSI-Shadow ASCII art is converted to plain rectangles so the wordmark
renders identically everywhere, independent of the viewer's monospace font.
"""

import io
import pyfiglet

CW, CH, OVER, PAD = 9.0, 16.0, 0.6, 14.0
T = CH * 0.26
THEMES = {"dark": ("#d8a0e8", "#f8a0d0"), "light": ("#9a4fc4", "#d1478f")}

art = pyfiglet.figlet_format("eXor404", font="ansi_shadow").rstrip("\n")
rows = [r for r in art.split("\n") if r.strip()]
cols = max(len(r) for r in rows)
rows = [r.ljust(cols) for r in rows]
W, H = cols * CW + PAD * 2, len(rows) * CH + PAD * 2


def shadow_rects(ch, x, y):
    cx, cy = x + (CW - T) / 2, y + (CH - T) / 2
    parts = {
        "═": [(x, cy, CW, T)],
        "║": [(cx, y, T, CH)],
        "╔": [(cx, cy, (CW + T) / 2, T), (cx, cy, T, (CH + T) / 2)],
        "╗": [(x, cy, (CW + T) / 2, T), (cx, cy, T, (CH + T) / 2)],
        "╚": [(cx, cy, (CW + T) / 2, T), (cx, y, T, (CH + T) / 2)],
        "╝": [(x, cy, (CW + T) / 2, T), (cx, y, T, (CH + T) / 2)],
    }
    return parts.get(ch, [])


for name, (c1, c2) in THEMES.items():
    body, shade = [], []
    for yi, row in enumerate(rows):
        y = PAD + yi * CH
        xi = 0
        while xi < cols:
            if row[xi] == "█":
                run = 0
                while xi + run < cols and row[xi + run] == "█":
                    run += 1
                body.append(
                    f'<rect x="{PAD+xi*CW:.1f}" y="{y:.1f}" '
                    f'width="{run*CW+OVER:.1f}" height="{CH+OVER:.1f}"/>'
                )
                xi += run
            else:
                for rx, ry, rw, rh in shadow_rects(row[xi], PAD + xi * CW, y):
                    shade.append(
                        f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{rw:.1f}" height="{rh:.1f}"/>'
                    )
                xi += 1

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="eXor404">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="0.4">
      <stop offset="0" stop-color="{c1}"/>
      <stop offset="1" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <g fill="url(#g)" opacity="0.42">
    {chr(10).join("    " + r for r in shade).strip()}
  </g>
  <g fill="url(#g)" shape-rendering="crispEdges">
    {chr(10).join("    " + r for r in body).strip()}
  </g>
</svg>
'''
    io.open(f"assets/wordmark-{name}.svg", "w", encoding="utf-8").write(svg)
    print(f"assets/wordmark-{name}.svg")
