"""Bytecode disassembler for Another World VM.

This script takes a bytecode blob (typically extracted via the unpacker) and
produces an assembly-like listing that mirrors the interpreter's instruction
set.  Labels are auto-generated for every branch/call target to make the
output easier to follow.  The format is intentionally round-trip friendly so
the assembler can ingest it without information loss.
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union

from opcodes import (
    OP_SETI,
    OP_SETR,
    OP_ADDR,
    OP_ADDI,
    OP_CALL,
    OP_RET,
    OP_YIELD,
    OP_JUMP,
    OP_START,
    OP_DBRA,
    OP_CJMP,
    OP_FADE,
    OP_RESET,
    OP_PAGE,
    OP_FILL,
    OP_COPY,
    OP_SHOW,
    OP_HALT,
    OP_PRINT,
    OP_SUBR,
    OP_ANDI,
    OP_IORI,
    OP_LSLI,
    OP_LSRI,
    OP_SOUND,
    OP_LOAD,
    OP_MUSIC,
    OP_POLY_BEGIN,
    OP_POLY_TYPE1_START,
    OP_POLY_TYPE2_START,
    OP_POLY_MAX,
    OPCODE_NAMES,
)

from common import format_label


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


class BytecodeStream:
    def __init__(self, bytecode: bytes, start: int):
        self.bytecode = bytecode
        self.pos = start
        self.end = len(bytecode)

    def remaining(self) -> int:
        return self.end - self.pos

    def read_u8(self) -> int:
        if self.pos >= self.end:
            raise ValueError("unexpected end of bytecode while decoding polygon")
        value = self.bytecode[self.pos]
        self.pos += 1
        return value

    def read_u16_be(self) -> int:
        hi = self.read_u8()
        lo = self.read_u8()
        return (hi << 8) | lo


def _read_u16(buffer: bytes, offset: int) -> int:
    return (buffer[offset] << 8) | buffer[offset + 1]


def _decode_poly1(bytecode: bytes, pc: int) -> Tuple[int, str, str]:
    opcode = bytecode[pc]
    stream = BytecodeStream(bytecode, pc + 1)

    raw_bytes = bytearray([opcode])

    offset = stream.read_u16_be()
    raw_bytes.extend(bytecode[pc + 1 : pc + 3])

    x_param = _poly1_get_x(opcode, stream, raw_bytes)
    y_param = _poly1_get_y(opcode, stream, raw_bytes)
    zoom_param, buffer_idx = _poly1_get_zoom_and_buffer(opcode, stream, raw_bytes)

    comment_parts = [
        f"flags=0x{opcode:02x}",
        f"addr_off=0x{(offset * 2) & 0xFFFF:04x}",
        f"x={x_param}",
        f"y={y_param}",
        f"buf={buffer_idx}",
        f"zoom={zoom_param}",
    ]

    raw_display = " ".join(f"0x{b:02x}" for b in raw_bytes)
    return len(raw_bytes), raw_display, " ".join(comment_parts)


def _poly1_get_x(opcode: int, stream: BytecodeStream, raw_bytes: bytearray) -> str:
    imm = stream.read_u8()
    raw_bytes.append(imm)

    if opcode & 0x20:
        if opcode & 0x10:
            value = (imm + 0x100) & 0xFFFF
            return f"0x{value:04x}"
        return f"0x{imm:02x}"
    else:
        if opcode & 0x10:
            return f"reg[{imm:02x}]"
        imm_low = stream.read_u8()
        raw_bytes.append(imm_low)
        combined = (imm << 8) | imm_low
        return f"0x{combined:04x}"


def _poly1_get_y(opcode: int, stream: BytecodeStream, raw_bytes: bytearray) -> str:
    imm = stream.read_u8()
    raw_bytes.append(imm)

    if opcode & 0x08:
        if opcode & 0x04:
            return f"0x{imm:02x}"
        return f"0x{imm:02x}"
    else:
        if opcode & 0x04:
            return f"reg[{imm:02x}]"
        imm_low = stream.read_u8()
        raw_bytes.append(imm_low)
        combined = (imm << 8) | imm_low
        return f"0x{combined:04x}"


def _poly1_get_zoom_and_buffer(opcode: int, stream: BytecodeStream, raw_bytes: bytearray) -> Tuple[str, int]:
    buffer_idx = 1

    if opcode & 0x02:
        if opcode & 0x01:
            buffer_idx = 2
            return "0x0040", buffer_idx
        zoom = stream.read_u8()
        raw_bytes.append(zoom)
        return f"0x{zoom:02x}", buffer_idx
    else:
        if opcode & 0x01:
            reg_idx = stream.read_u8()
            raw_bytes.append(reg_idx)
            return f"reg[{reg_idx:02x}]", buffer_idx
        return "0x0040", buffer_idx


def _decode_poly2(bytecode: bytes, pc: int) -> Tuple[int, str, str]:
    opcode = bytecode[pc]
    stream = BytecodeStream(bytecode, pc + 1)
    raw_bytes = bytearray([opcode]) 

    lsb = stream.read_u8()
    raw_bytes.append(lsb)
    x_val = stream.read_u8()
    raw_bytes.append(x_val)
    y_val = stream.read_u8()
    raw_bytes.append(y_val)

    offset = ((opcode << 8) | lsb) * 2

    comment = (
        f"flags=0x{opcode:02x} addr_off=0x{offset & 0xFFFF:04x} "
        f"x=0x{x_val:02x} y=0x{y_val:02x} buf=1 zoom=0x0040"
    )

    raw_display = " ".join(f"0x{b:02x}" for b in raw_bytes)
    return len(raw_bytes), raw_display, comment


@dataclass
class InstructionDef:
    name: str
    length: int


INSTRUCTION_SET: Dict[int, InstructionDef] = {
    OP_SETI: InstructionDef("SETI", 4),
    OP_SETR: InstructionDef("SETR", 3),
    OP_ADDR: InstructionDef("ADDR", 3),
    OP_ADDI: InstructionDef("ADDI", 4),
    OP_CALL: InstructionDef("CALL", 3),
    OP_RET: InstructionDef("RET", 1),
    OP_YIELD: InstructionDef("YIELD", 1),
    OP_JUMP: InstructionDef("JUMP", 3),
    OP_START: InstructionDef("START", 4),
    OP_DBRA: InstructionDef("DBRA", 4),
    # OP_CJMP handled specially (CJMP variants)
    OP_FADE: InstructionDef("FADE", 3),
    OP_RESET: InstructionDef("RESET", 4),
    OP_PAGE: InstructionDef("PAGE", 2),
    OP_FILL: InstructionDef("FILL", 3),
    OP_COPY: InstructionDef("COPY", 3),
    OP_SHOW: InstructionDef("SHOW", 2),
    OP_HALT: InstructionDef("HALT", 1),
    OP_PRINT: InstructionDef("PRINT", 6),
    OP_SUBR: InstructionDef("SUBR", 3),
    OP_ANDI: InstructionDef("ANDI", 4),
    OP_IORI: InstructionDef("IORI", 4),
    OP_LSLI: InstructionDef("LSLI", 4),
    OP_LSRI: InstructionDef("LSRI", 4),
    OP_SOUND: InstructionDef("SOUND", 6),
    OP_LOAD: InstructionDef("LOAD", 3),
    OP_MUSIC: InstructionDef("MUSIC", 7),
}

CONDITION_CODES = ["eq", "ne", "gt", "ge", "lt", "le"]


def _collect_labels(bytecode: bytes) -> Dict[int, str]:
    labels: Dict[int, str] = {}
    pc = 0
    size = len(bytecode)

    def assign_label(addr: int, prefix: str) -> None:
        if addr not in labels:
            labels[addr] = format_label(prefix, addr)

    def skip_polygon(current_pc: int) -> int:
        opcode = bytecode[current_pc]
        if OP_POLY_TYPE1_START <= opcode < OP_POLY_TYPE2_START:
            length, *_ = _decode_poly1(bytecode, current_pc)
            return length
        if OP_POLY_TYPE2_START <= opcode <= OP_POLY_MAX:
            length, *_ = _decode_poly2(bytecode, current_pc)
            return length
        return 1

    while pc < size:
        opcode = bytecode[pc]
        if opcode == OP_CALL:
            target = _read_u16(bytecode, pc + 1)
            assign_label(target, "func")
            pc += 3
        elif opcode == OP_JUMP:
            target = _read_u16(bytecode, pc + 1)
            assign_label(target, "label")
            pc += 3
        elif opcode == OP_START:
            target = _read_u16(bytecode, pc + 2)
            assign_label(target, "thread")
            pc += 4
        elif opcode == OP_DBRA:
            target = _read_u16(bytecode, pc + 2)
            assign_label(target, "label")
            pc += 4
        elif opcode == OP_CJMP:  # CJMP variants
            variant = bytecode[pc + 1]
            if variant & 0x80:
                target = _read_u16(bytecode, pc + 4)
                length = 6
            elif variant & 0x40:
                target = _read_u16(bytecode, pc + 5)
                length = 7
            else:
                target = _read_u16(bytecode, pc + 4)
                length = 6
            assign_label(target, "label")
            pc += length
        else:
            definition = INSTRUCTION_SET.get(opcode)
            if definition:
                pc += definition.length
            elif opcode >= OP_POLY_BEGIN:
                pc += skip_polygon(pc)
            else:
                pc += 1
    return labels


def _format_operand(value: int) -> str:
    return f"0x{value:04x}"


def _decode(bytecode: bytes, labels: Dict[int, str]) -> List[str]:
    lines: List[str] = []
    pc = 0
    size = len(bytecode)

    while pc < size:
        if pc in labels:
            lines.append(f"{labels[pc]}:")

        opcode = bytecode[pc]
        mnemonic = OPCODE_NAMES.get(opcode)
        definition = INSTRUCTION_SET.get(opcode)

        if definition is None and opcode == OP_CJMP:
            variant = bytecode[pc + 1]
            cond_idx = variant & 0x07
            if cond_idx < len(CONDITION_CODES) and (variant & ~0xC7) == 0:
                cond = CONDITION_CODES[cond_idx]
            else:
                cond = f"0x{variant:02x}"
            reg1 = bytecode[pc + 2]
            if variant & 0x80:
                reg2 = bytecode[pc + 3]
                addr = _read_u16(bytecode, pc + 4)
                target = labels.get(addr, _format_operand(addr))
                lines.append(f"    CJMP {cond}, [$%02x], [$%02x], {target}" % (reg1, reg2))
                pc += 6
            elif variant & 0x40:
                imm = _read_u16(bytecode, pc + 3)
                addr = _read_u16(bytecode, pc + 5)
                target = labels.get(addr, _format_operand(addr))
                lines.append("    CJMP %s, [$%02x], 0x%04x, %s" % (cond, reg1, imm, target))
                pc += 7
            else:
                imm = bytecode[pc + 3]
                addr = _read_u16(bytecode, pc + 4)
                target = labels.get(addr, _format_operand(addr))
                lines.append("    CJMP %s, [$%02x], 0x%02x, %s" % (cond, reg1, imm, target))
                pc += 6
            continue

        if definition is None and opcode >= OP_POLY_BEGIN:
            if OP_POLY_TYPE1_START <= opcode < OP_POLY_TYPE2_START:
                length, raw_display, comment = _decode_poly1(bytecode, pc)
            elif OP_POLY_TYPE2_START <= opcode <= OP_POLY_MAX:
                length, raw_display, comment = _decode_poly2(bytecode, pc)
            else:
                raw_display = f"0x{opcode:02x}"
                length = 1
                comment = ""
            if comment:
                lines.append(f"    POLYRAW {raw_display} ; {comment}")
            else:
                lines.append(f"    POLYRAW {raw_display}")
            pc += length
            continue

        if definition is None:
            lines.append(f"    DB 0x{opcode:02x}")
            pc += 1
            continue

        name = definition.name
        length = definition.length

        if name == "SETI":
            reg = bytecode[pc + 1]
            imm = _read_u16(bytecode, pc + 2)
            lines.append("    SETI [$%02x], 0x%04x" % (reg, imm))
        elif name in {"SETR", "ADDR", "SUBR"}:
            reg1 = bytecode[pc + 1]
            reg2 = bytecode[pc + 2]
            lines.append(f"    {name} [$%02x], [$%02x]" % (reg1, reg2))
        elif name in {"ADDI", "ANDI", "IORI", "LSLI", "LSRI"}:
            reg = bytecode[pc + 1]
            imm = _read_u16(bytecode, pc + 2)
            lines.append("    %s [$%02x], 0x%04x" % (name, reg, imm))
        elif name in {"CALL", "JUMP", "LOAD", "FADE"}:
            addr = _read_u16(bytecode, pc + 1)
            target = labels.get(addr, _format_operand(addr))
            lines.append(f"    {name} {target}")
        elif name == "DBRA":
            reg = bytecode[pc + 1]
            addr = _read_u16(bytecode, pc + 2)
            target = labels.get(addr, _format_operand(addr))
            lines.append("    DBRA [$%02x], %s" % (reg, target))
        elif name == "START":
            thread_id = bytecode[pc + 1]
            addr = _read_u16(bytecode, pc + 2)
            target = labels.get(addr, _format_operand(addr))
            lines.append(f"    START 0x{thread_id:02x}, {target}")
        elif name == "RESET":
            begin = bytecode[pc + 1]
            end = bytecode[pc + 2]
            state = bytecode[pc + 3]
            lines.append(f"    RESET 0x{begin:02x}, 0x{end:02x}, 0x{state:02x}")
        elif name == "PAGE":
            page = bytecode[pc + 1]
            lines.append(f"    PAGE 0x{page:02x}")
        elif name == "FILL":
            dst = bytecode[pc + 1]
            color = bytecode[pc + 2]
            lines.append(f"    FILL 0x{dst:02x}, 0x{color:02x}")
        elif name == "COPY":
            dst = bytecode[pc + 1]
            src = bytecode[pc + 2]
            lines.append(f"    COPY 0x{dst:02x}, 0x{src:02x}")
        elif name == "SHOW":
            lines.append(f"    SHOW 0x{bytecode[pc + 1]:02x}")
        elif name == "PRINT":
            string = _read_u16(bytecode, pc + 1)
            x = bytecode[pc + 3]
            y = bytecode[pc + 4]
            color = bytecode[pc + 5]
            lines.append(f"    PRINT 0x{string:04x}, 0x{x:02x}, 0x{y:02x}, 0x{color:02x}")
        elif name == "SOUND":
            sid = _read_u16(bytecode, pc + 1)
            freq = bytecode[pc + 3]
            vol = bytecode[pc + 4]
            channel = bytecode[pc + 5]
            lines.append(f"    SOUND 0x{sid:04x}, 0x{freq:02x}, 0x{vol:02x}, 0x{channel:02x}")
        elif name == "MUSIC":
            index = bytecode[pc + 1]
            mid = _read_u16(bytecode, pc + 2)
            delay = _read_u16(bytecode, pc + 4)
            pos = bytecode[pc + 6]
            lines.append(f"    MUSIC 0x{index:02x}, 0x{mid:04x}, 0x{delay:04x}, 0x{pos:02x}")
        else:
            lines.append(f"    {name}")

        pc += length

    return lines


def disassemble(bytecode: bytes) -> List[str]:
    labels = _collect_labels(bytecode)
    return _decode(bytecode, labels)


def main() -> int:
    parser = argparse.ArgumentParser(description="Disassemble Another World bytecode")
    parser.add_argument("input", type=Path, help="Path to bytecode binary")
    parser.add_argument("--output", type=Path, help="Where to write assembly output (defaults to stdout)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s: %(message)s")

    bytecode = args.input.read_bytes()
    lines = disassemble(bytecode)
    text = "\n".join(lines) + "\n"

    if args.output:
        args.output.write_text(text, encoding="utf-8")
        logging.info("Wrote disassembly to %s", args.output)
    else:
        print(text)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())


