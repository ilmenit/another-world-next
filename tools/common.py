"""Shared helpers for Another World tooling.

This module provides pure-Python implementations of the data structures
and codecs that the original interpreter uses (notably the ByteKiller
compressor/decompressor and the MEMLIST table handling).  The goal is to
give the command-line tools placed in the same directory a dependable
foundation without pulling in any third-party dependencies so the scripts
remain fully portable.

The implementations here are intentionally straightforward translations of
the C++ code that ships with the interpreter to guarantee behavioural
parity.  Only the pieces that are required by the current toolchain are
present; new tools should extend this module instead of re-implementing the
same logic.
"""

from __future__ import annotations

import dataclasses
import io
import re
import struct
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple, Dict


# ---------------------------------------------------------------------------
# ByteKiller codec
# ---------------------------------------------------------------------------


class ByteKillerError(RuntimeError):
    """Raised when ByteKiller data fails validation."""


def _read_le_uint32(buffer: bytes, offset: int) -> int:
    return struct.unpack_from("<I", buffer, offset)[0]


def _write_le_uint32(value: int) -> bytes:
    return struct.pack("<I", value & 0xFFFFFFFF)


def bytekiller_decompress(data: bytes, unpacked_size: int) -> bytes:
    """Decompresses *data* using the ByteKiller algorithm.

    The implementation mirrors the interpreter's C++ version.  The compressed
    stream stores its metadata (length/check/chunk) at the end of the buffer
    and relies on little-endian bit extraction working from the last byte
    backwards.  We follow that layout verbatim to guarantee bit-for-bit
    compatibility.
    """

    if unpacked_size <= 0:
        return b""

    src = memoryview(data)
    dst = bytearray(unpacked_size)

    src_pos = len(src) - 1
    dst_pos = len(dst) - 1

    def fetch_long() -> int:
        nonlocal src_pos
        if src_pos < 3:
            raise ByteKillerError("compressed stream truncated while reading metadata")
        value = 0
        for shift in (0, 8, 16, 24):
            value |= src[src_pos] << shift
            src_pos -= 1
        return value

    def write_byte(byte: int) -> None:
        nonlocal dst_pos, remaining
        if dst_pos < 0:
            raise ByteKillerError("destination buffer overflow")
        dst[dst_pos] = byte & 0xFF
        dst_pos -= 1
        remaining -= 1

    def copy_bytes(offset: int, count: int) -> None:
        # The stream is decoded backwards.  Previously written bytes reside at
        # higher indices (dst_pos + offset + 1).
        for _ in range(count):
            src_index = dst_pos + offset + 1
            if not (0 <= src_index < len(dst)):
                raise ByteKillerError("copy offset outside of already decoded data")
            write_byte(dst[src_index])

    def read_bits(count: int) -> int:
        result = 0
        bit_count = count
        while bit_count:
            bit = get_bit()
            result = (result << 1) | bit
            bit_count -= 1
        return result

    remaining = fetch_long()
    checksum = fetch_long()
    chunk = fetch_long()
    checksum ^= chunk

    # Consume the stream.  After each 32-bit block we XOR the checksum just
    # like the interpreter; the final value must be zero for the stream to be
    # considered valid.
    def get_bit() -> int:
        nonlocal chunk, checksum, src_pos
        bit = chunk & 0x1
        chunk >>= 1
        if chunk == 0:
            chunk = fetch_long()
            checksum ^= chunk
            bit = chunk & 0x1
            chunk = (chunk >> 1) | (1 << 31)
        return bit

    while remaining > 0:
        code = get_bit()
        if code == 0:
            code = (code << 1) | read_bits(1)
        else:
            code = (code << 2) | read_bits(2)

        if code == 0x00:
            count = read_bits(3) + 1
            for _ in range(count):
                write_byte(read_bits(8))
        elif code == 0x07:
            count = read_bits(8) + 9
            for _ in range(count):
                write_byte(read_bits(8))
        elif code == 0x01:
            count = 2
            offset = read_bits(8)
            copy_bytes(offset, count)
        elif code == 0x04:
            count = 3
            offset = read_bits(9)
            copy_bytes(offset, count)
        elif code == 0x05:
            count = 4
            offset = read_bits(10)
            copy_bytes(offset, count)
        elif code == 0x06:
            count = read_bits(8) + 1
            offset = read_bits(12)
            copy_bytes(offset, count)
        else:
            raise ByteKillerError(f"unsupported pattern code 0x{code:02x}")

    if checksum != 0:
        raise ByteKillerError("checksum mismatch while unpacking ByteKiller stream")

    if dst_pos != -1:
        # We filled the buffer backwards, so finishing with -1 means the
        # buffer has been exactly populated.
        raise ByteKillerError("decompressed size mismatch")

    return bytes(dst)


