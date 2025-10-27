# Platform Support

## Overview

This document describes the platform support for the Another World Interpreter, including supported platforms, platform-specific features, and implementation details. The interpreter is designed for cross-platform compatibility while maintaining identical game behavior.

## Supported Platforms

### Linux (Native)
**Status**: Fully Supported
**Target**: Native Linux executable
**Compiler**: GCC/G++ (C++14 standard)
**Libraries**: SDL2, zlib
**Output**: `bin/another-world.bin`

#### Features
- **Full Functionality**: Complete game functionality
- **Debug Support**: Full debugging capabilities
- **Performance**: Native performance
- **Audio**: High-quality audio output
- **Input**: Responsive input handling

#### Requirements
```bash
# Required packages
build-essential    # GCC compiler suite
libsdl2-dev        # SDL2 development headers
zlib1g-dev         # zlib compression library
```

#### Build Process
```bash
# Build Linux version
make -f Makefile.linux
# or
./build.sh linux
```

#### Runtime
```bash
# Run Linux version
./bin/another-world.bin
```

### WebAssembly (WASM)
**Status**: Fully Supported
**Target**: Web browser execution
**Compiler**: Emscripten (emcc/em++)
**Libraries**: SDL2, zlib (via Emscripten ports)
**Output**: `bin/another-world.html` + WASM files

#### Features
- **Browser Compatibility**: Runs in modern web browsers
- **Preloaded Data**: Game data embedded in WASM
- **Audio**: Web Audio API integration
- **Input**: Browser input handling
- **Performance**: Optimized for web execution

#### Requirements
```bash
# Required tools
emscripten          # WebAssembly toolchain
```

#### Build Process
```bash
# Build WASM version
make -f Makefile.wasm
# or
./build.sh wasm
```

#### Runtime
```bash
# Run WASM version
emrun bin/another-world.html
# or open bin/another-world.html in a web browser
```

## Platform-Specific Implementations

### Linux Backend (SDL2Backend)

#### Implementation
```cpp
class SDL2Backend : public Backend {
private:
    SDL_Window* _window;        // SDL2 window
    SDL_Renderer* _renderer;    // SDL2 renderer
    SDL_Texture* _texture;      // SDL2 texture
    SDL_AudioDeviceID _audioDevice; // Audio device
    
public:
    auto start() -> void override;
    auto stop() -> void override;
    auto getTicks() -> uint32_t override;
    auto processEvents(Controls& controls) -> void override;
    auto updateScreen(...) -> void override;
    auto startAudio(AudioCallback callback, void* userdata) -> void override;
};
```

#### Features
- **Hardware Acceleration**: Uses hardware-accelerated rendering
- **Audio Device**: Direct audio device access
- **Event Handling**: Native event processing
- **Timer Support**: High-resolution timers
- **Window Management**: Full window control

#### Performance Characteristics
- **Frame Rate**: 60 FPS target
- **Audio Latency**: ~20ms
- **Input Latency**: ~16ms
- **Memory Usage**: ~4-6MB

### WebAssembly Backend (EmscriptenBackend)

#### Implementation
```cpp
class EmscriptenBackend : public Backend {
private:
    EMSCRIPTEN_WEBGL_CONTEXT_HANDLE _glContext; // WebGL context
    uint32_t _canvasWidth;      // Canvas width
    uint32_t _canvasHeight;     // Canvas height
    
public:
    auto start() -> void override;
    auto stop() -> void override;
    auto getTicks() -> uint32_t override;
    auto processEvents(Controls& controls) -> void override;
    auto updateScreen(...) -> void override;
    auto startAudio(AudioCallback callback, void* userdata) -> void override;
};
```

#### Features
- **WebGL Rendering**: Uses WebGL for graphics
- **Web Audio**: Web Audio API integration
- **Canvas Management**: HTML5 canvas integration
- **Event Handling**: Browser event processing
- **Preloaded Data**: Embedded game data

#### Performance Characteristics
- **Frame Rate**: 60 FPS target (browser-dependent)
- **Audio Latency**: ~50ms (browser-dependent)
- **Input Latency**: ~33ms (browser-dependent)
- **Memory Usage**: ~8-12MB (browser-dependent)

## Platform Abstraction

### Backend Interface
The backend system provides a unified interface for platform-specific operations:

```cpp
class Backend : public SubSystem {
public:
    // Timing operations
    virtual auto getTicks() -> uint32_t = 0;
    virtual auto sleepFor(uint32_t delay) -> void = 0;
    virtual auto sleepUntil(uint32_t ticks) -> void = 0;
    
    // Event processing
    virtual auto processEvents(Controls& controls) -> void = 0;
    
    // Display operations
    virtual auto updateScreen(const Page& page, const Page& page0, const Page& page1, const Page& page2, const Page& page3, const Palette& palette) -> void = 0;
    
    // Audio operations
    virtual auto startAudio(AudioCallback callback, void* userdata) -> void = 0;
    virtual auto stopAudio() -> void = 0;
    virtual auto getAudioSampleRate() -> uint32_t = 0;
    
    // Timer operations
    virtual auto addTimer(uint32_t delay, TimerCallback callback, void* data) -> int = 0;
    virtual auto removeTimer(int timerId) -> void = 0;
};
```

### Backend Creation
```cpp
auto Backend::create(Engine& engine) -> Backend* {
    #ifdef __EMSCRIPTEN__
        return new EmscriptenBackend(engine);
    #else
        return new SDL2Backend(engine);
    #endif
}
```

## Platform-Specific Features

### Linux Features

#### Native Performance
- **Direct Hardware Access**: Direct access to hardware resources
- **Optimized Rendering**: Hardware-accelerated graphics
- **Low Latency Audio**: Direct audio device access
- **Responsive Input**: Native input handling

#### Debugging Support
- **Full Debugging**: Complete debugging capabilities
- **GDB Support**: Source-level debugging
- **Valgrind Support**: Memory debugging
- **AddressSanitizer**: Memory error detection

#### System Integration
- **File System**: Direct file system access
- **Process Management**: Native process control
- **Memory Management**: Native memory allocation
- **Threading**: Native threading support

### WebAssembly Features

#### Browser Integration
- **HTML5 Canvas**: Canvas-based rendering
- **Web Audio API**: Browser audio support
- **Event Handling**: Browser event processing
- **Local Storage**: Browser storage support

#### Performance Optimization
- **Preloaded Data**: Embedded game data
- **Optimized Compilation**: Emscripten optimizations
- **Memory Management**: WebAssembly memory model
- **Garbage Collection**: Automatic memory management

#### Security
- **Sandboxed Execution**: Browser security model
- **No File System Access**: Limited file access
- **Network Restrictions**: Controlled network access
- **Memory Protection**: WebAssembly memory protection

## Build System

### Linux Build

#### Makefile Configuration
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

#### Build Process
```bash
# Clean build
make -f Makefile.linux clean

# Build
make -f Makefile.linux -j$(nproc)

# Install dependencies
sudo apt-get install build-essential libsdl2-dev zlib1g-dev
```

### WebAssembly Build

#### Makefile Configuration
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

#### Build Process
```bash
# Clean build
make -f Makefile.wasm clean

# Build
make -f Makefile.wasm -j$(nproc)

# Install Emscripten
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install latest
./emsdk activate latest
source ./emsdk_env.sh
```

## Testing and Validation

### Cross-Platform Testing

#### Automated Testing
```bash
# Test Linux build
./build.sh linux
./bin/another-world.bin --debug-all

# Test WASM build
./build.sh wasm
emrun bin/another-world.html
```

#### Manual Testing
- **Functionality**: Test all game features
- **Performance**: Monitor frame rate and performance
- **Audio**: Verify audio quality and synchronization
- **Input**: Test all input controls
- **Graphics**: Verify visual quality and rendering

### Compatibility Testing

#### Game Data Compatibility
- **Original Data**: Test with original game data
- **Resource Loading**: Verify resource loading
- **Data Integrity**: Check data integrity
- **Format Support**: Test all supported formats

#### Platform Compatibility
- **Linux Distributions**: Test on various Linux distributions
- **Web Browsers**: Test on different web browsers
- **Hardware**: Test on different hardware configurations
- **Performance**: Verify performance across platforms

## Future Platform Support

### Potential Platforms

#### Windows
**Status**: Planned
**Target**: Native Windows executable
**Compiler**: Visual Studio/MSVC
**Libraries**: SDL2, zlib
**Features**: DirectX integration, Windows-specific optimizations

#### macOS
**Status**: Planned
**Target**: Native macOS executable
**Compiler**: Xcode/Clang
**Libraries**: SDL2, zlib
**Features**: Metal integration, macOS-specific optimizations

