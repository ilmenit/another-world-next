# Virtual Machine System

## Overview

The Virtual Machine (VM) is the core component of the Another World interpreter, responsible for executing the game's bytecode and managing game logic. It implements a custom bytecode interpreter that was originally designed by Eric Chahi for cross-platform compatibility.

## Architecture

### Core Components

```
VirtualMachine
├── ByteCode Storage
│   └── Game bytecode data
├── Thread Management
│   ├── 64 concurrent threads
│   ├── Thread states and priorities
│   └── Context switching
├── Register System
│   ├── 256 16-bit registers
│   ├── Signed/unsigned operations
│   └── Special variables
├── Stack Operations
│   ├── 256-element stack
│   ├── Function calls
│   └── Local variables
└── Instruction Set
    ├── Arithmetic operations
    ├── Control flow
    ├── System calls
    └── Graphics operations
```

### Thread Model

The VM supports up to 64 concurrent threads, each with:

- **Thread ID**: Unique identifier (0-63)
- **Program Counter**: Current instruction pointer
- **State**: Running, paused, or halted
- **Yield Flag**: Cooperative multitasking control

### Register System

#### Special Variables
- **`VM_VARIABLE_RANDOM_SEED` (0x3c)**: Random number generator seed
- **`VM_VARIABLE_INPUT_KEY` (0xda)**: Current input key state
- **`VM_VARIABLE_HERO_POS_UP_DOWN` (0xe5)**: Hero vertical position
- **`VM_VARIABLE_MUSIC_MARK` (0xf4)**: Music synchronization marker
- **`VM_VARIABLE_SCROLL_Y` (0xf9)**: Screen scroll position
- **`VM_VARIABLE_HERO_ACTION` (0xfa)**: Hero action state
- **`VM_VARIABLE_HERO_POS_JUMP_DOWN` (0xfb)**: Hero jump/down position
- **`VM_VARIABLE_HERO_POS_LEFT_RIGHT` (0xfc)**: Hero horizontal position
- **`VM_VARIABLE_HERO_POS_MASK` (0xfd)**: Hero position mask
- **`VM_VARIABLE_HERO_ACTION_POS_MASK` (0xfe)**: Hero action position mask
- **`VM_VARIABLE_PAUSE_SLICES` (0xff)**: Pause timing control

## Instruction Set

### Arithmetic Operations

#### `op_seti` - Set Immediate
```assembly
SETI reg, immediate_value
```
Sets a register to an immediate value.

#### `op_setr` - Set Register
```assembly
SETR reg, value
```
Sets a register to a specific value.

#### `op_addr` - Add Register
```assembly
ADDR reg1, reg2
```
Adds two registers and stores result in first register.

#### `op_addi` - Add Immediate
```assembly
ADDI reg, immediate_value
```
Adds immediate value to register.

#### `op_subr` - Subtract Register
```assembly
SUBR reg1, reg2
```
Subtracts second register from first register.

#### `op_andi` - AND Immediate
```assembly
ANDI reg, immediate_value
```
Performs bitwise AND with immediate value.

#### `op_iori` - OR Immediate
```assembly
ORI reg, immediate_value
```
Performs bitwise OR with immediate value.

#### `op_lsli` - Left Shift Immediate
```assembly
LSLI reg, shift_count
```
Left shifts register by immediate value.

#### `op_lsri` - Right Shift Immediate
```assembly
LSRI reg, shift_count
```
Right shifts register by immediate value.

### Control Flow

#### `op_jump` - Unconditional Jump
```assembly
JUMP address
```
Jumps to specified address.

#### `op_cjmp` - Conditional Jump
```assembly
CJMP condition, address
```
Jumps to address if condition is true.

#### `op_dbra` - Decrement and Branch
```assembly
DBRA reg, address
```
Decrements register and branches if not zero.

#### `op_call` - Function Call
```assembly
CALL address
```
Calls function at specified address.

#### `op_ret` - Return
```assembly
RET
```
Returns from function call.

### Thread Management

#### `op_start` - Start Thread
```assembly
START thread_id, address
```
Starts a new thread at specified address.

#### `op_reset` - Reset Thread
```assembly
RESET thread_id
```
Resets thread to initial state.

#### `op_yield` - Yield Control
```assembly
YIELD
```
Yields control to other threads.

#### `op_halt` - Halt Thread
```assembly
HALT
```
Halts current thread.

### System Operations

#### `op_load` - Load Resource
```assembly
LOAD resource_id
```
Loads game resource into memory.

#### `op_fade` - Fade Effect
```assembly
FADE type, duration
```
Performs screen fade effect.

#### `op_page` - Page Operations
```assembly
PAGE operation, page_id
```
Manipulates video pages.

#### `op_fill` - Fill Page
```assembly
FILL page_id, color
```
Fills page with specified color.

#### `op_copy` - Copy Page
```assembly
COPY dest_page, src_page, scroll
```
Copies one page to another.

#### `op_show` - Show Page
```assembly
SHOW page_id
```
Displays specified page.

#### `op_print` - Print Text
```assembly
PRINT string_id, x, y, color
```
Prints text to screen.

#### `op_sound` - Play Sound
```assembly
SOUND sound_id, channel, volume, frequency
```
Plays sound effect.

