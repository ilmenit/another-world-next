# Data Structures

## Overview

This document describes the core data structures used throughout the Another World Interpreter. These structures define the memory layout, data formats, and interfaces used by all game systems.

## Core Data Types

### Basic Types

```cpp
// Standard integer types
using uint8_t  = unsigned char;      // 8-bit unsigned
using uint16_t = unsigned short;     // 16-bit unsigned
using uint32_t = unsigned int;       // 32-bit unsigned
using int8_t   = signed char;        // 8-bit signed
using int16_t  = signed short;       // 16-bit signed
using int32_t  = signed int;         // 32-bit signed

// Size types
using size_t   = std::size_t;        // Size type
using ssize_t  = std::ptrdiff_t;     // Signed size type
```

### Point and Rectangle Types

```cpp
struct Point {
    int16_t x;    // X coordinate
    int16_t y;    // Y coordinate
};

struct Rectangle {
    int16_t x;      // Left coordinate
    int16_t y;      // Top coordinate
    int16_t width;  // Width
    int16_t height; // Height
};
```

## Video System Data Structures

### Page Structure

```cpp
struct Page {
    uint8_t id = 0;                    // Page identifier
    uint8_t data[((320 / 2) * 200)];  // Page data (32,000 bytes)
    
    // Page dimensions
    static constexpr int16_t PAGE_W = 320;  // Page width
    static constexpr int16_t PAGE_H = 200;  // Page height
    static constexpr int16_t PAGE_SIZE = (PAGE_W * PAGE_H / 2);  // 32,000 bytes
};
```

### Palette Structure

```cpp
struct Color3u8 {
    uint8_t r = 0;  // Red component
    uint8_t g = 0;  // Green component
    uint8_t b = 0;  // Blue component
};

struct Palette {
    uint8_t  id = 0;        // Palette identifier
    Color3u8 data[16];      // 16 colors per palette
};
```

### Polygon Structure

```cpp
struct Polygon {
    uint16_t bbw;        // Bounding box width
    uint16_t bbh;        // Bounding box height
    uint8_t  count;      // Number of vertices
    Point    points[50]; // Vertex coordinates (max 50 points)
};
```

## Audio System Data Structures

### Audio Sample Structure

```cpp
struct AudioSample {
    uint16_t       sample_id = 0xffff; // Sample identifier
    uint16_t       frequency = 0;      // Frequency
    uint8_t        volume    = 0;      // Volume level
    const uint8_t* data_ptr  = nullptr; // Sample data pointer
    uint32_t       data_len  = 0;      // Sample length
    uint32_t       loop_pos  = 0;      // Loop start position
    uint32_t       loop_len  = 0;      // Loop length
    uint16_t       unused1   = 0;      // Unused field
    uint16_t       unused2   = 0;      // Unused field
};
```

### Audio Channel Structure

```cpp
struct AudioChannel {
    uint8_t        channel_id = 0xff;  // Channel identifier
    uint8_t        active     = 0;     // Active flag
    uint8_t        volume     = 0;     // Volume level
    uint16_t       sample_id  = 0xffff; // Sample identifier
    const uint8_t* data_ptr   = nullptr; // Sample data pointer
    uint32_t       data_len   = 0;     // Sample length
    uint32_t       data_pos   = 0;     // Current position
    uint32_t       data_inc   = 0;     // Position increment
    uint32_t       loop_pos   = 0;     // Loop start position
    uint32_t       loop_len   = 0;     // Loop length
};
```

### Music Track Structure

```cpp
struct MusicTrack {
    const uint8_t* data;    // Music data
    uint32_t length;        // Track length
    uint32_t position;      // Current position
    uint16_t delay;         // Delay between notes
    bool playing;           // Playing flag
    bool loop;              // Loop flag
    uint8_t tempo;          // Tempo
};
```

## Virtual Machine Data Structures

### Thread Structure

```cpp
struct Thread {
    uint32_t thread_id;       // Thread identifier (0-63)
    uint16_t current_pc;      // Current program counter
    uint16_t requested_pc;    // Requested program counter
    uint8_t  current_state;   // Current thread state
    uint8_t  requested_state; // Requested thread state
    uint8_t  opcode;          // Current opcode
    bool     yield;           // Yield flag
    
    // Thread states
    static constexpr uint8_t THREAD_RUNNING = 0;
    static constexpr uint8_t THREAD_PAUSED  = 1;
    static constexpr uint8_t THREAD_HALTED  = 2;
};
```

### Register Structure

```cpp
struct Register {
    union {
        int16_t  s;        // Signed 16-bit value
        uint16_t u;        // Unsigned 16-bit value
    };
};
```

