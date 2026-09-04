"""Regenerates the animated terminal greeting in assets/.

    python3 .github/scripts/greeting.py

`textLength` pins each line to an exact width, so the typing clip and the
cursor stay in sync no matter which monospace font the viewer has.
"""

import io


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


MONO = "ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, monospace"
FS = 17.0
CW = FS * 0.6                     # enforced advance width per character
LH = 26.0
PAD_X, PAD_Y = 22.0, 24.0
TYPED = "Hello there."
STEP = 0.085                      # seconds per character

LINES = [
    ("prompt", "$ whoami"),
    ("typed",  TYPED),
    ("muted",  "Maurice Däppen  ·  Fullstack, DevOps & Security  ·  Bern, CH"),
]

THEMES = {
    "dark":  dict(bg="#150d24", prompt="#d8a0e8", text="#f2e6f8",
                  muted="#a892c0", cursor="#f8a0d0", border="#d8a0e8", bo=0.26),
    "light": dict(bg="#fdf3fd", prompt="#9a4fc4", text="#301068",
                  muted="#5f4a7a", cursor="#d1478f", border="#9a4fc4", bo=0.30),
}

n = len(TYPED)
type_dur = n * STEP
W = 640.0
H = PAD_Y * 2 + LH * len(LINES)

# Discrete keyframes: one per character, so the reveal reads as keystrokes.
times  = ";".join(f"{i/n:.4f}" for i in range(n + 1))
widths = ";".join(f"{i*CW:.2f}" for i in range(n + 1))
curxs  = ";".join(f"{PAD_X + i*CW:.2f}" for i in range(n + 1))

for name, t in THEMES.items():
    y = {k: PAD_Y + 18 + i * LH for i, (k, _) in enumerate(LINES)}
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="Hello there. Maurice Daeppen, Fullstack, DevOps and Security, Bern, Switzerland">
  <title>General Kenobi!</title>
  <defs>
    <clipPath id="type">
      <rect x="{PAD_X}" y="{y['typed']-FS:.1f}" height="{FS+8:.1f}" width="0">
        <animate attributeName="width" dur="{type_dur:.2f}s" fill="freeze"
                 calcMode="discrete" keyTimes="{times}" values="{widths}"/>
      </rect>
    </clipPath>
  </defs>

  <rect x="0.5" y="0.5" width="{W-1:.0f}" height="{H-1:.0f}" rx="10"
        fill="{t['bg']}" stroke="{t['border']}" stroke-opacity="{t['bo']}"/>

  <text x="{PAD_X}" y="{y['prompt']:.1f}" font-family="{MONO}" font-size="{FS-3:.0f}"
        fill="{t['prompt']}" textLength="{8*(FS-3)*0.6:.1f}" lengthAdjust="spacingAndGlyphs">{esc(LINES[0][1])}</text>

  <g clip-path="url(#type)">
    <text x="{PAD_X}" y="{y['typed']:.1f}" font-family="{MONO}" font-size="{FS:.0f}"
          font-weight="700" fill="{t['text']}"
          textLength="{n*CW:.1f}" lengthAdjust="spacingAndGlyphs">{esc(TYPED)}</text>
  </g>

  <rect y="{y['typed']-FS+2:.1f}" width="{CW:.1f}" height="{FS:.0f}" fill="{t['cursor']}" x="{PAD_X}">
    <animate attributeName="x" dur="{type_dur:.2f}s" fill="freeze"
             calcMode="discrete" keyTimes="{times}" values="{curxs}"/>
    <animate attributeName="opacity" values="1;1;0;0;1" dur="1.1s"
             begin="{type_dur:.2f}s" repeatCount="indefinite"/>
  </rect>

  <text x="{PAD_X}" y="{y['muted']:.1f}" font-family="{MONO}" font-size="12"
        fill="{t['muted']}" opacity="0">{esc(LINES[2][1])}
    <animate attributeName="opacity" from="0" to="1" dur="0.5s"
             begin="{type_dur+0.15:.2f}s" fill="freeze"/>
  </text>
</svg>
'''
    io.open(f"assets/greeting-{name}.svg", "w", encoding="utf-8").write(svg)
    print(f"assets/greeting-{name}.svg  {W:.0f}x{H:.0f}  typing {type_dur:.2f}s")
