# Analytics System

The Analytics system provides comprehensive logging for analyzing Another World's behavior during execution. This is particularly useful for porting the game to other platforms like the 6502 Atari 800.

## Features

- **VM Opcode Logging**: Tracks all virtual machine instruction execution with program counter
- **Drawing Operations**: Logs polygon and pixel drawing operations
- **Frame Statistics**: Counts pixels drawn per frame for performance analysis
- **Function Call Tracking**: Optional logging of function calls and returns
- **Concise Format**: Human-readable log format without timestamps

## Log Format

The analytics log uses a simple, parseable format:

```
# Another World Analytics Log
# Format: [TYPE] [DATA]
# Types: OPCODE, FUNC_CALL, FUNC_RET, PIXEL, POLYGON, PAGE, FRAME
#
OPCODE 0x00 SETI PC=0x1234
OPCODE 0x40 POLY1 PC=0x5678 opcode=0x40
POLYGON x=100 y=50 zoom=256 color=15 points=4
PIXEL x=150 y=75 color=12
FRAME_START frame=1
FRAME_END frame=100 pixels=1500 total=150000
```

## Usage

The analytics system is automatically initialized when the Engine starts and logs to `analytics.log` (or `dumpdir/analytics.log` if dump directory is specified).

### Configuration

You can control what gets logged by modifying the Engine constructor:

```cpp
// Enable/disable different logging types
Analytics::getInstance().enableOpcodeLogging(true);
Analytics::getInstance().enableFunctionLogging(false);
Analytics::getInstance().enableDrawingLogging(true);
Analytics::getInstance().enableFrameStats(true);
```

### Manual Logging

You can also add custom logging throughout the codebase:

```cpp
// Log opcodes
LOG_OPCODE(0x12, "PRINT", pc);

// Log with parameters
LOG_OPCODE_PARAMS(0x40, "POLY1", pc, "x=100 y=50");

// Log function calls
LOG_FUNCTION_CALL("renderPolygon", "x=100 y=50 zoom=256");

// Log drawing operations
LOG_PIXEL_DRAW(150, 75, 12);
LOG_POLYGON_DRAW(100, 50, 256, 15, 4);

// Frame tracking
START_FRAME();
// ... frame processing ...
END_FRAME();
```

## Key Metrics for 6502 Port

The analytics system tracks several metrics crucial for porting to 6502:

1. **Opcode Frequency**: Which VM instructions are used most
2. **Drawing Patterns**: How polygons and pixels are drawn
3. **Frame Complexity**: Pixels per frame for performance optimization
4. **Memory Access Patterns**: Through opcode parameter analysis

## Log Analysis

The log file can be analyzed to understand:

- **Performance bottlenecks**: High pixel count frames
- **Drawing patterns**: Common polygon shapes and sizes
- **VM usage**: Most frequently executed opcodes
- **Memory requirements**: Resource loading patterns

This data is essential for optimizing the 6502 Atari 800 port.
