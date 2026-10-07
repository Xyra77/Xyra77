#!/usr/bin/env python3

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone

from pathlib import Path


USER = os.environ.get("GH_USERNAME", "Xyra77")
OUT = Path("assets/monthly-language.svg")

# Public GitHub API: do NOT use Actions GITHUB_TOKEN for cross-repository reads.
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10",
    "User-Agent": "Xyra77-monthly-language",
}


EXTENSIONS = {
    ".lp": "Loop",
    ".lua": "Lua",

    ".py": "Python",
    ".pyi": "Python",

    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",

    ".ts": "TypeScript",
    ".tsx": "TypeScript",

    ".go": "Go",
    ".rs": "Rust",

    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin",

    ".rb": "Ruby",

    ".php": "PHP",

    ".sh": "Bash",
    ".bash": "Bash",
    ".zsh": "Zsh",
    ".fish": "Fish",

    ".html": "HTML",
    ".htm": "HTML",

    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "SCSS",

    ".c": "C",
    ".h": "C",

    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++",
    ".hxx": "C++",

    ".cs": "C#",
    ".swift": "Swift",

    ".sql": "SQL",

    ".dart": "Dart",

    ".ex": "Elixir",
    ".exs": "Elixir",

    ".erl": "Erlang",

    ".hs": "Haskell",

    ".scala": "Scala",

    ".vue": "Vue",
    ".svelte": "Svelte",

    ".yml": "YAML",
    ".yaml": "YAML",

    ".tf": "HCL",

    ".pl": "Perl",
}


# Nama tampilan. Kalau ada bahasa yang mau diganti namanya, taruh di sini.
ALIASES = {
    "Shell": "Bash",
}


ABBREVIATIONS = {
    "Python": "PY",
    "JavaScript": "JS",
    "TypeScript": "TS",
    "Bash": "BASH",
    "Zsh": "ZSH",
    "Fish": "FISH",
    "Ruby": "RB",
    "PHP": "PHP",
    "Lua": "LUA",
    "Go": "GO",
    "Rust": "RS",
    "Java": "JAVA",
    "C": "C",
    "C++": "C++",
    "C#": "C#",
    "HTML": "HTML",
    "CSS": "CSS",
    "SCSS": "SCSS",
    "SQL": "SQL",
    "YAML": "YML",
}


def api(url):
    req = urllib.request.Request(url, headers=HEADERS)

    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def pages(url):
    page = 1

    while True:
        separator = "&" if "?" in url else "?"

        current = api(
            f"{url}{separator}per_page=100&page={page}"
        )

        if not current:
            break

        yield from current

        if len(current) < 100:
            break

        page += 1


