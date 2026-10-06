#!/usr/bin/env python3
"""Generate the bespoke SVG assets for the Absterrg0 profile README.

Everything the profile shows is drawn here: the header banner, the system
cards, and the activity panel. Colors come from the abstergo.fyi palette.
The activity panel is regenerated from the GitHub GraphQL API, so the
profile stays current without any third-party widgets.

Usage:
    GITHUB_TOKEN=... python3 scripts/build_assets.py            # everything
    GITHUB_TOKEN=... python3 scripts/build_assets.py --static   # banner + capability
    GITHUB_TOKEN=... python3 scripts/build_assets.py --numbers  # only the record
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import date

LOGIN = "Absterrg0"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

# ---------------------------------------------------------------- palette
PAGE = "#0c100d"
PANEL = "#0e130f"
PANEL_DEEP = "#0b0f0c"
GRID = "#131a13"
BORDER = "#1d261d"
CREAM = "#eee7dc"
BODY = "#c9c0b5"
MUTED = "#8b948a"
FAINT = "#6d7568"
FAINTEST = "#526052"
CLAY = "#bd5d42"
EMBER = "#e36f45"
LIME = "#b6ff4a"

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
SERIF = "Georgia, 'Iowan Old Style', 'Times New Roman', serif"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

STYLE = f"""
  .mono {{ font-family: {MONO}; }}
  .serif {{ font-family: {SERIF}; }}
  .sans {{ font-family: {SANS}; }}
