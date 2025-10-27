# Bytecode Reference

This document provides a comprehensive reference for the Another World virtual machine bytecode instructions.

## Overview

The Another World VM uses a custom bytecode instruction set with 27 different opcodes. Each instruction is encoded as a single byte, followed by its operands.

## Instruction Format

All instructions follow this general format:
```
[opcode] [operand1] [operand2] [operand3] ...
```

Where:
- `opcode`: 8-bit instruction code
- `operands`: Variable number of 8-bit or 16-bit values depending on instruction

## Instruction Set

### Arithmetic Operations

#### SETI - Set Immediate
```assembly
SETI reg, immediate_value
```
**Description**: Sets a register to an immediate value.
**Opcode**: `0x00`
**Operands**:
- `reg`: Register index (8-bit)
- `immediate_value`: 16-bit immediate value

**Example**:
```assembly
SETI 0x20, 0x1234  ; Set register 32 to value 4660
```

#### SETR - Set Register from Register
```assembly
SETR reg_dst, reg_src
```
**Description**: Copies the value from one register into another.
**Opcode**: `0x01`
**Operands**: 
- `reg_dst`: Destination register index (8-bit)
- `reg_src`: Source register index (8-bit)

**Example**:
```assembly
SETR 0x10, 0x42    ; Set register 16 to value 66
```

#### ADDR - Add Register
```assembly
ADDR reg1, reg2
```
**Description**: Adds two registers and stores result in first register.
**Opcode**: `0x02`
**Operands**:
- `reg1`: Destination register (8-bit)
- `reg2`: Source register (8-bit)

**Example**:
```assembly
ADDR 0x10, 0x20    ; Add register 32 to register 16
```

#### ADDI - Add Immediate
```assembly
ADDI reg, immediate_value
```
**Description**: Adds immediate value to register.
**Opcode**: `0x03`
**Operands**:
- `reg`: Register index (8-bit)
- `immediate_value`: 16-bit immediate value

**Example**:
```assembly
ADDI 0x10, 0x0100  ; Add 256 to register 16
```

#### SUBR - Subtract Register
```assembly
SUBR reg1, reg2
```
**Description**: Subtracts second register from first register.
**Opcode**: `0x13`
**Operands**:
- `reg1`: Destination register (8-bit)
- `reg2`: Source register (8-bit)

**Example**:
```assembly
SUBR 0x10, 0x20    ; Subtract register 32 from register 16
```

#### ANDI - AND Immediate
```assembly
ANDI reg, immediate_value
```
**Description**: Performs bitwise AND with immediate value.
**Opcode**: `0x14`
**Operands**:
- `reg`: Register index (8-bit)
- `immediate_value`: 16-bit immediate value

**Example**:
```assembly
ANDI 0x10, 0xFF00  ; AND register 16 with 0xFF00
```

#### IORI - OR Immediate
```assembly
IORI reg, immediate_value
```
**Description**: Performs bitwise OR with immediate value.
**Opcode**: `0x15`
**Operands**:
- `reg`: Register index (8-bit)
- `immediate_value`: 16-bit immediate value

**Example**:
```assembly
IORI 0x10, 0x00FF  ; OR register 16 with 0x00FF
```

#### LSLI - Left Shift Immediate
```assembly
LSLI reg, shift_count
```
**Description**: Left shifts register by immediate value.
**Opcode**: `0x16`
**Operands**:
- `reg`: Register index (8-bit)
- `shift_count`: Shift count (16-bit)

**Example**:
```assembly
LSLI 0x10, 0x0004  ; Left shift register 16 by 4 bits
```

#### LSRI - Right Shift Immediate
```assembly
LSRI reg, shift_count
```
**Description**: Right shifts register by immediate value.
**Opcode**: `0x17`
**Operands**:
- `reg`: Register index (8-bit)
- `shift_count`: Shift count (16-bit)

**Example**:
```assembly
LSRI 0x10, 0x0004  ; Right shift register 16 by 4 bits
```

### Control Flow

#### CALL - Function Call
```assembly
CALL address
```
**Description**: Calls function at specified address.
**Opcode**: `0x04`
**Operands**:
- `address`: 16-bit function address

**Example**:
```assembly
CALL 0x2000        ; Call function at address 0x2000
```

#### RET - Return
```assembly
RET
```
**Description**: Returns from function call.
**Opcode**: `0x05`
**Operands**: None

**Example**:
```assembly
RET               ; Return from function
```