def escape(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def detect_shebang(patch):
    if not patch:
        return None

    text = str(patch)

    patterns = (
        (r"^\+\s*#!.*(?:/| )bash\b", "Bash"),
        (r"^\+\s*#!.*(?:/| )sh\b", "Bash"),
        (r"^\+\s*#!.*(?:/| )zsh\b", "Zsh"),
        (r"^\+\s*#!.*(?:/| )python(?:3)?\b", "Python"),
        (r"^\+\s*#!.*(?:/| )ruby\b", "Ruby"),
        (r"^\+\s*#!.*(?:/| )node\b", "JavaScript"),
    )

    for pattern, language in patterns:
        if re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
            return language

    return None


def detect_language(file_info):
    filename = file_info.get("filename", "")
    suffix = Path(filename).suffix.lower()

    language = EXTENSIONS.get(suffix)

    if not language:
        # Also detect extensionless/oddly named scripts by shebang.
        language = detect_shebang(file_info.get("patch"))

    return ALIASES.get(language, language)


def month_range():
    now = datetime.now(timezone.utc)

    start = now.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    if start.month == 12:
        end = start.replace(
            year=start.year + 1,
            month=1,
        )
    else:
        end = start.replace(
            month=start.month + 1,
        )

    return start, end


def make_svg(language, changed_lines, month_label):
    abbreviation = ABBREVIATIONS.get(
        language,
        language[:6].upper(),
    )

    # Decorative segmented bar (same "flavor" meter as before — not a
    # computed percentage, just a stable visual accent).
    filled_segments = 6
    total_segments = 8
    seg_w, seg_gap = 34, 5
    bar_x, bar_y = 112, 86
    segments = []
    for i in range(total_segments):
        sx = bar_x + i * (seg_w + seg_gap)
        color = "#ff4fd8" if i < filled_segments else "#1c1c2e"
        segments.append(
            f'<rect x="{sx}" y="{bar_y}" width="{seg_w}" height="10" fill="{color}"/>'
        )
    bar_svg = "\n".join(segments)

    return f"""<svg xmlns="http://www.w3.org/2000/svg"
width="430"
height="118"
viewBox="0 0 430 118"
role="img"
aria-label="Top programming language this month: {escape(language)}">

<rect
x="1"
y="1"
width="428"
height="116"
fill="#07070f"
stroke="#00e5ff"
stroke-width="3"/>

<rect x="1" y="1" width="8" height="8" fill="#ff4fd8"/>
<rect x="421" y="1" width="8" height="8" fill="#ff4fd8"/>
<rect x="1" y="109" width="8" height="8" fill="#ff4fd8"/>
<rect x="421" y="109" width="8" height="8" fill="#ff4fd8"/>

<text
x="20"
y="26"
font-family="'Courier New',Consolas,monospace"
font-size="13"
font-weight="700"
letter-spacing="2"
fill="#00e5ff">
TOP LANG · {escape(month_label.upper())}
</text>

<rect x="20" y="44" width="58" height="58" fill="#0d0d1c" stroke="#ff4fd8" stroke-width="3"/>
<text
x="49"
y="80"
text-anchor="middle"
font-family="'Courier New',Consolas,monospace"
font-size="14"
font-weight="700"
fill="#ffe14d">
{escape(abbreviation)}
</text>

<text
x="112"
y="64"
font-family="'Courier New',Consolas,monospace"
font-size="20"
font-weight="700"
fill="#eafcff">
{escape(language)}
</text>

{bar_svg}

<text
x="112"
y="108"
font-family="'Courier New',Consolas,monospace"
font-size="12"
letter-spacing="1"
fill="#6a7aa0">
{changed_lines:,} CHANGED LINES THIS MONTH
</text>

</svg>
"""


def main():
    start, end = month_range()

    since = start.isoformat().replace("+00:00", "Z")
    until = end.isoformat().replace("+00:00", "Z")

    counts = Counter()
    per_repo = Counter()

    repos = list(
        pages(
            "https://api.github.com/users/"
            f"{urllib.parse.quote(USER)}"
            "/repos?type=owner&sort=pushed"
        )
    )

    print(f"Found {len(repos)} repositories owned by {USER}")

    for repo in repos:
        if repo.get("fork"):
            continue

        # Repo profil (isinya cuma README + tooling) tidak ikut dihitung.
        if repo["name"].lower() == USER.lower():
            continue

        if repo.get("archived"):
            continue

        full_name = repo["full_name"]

        commits_url = (
            "https://api.github.com/repos/"
            f"{urllib.parse.quote(full_name, safe='/')}"
            "/commits?"
            f"author={urllib.parse.quote(USER)}"
            f"&since={urllib.parse.quote(since)}"
            f"&until={urllib.parse.quote(until)}"
        )

        try:
            commits = list(pages(commits_url))
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
        ) as exc:
            print(f"[WARN] {full_name}: {exc}")
            continue

        if not commits:
            continue

        print(
            f"[INFO] {full_name}: "
            f"{len(commits)} commit(s)"
        )

        for commit in commits:
            sha = commit.get("sha")

            if not sha:
                continue

            detail_url = (
                "https://api.github.com/repos/"
                f"{urllib.parse.quote(full_name, safe='/')}"
                f"/commits/{sha}"
            )

            try:
                detail = api(detail_url)
            except (
                urllib.error.HTTPError,
                urllib.error.URLError,
                TimeoutError,
            ) as exc:
                print(
                    f"[WARN] {full_name}@{sha[:7]}: {exc}"
                )
                continue

            for file_info in detail.get("files", []):
                language = detect_language(file_info)

                if not language:
                    continue

                additions = int(
                    file_info.get("additions", 0)
                )

                deletions = int(
                    file_info.get("deletions", 0)
                )

                counts[language] += additions + deletions
                per_repo[(full_name, language)] += additions + deletions

    print("\nLanguage totals:")

    for language, value in counts.most_common():
        print(f"  {language}: {value}")

    print("\nPer repo:")

    for (name, language), value in per_repo.most_common():
        print(f"  {name} [{language}]: {value}")

    if counts:
        language, changed_lines = counts.most_common(1)[0]
    else:
        language = "No activity yet"
        changed_lines = 0

    month_label = start.strftime("%B %Y")

    OUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUT.write_text(
        make_svg(
            language,
            changed_lines,
            month_label,
        ),
        encoding="utf-8",
    )

    print(
        f"\nGenerated {OUT}: "
        f"{language} ({changed_lines} changed lines)"
    )


if __name__ == "__main__":
    main()