### Stack Structure

```cpp
struct Stack {
    uint32_t array[256];   // Stack storage (256 elements)
    uint32_t index;        // Current stack pointer
    
    // Stack operations
    auto push(uint32_t value) -> void;
    auto pop() -> uint32_t;
    auto peek() -> uint32_t;
    auto isEmpty() -> bool;
    auto isFull() -> bool;
};
```

### ByteCode Structure

```cpp
class ByteCode {
public:
    ByteCode();
    ByteCode(const uint8_t* buffer);
    ByteCode(const uint8_t* buffer, uint32_t offset);
    
    auto get() const -> const uint8_t*;
    auto reset() -> void;
    auto reset(const uint8_t* buffer) -> void;
    auto offset() -> uint32_t;
    auto seek(uint32_t offset) -> void;
    auto fetchByte() -> uint8_t;
    auto fetchWord() -> uint16_t;
    auto fetchLong() -> uint32_t;
    
private:
    const uint8_t* _buffer;
    const uint8_t* _bufptr;
};
```

## Resource System Data Structures

### Resource Structure

```cpp
struct Resource {
    uint16_t id            = 0;      // Resource identifier
    uint8_t  state         = 0xff;  // Resource state
    uint8_t  type          = 0xff;  // Resource type
    uint16_t unused1       = 0;     // Unused field
    uint16_t unused2       = 0;     // Unused field
    uint8_t  unused3       = 0;     // Unused field
    uint8_t  bank_id       = 0;     // Bank identifier
    uint32_t bank_offset   = 0;     // Bank offset
    uint16_t unused4       = 0;     // Unused field
    uint16_t packed_size   = 0;     // Packed size
    uint16_t unused5       = 0;     // Unused field
    uint16_t unpacked_size = 0;     // Unpacked size
    uint8_t* data          = nullptr; // Resource data
};
```

### String Structure

```cpp
struct String {
    uint16_t    id    = 0xffff; // String identifier
    const char* value = nullptr; // String value
};
```

### MemList Entry Structure

```cpp
struct MemListEntry {
    uint16_t resourceId;    // Resource identifier
    uint32_t offset;        // File offset
    uint32_t size;          // Resource size
    uint8_t  type;          // Resource type
    uint8_t  compressed;    // Compression flag
    uint8_t  reserved[2];   // Reserved bytes
};
```

## Input System Data Structures

### Controls Structure

```cpp
struct Controls {
    static constexpr uint16_t DPAD_RIGHT  = (1 << 0);
    static constexpr uint16_t DPAD_LEFT   = (1 << 1);
    static constexpr uint16_t DPAD_DOWN   = (1 << 2);
    static constexpr uint16_t DPAD_UP     = (1 << 3);
    static constexpr uint16_t DPAD_BUTTON = (1 << 7);

    uint16_t mask  = 0;    // Bit mask for input state
    int16_t  horz  = 0;    // Horizontal movement (-1, 0, 1)
    int16_t  vert  = 0;    // Vertical movement (-1, 0, 1)
    int16_t  btns  = 0;    // Button state
    uint8_t  input = 0;    // Current input character
    bool     quit  = false; // Quit flag
    bool     pause = false; // Pause flag
};
```

## Backend System Data Structures

### Timer Structure

```cpp
struct Timer {
    int id;                    // Timer identifier
    uint32_t delay;           // Delay in milliseconds
    uint32_t nextFire;        // Next fire time
    TimerCallback callback;   // Callback function
    void* userdata;           // User data
    bool active;              // Active flag
    bool repeat;              // Repeat flag
};
```

### Audio Callback Types

```cpp
using AudioCallback = void (*)(void* data, uint8_t* buffer, int length);
using TimerCallback = uint32_t (*)(uint32_t delay, void* param);
```

**AudioCallback Description**: Callback function for audio output.
**Parameters**:
- `data`: User data pointer
- `buffer`: Audio buffer to fill
- `length`: Buffer length in bytes

**TimerCallback Description**: Callback function for timers.
**Parameters**:
- `delay`: Timer delay in milliseconds
- `param`: User parameter
**Returns**: New delay value in milliseconds

## File System Data Structures

### File Structure

```cpp
class File {
public:
    static auto open(const std::string& path) -> File*;
    auto read(void* buffer, size_t size) -> size_t;
    auto write(const void* buffer, size_t size) -> size_t;
    auto seek(size_t offset) -> bool;
    auto tell() -> size_t;
    auto size() -> size_t;
    auto close() -> void;
    
private:
    FILE* _file;        // File handle
    std::string _path;  // File path
    bool _readOnly;     // Read-only flag
};
```

