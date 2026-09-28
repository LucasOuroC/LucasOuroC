"""Generate profile cards from the public GitHub API."""

import json
import os
from collections import Counter
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen


USERNAME = "LucasOuroC"
OUTPUT = Path(__file__).resolve().parents[1] / "assets"


def github(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-cards"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(f"https://api.github.com{path}", headers=headers), timeout=30) as response:
        return json.load(response)


def card(title, body):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="340" height="200" '
        'viewBox="0 0 340 200" role="img">'
        '<rect x="1" y="1" width="338" height="198" rx="6" '
        'fill="#0d1117" stroke="#30363d" stroke-width="2"/>'
        f'<text x="22" y="35" fill="#e6edf3" font-size="17" font-weight="600" '
        f'font-family="Segoe UI, Arial, sans-serif">{escape(title)}</text>'
        f'{body}</svg>\n'
    )


def text(x, y, value, color="#8b949e", size=13, weight="400"):
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
        f'font-weight="{weight}" font-family="Segoe UI, Arial, sans-serif">'
        f'{escape(str(value))}</text>'
    )


def main():
    user = github(f"/users/{USERNAME}")
    repos = []
    page = 1
    while True:
        batch = github(f"/users/{USERNAME}/repos?type=owner&per_page=100&page={page}")
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    public_repos = [repo for repo in repos if not repo["fork"]]
    stars = sum(repo["stargazers_count"] for repo in public_repos)
    stats = [
        ("Repositórios públicos", user["public_repos"]),
        ("Estrelas recebidas", stars),
        ("Seguidores", user["followers"]),
    ]
    stats_body = "".join(
        text(22, 76 + index * 44, label)
        + text(275, 76 + index * 44, value, "#58a6ff", 20, "700")
        for index, (label, value) in enumerate(stats)
    )

    languages = Counter(repo["language"] for repo in public_repos if repo["language"])
    top = languages.most_common(5)
    language_body = ""
    colors = ["#58a6ff", "#3fb950", "#d2a8ff", "#f2cc60", "#ff7b72"]
    for index, (language, count) in enumerate(top):
        y = 62 + index * 27
        language_body += text(22, y, language, "#e6edf3", 12)
        language_body += f'<rect x="145" y="{y - 10}" width="150" height="10" rx="5" fill="#21262d"/>'
        language_body += (
            f'<rect x="145" y="{y - 10}" width="{round(150 * count / top[0][1])}" '
            f'height="10" rx="5" fill="{colors[index]}"/>'
        )
        language_body += text(303, y, count, "#8b949e", 11)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "stats.svg").write_text(card("Estatísticas no GitHub", stats_body), encoding="utf-8")
    (OUTPUT / "languages.svg").write_text(
        card("Linguagens por repositório", language_body), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