#### YIELD - Yield Control
```assembly
YIELD
```
**Description**: Yields control to other threads.
**Opcode**: `0x06`
**Operands**: None

**Example**:
```assembly
YIELD              ; Yield control
```

#### JUMP - Unconditional Jump
```assembly
JUMP address
```
**Description**: Jumps to specified address.
**Opcode**: `0x07`
**Operands**:
- `address`: 16-bit jump target

**Example**:
```assembly
JUMP 0x1000        ; Jump to address 0x1000
```

#### START - Start Thread
```assembly
START thread_id, address
```
**Description**: Starts a new thread at specified address.
**Opcode**: `0x08`
**Operands**:
- `thread_id`: Thread ID (8-bit, 0-63)
- `address`: 16-bit thread start address

**Example**:
```assembly
START 0x01, 0x3000 ; Start thread 1 at address 0x3000
```

#### DBRA - Decrement and Branch
```assembly
DBRA reg, address
```
**Description**: Decrements register and branches if not zero.
**Opcode**: `0x09`
**Operands**:
- `reg`: Register index (8-bit)
- `address`: 16-bit branch target

**Example**:
```assembly
DBRA 0x10, 0x1000  ; Decrement register 16, branch if not zero
```

#### CJMP - Conditional Jump
```assembly
CJMP condition, reg, operand, address
```
**Description**: Compares a register against either another register or an
immediate value and jumps if the condition holds.  The comparison mode is
encoded in the variant byte written immediately after the opcode.
**Opcode**: `0x0A`
**Operands**:
- `condition`: Condition code (lower 3 bits of the variant byte)
- `reg`: Left-hand register operand (8-bit)
- `operand`: Either a register (if bit 7 of the variant is set), a 16-bit
  immediate (bit 6 set), or an 8-bit immediate (neither bit set)
- `address`: 16-bit jump target

**Condition Codes**:
- `0x00`: Equal (==)
- `0x01`: Not equal (!=)
- `0x02`: Greater than (>)
- `0x03`: Greater than or equal (>=)
- `0x04`: Less than (<)
- `0x05`: Less than or equal (<=)

**Example**:
```assembly
CJMP 0x00, 0x10, 0x1000  ; Jump if register 16 equals 0
```

### Thread Management

#### RESET - Reset Thread
```assembly
RESET begin, end, state
```
**Description**: Resets threads to initial state.
**Opcode**: `0x0C`
**Operands**:
- `begin`: Start thread ID (8-bit)
- `end`: End thread ID (8-bit)
- `state`: New state (8-bit)

**Example**:
```assembly
RESET 0x00, 0x0F, 0x00  ; Reset threads 0-15 to state 0
```

#### HALT - Halt Thread
```assembly
HALT
```
**Description**: Halts current thread.
**Opcode**: `0x11`
**Operands**: None

**Example**:
```assembly
HALT               ; Halt current thread
```

### Video Operations

#### FADE - Fade Effect
```assembly
FADE palette_id
```
**Description**: Performs screen fade effect.
**Opcode**: `0x0B`
**Operands**:
- `palette_id`: Palette identifier (16-bit)

**Example**:
```assembly
FADE 0x0100        ; Fade to palette 256
```

#### PAGE - Page Operations
```assembly
PAGE src
```
**Description**: Manipulates video pages.
**Opcode**: `0x0D`
**Operands**:
- `src`: Source page identifier (8-bit)

**Example**:
```assembly
PAGE 0x01          ; Select page 1
```

#### FILL - Fill Page
```assembly
FILL dst, color
```
**Description**: Fills page with specified color.
**Opcode**: `0x0E`
**Operands**:
- `dst`: Destination page (8-bit)
- `color`: Fill color (8-bit)

**Example**:
```assembly
FILL 0x01, 0x00    ; Fill page 1 with color 0
```

#### COPY - Copy Page
```assembly
COPY dst, src
```
**Description**: Copies one page to another.
**Opcode**: `0x0F`
**Operands**:
- `dst`: Destination page (8-bit)
- `src`: Source page (8-bit)

**Example**:
```assembly
COPY 0x01, 0x00    ; Copy page 0 to page 1
```

#### SHOW - Show Page
```assembly
SHOW src
```
**Description**: Displays specified page.
**Opcode**: `0x10`
**Operands**:
- `src`: Source page identifier (8-bit)

**Example**:
```assembly
SHOW 0x01          ; Show page 1
```

