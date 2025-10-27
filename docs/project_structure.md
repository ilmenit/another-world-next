# Project Structure

## Directory Organization

```
another-world-interpreter/
├── bin/                          # Build output directory
│   ├── another-world.bin        # Linux executable
│   ├── another-world.html       # WASM web version
│   ├── another-world.wasm       # WASM binary
│   ├── another-world.js         # WASM JavaScript glue
│   └── share/                   # Game data files
│       └── another-world/       # Original game data
│           ├── BANK01-BANK0D    # Game resource banks
│           ├── MEMLIST.BIN      # Memory layout file
│           ├── CONFIG.dat       # Game configuration
│           ├── CONFIG.lng       # Language configuration
│           ├── INTRO.exe        # Intro executable
│           ├── LOGO             # Logo data
│           ├── MUSIC           # Music data
│           ├── README.txt      # Game readme
│           ├── TABVOL.bin      # Volume table
│           └── VOL.1-VOL.end   # Volume files
├── docs/                        # Documentation directory
│   ├── README.md               # Main documentation index
│   ├── project_overview.md     # Project overview
│   ├── project_structure.md    # This file
│   ├── architecture/           # Architecture documentation
│   ├── game_systems/          # Game system documentation
│   ├── technical/             # Technical documentation
│   └── development/           # Development guides
├── share/                      # Shared resources
│   └── another-world/         # Game assets
│       ├── another-world.png  # Game screenshot
│       └── README.md          # Asset readme
├── src/                       # Source code directory
│   ├── main.cc/.h             # Main entry point
│   ├── config.h              # Build configuration
│   ├── logger.cc/.h          # Logging system
│   ├── bytekiller.cc/.h      # Data decompression
│   ├── file.cc/.h            # File I/O operations
│   ├── intern.h              # Common data structures
│   ├── data.cc/.h            # Data management
│   ├── engine.cc/.h          # Main game engine
│   ├── backend.cc/.h         # Platform abstraction
│   ├── resources.cc/.h       # Resource management
│   ├── video.cc/.h           # Video/graphics system
│   ├── audio.cc/.h           # Audio system
│   ├── mixer.cc/.h           # Audio mixing
│   ├── sound.cc/.h           # Sound effects
│   ├── music.cc/.h           # Music playback
│   ├── input.cc/.h           # Input handling
│   └── vm.cc/.h              # Virtual machine
├── build.sh                   # Build script
├── Makefile.linux            # Linux build configuration
├── Makefile.wasm             # WASM build configuration
├── README.md                 # Project readme
├── COPYING                   # GPL license
└── AUTHORS                   # Author credits
```

## Source Code Structure

### Core Architecture

The project follows a modular, component-based architecture with clear separation of concerns:

```
Engine (Main Controller)
├── Backend (Platform Abstraction)
│   ├── SDL2 Integration
│   ├── Event Processing
│   ├── Audio Callbacks
│   └── Timer Management
├── Resources (Data Management)
│   ├── File Loading
│   ├── Memory Management
│   ├── Resource Caching
│   └── Data Decompression
├── Video (Graphics System)
│   ├── Page Management
│   ├── Polygon Rendering
│   ├── Palette Handling
│   └── Bitmap Drawing
├── Audio (Sound System)
│   ├── Mixer
│   ├── Sound Effects
│   └── Music Playback
├── Input (Control System)
│   ├── Keyboard Input
│   ├── Control Mapping
│   └── Event Processing
└── VirtualMachine (Game Logic)
    ├── Bytecode Interpreter
    ├── Thread Management
    ├── Register Operations
    └── Instruction Execution
```

### File Descriptions

#### Main Entry Point
- **`main.cc/.h`**: Application entry point, command-line parsing, and main loop
- **`config.h`**: Build-time configuration options and feature flags

#### Core Systems
- **`engine.cc/.h`**: Main game engine coordinator and system integration
- **`backend.cc/.h`**: Platform abstraction layer for SDL2 integration
- **`intern.h`**: Common data structures, types, and constants

#### Data Management
- **`data.cc/.h`**: Core data structures and memory management
- **`file.cc/.h`**: File I/O operations and path management
- **`bytekiller.cc/.h`**: Data decompression (ByteKiller algorithm)
- **`resources.cc/.h`**: Resource loading, caching, and management

