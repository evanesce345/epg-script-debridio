"""
This file generates values for mapping based on an m3u8 playlist in the directory.
Use this as the foundation of a mapping.json file.
"""

import json
from pathlib import Path
import re


def parse_m3u(m3u_path: Path):
    """Extract tvg-id and tvg-name from M3U."""
    channels = {}
    with m3u_path.open("r", encoding="utf-8") as f:
        content = f.read()

    # Find #EXTINF lines
    for match in re.finditer(
        r'#EXTINF:.*?tvg-id="([^"]+)"[^,]*,(.*?)(?=\nhttp|$)', content, re.DOTALL
    ):
        tvg_id, name = match.groups()
        channels[tvg_id] = name.strip()

    return channels


def main():
    channels = parse_m3u(Path("playlist.m3u8"))
    mapping = {str(i): v for i, v in enumerate(channels.keys())}
    json.dump(mapping, open("mappings.json", "w"), indent=2)


if __name__ == "__main__":
    main()
