# Architecture Overview

## System Architecture

The Another World Interpreter follows a modular, component-based architecture that separates concerns and provides clean interfaces between systems. This design enables maintainability, extensibility, and cross-platform compatibility.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Main Entry Point                     │
│                         (main.cc)                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                      Engine                                  │
│                   (engine.cc/.h)                            │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │   Backend   │  Resources  │    Video    │    Audio    │  │
│  │ (backend.cc)│(resources.cc)│ (video.cc)  │ (audio.cc)  │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │    Input    │      VM     │   Logger    │    Data    │  │
│  │ (input.cc)  │   (vm.cc)   │(logger.cc)  │ (data.cc)  │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### Engine (Main Controller)
The Engine class serves as the central coordinator, managing all subsystems and providing a unified interface for game operations.

**Responsibilities:**
- System initialization and shutdown
- Inter-system communication
- Game loop coordination
- Resource management coordination

**Key Methods:**
```cpp
class Engine {
    auto main() -> void;                    // Main game loop
    auto initPart(uint16_t id) -> void;     // Initialize game part
    auto switchPalettes() -> void;          // Switch color palettes
    auto processVirtualMachine() -> void;   // Run VM execution
};
```

### Backend (Platform Abstraction)
The Backend provides platform-specific implementations for audio, video, input, and timing operations.

**Responsibilities:**
- SDL2 integration (Linux)
- WebAssembly integration (WASM)
- Platform-specific event handling
- Audio device management
- Timer management

**Key Methods:**
```cpp
class Backend {
    virtual auto getTicks() -> uint32_t = 0;
    virtual auto processEvents(Controls& controls) -> void = 0;
    virtual auto updateScreen(...) -> void = 0;
    virtual auto startAudio(AudioCallback callback, void* userdata) -> void = 0;
    virtual auto addTimer(uint32_t delay, TimerCallback callback, void* data) -> int = 0;
};
```

### Virtual Machine (Game Logic)
The VM executes the game's bytecode and manages game state, providing the core game logic engine.

**Responsibilities:**
- Bytecode interpretation
- Multi-threaded execution
- Register management
- System call handling

**Key Methods:**
```cpp
class VirtualMachine {
    auto run(Controls& controls) -> void;   // Execute VM
    auto setByteCode(const uint8_t* bytecode) -> void;
    auto getRegister(uint8_t index) const -> uint16_t;
    auto setRegister(uint8_t index, uint16_t value) -> void;
};
```

### Video System (Graphics)
The Video system handles all graphics rendering, including polygon-based character animation and page-based graphics.

**Responsibilities:**
- Polygon rendering
- Page management
- Palette handling
- Bitmap drawing
- Text rendering

**Key Methods:**
```cpp
class Video {
    auto selectPage(uint8_t dst) -> void;
    auto fillPage(uint8_t dst, uint8_t col) -> void;
    auto copyPage(uint8_t dst, uint8_t src, int16_t vscroll) -> void;
    auto drawPolygons(const uint8_t* buffer, uint16_t offset, const Point& point, uint16_t zoom) -> void;
};
```

### Audio System (Sound)
The Audio system provides comprehensive sound and music capabilities with multi-channel mixing.

**Responsibilities:**
- Multi-channel audio mixing
- Sound effect playback
- Music sequencing
- Audio device management

**Key Methods:**
```cpp
class Audio {
    auto playSound(uint16_t id, uint8_t channel, uint8_t volume, uint8_t frequency) -> void;
    auto playMusic(uint16_t id, uint8_t position, uint16_t delay) -> void;
    auto playChannel(uint8_t channel, const AudioSample& sample) -> void;
    auto setChannelVolume(uint8_t channel, uint8_t volume) -> void;
};
```

### Resource Management (Data)
The Resources system handles all game data loading, caching, and memory management.

**Responsibilities:**
- Game data loading
- Memory pool management
- Resource caching
- Part management
- Data decompression

**Key Methods:**
```cpp
class Resources {
    auto loadPart(uint16_t partId) -> void;
    auto loadResource(uint16_t resourceId) -> void;
    auto getResource(uint16_t resourceId) -> Resource*;
    auto getString(uint16_t stringId) -> const String*;
};
```

### Input System (Controls)
The Input system processes player input and provides a unified control interface.

**Responsibilities:**
- Keyboard input processing
- Control mapping
- Event handling
- Input state management

**Key Methods:**
```cpp
class Input {
    auto getControls() -> Controls&;
    auto isRunning() const -> bool;
    auto isPaused() const -> bool;
    auto isStopped() const -> bool;
};
```

## Data Flow Architecture

### Game Loop Data Flow

```
Input Events → Backend → Engine → VM → Game Logic
                                    ↓
Audio ← Engine ← Audio System ← VM Audio Calls
                                    ↓
Video ← Engine ← Video System ← VM Video Calls
                                    ↓
Display ← Backend ← Engine ← Video System
```

### Resource Loading Data Flow

```
File System → Resources → Memory Pool → Game Systems
                ↓
            Decompression → ByteKiller → Raw Data
                ↓
            Resource Cache → System Access
```

### Audio Processing Data Flow

```
VM Audio Calls → Audio System → Mixer → Audio Channels
                                    ↓
                                Backend → SDL2/WebAudio
```

## Design Patterns

### SubSystem Pattern
All major systems inherit from a common SubSystem base class, providing consistent lifecycle management:

```cpp
class SubSystem {
public:
    virtual auto start() -> void = 0;
    virtual auto reset() -> void = 0;
    virtual auto stop() -> void = 0;
    
protected:
    Engine& _engine;
    std::string _name;
};
```

### Factory Pattern
The Backend system uses a factory pattern for platform-specific implementations:

```cpp
auto Backend::create(Engine& engine) -> Backend* {
    #ifdef __EMSCRIPTEN__
        return new EmscriptenBackend(engine);
    #else
        return new SDL2Backend(engine);
    #endif
}
```

### Observer Pattern
The Engine coordinates between systems using a form of the observer pattern, where systems register for updates and notifications.

### Resource Pool Pattern
The Resources system uses a memory pool pattern for efficient memory management:

```cpp
class Resources {
private:
    uint8_t _buffer[TOTAL_SIZE];  // Fixed memory pool
    uint8_t* _bufptr;             // Current allocation pointer
    uint8_t* _bufend;             // End of pool
};
```

## System Interactions

### Engine ↔ Backend
- **Engine** requests platform operations (audio, video, input, timing)
- **Backend** provides platform-specific implementations
- **Interface**: Direct method calls through Engine's backend reference

### Engine ↔ VM
- **Engine** provides system access to VM
- **VM** executes game logic and makes system calls
- **Interface**: VM calls Engine methods for system operations

### Engine ↔ Video
- **Engine** coordinates video operations
- **Video** handles graphics rendering
- **Interface**: Engine calls Video methods for rendering operations

### Engine ↔ Audio
- **Engine** coordinates audio operations
- **Audio** handles sound and music
- **Interface**: Engine calls Audio methods for audio operations

### Engine ↔ Resources
- **Engine** requests resource loading
- **Resources** manages game data
- **Interface**: Engine calls Resources methods for data access

### Engine ↔ Input
- **Engine** processes input events
- **Input** manages control states
- **Interface**: Engine accesses Input control states

## Memory Architecture

### Memory Layout

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Memory                       │
├─────────────────────────────────────────────────────────────┤
│  Engine + SubSystems  │  ~1MB  │  Core game systems        │
├─────────────────────────────────────────────────────────────┤
│  Resource Pool        │  ~2MB  │  Game data storage        │
├─────────────────────────────────────────────────────────────┤
│  Video Pages          │  ~128KB│  4 × 320×200 pages        │
├─────────────────────────────────────────────────────────────┤
│  Audio Buffers        │  ~64KB │  Audio mixing buffers     │
├─────────────────────────────────────────────────────────────┤
│  VM Memory            │  ~32KB │  Registers, stack, etc.   │
├─────────────────────────────────────────────────────────────┤
│  System Memory        │  ~1MB  │  SDL2, system libraries  │
└─────────────────────────────────────────────────────────────┘
```

### Memory Management Strategy

1. **Fixed Pool Allocation**: Resources system uses a fixed memory pool
2. **Stack-based VM**: Virtual machine uses stack-based memory management
3. **Page-based Graphics**: Video system uses fixed-size page buffers
4. **Buffer Management**: Audio system uses circular buffers for mixing

## Threading Model

### Single-threaded Design
The interpreter uses a single-threaded design with cooperative multitasking:

- **Main Thread**: Handles all game systems
- **Cooperative Multitasking**: VM threads yield control voluntarily
- **Event-driven**: Systems respond to events and callbacks

### VM Threading
The Virtual Machine implements its own threading model:

```cpp
struct Thread {
    uint32_t thread_id;       // Thread identifier
    uint16_t current_pc;      // Program counter
    uint8_t  current_state;   // Thread state
    bool     yield;           // Yield flag
};
```

## Error Handling

### Error Propagation
The system uses a combination of error handling strategies:

1. **Return Values**: Functions return success/failure status
2. **Exceptions**: Critical errors throw exceptions
3. **Logging**: All errors are logged with appropriate detail
4. **Graceful Degradation**: Systems continue operating when possible

### Error Recovery
- **Resource Errors**: Fallback to default resources
- **Audio Errors**: Continue without audio
- **Video Errors**: Fallback to basic rendering
- **Input Errors**: Continue with limited input

## Performance Characteristics

### System Performance
- **Frame Rate**: 60 FPS target
- **Memory Usage**: ~4-6MB total
- **CPU Usage**: ~10-20% on modern systems
- **Audio Latency**: ~20ms

### Optimization Strategies
1. **Memory Pool**: Reduces allocation overhead
2. **Page-based Graphics**: Efficient memory usage
3. **Cooperative Multitasking**: Low threading overhead
4. **Resource Caching**: Reduces loading time

## Extensibility

### Adding New Platforms
1. Implement Backend interface
2. Add platform-specific code
3. Update build system
4. Test and validate

### Adding New Features
1. Extend appropriate system interface
2. Implement feature in system
3. Add VM instructions if needed
4. Update documentation

### Modifying Game Behavior
1. Modify VM bytecode interpretation
2. Update system call implementations
3. Adjust resource loading
4. Test compatibility

## Security Considerations

### Memory Safety
- **Bounds Checking**: All array access is bounds-checked
- **Null Pointer Checks**: All pointer access is validated
- **Buffer Overflow Protection**: Stack protection enabled

### Input Validation
- **Resource Validation**: All resources are validated before use
- **Input Sanitization**: All input is sanitized
- **Error Handling**: Comprehensive error handling

## Testing Strategy

### Unit Testing
- **System Isolation**: Each system can be tested independently
- **Mock Objects**: Systems can be mocked for testing
- **Interface Testing**: All interfaces are testable

### Integration Testing
- **System Integration**: Full system integration tests
- **Platform Testing**: Cross-platform compatibility tests
- **Performance Testing**: Performance regression tests

### Compatibility Testing
- **Original Game Data**: All original game data is tested
- **Platform Compatibility**: All supported platforms are tested
- **Regression Testing**: Changes are tested for regressions

This architecture provides a solid foundation for the Another World Interpreter, enabling maintainability, extensibility, and cross-platform compatibility while preserving the original game's behavior and technical achievements.
