"""Resource unpacker for Another World game data.

The unpacker reads MEMLIST.BIN and the BANKxx files from a supplied data
directory and writes the decompressed resources to an output tree mirroring
the layout produced by the interpreter at runtime.  Each resource is written
as ``{id:02x}_{type}.bin`` inside the specified destination directory.

Usage example::

    python unpacker.py --data-dir ../bin/share/another-world --output ./dump

Where ``--data-dir`` points to the folder containing the BANK files and
``MEMLIST.BIN``.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Dict

from common import (
    ByteKillerError,
    MemList,
    bytekiller_decompress,
    ensure_directory,
    write_file,
)


_RESOURCE_TYPE_NAMES = {
    0x00: "sound",
    0x01: "music",
    0x02: "bitmap",
    0x03: "palette",
    0x04: "bytecode",
    0x05: "polygon1",
    0x06: "polygon2",
    0xFF: "end",
}


def _load_bank(path: Path) -> bytes:
    return path.read_bytes()


def _extract_resources(data_dir: Path, output_dir: Path) -> None:
    memlist = MemList.load(data_dir / "MEMLIST.BIN")

    bank_cache: Dict[int, bytes] = {}

    for resource_id, entry in memlist.iter_resources():
        if entry.is_terminal:
            logging.debug("Reached terminal resource entry at %02x", resource_id)
            break

        resource_type_name = _RESOURCE_TYPE_NAMES.get(entry.type, f"type{entry.type:02x}")
        target_name = f"{resource_id:02x}_{resource_type_name}.bin"
        target_path = output_dir / target_name

        bank_path = data_dir / f"BANK{entry.bank_id:02X}"
        bank_data = bank_cache.setdefault(entry.bank_id, _load_bank(bank_path))

        compressed = bank_data[entry.bank_offset : entry.bank_offset + entry.packed_size]

        if entry.packed_size == entry.unpacked_size:
            logging.debug("%s -> copied raw bytes (%d bytes)", target_name, entry.unpacked_size)
            payload = compressed
        else:
            try:
                payload = bytekiller_decompress(compressed, entry.unpacked_size)
                logging.debug(
                    "%s -> decompressed %d -> %d bytes",
                    target_name,
                    entry.packed_size,
                    entry.unpacked_size,
                )
            except ByteKillerError as exc:
                logging.error("Failed to decompress resource %02x: %s", resource_id, exc)
                raise

        write_file(target_path, payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Unpack Another World resources")
    parser.add_argument("--data-dir", type=Path, required=True, help="Directory containing MEMLIST.BIN and BANK files")
    parser.add_argument("--output", type=Path, required=True, help="Destination directory for decompressed resources")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s: %(message)s")

    ensure_directory(args.output)

    _extract_resources(args.data_dir, args.output)

    logging.info("Resources unpacked to %s", args.output)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())


