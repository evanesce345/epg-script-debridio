"""
This is the main file that generates the epg based on supplied sources and ids text file.
"""

import argparse
import gzip
import io
import json
import sys
from pathlib import Path
from typing import Dict
import logging

import requests
import xml.etree.ElementTree as ET


def load_ids(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8") as f:
        a = [line.strip() for line in f]
        return a


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


def transform_xml(xml_bytes: bytes, ids: list[str]) -> bytes:
    # parse XML
    parser = ET.XMLParser(target=ET.TreeBuilder())
    root = ET.fromstring(xml_bytes, parser=parser)
    tree = ET.ElementTree(root)

    # # 1) rewrite chanel associated id
    # for ch in root.findall("channel"):
    #     cid = ch.get("id")
    #     if cid in ids:
    #         ch.set("id", cid)

    # # 2) rewrite programme associated channels
    # for prog in root.findall("programme"):
    #     cid = prog.get("channel")
    #     if cid in ids:
    #         prog.set("channel", cid)

    # keep only channels/programmes that were mapped
    mapped_ids = set(ids)
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
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.INFO,
        datefmt="[%H:%M:%S]",
    )

    logging.info("EPG generation started...")

    parser = argparse.ArgumentParser(
        description="Download XMLTV, map IDs, and output custom XML."
    )
    parser.add_argument(
        "--source-url",
        nargs="+",
        required=True,
        help="XMLTV URL(s), e.g. https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz",
    )
    parser.add_argument(
        "--ids",
        default="ids.txt",
        help="Path to txt file with ids.",
    )
    parser.add_argument(
        "--output",
        default="/app/epg/guide.xml",
        help="Output XMLTV file path (e.g. web root file).",
    )
    args = parser.parse_args()

    ids_path = Path(args.ids)
    output_path = Path(args.output)

    try:
        ids = load_ids(ids_path)
    except Exception as e:
        logging.error(f"Failed to load ids from {ids_path}: {e}")
        sys.exit(1)

    # master root to append all source url info to
    master_root = ET.Element("tv")

    for source in args.source_url:
        logging.info(
            f"Transforming from source #{args.source_url.index(source) + 1} of {len(args.source_url)} - {source}"
        )
        try:
            xml_bytes = download_and_decompress(source)
        except Exception as e:
            logging.error(f"Failed to download/decompress XML from {source}: {e}")
            sys.exit(1)

        try:
            out_bytes = transform_xml(xml_bytes, ids)
        except Exception as e:
            logging.error(f"ERROR: Failed to transform XML: {e}")
            sys.exit(1)

        try:
            root = ET.fromstring(out_bytes)
        except Exception as e:
            logging.error(f"Failed to parse transformed XML from {source}: {e}")
            sys.exit(1)

        # Append all channels and programmes to master root
        for ch in root.findall("channel"):
            master_root.append(ch)

        for prog in root.findall("programme"):
            master_root.append(prog)

    # Serialize master_root to bytes before writing
    try:
        tree = ET.ElementTree(master_root)

        with gzip.open(str(output_path) + ".gz", "wb") as f:
            tree.write(f, encoding="utf-8", xml_declaration=True)

    except Exception as e:
        logging.error(f"Failed to write output XML to {output_path}: {e}")
        sys.exit(1)

    logging.info(f"EPG updated: {output_path}.gz")


if __name__ == "__main__":
    main()
