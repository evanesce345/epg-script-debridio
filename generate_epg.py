import argparse
import gzip
import io
import json
import sys
from pathlib import Path
from typing import Dict

import requests
import xml.etree.ElementTree as ET


def load_mapping(path: Path) -> Dict[str, str]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def download_and_decompress(url: str) -> bytes:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    data = resp.content

    # decompress the gz
    try:
        return gzip.decompress(data)
    except OSError:
        # in case not gzipped - return raw data
        return data


def transform_xml(xml_bytes: bytes, mapping: Dict[str, str]) -> bytes:
    # parse XML
    parser = ET.XMLParser(target=ET.TreeBuilder())
    root = ET.fromstring(xml_bytes, parser=parser)
    tree = ET.ElementTree(root)

    # 1) rewrite chanel associated id
    for ch in root.findall("channel"):
        cid = ch.get("id")
        if cid in mapping:
            ch.set("id", mapping[cid])

    # 2) rewrite programme associated channels
    for prog in root.findall("programme"):
        cid = prog.get("channel")
        if cid in mapping:
            prog.set("channel", mapping[cid])

    # keep only channels/programmes that were mapped
    mapped_ids = set(mapping.values())
    if mapped_ids:
        # remove channels not in mapped_ids
        for ch in list(root.findall("channel")):
            cid = ch.get("id")
            if cid not in mapped_ids:
                root.remove(ch)

        # remove programmes not in mapped_ids
        for prog in list(root.findall("programme")):
            cid = prog.get("channel")
            if cid not in mapped_ids:
                root.remove(prog)

    # serialize back to bytes
    buf = io.BytesIO()
    tree.write(buf, encoding="utf-8", xml_declaration=True)
    return buf.getvalue()


def main():
    parser = argparse.ArgumentParser(
        description="Download epgshare XMLTV, remap IDs, and output custom XML."
    )
    parser.add_argument(
        "--source-url",
        required=True,
        help="epgshare XMLTV URL, e.g. https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz",
    )
    parser.add_argument(
        "--mapping",
        default="mapping.json",
        help="Path to JSON file with {source_id: target_id} mapping.",
    )
    parser.add_argument(
        "--output",
        default="custom_epg.xml",
        help="Output XMLTV file path (e.g. web root file).",
    )
    args = parser.parse_args()

    mapping_path = Path(args.mapping)
    output_path = Path(args.output)

    try:
        mapping = load_mapping(mapping_path)
    except Exception as e:
        print(
            f"ERROR: Failed to load mapping from {mapping_path}: {e}", file=sys.stderr
        )
        sys.exit(1)

    try:
        xml_bytes = download_and_decompress(args.source_url)
    except Exception as e:
        print(
            f"ERROR: Failed to download/decompress XML from {args.source_url}: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        out_bytes = transform_xml(xml_bytes, mapping)
    except Exception as e:
        print(f"ERROR: Failed to transform XML: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        output_path.write_bytes(out_bytes)
    except Exception as e:
        print(
            f"ERROR: Failed to write output XML to {output_path}: {e}", file=sys.stderr
        )
        sys.exit(1)

    print(f"EPG updated: {output_path}")


if __name__ == "__main__":
    main()