#### `op_music` - Play Music
```assembly
MUSIC music_id, position, delay
```
Plays music track.

#### `op_poly1` - Draw Polygon Type 1
```assembly
POLY1 polygon_data, offset, x, y, zoom
```
Draws polygon with type 1 rendering.

#### `op_poly2` - Draw Polygon Type 2
```assembly
POLY2 polygon_data, offset, x, y, zoom
```
Draws polygon with type 2 rendering.

## Execution Model

### Main Loop

```cpp
auto VirtualMachine::run(Controls& controls) -> void
{
    // Process all active threads
    for(auto& thread : _threads) {
        if(thread.current_state == THREAD_RUNNING) {
            executeThread(thread, controls);
        }
    }
    
    // Handle thread state transitions
    updateThreadStates();
}
```

### Thread Execution

```cpp
auto executeThread(Thread& thread, Controls& controls) -> void
{
    // Fetch instruction
    uint8_t opcode = _bytecode[thread.current_pc];
    
    // Decode and execute
    switch(opcode) {
        case OP_SETR: op_setr(thread); break;
        case OP_SETI: op_seti(thread); break;
        case OP_ADDR: op_addr(thread); break;
        // ... other instructions
        default: op_invalid(thread); break;
    }
    
    // Update program counter
    if(!thread.yield) {
        thread.current_pc += instructionSize(opcode);
    }
}
```

### Cooperative Multitasking

The VM uses cooperative multitasking where threads voluntarily yield control:

1. **Thread Execution**: Each thread runs until it yields
2. **Yield Points**: Threads yield at specific instructions
3. **Context Switching**: VM switches to next thread
4. **Round Robin**: Threads are executed in order

## Memory Management

### Bytecode Storage

```cpp
struct ByteCode {
    const uint8_t* data;    // Bytecode data
    size_t size;           // Total size
    size_t offset;         // Current offset
};
```

### Stack Operations

```cpp
struct Stack {
    uint32_t array[256];   // Stack storage
    uint32_t index;        // Current stack pointer
};
```

### Register Operations

```cpp
struct Register {
    union {
        int16_t  s;        // Signed 16-bit
        uint16_t u;        // Unsigned 16-bit
    };
};
```

## Integration with Game Systems

### Engine Interface

The VM integrates with other game systems through the Engine:

```cpp
class VirtualMachine {
    Engine& _engine;  // Reference to main engine
    
    // System access methods
    auto getResource(uint16_t id) -> Resource*;
    auto playSound(uint16_t id, uint8_t channel, uint8_t volume, uint8_t frequency) -> void;
    auto drawPolygons(const uint8_t* buffer, uint16_t offset, const Point& point, uint16_t zoom) -> void;
    // ... other system calls
};
```

### Input Handling

The VM processes input through the Controls structure:

```cpp
struct Controls {
    bool up, down, left, right;  // Movement keys
    bool fire, run;              // Action keys
    bool pause, quit;            // System keys
    uint8_t key;                 // Current key code
};
```

## Performance Characteristics

### Execution Speed
- **Instruction Throughput**: ~1000-10000 instructions per frame
- **Thread Switching**: Minimal overhead due to cooperative multitasking
- **Memory Access**: Efficient register-based operations

### Memory Usage
- **Bytecode**: ~64KB typical game data
- **Registers**: 512 bytes (256 × 16-bit)
- **Stack**: 1KB (256 × 32-bit)
- **Threads**: ~2KB (64 × thread structure)

## Debugging Support

### Debug Output

```cpp
// Enable VM debugging
./another-world.bin --debug-vm

// Debug all systems
./another-world.bin --debug-all
```

### Debug Features
- **Instruction Tracing**: Log each executed instruction
- **Register Monitoring**: Track register values
- **Thread State**: Monitor thread execution
- **Performance Metrics**: Instruction counts and timing

## Bytecode Format

### Instruction Encoding

Most instructions follow this format:
```
[Opcode: 8 bits] [Operand1: 8 bits] [Operand2: 8 bits]
```

### Special Instructions

Some instructions have variable-length encoding:
- **Immediate Values**: 16-bit immediate operands
- **Addresses**: 16-bit jump targets
- **Resource IDs**: 16-bit resource identifiers

## Error Handling

### Invalid Instructions

```cpp
auto op_invalid(Thread& thread) -> void
{
    LOG_DEBUG("invalid opcode 0x%02x at pc 0x%04x", 
              thread.opcode, thread.current_pc);
    thread.current_state = THREAD_HALTED;
}
```

### Thread Errors

- **Stack Overflow**: Detected and handled gracefully
- **Invalid Jumps**: Prevented by bounds checking
- **Resource Errors**: Handled by resource system

## Historical Context

### Original Design (1991)

Eric Chahi designed the VM for:
- **Cross-platform Compatibility**: Single bytecode for all platforms
- **Efficient Execution**: Optimized for 16-bit processors
- **Modular Design**: Separated game logic from platform code

### Modern Implementation

This interpreter adds:
- **Modern C++**: Clean, maintainable code
- **Better Debugging**: Comprehensive logging and debugging
- **Performance**: Optimized for modern processors
- **Documentation**: Complete technical documentation

The Virtual Machine represents one of the earliest examples of game engine virtualization, demonstrating sophisticated software architecture that was ahead of its time in 1991.
