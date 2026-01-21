"""
This file generates a text file of all tvg-ids from a playlist. Used as the basis for generate_epg.py
"""

import json
from pathlib import Path
import re


def parse_m3u(m3u_path: Path):
    """Extract tvg-id from M3U."""
    channels = []
    with m3u_path.open("r", encoding="utf-8") as f:
        content = f.read()

    # Find #EXTINF lines
    for match in re.finditer(r'#EXTINF:.*?tvg-id="([^"]+)"', content, re.DOTALL):
        channels.append(match.groups()[0])

    return channels


def main():
    channels = parse_m3u(Path("playlist.m3u8"))

    with open("ids.txt", "w") as f:
        for channel in channels:
            f.write(channel + "\n")


if __name__ == "__main__":
    main()
