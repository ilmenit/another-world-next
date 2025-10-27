"""Opcode constants for the Another World virtual machine."""

OP_SETI = 0x00
OP_SETR = 0x01
OP_ADDR = 0x02
OP_ADDI = 0x03
OP_CALL = 0x04
OP_RET = 0x05
OP_YIELD = 0x06
OP_JUMP = 0x07
OP_START = 0x08
OP_DBRA = 0x09
OP_CJMP = 0x0A
OP_FADE = 0x0B
OP_RESET = 0x0C
OP_PAGE = 0x0D
OP_FILL = 0x0E
OP_COPY = 0x0F
OP_SHOW = 0x10
OP_HALT = 0x11
OP_PRINT = 0x12
OP_SUBR = 0x13
OP_ANDI = 0x14
OP_IORI = 0x15
OP_LSLI = 0x16
OP_LSRI = 0x17
OP_SOUND = 0x18
OP_LOAD = 0x19
OP_MUSIC = 0x1A

# Polygon opcodes start at 0x1B in the VM dispatcher. Values below 0x40
# trigger the invalid handler, values from 0x40-0x7F execute POLY1 and values
# from 0x80-0xFF execute POLY2.
OP_POLY_BEGIN = 0x1B
OP_POLY_TYPE1_START = 0x40
OP_POLY_TYPE2_START = 0x80
OP_POLY_MAX = 0xFF


OPCODE_NAMES = {
    OP_SETI: "SETI",
    OP_SETR: "SETR",
    OP_ADDR: "ADDR",
    OP_ADDI: "ADDI",
    OP_CALL: "CALL",
    OP_RET: "RET",
    OP_YIELD: "YIELD",
    OP_JUMP: "JUMP",
    OP_START: "START",
    OP_DBRA: "DBRA",
    OP_CJMP: "CJMP",
    OP_FADE: "FADE",
    OP_RESET: "RESET",
    OP_PAGE: "PAGE",
    OP_FILL: "FILL",
    OP_COPY: "COPY",
    OP_SHOW: "SHOW",
    OP_HALT: "HALT",
    OP_PRINT: "PRINT",
    OP_SUBR: "SUBR",
    OP_ANDI: "ANDI",
    OP_IORI: "IORI",
    OP_LSLI: "LSLI",
    OP_LSRI: "LSRI",
    OP_SOUND: "SOUND",
    OP_LOAD: "LOAD",
    OP_MUSIC: "MUSIC",
}

