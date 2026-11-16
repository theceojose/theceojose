#!/usr/bin/env python3
"""Actualiza la seccion de WakaTime del README usando un token OAuth (Bearer)."""
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request

API_URL = "https://wakatime.com/api/v1/users/current/stats/last_7_days"
README = os.environ.get("README_PATH", "README.md")
LANG_COUNT = 8
BAR_WIDTH = 25
BLOCKS = "░▒▓█"


def fetch_stats(token: str) -> dict:
    req = urllib.request.Request(API_URL, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)["data"]
    except urllib.error.HTTPError as e:
        sys.exit(f"WakaTime API error {e.code}: {e.read().decode(errors='replace')[:300]}")


def bar(percent: float) -> str:
    filled = percent / 100 * BAR_WIDTH
    full = int(filled)
    frac = filled - full
    out = BLOCKS[3] * full
    if full < BAR_WIDTH:
        out += BLOCKS[min(int(frac * 4), 3)] if frac else BLOCKS[0]
    return out.ljust(BAR_WIDTH, BLOCKS[0])


def render(data: dict) -> str:
    lines = [f"Total Time: {data.get('human_readable_total', '0 mins')}", ""]
    for lang in data.get("languages", [])[:LANG_COUNT]:
        lines.append(
            f"{lang['name']:<20} {lang['text']:<21} {bar(lang['percent'])}   {lang['percent']:05.2f} %"
        )
    return "```txt\n" + "\n".join(lines) + "\n```"


def main() -> None:
    token = os.environ.get("WAKATIME_ACCESS_TOKEN", "").strip()
    if not token:
        sys.exit("Falta el secret WAKATIME_ACCESS_TOKEN (token OAuth con scope read_stats).")

    block = render(fetch_stats(token))
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    with open(README, encoding="utf-8") as f:
        text = f.read()

    text, n1 = re.subn(
        r"(<!--START_SECTION:waka-->\n\n).*?(\n\n<!--END_SECTION:waka-->)",
        lambda m: m.group(1) + block + m.group(2),
        text,
        flags=re.S,
    )
    text, n2 = re.subn(
        r"<!--START_UPDATED-->.*?<!--END_UPDATED-->",
        f"<!--START_UPDATED-->{today}<!--END_UPDATED-->",
        text,
    )
    if not (n1 and n2):
        sys.exit("No se encontraron los marcadores en el README.")

    with open(README, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
