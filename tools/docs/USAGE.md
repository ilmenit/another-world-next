# Another World Toolchain Usage Guide

This guide explains how to use the Python tooling located in `docs/tools` to unpack
resources, manipulate bytecode, and rebuild archives for the Another World
interpreter.  All commands assume the current working directory is the project
root and that you are using Python 3.10 or newer.

## Environment Setup

- Install required standard-library-friendly dependencies: none beyond Python.
- Ensure the repository’s submodules and assets (e.g. `bin/share/another-world`)
  are present.  The scripts assume the original data files are available there.
- Optional: create a virtual environment and activate it to isolate Python packages.

```
python3 -m venv .venv
source .venv/bin/activate
```

## Shared Concepts

- **MEMLIST.BIN**: resource index describing each asset: type, bank, offsets,
  and compressed size.  The unpacker/packer rely on it to locate assets.
- **Bank Files (`BANKXX`)**: raw data banks referenced by MEMLIST entries.
- **ByteKiller Compression**: custom back-to-front LZ-style codec used for many
  assets.  We provide a fully compatible Python decompressor; compression is
  not yet implemented.
- **Bytecode**: Another World’s VM instruction stream.  The disassembler and
  assembler operate on these blobs and support round-trip fidelity.
- **Polygon Opcodes**: Variable-length instructions decoded using VM semantics.
  They are emitted (and re-assembled) via `POLYRAW` to guarantee bit accuracy.

## Tool Overview

### `common.py`

Shared helpers used by every script:

- `bytekiller_decompress(data, unpacked_size)` mirrors the C++ implementation.
- `MemList` class loads and writes MEMLIST tables.
- Label utilities ensure consistent naming for disassembly/assembly.
- `BytecodeStream` reproduces the VM’s byte-fetched semantics around polygons.

### `unpacker.py`

Extracts resources from the original data directories.

Usage:

```
python -m docs.tools.unpacker --input bin/share/another-world --output out_dir
```

Key behaviours:

- Reads `MEMLIST.BIN`, iterates all resources, and emits files such as
  `part_000_bytecode.bin` or `music_004.bin` into `out_dir`.
- Automatically decompresses ByteKiller-compressed entries when possible.
- Preserves metadata (resource id, type, original bank offset) in filenames.

### `packer.py`

Performs the inverse operation, rebuilding MEMLIST and bank files from a
directory of resources.

Usage:

```
python -m docs.tools.packer --input out_dir --output build_dir
```

Current capabilities and limitations:

- Reuses original compressed payloads if unchanged assets are provided.
- Emits raw (uncompressed) versions for modified data; warns when compression
  would be needed because `bytekiller_compress` is not yet implemented.
- Regenerates `MEMLIST.BIN` using updated sizes and bank offsets.

### `disassembler.py`

Converts a bytecode blob into a round-trip friendly textual representation.

Usage:

```
python -m docs.tools.disassembler --input extracted_bytecode.bin --output script.asm
```

Features:

- Mirrors `vm.cc`’s decoding rules, including conditionals, threads, and
  polygons (`POLYRAW` directives).
- Emits labels for every call/jump target (`func_xxxx`, `label_xxxx`,
  `thread_xxxx`).
- Output is stable for re-assembly: running through the assembler yields
  bit-identical binaries (verified in automated checks).

### `assembler.py`

Rebuilds bytecode from the textual format produced by the disassembler.

Usage:

```
python -m docs.tools.assembler script.asm --output rebuilt_bytecode.bin
```

Features:

- Two-pass assembler that resolves labels and patching distances.
- Supports `POLYRAW` directives to embed raw bytes for polygons.
- Validates operand formats; raises `AssemblyError` for unknown opcodes or
  label mismatches.

## Recommended Workflow

1. **Unpack resources** into a working directory:

   ```
   python -m docs.tools.unpacker --input bin/share/another-world --output build/resources
   ```

2. **Disassemble** the desired bytecode file:

   ```
   python -m docs.tools.disassembler --input build/resources/part_000_bytecode.bin --output part0.asm
   ```

3. **Modify** `part0.asm` (or other assets).  For bytecode, prefer editing the
   assembly rather than hex patches.

4. **Reassemble** the modified script:

   ```
   python -m docs.tools.assembler part0.asm --output build/resources/part_000_bytecode.bin
   ```

5. **Repack** all resources:

   ```
   python -m docs.tools.packer --input build/resources --output build/game
   ```

6. **Deploy/Test** by pointing the interpreter to the rebuilt assets directory.

## Round-Trip Verification

To confirm changes maintain bit-for-bit integrity, use the provided smoke test:

```
python - <<'PY'
import sys
sys.path.append('docs/tools')
from disassembler import disassemble
from assembler import assemble
from unpacker import _extract_resources
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)
    _extract_resources(Path('bin/share/another-world'), tmpdir)
    original = sorted(tmpdir.glob('*_bytecode.bin'))[0].read_bytes()
    asm = '\n'.join(disassemble(original))
    rebuilt = assemble(asm)
    assert rebuilt == original
PY
```

## Known Limitations & Future Work

- `bytekiller_compress` is not implemented; packer falls back to uncompressed
  payloads for modified resources.
- No automated test harness yet; consider adding pytest-based suites covering
  decode→encode cycles and polygon edge cases.
- Some tooling still assumes the original directory layout under
  `bin/share/another-world`; make paths configurable if you relocate assets.

## Troubleshooting

- **`AssemblyError: unsupported opcode`** – ensure you are using directives
  emitted by the current disassembler; remove manual hex edits unless wrapped
  in `POLYRAW` or `DB` directives.
- **Round-trip mismatch** – run the verification snippet above, inspect the
  first mismatching byte, and confirm polygon/endian-sensitive instructions are
  preserved.
- **`bytekiller_decompress` errors** – indicates truncated or corrupted bank
  data.  Verify the original archives and MEMLIST entries.

---

Document maintained at `/docs/tools/docs/USAGE.md`.  Update this guide whenever
tool behaviour changes to keep workflows reproducible.

