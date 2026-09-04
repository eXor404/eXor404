// Renders one SVG "card" per showcased project, in light and dark variants.
// Data is pulled live from the GitHub and npm registry APIs at build time.

import { mkdir, writeFile } from "node:fs/promises";

const OWNER = "eXor404";

const PROJECTS = [
  {
    repo: "mdstack",
    npm: "@exor404/mdstack",
    site: "mdstack.dev",
    blurb:
      "Zero-config static-site CLI for markdown. Dev server, builds, four themes, deploy anywhere static.",
  },
  {
    repo: "mdslides",
    npm: "@exor404/mdslides",
    site: "mdslides.mdstack.dev",
    blurb:
      "One markdown file becomes the whole deck. Present with live reload, build to static HTML, or export a PDF.",
  },
  {
    repo: "git-art",
    npm: null,
    site: "git-art.net",
    blurb:
      "Draw pixel art into a GitHub contribution graph. Sketch a pattern, get the commits that paint it.",
  },
];

const THEMES = {
  dark: {
    bg: "#0d0d12",
    border: "#ffb000",
    borderOpacity: 0.22,
    title: "#e8e8e8",
    body: "#8b8f98",
    accent: "#ffb000",
    meta: "#6e727a",
  },
  light: {
    bg: "#faf8f3",
    border: "#b37800",
    borderOpacity: 0.28,
    title: "#111111",
    body: "#57606a",
    accent: "#b37800",
    meta: "#6e7781",
  },
};

const W = 820;
const H = 130;
const PAD = 30;
const MONO = "ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, monospace";

const esc = (s) =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

// Monospace advance width is a stable ~0.6em, so wrapping can be computed exactly.
function wrap(text, fontSize, maxWidth, maxLines) {
  const perChar = fontSize * 0.6;
  const limit = Math.floor(maxWidth / perChar);
  const words = text.split(/\s+/);
  const lines = [];
  let line = "";
  for (const w of words) {
    const next = line ? `${line} ${w}` : w;
    if (next.length > limit && line) {
      lines.push(line);
      line = w;
      if (lines.length === maxLines) break;
    } else {
      line = next;
    }
  }
  if (lines.length < maxLines && line) lines.push(line);
  if (lines.length === maxLines && line && !lines.includes(line)) {
    const last = lines[maxLines - 1];
    if (last.length > limit - 1) lines[maxLines - 1] = last.slice(0, limit - 1) + "…";
  }
  return lines.slice(0, maxLines);
}

async function json(url, headers = {}) {
  const res = await fetch(url, {
    headers: { "user-agent": `${OWNER}-profile-cards`, ...headers },
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} for ${url}`);
  return res.json();
}

async function collect(project) {
  const gh = await json(`https://api.github.com/repos/${OWNER}/${project.repo}`, {
    accept: "application/vnd.github+json",
    ...(process.env.GITHUB_TOKEN
      ? { authorization: `Bearer ${process.env.GITHUB_TOKEN}` }
      : {}),
  });

  let version = null;
  if (project.npm) {
    try {
      const meta = await json(`https://registry.npmjs.org/${project.npm}/latest`);
      version = meta.version;
    } catch {
      version = null; // npm is decoration, never a build blocker
    }
  }

  return {
    ...project,
    stars: gh.stargazers_count ?? 0,
    language: gh.language ?? null,
    version,
  };
}

function card(p, index, themeName) {
  const t = THEMES[themeName];
  const num = String(index + 1).padStart(2, "0");
  const nameX = PAD + 42;

  const lines = wrap(p.blurb, 13, W - nameX - PAD, 2);
  const body = lines
    .map(
      (line, i) =>
        `<text x="${nameX}" y="${71 + i * 19}" font-family="${MONO}" font-size="13" fill="${t.body}">${esc(line)}</text>`,
    )
    .join("\n    ");

  const meta = [
    p.language,
    `${p.stars} ★`,
    p.version ? `v${p.version}` : null,
    p.site,
  ].filter(Boolean);

  let x = nameX;
  const metaParts = [];
  meta.forEach((part, i) => {
    if (i > 0) {
      metaParts.push(
        `<text x="${x}" y="${112}" font-family="${MONO}" font-size="11.5" fill="${t.meta}" opacity="0.55">/</text>`,
      );
      x += 6.9 + 8;
    }
    const isSite = i === meta.length - 1;
    metaParts.push(
      `<text x="${x}" y="${112}" font-family="${MONO}" font-size="11.5" fill="${isSite ? t.accent : t.meta}">${esc(part)}</text>`,
    );
    x += part.length * 11.5 * 0.6 + 8;
  });

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(p.repo)} — ${esc(p.blurb)}">
  <g>
    <rect x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="10" fill="${t.bg}" stroke="${t.border}" stroke-opacity="${t.borderOpacity}"/>
    <rect x="0.5" y="0.5" width="3" height="${H - 1}" rx="1.5" fill="${t.accent}"/>
    <text x="${PAD}" y="47" font-family="${MONO}" font-size="13" fill="${t.accent}" opacity="0.75">${num}</text>
    <text x="${nameX}" y="47" font-family="${MONO}" font-size="20" font-weight="700" fill="${t.title}">${esc(p.repo)}</text>
    ${body}
    ${metaParts.join("\n    ")}
  </g>
</svg>
`;
}

const out = process.argv[2] ?? "dist";
await mkdir(out, { recursive: true });

const data = [];
for (const p of PROJECTS) data.push(await collect(p));

for (const theme of Object.keys(THEMES)) {
  for (const [i, p] of data.entries()) {
    await writeFile(`${out}/card-${p.repo}-${theme}.svg`, card(p, i, theme), "utf8");
  }
}

console.log(
  data
    .map((p) => `${p.repo}: ${p.stars} stars, ${p.language}, ${p.version ?? "no npm"}`)
    .join("\n"),
);
