#!/usr/bin/env python3
"""Generate an SVG flower garden from a GitHub user's contribution calendar."""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime

USERNAME = os.environ.get("GITHUB_USERNAME", "Smyle-Goyal")
TOKEN = os.environ.get("PROFILE_TOKEN") or os.environ.get("GH_TOKEN")
OUT = os.path.join("assets", "flower-contributions.svg")

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            color
          }
        }
      }
    }
  }
}
"""

def fetch_calendar():
    if not TOKEN:
        raise SystemExit("Missing PROFILE_TOKEN (GitHub token with read:user permission).")
    payload = json.dumps({
        "query": QUERY,
        "variables": {"login": USERNAME}
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "smyle-flower-contribution-garden"
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"GitHub API error {exc.code}: {detail}")
    if result.get("errors"):
        raise SystemExit("GraphQL error: " + json.dumps(result["errors"]))
    user = result.get("data", {}).get("user")
    if not user:
        raise SystemExit(f"GitHub user '{USERNAME}' was not found or is inaccessible.")
    return user["contributionsCollection"]["contributionCalendar"]

def flower(cx, cy, count, max_count, date):
    # Four bloom stages: seed, sprout, bud, flower. Petal size scales with intensity.
    stage = 0 if count == 0 else 1 if count == 1 else 2 if count <= 3 else 3
    palette = ["#c9d1d9", "#a7d7a8", "#6fcf97", "#f4a7c5", "#c084fc"]
    stem = "#5b9b68"
    if stage == 0:
        return f'<circle cx="{cx}" cy="{cy}" r="2.4" fill="#30363d" stroke="#484f58" stroke-width="0.7"><title>{date}: 0 contributions</title></circle>'
    if stage == 1:
        return (f'<path d="M {cx} {cy+3} q -1 -4 0 -7" stroke="{stem}" stroke-width="1.5" fill="none"/>'
                f'<ellipse cx="{cx-2}" cy="{cy-1}" rx="2.2" ry="1.2" transform="rotate(30 {cx-2} {cy-1})" fill="{palette[1]}">'
                f'<title>{date}: {count} contribution(s)</title></ellipse>')
    if stage == 2:
        r = 3.1
        return (f'<path d="M {cx} {cy+4} L {cx} {cy-1}" stroke="{stem}" stroke-width="1.5"/>'
                f'<circle cx="{cx}" cy="{cy-2}" r="{r}" fill="{palette[2]}">'
                f'<title>{date}: {count} contributions</title></circle>'
                f'<circle cx="{cx}" cy="{cy-2}" r="1.3" fill="#f9e2af"/>')
    petal = 2.1 + min(count, 10) * 0.13
    center = "#f9d976"
    color = palette[3] if count < 6 else palette[4]
    petals = []
    for angle in range(0, 360, 45):
        petals.append(f'<ellipse cx="{cx}" cy="{cy-3.1}" rx="{petal:.2f}" ry="{petal*0.68:.2f}" fill="{color}" transform="rotate({angle} {cx} {cy})"/>')
    return (f'<path d="M {cx} {cy+6} Q {cx-1} {cy+1} {cx} {cy-1}" stroke="{stem}" stroke-width="1.6" fill="none"/>'
            + "".join(petals)
            + f'<circle cx="{cx}" cy="{cy}" r="2.1" fill="{center}"/>'
            + f'<title>{date}: {count} contributions</title>')

def main():
    calendar = fetch_calendar()
    weeks = calendar["weeks"]
    days = []
    for week in weeks:
        days.extend(week["contributionDays"])
    # GitHub calendar has 7 rows; each week is a column.
    cell_w, cell_h, gap = 18, 18, 5
    left, top = 42, 32
    width = left + len(weeks) * (cell_w + gap) + 16
    height = top + 7 * (cell_h + gap) + 56
    max_count = max((d["contributionCount"] for d in days), default=1)
    months = {}
    for wi, week in enumerate(weeks):
        first = week["contributionDays"][0]["date"]
        dt = datetime.strptime(first, "%Y-%m-%d")
        if dt.day <= 7:
            months[wi] = dt.strftime("%b")
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Smyle Goyal contribution flower garden</title>',
        '<desc id="desc">Each day is a flower whose bloom reflects the number of GitHub contributions.</desc>',
        '<rect width="100%" height="100%" rx="16" fill="#0d1117"/>',
        '<text x="20" y="22" fill="#e6edf3" font-family="Verdana, sans-serif" font-size="14" font-weight="bold">🌸 Smyle’s contribution garden</text>',
    ]
    for wi, label in months.items():
        x = left + wi * (cell_w + gap)
        pieces.append(f'<text x="{x}" y="{top-8}" fill="#8b949e" font-family="Verdana, sans-serif" font-size="10">{label}</text>')
    day_labels = [(0, "Mon"), (2, "Wed"), (4, "Fri")]
    for row, label in day_labels:
        y = top + row * (cell_h + gap) + 10
        pieces.append(f'<text x="4" y="{y}" fill="#8b949e" font-family="Verdana, sans-serif" font-size="9">{label}</text>')
    for wi, week in enumerate(weeks):
        for day in week["contributionDays"]:
            date = datetime.strptime(day["date"], "%Y-%m-%d")
            # GitHub's week columns begin Sunday; convert to Monday-first rows.
            row = (date.weekday())
            x = left + wi * (cell_w + gap) + cell_w / 2
            y = top + row * (cell_h + gap) + cell_h / 2 + 1
            pieces.append(flower(x, y, day["contributionCount"], max_count, day["date"]))
    total = calendar["totalContributions"]
    legend_y = height - 20
    pieces.append(f'<text x="20" y="{legend_y}" fill="#8b949e" font-family="Verdana, sans-serif" font-size="10">{total} contributions in the last year</text>')
    pieces.append('</svg>')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(pieces))
    print(f"Updated {OUT}: {total} contributions across {len(days)} days.")

if __name__ == "__main__":
    main()
