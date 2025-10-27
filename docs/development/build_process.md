# Build Process and Platform Support

## Overview

The Another World Interpreter supports multiple build targets with a unified build system. The project uses Makefiles for compilation and a shell script for convenient building across different platforms.

## Supported Platforms

### Linux (Native)
- **Target**: Native Linux executable
- **Compiler**: GCC/G++ (C++14 standard)
- **Libraries**: SDL2, zlib
- **Output**: `bin/another-world.bin`

### WebAssembly (WASM)
- **Target**: Web browser execution
- **Compiler**: Emscripten (emcc/em++)
- **Libraries**: SDL2, zlib (via Emscripten ports)
- **Output**: `bin/another-world.html` + WASM files

## Prerequisites

### Linux Build Requirements

#### Debian/Ubuntu
```bash
sudo apt-get install build-essential libsdl2-dev zlib1g-dev
```

#### Fedora/RHEL
```bash
sudo dnf install gcc-c++ SDL2-devel zlib-devel
```

#### Arch Linux
```bash
sudo pacman -S base-devel sdl2 zlib
```

### WASM Build Requirements

#### Install Emscripten
```bash
# Download and install Emscripten
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install latest
./emsdk activate latest
source ./emsdk_env.sh
```

#### Verify Installation
```bash
emcc --version
em++ --version
```

## Build System

### Makefiles

The project uses separate Makefiles for each platform:

#### `Makefile.linux`
```makefile
# Compiler settings
CC       = gcc
CXX      = g++
CFLAGS   = -std=c99 -O2 -g -Wall -pthread -fstack-protector-strong
CXXFLAGS = -std=c++14 -O2 -g -Wall -pthread -fstack-protector-strong

# Libraries
LDADD = -lSDL2 -lz

# Output
PROGRAM = bin/another-world.bin
```

#### `Makefile.wasm`
```makefile
# Compiler settings
CC       = emcc
CXX      = em++
CFLAGS   = -std=c99 -O2 -Wall -sUSE_SDL=2 -sUSE_ZLIB=1
CXXFLAGS = -std=c++14 -O2 -Wall -sUSE_SDL=2 -sUSE_ZLIB=1

# Emscripten-specific flags
LDFLAGS = --use-preload-plugins --preload-file share/another-world/...

# Output
PROGRAM = bin/another-world.html
```

### Build Script

The `build.sh` script provides a unified interface:

```bash
#!/bin/sh
# Usage: build.sh [TARGET]
# Targets: linux, wasm, clean, help
```

#### Script Features
- **Parallel Compilation**: Uses `nproc` for optimal build speed
- **Automatic Cleanup**: Cleans before building
- **Error Handling**: Exits on build failures
- **Help System**: Built-in usage information

## Build Commands

### Quick Build (Recommended)

#### Linux
```bash
./build.sh linux
```

#### WASM
```bash
./build.sh wasm
```

### Manual Build

#### Linux
```bash
make -f Makefile.linux clean
make -f Makefile.linux -j$(nproc)
```

#### WASM
```bash
make -f Makefile.wasm clean
make -f Makefile.wasm -j$(nproc)
```

### Clean Build
```bash
./build.sh clean
# or
make -f Makefile.linux clean
make -f Makefile.wasm clean
```

## Build Process Details

### Compilation Steps

1. **Clean Previous Build**
   - Remove object files (`src/*.o`)
   - Remove output binaries

2. **Compile Source Files**
   - Compile each `.cc` file to `.o` object file
   - Apply platform-specific compiler flags
   - Use parallel compilation (`-j` flag)

3. **Link Final Binary**
   - Link all object files with required libraries
   - Apply platform-specific linker flags
   - Generate final executable/web files

### Source Files Compilation Order

```
src/main.cc          -> src/main.o
src/logger.cc        -> src/logger.o
src/bytekiller.cc    -> src/bytekiller.o
src/file.cc          -> src/file.o
src/intern.cc        -> src/intern.o
src/data.cc          -> src/data.o
src/engine.cc        -> src/engine.o
src/backend.cc       -> src/backend.o
src/resources.cc     -> src/resources.o
src/video.cc         -> src/video.o
src/audio.cc         -> src/audio.o
src/mixer.cc         -> src/mixer.o
src/sound.cc         -> src/sound.o
src/music.cc         -> src/music.o
src/input.cc         -> src/input.o
src/vm.cc            -> src/vm.o
```

### Platform-Specific Build Details