## Logger Data Structures

### Log Level Enumeration

```cpp
enum LogLevel {
    LOG_DEBUG = 0x01,   // Debug messages
    LOG_PRINT = 0x02,   // Print messages
    LOG_ALERT = 0x04,   // Alert messages
    LOG_ERROR = 0x08,   // Error messages
    LOG_FATAL = 0x10    // Fatal messages
};
```

### System Mask Enumeration

```cpp
enum SystemMask {
    SYS_ENGINE     = 0x01,  // Engine system
    SYS_BACKEND    = 0x02,  // Backend system
    SYS_RESOURCES  = 0x04,  // Resources system
    SYS_VIDEO      = 0x08,  // Video system
    SYS_AUDIO      = 0x10,  // Audio system
    SYS_MIXER      = 0x20,  // Mixer system
    SYS_SOUND      = 0x40,  // Sound system
    SYS_MUSIC      = 0x80,  // Music system
    SYS_INPUT      = 0x100, // Input system
    SYS_VM         = 0x200  // Virtual machine
};
```

## Memory Management Data Structures

### Memory Pool Structure

```cpp
class MemoryPool {
private:
    static constexpr uint32_t BLOCK_COUNT = 1792;  // Total blocks
    static constexpr uint32_t BLOCK_SIZE  = 1024;  // Block size (1KB)
    static constexpr uint32_t TOTAL_SIZE  = (BLOCK_COUNT * BLOCK_SIZE);  // ~1.8MB
    
    uint8_t  _buffer[TOTAL_SIZE];  // Memory pool
    uint8_t* _bufptr;              // Current pointer
    uint8_t* _bufend;              // End pointer
    size_t   _allocated;           // Allocated bytes
    size_t   _peak;                // Peak allocation
    
public:
    auto allocate(size_t size) -> uint8_t*;
    auto deallocate(uint8_t* ptr) -> void;
    auto getUsage() -> size_t;
    auto getPeak() -> size_t;
    auto reset() -> void;
};
```

## Configuration Data Structures

### Build Configuration

```cpp
struct BuildConfig {
    bool debug;              // Debug build
    bool emscripten;         // Emscripten build
    bool skipGamePart0;      // Skip protection screen
    bool bypassProtection;    // Bypass protection
    bool preloadResources;   // Preload resources
    uint32_t audioSampleRate; // Audio sample rate
};
```

## Error Handling Data Structures

### Error Structure

```cpp
struct Error {
    int code;                // Error code
    std::string message;     // Error message
    std::string file;        // Source file
    int line;                // Source line
    std::string function;    // Function name
    
    auto toString() -> std::string;
};
```

### Exception Classes

```cpp
class Panic : public std::exception {
public:
    Panic(const std::string& message);
    auto what() -> const char* override;
    
private:
    std::string _message;
};

class ResourceError : public std::exception {
public:
    ResourceError(const std::string& resource, const std::string& message);
    auto what() -> const char* override;
    
private:
    std::string _resource;
    std::string _message;
};
```

## Performance Monitoring Data Structures

### Performance Metrics

```cpp
struct PerformanceMetrics {
    uint32_t frameCount;     // Frame count
    uint32_t frameTime;      // Frame time (ms)
    uint32_t audioTime;      // Audio processing time (ms)
    uint32_t videoTime;      // Video processing time (ms)
    uint32_t vmTime;         // VM processing time (ms)
    uint32_t inputTime;      // Input processing time (ms)
    uint32_t totalTime;      // Total frame time (ms)
    
    auto getFPS() -> float;
    auto getAverageFrameTime() -> float;
    auto reset() -> void;
};
```

## Platform-Specific Data Structures

### SDL2 Backend Data

```cpp
struct SDL2BackendData {
    SDL_Window* window;        // SDL2 window
    SDL_Renderer* renderer;    // SDL2 renderer
    SDL_Texture* texture;       // SDL2 texture
    SDL_AudioDeviceID audioDevice; // Audio device
    uint32_t startTicks;       // Start ticks
    uint32_t currentTicks;     // Current ticks
};
```

### WebAssembly Backend Data

```cpp
struct EmscriptenBackendData {
    EMSCRIPTEN_WEBGL_CONTEXT_HANDLE glContext; // WebGL context
    uint32_t canvasWidth;      // Canvas width
    uint32_t canvasHeight;     // Canvas height
    bool audioInitialized;     // Audio initialized
    bool webglInitialized;     // WebGL initialized
};
```

These data structures provide the foundation for the Another World Interpreter, defining the memory layout, data formats, and interfaces used throughout the system. They enable efficient memory management, clear system interfaces, and maintainable code organization.