"""


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- data
CAPABILITY = [
    ("LANGUAGES", ["TypeScript", "JavaScript", "Python", "Go", "Rust", "Solidity"]),
    ("INTERFACE", ["React", "Next.js", "Tailwind", "Motion", "TanStack Query", "Zustand"]),
    ("SYSTEMS", ["Node.js", "NestJS", "PostgreSQL", "Redis", "Prisma", "REST"]),
    ("PROTOCOL", ["Solana", "Anchor", "Web3.js", "Smart contracts"]),
    ("DELIVERY", ["Docker", "AWS", "Linux", "GitHub Actions", "Vercel"]),
]


# ---------------------------------------------------------------- helpers
def svg_doc(width: int, height: int, body: str) -> str:
    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img">\n'
        f"<style>{STYLE}</style>\n{body}\n</svg>\n"
    )


def panel_defs(name: str = "g") -> str:
    return (
        "<defs>"
        f'<pattern id="{name}" width="24" height="24" patternUnits="userSpaceOnUse">'
        f'<path d="M24 0H0v24" stroke="{GRID}" stroke-width="1" fill="none"/></pattern>'
        "</defs>"
    )


def panel_base(width: int, height: int, name: str = "g") -> str:
    """Rounded panel with faint grid, used by every card."""
    r = 16
    return (
        panel_defs(name)
        + f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{r}" fill="{PANEL}"/>'
        + f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{r}" fill="url(#{name})" opacity="0.55"/>'
        + f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{r}" fill="none" stroke="{BORDER}"/>'
    )


def write(name: str, content: str) -> None:
    path = os.path.join(ASSETS, name)
    os.makedirs(ASSETS, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    print(f"wrote {os.path.relpath(path, ROOT)}")


# ---------------------------------------------------------------- header
def render_header() -> None:
    w, h = 1200, 300
    body = (
        f'<defs>'
        f'<pattern id="g" width="48" height="48" patternUnits="userSpaceOnUse">'
        f'<path d="M48 0H0v48" stroke="{GRID}" stroke-width="1" fill="none"/></pattern>'
        f'<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{CLAY}" stop-opacity="0.14"/>'
        f'<stop offset="1" stop-color="{CLAY}" stop-opacity="0"/>'
        f"</radialGradient></defs>"
        f'<rect width="{w}" height="{h}" fill="{PAGE}"/>'
        f'<rect width="{w}" height="{h}" fill="url(#g)" opacity="0.6"/>'
        f'<ellipse cx="1020" cy="80" rx="340" ry="200" fill="url(#glow)"/>'
        # node graph
        f'<g stroke="#1e271e" stroke-width="1.5" fill="none">'
        f'<path d="M940 70 1060 50"/><path d="M940 70 1020 125"/><path d="M1060 50 1110 105"/>'
        f'<path d="M1020 125 1110 105"/><path d="M1020 125 990 195"/><path d="M1110 105 1085 205"/>'
        f'<path d="M990 195 1085 205"/></g>'
        f'<circle cx="940" cy="70" r="3.5" fill="#334033"/>'
        f'<circle cx="1060" cy="50" r="3" fill="{CREAM}" fill-opacity="0.75"/>'
        f'<circle cx="1020" cy="125" r="5" fill="{CLAY}">'
        f'<animate attributeName="opacity" values="1;0.55;1" dur="3.6s" repeatCount="indefinite"/></circle>'
        f'<circle cx="1110" cy="105" r="3.5" fill="#334033"/>'
        f'<circle cx="990" cy="195" r="3.5" fill="#334033"/>'
        f'<circle cx="1085" cy="205" r="3" fill="{LIME}">'
        f'<animate attributeName="opacity" values="1;0.5;1" dur="3.6s" begin="1.2s" repeatCount="indefinite"/></circle>'
        # identity
        f'<rect x="64" y="70" width="10" height="10" fill="{CLAY}"/>'
        f'<text x="86" y="79" class="mono" font-size="12.5" letter-spacing="3.5" fill="{MUTED}">ABSTERGO / PRODUCT SYSTEMS</text>'
        f'<text x="60" y="174" class="serif" font-size="80" letter-spacing="-1.5" fill="{CREAM}">Parv Jain</text>'
        f'<text x="64" y="214" class="mono" font-size="15" letter-spacing="2.5" fill="{BODY}">FULL-STACK DEVELOPER — SYSTEMS + INTERFACE</text>'
        f'<text x="64" y="242" class="mono" font-size="12" letter-spacing="1.5" fill="{FAINT}">Bengaluru · 12.97°N / 77.59°E · TypeScript / Solana / real-time / dev tools</text>'
        f'<rect x="64" y="266" width="72" height="2" fill="{CLAY}"/>'
        f'<circle cx="152" cy="267" r="3" fill="{LIME}"/>'
        f'<text x="163" y="271" class="mono" font-size="10.5" letter-spacing="2" fill="{MUTED}">OPEN TO WORK</text>'
        f'<text x="1136" y="272" class="mono" font-size="11" letter-spacing="2.5" fill="{FAINTEST}" text-anchor="end">SYS.PJ / MMXXVI</text>'
    )
    write("header.svg", svg_doc(w, h, body))


# ---------------------------------------------------------------- cards
def render_capability() -> None:
    w = 1200
    row_h = 44
    top = 96
    h = top + row_h * (len(CAPABILITY) - 1) + 48
    body = panel_base(w, h)
    body += (
        f'<text x="44" y="46" class="mono" font-size="11.5" letter-spacing="3" fill="{MUTED}">'
        f"CAPABILITY · WHAT I BUILD WITH</text>"
    )
    for i, (label, items) in enumerate(CAPABILITY):
        cy = top + i * row_h
        body += f'<circle cx="48" cy="{cy}" r="3" fill="{CLAY}"/>'
        body += (
            f'<text x="62" y="{cy + 4}" class="mono" font-size="11" letter-spacing="2.5" fill="{MUTED}">'
            f"{label}</text>"
        )
        x = 220
        for item in items:
            chip_w = int(len(item) * 7.6) + 28
            body += (
                f'<rect x="{x}" y="{cy - 15}" width="{chip_w}" height="30" rx="15" fill="#141b14" stroke="#242e24"/>'
                f'<text x="{x + 14}" y="{cy + 4.5}" class="mono" font-size="12.5" fill="#d5cfc4">{esc(item)}</text>'
            )
            x += chip_w + 10
    write("capability.svg", svg_doc(w, h, body))


# ---------------------------------------------------------------- numbers
QUERY = """
query ($login: String!, $after: String) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
      totalCommitContributions
      totalPullRequestContributions
    }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, after: $after) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        primary: languages(first: 1, orderBy: {field: SIZE, direction: DESC}) {
          edges { node { name } }
        }
      }
    }
  }
}
"""


def gql(query: str, variables: dict) -> dict:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is required to fetch activity data")
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "absterrg0-profile-assets",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]


def collect() -> dict:
    days: list[dict] = []
    weeks: list[dict] = []
    langs: dict[str, int] = {}
    cursor = None
    totals: dict = {}
    while True:
        data = gql(QUERY, {"login": LOGIN, "after": cursor})["user"]
        collection = data["contributionsCollection"]
        if not days:
            totals = {
                "commits": collection["totalCommitContributions"],
                "prs": collection["totalPullRequestContributions"],
                "contributions": collection["contributionCalendar"]["totalContributions"],
            }
            weeks = collection["contributionCalendar"]["weeks"]
            for week in weeks:
                days.extend(week["contributionDays"])
        repos = data["repositories"]
        totals["repos"] = repos["totalCount"]
        for node in repos["nodes"]:
            edges = node["primary"]["edges"]
            if edges:
                name = edges[0]["node"]["name"]
                langs[name] = langs.get(name, 0) + 1
        if not repos["pageInfo"]["hasNextPage"]:
            break
        cursor = repos["pageInfo"]["endCursor"]
    return {"days": days, "weeks": weeks, "langs": langs, "totals": totals}


def streaks(days: list[dict]) -> tuple[int, int]:
    """Return (active_days, longest_streak)."""
    active = [d for d in days if d["date"] <= date.today().isoformat()]
    active_days = sum(1 for d in active if d["contributionCount"] > 0)
    longest = run = 0
    for day in active:
        run = run + 1 if day["contributionCount"] > 0 else 0
        longest = max(longest, run)
    return active_days, longest


def fmt(value: int) -> str:
    return f"{value:,}"


def render_numbers(data: dict) -> None:
    w, h = 1200, 500
    days = data["days"]
    totals = data["totals"]
    active_days, longest = streaks(days)

    top_langs = sorted(data["langs"].items(), key=lambda kv: kv[1], reverse=True)[:6]
    lang_max = top_langs[0][1] if top_langs else 1

    # stats block (2 x 2)
    stats = [
        (44, 132, fmt(totals["commits"]), "COMMITS", "last 12 months"),
        (330, 132, fmt(totals["prs"]), "PULL REQUESTS", "opened"),
        (44, 240, fmt(totals["contributions"]), "CONTRIBUTIONS", "public activity"),
        (330, 240, fmt(totals["repos"]), "PUBLIC REPOS", "owned, non-fork"),
    ]
    stat_svg = "".join(
        f'<text x="{x}" y="{y}" class="serif" font-size="44" fill="{CREAM}">{value}</text>'
        f'<text x="{x}" y="{y + 26}" class="mono" font-size="11" letter-spacing="2.5" fill="{MUTED}">{label}</text>'
        f'<text x="{x}" y="{y + 44}" class="mono" font-size="10" letter-spacing="1" fill="{FAINTEST}">{sub}</text>'
        for x, y, value, label, sub in stats
    )

    # language rows — one bar per repository with that primary language
    bars = []
    for i, (name, count) in enumerate(top_langs):
        y = 138 + i * 30
        width = max(6, round(310 * count / lang_max))
        bars.append(
            f'<text x="620" y="{y}" class="mono" font-size="11.5" fill="{BODY}">{esc(name)}</text>'
            f'<rect x="780" y="{y - 7}" width="310" height="6" rx="3" fill="#161d16"/>'
            f'<rect x="780" y="{y - 7}" width="{width}" height="6" rx="3" fill="{CLAY}"/>'
            f'<text x="1104" y="{y}" class="mono" font-size="10.5" fill="{FAINT}">{count}</text>'
        )
    bar_svg = "".join(bars)

    # heatmap (weeks x days)
    counts = [d["contributionCount"] for d in days]
    peak = max(counts) if counts else 1
    today = date.today().isoformat()
    cell, gap = 9, 3
    cell_svg = []
    grid_w = 53 * (cell + gap) - gap
    x0 = (1200 - grid_w) // 2
    y0 = 378
    for col, week in enumerate(data["weeks"]):
        for row, day in enumerate(week["contributionDays"]):
            count = day["contributionCount"]
            if day["date"] > today:
                fill = "#111711"
            elif count == 0:
                fill = "#182018"
            elif count <= peak * 0.08:
                fill = "#2c382c"
            elif count <= peak * 0.25:
                fill = "#57684f"
            elif count <= peak * 0.55:
                fill = "#9aa88f"
            else:
                fill = EMBER
            cell_svg.append(
                f'<rect x="{x0 + col * (cell + gap)}" y="{y0 + row * (cell + gap)}" '
                f'width="{cell}" height="{cell}" rx="2" fill="{fill}"/>'
            )

    body = (
        panel_base(w, h)
        + f'<text x="44" y="46" class="mono" font-size="11.5" letter-spacing="3" fill="{MUTED}">THE RECORD · ROLLING 12 MONTHS</text>'
        + f'<text x="1156" y="46" class="mono" font-size="10.5" letter-spacing="1.5" fill="{FAINTEST}" text-anchor="end">DRAWN FROM THE GITHUB API</text>'
        + stat_svg
        + f'<text x="620" y="106" class="mono" font-size="11" letter-spacing="2.5" fill="{MUTED}">LANGUAGES · BY REPOSITORY</text>'
        + bar_svg
        + f'<line x1="44" y1="330" x2="1156" y2="330" stroke="#182018" stroke-width="1"/>'
        + f'<text x="44" y="354" class="mono" font-size="11" letter-spacing="2.5" fill="{MUTED}">CONSISTENCY · 52 WEEKS</text>'
        + "".join(cell_svg)
        + f'<text x="1156" y="392" class="mono" font-size="10" letter-spacing="2" fill="{FAINT}" text-anchor="end">LONGEST STREAK</text>'
        + f'<text x="1156" y="418" class="serif" font-size="22" fill="{CREAM}" text-anchor="end">{longest} days</text>'
        + f'<text x="1156" y="446" class="mono" font-size="10" letter-spacing="2" fill="{FAINT}" text-anchor="end">ACTIVE DAYS</text>'
        + f'<text x="1156" y="472" class="serif" font-size="22" fill="{CREAM}" text-anchor="end">{active_days} of 365</text>'
    )
    write("numbers.svg", svg_doc(w, h, body))


# ---------------------------------------------------------------- main
def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--all"
    if mode in ("--all", "--static"):
        render_header()
        render_capability()
    if mode in ("--all", "--numbers"):
        data = collect()
        render_numbers(data)


if __name__ == "__main__":
    main()