#### Linux Build
- **Compiler**: GCC 7+ with C++14 support
- **Optimization**: `-O2` for performance
- **Debugging**: `-g` for debug symbols
- **Security**: `-fstack-protector-strong`
- **Threading**: `-pthread` for multi-threading support
- **Libraries**: Native SDL2 and zlib libraries

#### WASM Build
- **Compiler**: Emscripten 3.0+
- **Optimization**: `-O2` for size optimization
- **Libraries**: Emscripten ports for SDL2 and zlib
- **Preloading**: Game data files embedded in WASM
- **Debugging**: Disabled (`NDEBUG` forced)

## Output Files

### Linux Build Output
```
bin/
├── another-world.bin    # Native Linux executable
└── share/another-world/ # Game data directory
```

### WASM Build Output
```
bin/
├── another-world.html   # Web page with embedded game
├── another-world.wasm   # WebAssembly binary
├── another-world.js     # JavaScript glue code
├── another-world.data   # Preloaded game data
└── share/another-world/ # Game data directory
```

## Game Data Setup

### Required Game Files

The original game data files must be copied to `share/another-world/`:

```bash
# Copy from original game installation
cp /path/to/original/game/BANK* share/another-world/
cp /path/to/original/game/MEMLIST.BIN share/another-world/
cp /path/to/original/game/CONFIG.* share/another-world/
cp /path/to/original/game/VOL.* share/another-world/
cp /path/to/original/game/MUSIC share/another-world/
cp /path/to/original/game/LOGO share/another-world/
cp /path/to/original/game/TABVOL.bin share/another-world/
```

### File Descriptions
- **BANK01-BANK0D**: Compressed game resource banks
- **MEMLIST.BIN**: Memory layout and resource index
- **CONFIG.dat/.lng**: Game configuration and localization
- **VOL.1-VOL.end**: Game volume files
- **MUSIC**: Music data
- **LOGO**: Logo graphics
- **TABVOL.bin**: Volume table for audio

## Running the Game

### Linux
```bash
./bin/another-world.bin
```

### WASM (Web Browser)
```bash
emrun bin/another-world.html
# or open bin/another-world.html in a web browser
```

## Debugging and Development

### Debug Builds

#### Enable Debug Mode
```bash
# Build with debug symbols
make -f Makefile.linux CXXFLAGS="-std=c++14 -O0 -g -Wall"

# Run with debug output
./bin/another-world.bin --debug-all
```

#### Subsystem Debugging
```bash
# Debug specific subsystems
./bin/another-world.bin --debug-engine
./bin/another-world.bin --debug-video
./bin/another-world.bin --debug-audio
./bin/another-world.bin --debug-vm
```

### Development Workflow

1. **Edit Source Code**: Modify files in `src/`
2. **Build**: Run `./build.sh linux` or `./build.sh wasm`
3. **Test**: Execute the game and verify functionality
4. **Debug**: Use appropriate debug flags for troubleshooting
5. **Iterate**: Repeat the cycle as needed

## Troubleshooting

### Common Build Issues

#### Missing Dependencies
```bash
# Error: SDL2 not found
sudo apt-get install libsdl2-dev

# Error: zlib not found
sudo apt-get install zlib1g-dev
```

#### Compiler Issues
```bash
# Error: C++14 not supported
# Update to GCC 5+ or use -std=c++11
```

#### Emscripten Issues
```bash
# Error: emcc not found
source /path/to/emsdk/emsdk_env.sh

# Error: WASM build fails
# Ensure Emscripten is properly activated
```

### Runtime Issues

#### Missing Game Data
```bash
# Error: Cannot find game data
# Ensure all required files are in share/another-world/
```

#### Permission Issues
```bash
# Error: Permission denied
chmod +x bin/another-world.bin
```

## Performance Considerations

### Linux Build
- **Optimization**: Use `-O2` for release builds
- **Debugging**: Use `-O0 -g` for development
- **Parallel Builds**: Use `-j$(nproc)` for faster compilation

### WASM Build
- **Size Optimization**: Emscripten automatically optimizes for size
- **Preloading**: Game data is embedded for faster loading
- **Browser Compatibility**: Tested on modern browsers

## Future Platform Support

### Potential Targets
- **Windows**: Native Windows port with Visual Studio
- **macOS**: Native macOS port with Xcode
- **Mobile**: iOS/Android ports with appropriate frameworks
- **Console**: Modern console ports

### Adding New Platforms
1. Create new `Makefile.platform`
2. Implement platform-specific backend
3. Update build script
4. Test and document

This build system provides a robust foundation for cross-platform development while maintaining simplicity and ease of use.