#### Graphics System
- **`video.cc/.h`**: Video rendering, page management, and polygon drawing

#### Audio System
- **`audio.cc/.h`**: Audio system coordinator
- **`mixer.cc/.h`**: Multi-channel audio mixing
- **`sound.cc/.h`**: Sound effect playback
- **`music.cc/.h`**: Music playback and sequencing

#### Input and Control
- **`input.cc/.h`**: Input handling and control mapping

#### Game Logic
- **`vm.cc/.h`**: Virtual machine bytecode interpreter and execution

#### Utilities
- **`logger.cc/.h`**: Logging system with subsystem-specific debugging

## Build System

### Makefiles

#### `Makefile.linux`
- **Compiler**: GCC/G++ with C++14 standard
- **Libraries**: SDL2, zlib
- **Flags**: Optimization (-O2), debugging (-g), warnings (-Wall)
- **Output**: `bin/another-world.bin`

#### `Makefile.wasm`
- **Compiler**: Emscripten (emcc/em++)
- **Libraries**: SDL2, zlib (via Emscripten ports)
- **Flags**: WebAssembly optimization, preloaded files
- **Output**: `bin/another-world.html` + WASM files

### Build Script

#### `build.sh`
- **Purpose**: Unified build interface
- **Targets**: `linux`, `wasm`, `clean`, `help`
- **Features**: Parallel compilation, automatic cleanup

### Dependencies

#### Linux Build
```bash
# Required packages
build-essential    # GCC compiler suite
libsdl2-dev        # SDL2 development headers
zlib1g-dev         # zlib compression library
```

#### WASM Build
```bash
# Required tools
emscripten          # WebAssembly toolchain
```

## Data Files

### Game Resources

The original game data files must be placed in `share/another-world/`:

- **BANK01-BANK0D**: Compressed game resource banks
- **MEMLIST.BIN**: Memory layout and resource index
- **CONFIG.dat/.lng**: Game configuration and localization
- **VOL.1-VOL.end**: Game volume files
- **MUSIC**: Music data
- **LOGO**: Logo graphics
- **TABVOL.bin**: Volume table for audio

### Asset Organization

```
share/another-world/
├── Game Data Files (from original game)
│   ├── BANK01-BANK0D    # Resource banks
│   ├── MEMLIST.BIN      # Memory layout
│   ├── CONFIG.*         # Configuration
│   ├── VOL.*            # Volume files
│   └── Other assets
└── Project Assets
    ├── another-world.png  # Screenshot
    └── README.md         # Asset documentation
```

## Compilation Process

### Linux Build
```bash
make -f Makefile.linux
# or
./build.sh linux
```

### WASM Build
```bash
make -f Makefile.wasm
# or
./build.sh wasm
```

### Clean Build
```bash
make -f Makefile.linux clean
make -f Makefile.wasm clean
# or
./build.sh clean
```

## Output Files

### Linux Build Output
- **`bin/another-world.bin`**: Native Linux executable
- **Object files**: `src/*.o` (temporary)

### WASM Build Output
- **`bin/another-world.html`**: Web page with embedded game
- **`bin/another-world.wasm`**: WebAssembly binary
- **`bin/another-world.js`**: JavaScript glue code
- **`bin/another-world.data`**: Preloaded game data

## Development Workflow

### Typical Development Cycle
1. **Edit Source**: Modify `.cc/.h` files in `src/`
2. **Build**: Run `./build.sh linux` or `./build.sh wasm`
3. **Test**: Execute `./bin/another-world.bin` or open HTML file
4. **Debug**: Use debug flags (`--debug-*`) for subsystem debugging
5. **Document**: Update documentation in `docs/`

### Debugging Support
- **Subsystem Debugging**: `--debug-engine`, `--debug-video`, etc.
- **Full Debug**: `--debug-all` for comprehensive logging
- **Quiet Mode**: `--quiet` for minimal output

## Platform-Specific Considerations

### Linux
- Uses native SDL2 libraries
- Direct file system access
- Full debugging support

### WebAssembly
- Preloaded game data files
- Limited debugging (NDEBUG forced)
- Browser-based execution
- Emscripten-specific optimizations

This structure provides a clean, maintainable codebase with clear separation between platform-specific and platform-independent code, making it easy to add new platforms or modify existing functionality.