#### PRINT - Print Text
```assembly
PRINT string_id, x, y, color
```
**Description**: Prints text to screen.
**Opcode**: `0x12`
**Operands**:
- `string_id`: String identifier (16-bit)
- `x`: X coordinate (8-bit)
- `y`: Y coordinate (8-bit)
- `color`: Text color (8-bit)
**Total Size**: 6 bytes (opcode + 5 operand bytes)

**Example**:
```assembly
PRINT 0x0100, 0x64, 0x64, 0x0F ; Print string 256 at (100,100) in color 15
```

### Audio Operations

#### SOUND - Play Sound
```assembly
SOUND sound_id, frequency, volume, channel
```
**Description**: Plays sound effect.
**Opcode**: `0x18`
**Operands**:
- `sound_id`: Sound identifier (16-bit)
- `frequency`: Frequency (8-bit)
- `volume`: Volume level (8-bit)
- `channel`: Audio channel (8-bit)

**Example**:
```assembly
SOUND 0x0200, 0x01, 0x80, 0x01 ; Play sound 512, frequency 1, volume 128, channel 1
```

#### MUSIC - Play Music
```assembly
MUSIC track_index, music_id, delay, position
```
**Description**: Starts music playback.
**Opcode**: `0x1A`
**Operands**:
- `track_index`: Slot/index (8-bit)
- `music_id`: Music identifier (16-bit)
- `delay`: Delay between loop iterations (16-bit)
- `position`: Start pattern/position (8-bit)
**Total Size**: 7 bytes (opcode + 6 operand bytes)

**Example**:
```assembly
MUSIC 0x02, 0x0300, 0x0064, 0x00 ; Start track index 2, song 0x0300, delay 100, from start
```

### Resource Management

#### LOAD - Load Resource
```assembly
LOAD resource_id
```
**Description**: Loads game resource into memory.
**Opcode**: `0x19`
**Operands**:
- `resource_id`: 16-bit resource identifier

**Example**:
```assembly
LOAD 0x0100        ; Load resource 256
```

### Graphics Operations

### Polygon Opcodes

- `0x1B-0x3F`: Treated as invalid polygons by the VM.  The interpreter consumes
  only the opcode byte.
- `0x40-0x7F`: `op_poly1` – variable-length instructions.  Operand layout is
  determined by opcode flag bits controlling address offset, X/Y source (register
  vs immediate), zoom/buffer selection, etc.
- `0x80-0xFF`: `op_poly2` – similar variable-length decoding with a different
  flag interpretation.

Because the flag bits influence how many bytes are fetched, the tooling mirrors
the VM’s `op_poly1`/`op_poly2` logic at decode time and preserves the raw byte
stream via the `POLYRAW` directive for guaranteed round-trip fidelity.

## Opcode Summary

| Opcode | Instruction | Description |
|--------|-------------|-------------|
| 0x00 | SETI | Set immediate value |
| 0x01 | SETR | Set register value |
| 0x02 | ADDR | Add register to register |
| 0x03 | ADDI | Add immediate to register |
| 0x04 | CALL | Function call |
| 0x05 | RET | Return from function |
| 0x06 | YIELD | Yield control |
| 0x07 | JUMP | Unconditional jump |
| 0x08 | START | Start thread |
| 0x09 | DBRA | Decrement and branch |
| 0x0A | CJMP | Conditional jump |
| 0x0B | FADE | Fade effect |
| 0x0C | RESET | Reset threads |
| 0x0D | PAGE | Page operations |
| 0x0E | FILL | Fill page |
| 0x0F | COPY | Copy page |
| 0x10 | SHOW | Show page |
| 0x11 | HALT | Halt thread |
| 0x12 | PRINT | Print text |
| 0x13 | SUBR | Subtract register |
| 0x14 | ANDI | AND immediate |
| 0x15 | IORI | OR immediate |
| 0x16 | LSLI | Left shift immediate |
| 0x17 | LSRI | Right shift immediate |
| 0x18 | SOUND | Play sound |
| 0x19 | LOAD | Load resource |
| 0x1A | MUSIC | Play music |
| 0x1B-0x3F | POLY invalid | Invalid polygon opcode (consumes 1 byte) |
| 0x40-0x7F | POLY1 | Polygon type 1 (variable length) |
| 0x80-0xFF | POLY2 | Polygon type 2 (variable length) |

## Notes

- All addresses are 16-bit values
- Register indices are 8-bit values (0-255)
- Thread IDs are 8-bit values (0-63)
- Color values are 8-bit values (0-15 for palette indices)
- The VM supports up to 64 concurrent threads
- The VM has 256 registers (0x00-0xFF)
- The VM has a 256-element stack