# TODO: Implement ByteKiller compression.  The packer currently relies on the
# original compressed payloads when possible and falls back to emitting raw
# (uncompressed) data for modified resources.  The placeholder implementation
# is kept to make the API future-proof.


def bytekiller_compress(data: bytes) -> bytes:
    """Returns a ByteKiller-compressed payload for *data*.

    The full encoder is fairly involved.  For now we raise an explicit
    exception so callers can decide how to proceed (for example by copying the
    original compressed data when no modifications were made).  The packer tool
    uses this behaviour to emit clear error messages when compression would be
    required.
    """

    raise NotImplementedError("ByteKiller compression not yet implemented")


# ---------------------------------------------------------------------------
# MEMLIST handling
# ---------------------------------------------------------------------------


MEMLIST_ENTRY_SIZE = 20


@dataclasses.dataclass
class MemListEntry:
    state: int
    type: int
    unused1: int
    unused2: int
    unused3: int
    bank_id: int
    bank_offset: int
    unused4: int
    packed_size: int
    unused5: int
    unpacked_size: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "MemListEntry":
        if len(data) != MEMLIST_ENTRY_SIZE:
            raise ValueError("invalid MEMLIST entry size")
        fields = struct.unpack(
            ">BBHHBBIHHHH", data
        )
        return cls(*fields)

    def to_bytes(self) -> bytes:
        return struct.pack(
            ">BBHHBBIHHHH",
            self.state,
            self.type,
            self.unused1,
            self.unused2,
            self.unused3,
            self.bank_id,
            self.bank_offset,
            self.unused4,
            self.packed_size,
            self.unused5,
            self.unpacked_size,
        )

    @property
    def is_terminal(self) -> bool:
        return self.type == 0xFF


class MemList:
    """Utility helpers for working with ``MEMLIST.BIN`` files."""

    def __init__(self, entries: List[MemListEntry]):
        self.entries = entries

    @classmethod
    def load(cls, path: Path) -> "MemList":
        data = path.read_bytes()
        entries: List[MemListEntry] = []
        for offset in range(0, len(data), MEMLIST_ENTRY_SIZE):
            chunk = data[offset : offset + MEMLIST_ENTRY_SIZE]
            if len(chunk) < MEMLIST_ENTRY_SIZE:
                break
            entry = MemListEntry.from_bytes(chunk)
            entries.append(entry)
            if entry.is_terminal:
                break
        return cls(entries)

    def save(self, path: Path) -> None:
        with path.open("wb") as handle:
            for entry in self.entries:
                handle.write(entry.to_bytes())

    def iter_resources(self) -> Iterator[Tuple[int, MemListEntry]]:
        """Yields ``(resource_id, entry)`` tuples for each non-terminal entry."""

        for index, entry in enumerate(self.entries):
            yield index, entry
            if entry.is_terminal:
                break


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_file(path: Path) -> bytes:
    return path.read_bytes()


def write_file(path: Path, payload: bytes) -> None:
    ensure_directory(path.parent)
    path.write_bytes(payload)


LABEL_PREFIXES = {
    "func": "func_",
    "label": "label_",
    "thread": "thread_",
}


def format_label(prefix: str, address: int) -> str:
    return f"{LABEL_PREFIXES.get(prefix, prefix)}{address:04x}"


_LABEL_PATTERN = re.compile(r"^(?P<prefix>[a-zA-Z_]+)_(?P<addr>[0-9a-fA-F]{4})$")


def resolve_label(value: str, labels: Dict[str, int]) -> int:
    if value in labels:
        return labels[value]
    match = _LABEL_PATTERN.match(value)
    if match:
        return int(match.group("addr"), 16)
    if value.startswith("0x"):
        return int(value, 16)
    return int(value)