#### Mobile Platforms
**Status**: Under Consideration
**Target**: iOS/Android
**Compiler**: Platform-specific toolchains
**Libraries**: Platform-specific libraries
**Features**: Touch input, mobile-optimized UI

#### Console Platforms
**Status**: Under Consideration
**Target**: Modern consoles
**Compiler**: Platform-specific toolchains
**Libraries**: Platform-specific libraries
**Features**: Console-specific optimizations

### Adding New Platforms

#### Implementation Steps
1. **Create Backend**: Implement Backend interface
2. **Platform Integration**: Integrate with platform APIs
3. **Build System**: Add platform-specific build configuration
4. **Testing**: Test and validate platform implementation
5. **Documentation**: Document platform-specific features

#### Backend Implementation
```cpp
class NewPlatformBackend : public Backend {
public:
    NewPlatformBackend(Engine& engine);
    
    // Implement all virtual methods
    virtual auto getTicks() -> uint32_t override;
    virtual auto processEvents(Controls& controls) -> void override;
    virtual auto updateScreen(...) -> void override;
    virtual auto startAudio(AudioCallback callback, void* userdata) -> void override;
    // ... other methods
};
```

#### Build Configuration
```makefile
# Platform-specific Makefile
Makefile.newplatform

# Compiler settings
CC       = newplatform-cc
CXX      = newplatform-c++
CFLAGS   = -std=c99 -O2 -Wall
CXXFLAGS = -std=c++14 -O2 -Wall

# Libraries
LDADD = -lplatform-sdl2 -lplatform-zlib

# Output
PROGRAM = bin/another-world.newplatform
```

## Performance Considerations

### Platform-Specific Optimizations

#### Linux Optimizations
- **Compiler Optimizations**: Use -O2 or -O3
- **Hardware Acceleration**: Enable hardware acceleration
- **Memory Management**: Optimize memory allocation
- **Threading**: Use multi-threading where appropriate

#### WebAssembly Optimizations
- **Size Optimization**: Minimize WASM file size
- **Preloading**: Preload game data
- **Memory Management**: Optimize memory usage
- **Browser Compatibility**: Ensure browser compatibility

### Performance Monitoring

#### Metrics Collection
```cpp
class PerformanceMonitor {
private:
    uint32_t _frameCount;
    uint32_t _totalTime;
    uint32_t _vmTime;
    uint32_t _videoTime;
    uint32_t _audioTime;
    
public:
    auto collectMetrics() -> void {
        // Collect performance metrics
        _frameCount++;
        _totalTime += getFrameTime();
        _vmTime += getVMTime();
        _videoTime += getVideoTime();
        _audioTime += getAudioTime();
    }
    
    auto reportMetrics() -> void {
        if(_frameCount % 60 == 0) {
            log_debug("Performance: FPS=%.1f, VM=%.1f%%, Video=%.1f%%, Audio=%.1f%%",
                      getFPS(), getVMPercentage(), getVideoPercentage(), getAudioPercentage());
        }
    }
};
```

## Troubleshooting

### Common Issues

#### Linux Issues
- **Missing Dependencies**: Install required packages
- **Audio Issues**: Check audio device configuration
- **Graphics Issues**: Verify graphics driver support
- **Performance Issues**: Check system resources

#### WebAssembly Issues
- **Browser Compatibility**: Use supported browsers
- **Audio Issues**: Check Web Audio API support
- **Performance Issues**: Check browser performance
- **Loading Issues**: Verify preloaded data

### Debugging Platform Issues

#### Platform-Specific Debugging
```cpp
// Platform detection
#ifdef __EMSCRIPTEN__
    log_debug("Running on WebAssembly platform");
#else
    log_debug("Running on native platform");
#endif

// Platform-specific debugging
auto debugPlatform() -> void {
    #ifdef __EMSCRIPTEN__
        debugWebAssembly();
    #else
        debugNative();
    #endif
}
```

#### Performance Debugging
```cpp
auto debugPerformance() -> void {
    log_debug("Platform: %s", getPlatformName());
    log_debug("Frame rate: %.1f FPS", getFrameRate());
    log_debug("Memory usage: %zu bytes", getMemoryUsage());
    log_debug("Audio latency: %d ms", getAudioLatency());
}
```

This platform support documentation provides comprehensive information about the Another World Interpreter's cross-platform capabilities, enabling effective development and deployment across different platforms.
