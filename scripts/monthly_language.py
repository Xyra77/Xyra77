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
rx="13"
fill="#1c173d"
stroke="#5b2a86"/>

<text
x="22"
y="27"
font-family="Arial,sans-serif"
font-size="14"
font-weight="700"
fill="#ffb36b">
MONTHLY LANGUAGE · {escape(month_label.upper())}
</text>

<circle
cx="67"
cy="76"
r="28"
fill="none"
stroke="#4b315b"
stroke-width="7"/>

<circle
cx="67"
cy="76"
r="28"
fill="none"
stroke="#ff6b8b"
stroke-width="7"
stroke-linecap="round"
stroke-dasharray="125 176"
transform="rotate(-90 67 76)"/>

<text
x="67"
y="81"
text-anchor="middle"
font-family="Arial,sans-serif"
font-size="13"
font-weight="700"
fill="#fff1e0">
{escape(abbreviation)}
</text>

<text
x="112"
y="66"
font-family="Arial,sans-serif"
font-size="22"
font-weight="700"
fill="#fff1e0">
{escape(language)}
</text>

<text
x="112"
y="90"
font-family="Arial,sans-serif"
font-size="12"
fill="#c8b6e8">
{changed_lines:,} changed lines
</text>

<text
x="112"
y="106"
font-family="Arial,sans-serif"
font-size="11"
fill="#c8b6e8">
TOP LANGUAGE THIS MONTH
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
