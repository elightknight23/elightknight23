import json
import urllib.request

USERNAME = "elightknight23"
OUT_PATH = "dist/leetcode-stats.svg"
FONTFACE_PATH = "assets/fontface.txt"

QUERY = """
query userProblemsSolved($username: String!) {
  matchedUser(username: $username) {
    submitStatsGlobal { acSubmissionNum { difficulty count } }
  }
  allQuestionsCount { difficulty count }
}
"""

FONT_STACK = "'Fira Code','SF Mono',Consolas,monospace"
COLORS = {"Easy": "#2ea043", "Medium": "#e3b341", "Hard": "#f85149"}


def fetch_stats():
    req = urllib.request.Request(
        "https://leetcode.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"username": USERNAME}}).encode(),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            "Referer": "https://leetcode.com",
            "Origin": "https://leetcode.com",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.load(resp)["data"]

    solved = {d["difficulty"]: d["count"] for d in data["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]}
    total = {d["difficulty"]: d["count"] for d in data["allQuestionsCount"]}
    return solved, total


def arc_dasharray(fraction, radius):
    circumference = 2 * 3.14159265 * radius
    return f"{fraction * circumference:.2f} {circumference:.2f}"


def bar(y, label, count, total, color):
    width = 380
    frac = count / total if total else 0
    return f"""
    <text x="0" y="{y}" font-size="13" fill="#8b949e">{label}</text>
    <text x="{width}" y="{y}" font-size="13" fill="#c9d1d9" text-anchor="end">{count} / {total}</text>
    <rect x="0" y="{y + 10}" width="{width}" height="6" rx="3" fill="#30363d"/>
    <rect x="0" y="{y + 10}" width="{width * frac:.1f}" height="6" rx="3" fill="{color}"/>
    """


def build_svg(solved, total):
    radius = 50
    stroke = 10
    all_solved = solved.get("All", 0)
    all_total = total.get("All", 1)
    frac = all_solved / all_total if all_total else 0

    ring = f"""
    <g transform="translate(65,65)">
      <circle r="{radius}" fill="none" stroke="#30363d" stroke-width="{stroke}"/>
      <circle r="{radius}" fill="none" stroke="#39d353" stroke-width="{stroke}"
        stroke-linecap="round" stroke-dasharray="{arc_dasharray(frac, radius)}"
        transform="rotate(-90)"/>
      <text x="0" y="7" font-size="26" font-weight="600" fill="#c9d1d9" text-anchor="middle">{all_solved}</text>
    </g>
    """

    bars = f"""
    <g transform="translate(160,25)">
      {bar(0, "Easy", solved.get("Easy", 0), total.get("Easy", 0), COLORS["Easy"])}
      {bar(38, "Medium", solved.get("Medium", 0), total.get("Medium", 0), COLORS["Medium"])}
      {bar(76, "Hard", solved.get("Hard", 0), total.get("Hard", 0), COLORS["Hard"])}
    </g>
    """

    with open(FONTFACE_PATH) as f:
        fontface = f.read()

    return f"""<svg viewBox="0 0 560 130" xmlns="http://www.w3.org/2000/svg" font-family="{FONT_STACK}">
  {fontface}
  {ring}
  {bars}
</svg>
"""


def main():
    import os
    solved, total = fetch_stats()
    svg = build_svg(solved, total)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(svg)


if __name__ == "__main__":
    main()
