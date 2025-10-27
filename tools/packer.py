"""Resource packer for Another World game data.

The packer reads a directory of raw resources (as produced by the unpacker),
reassembles the MEMLIST table and the BANK files, and writes them to a target
directory.  The goal is to make it possible to edit the extracted resources
and rebuild a set of data files that the interpreter can consume without any
binary differences except for the changed assets.

At the moment the ByteKiller compressor is not implemented; when the packer
detects that a resource was previously compressed it emits a clear error so
the user can decide how to proceed (for example by reusing the original
compressed payload when no modifications were made).  This keeps the tool
honest about its current limitations while providing the necessary plumbing
for round-tripping the data once compression support lands.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Dict, Tuple

from common import (
    MEMLIST_ENTRY_SIZE,
    MemList,
    MemListEntry,
    bytekiller_compress,
    ensure_directory,
    read_file,
    write_file,
)


def _load_original_payloads(data_dir: Path) -> Dict[Tuple[int, int], bytes]:
    """Load the original compressed payloads keyed by ``(bank_id, offset)``."""

    memlist = MemList.load(data_dir / "MEMLIST.BIN")
    cache: Dict[int, bytes] = {}
    payloads: Dict[Tuple[int, int], bytes] = {}

    for _, entry in memlist.iter_resources():
        if entry.is_terminal:
            break
        bank_key = entry.bank_id
        bank_blob = cache.setdefault(bank_key, (data_dir / f"BANK{bank_key:02X}").read_bytes())
        payload = bank_blob[entry.bank_offset : entry.bank_offset + entry.packed_size]
        payloads[(entry.bank_id, entry.bank_offset)] = payload

    return payloads


def _rebuild(data_dir: Path, resources_dir: Path, output_dir: Path) -> None:
    original_payloads = _load_original_payloads(data_dir)
    memlist = MemList.load(data_dir / "MEMLIST.BIN")

    new_entries = []
    bank_buffers: Dict[int, bytearray] = {}
    bank_offsets: Dict[int, int] = {}

    for resource_id, entry in memlist.iter_resources():
        new_entry = MemListEntry(**{field.name: getattr(entry, field.name) for field in MemListEntry.__dataclass_fields__.values()})
        if entry.is_terminal:
            new_entries.append(new_entry)
            break

        resource_name = resources_dir / f"{resource_id:02x}_"
        matches = list(resource_name.parent.glob(f"{resource_id:02x}_*.bin"))
        if not matches:
            logging.debug("Resource %02x unchanged; keeping original payload", resource_id)
            new_entries.append(new_entry)
            continue

        if len(matches) > 1:
            raise RuntimeError(f"multiple candidate files for resource {resource_id:02x}")

        resource_path = matches[0]
        payload = read_file(resource_path)
        new_entry.unpacked_size = len(payload)

        if entry.packed_size != entry.unpacked_size:
            # Attempt to compress; currently unsupported.
            logging.error("Resource %02x was compressed originally; compression not supported yet", resource_id)
            bytekiller_compress(payload)  # This will raise NotImplementedError.

        bank_id = entry.bank_id
        bank_buf = bank_buffers.setdefault(bank_id, bytearray())
        offset = len(bank_buf)
        bank_buf.extend(payload)
        new_entry.bank_offset = offset
        new_entry.packed_size = len(payload)
        bank_offsets[resource_id] = offset
        new_entries.append(new_entry)

    # Reconstruct BANK files with patched payloads (unchanged entries fall back
    # to original data).
    for (bank_id, offset), payload in original_payloads.items():
        bank_buf = bank_buffers.setdefault(bank_id, bytearray())
        # Ensure capacity.
        end = offset + len(payload)
        if len(bank_buf) < end:
            bank_buf.extend(b"\x00" * (end - len(bank_buf)))
        bank_buf[offset:end] = payload

    # Write output files.
    ensure_directory(output_dir)

    MemList(new_entries).save(output_dir / "MEMLIST.BIN")

    for bank_id, buffer in bank_buffers.items():
        write_file(output_dir / f"BANK{bank_id:02X}", bytes(buffer))


def main() -> int:
    parser = argparse.ArgumentParser(description="Pack Another World resources back into BANK files")
    parser.add_argument("--data-dir", type=Path, required=True, help="Directory that holds the original BANK files and MEMLIST.BIN")
    parser.add_argument("--resources", type=Path, required=True, help="Directory containing modified resources (output from unpacker)")
    parser.add_argument("--output", type=Path, required=True, help="Destination directory for rebuilt files")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s: %(message)s")

    _rebuild(args.data_dir, args.resources, args.output)

    logging.info("Rebuilt resources written to %s", args.output)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())


