# Resource Management System

## Overview

The Resource Management System handles all game data loading, caching, and memory management for Another World. This system is responsible for loading compressed game resources, managing memory allocation, and providing efficient access to game data throughout the interpreter.

## Architecture

### Core Components

```
Resource Management
├── Data Loading
│   ├── File I/O Operations
│   ├── ByteKiller Decompression
│   ├── Resource Parsing
│   └── Memory Allocation
├── Resource Caching
│   ├── Memory Pool Management
│   ├── Resource Indexing
│   ├── Cache Invalidation
│   └── Memory Optimization
├── Part Management
│   ├── Game Part Loading
│   ├── Part Switching
│   ├── Resource Dependencies
│   └── Memory Layout
└── Data Structures
    ├── Resource Objects
    ├── String Management
    ├── Polygon Data
    └── Bytecode Storage
```

## Memory Management

### Memory Pool System

The resource system uses a fixed-size memory pool for efficient allocation:

```cpp
class Resources {
private:
    static constexpr uint32_t BLOCK_COUNT = 1792;  // Total blocks
    static constexpr uint32_t BLOCK_SIZE  = 1024;  // Block size (1KB)
    static constexpr uint32_t TOTAL_SIZE  = (BLOCK_COUNT * BLOCK_SIZE);  // ~1.8MB
    
    uint8_t  _buffer[TOTAL_SIZE];  // Memory pool
    uint8_t* _bufptr;              // Current pointer
    uint8_t* _bufend;              // End pointer
};
```

### Memory Allocation

```cpp
auto allocateMemory(size_t size) -> uint8_t*
{
    // Align to block boundary
    size = (size + BLOCK_SIZE - 1) & ~(BLOCK_SIZE - 1);
    
    // Check available space
    if(_bufptr + size > _bufend) {
        log_error("Out of memory: requested %zu bytes", size);
        return nullptr;
    }
    
    // Allocate memory
    uint8_t* ptr = _bufptr;
    _bufptr += size;
    return ptr;
}
```

## Resource System

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

### Resource Types

```cpp
enum ResourceType {
    RESOURCE_BITMAP = 0,    // Bitmap graphics
    RESOURCE_PALETTE = 1,   // Color palettes
    RESOURCE_SOUND = 2,     // Sound effects
    RESOURCE_MUSIC = 3,     // Music tracks
    RESOURCE_STRING = 4,    // Text strings
    RESOURCE_POLYGON = 5,   // Polygon data
    RESOURCE_BYTECODE = 6,  // VM bytecode
    RESOURCE_VOICE = 7,     // Voice/speech
    RESOURCE_OTHER = 8      // Other data
};
```

### Resource Operations

#### Load Resource
```cpp
auto loadResource(uint16_t resourceId) -> void
{
    if(resourceId < _resourcesCount) {
        Resource& resource = _resourcesArray[resourceId];
        
        if(!resource.loaded) {
            // Load resource data
            loadResourceData(resource);
            resource.loaded = true;
        }
    }
}
```

#### Get Resource
```cpp
auto getResource(uint16_t resourceId) -> Resource*
{
    if(resourceId < _resourcesCount) {
        Resource& resource = _resourcesArray[resourceId];
        
        if(!resource.loaded) {
            loadResource(resourceId);
        }
        
        return &resource;
    }
    return nullptr;
}
```

## Part Management

### Game Parts

Another World is divided into multiple parts (levels/scenes):

```cpp
class Resources {
private:
    uint16_t _curPartId;    // Current part ID
    uint16_t _reqPartId;    // Requested part ID
    uint8_t  _dictionaryId; // Dictionary ID
};
```

### Part Operations

#### Load Part
```cpp
auto loadPart(uint16_t partId) -> void
{
    if(partId != _curPartId) {
        // Invalidate current resources
        invalidateAll();
        
        // Load new part
        loadPartData(partId);
        _curPartId = partId;
    }
}
```

#### Request Part
```cpp
auto requestPartId(uint16_t partId) -> void
{
    _reqPartId = partId;
}
```

### Part Data Loading

```cpp
auto loadPartData(uint16_t partId) -> void
{
    // Load part-specific resources
    loadPartResources(partId);
    
    // Load bytecode for part
    loadPartBytecode(partId);
    
    // Load polygon data
    loadPartPolygons(partId);
    
    // Load palettes
    loadPartPalettes(partId);
}
```

## Data Loading

### File Operations

The system uses a file abstraction layer for cross-platform file access:

```cpp
class File {
public:
    static auto open(const std::string& path) -> File*;
    auto read(void* buffer, size_t size) -> size_t;
    auto seek(size_t offset) -> bool;
    auto tell() -> size_t;
    auto close() -> void;
};
```

### Resource Loading Process

```cpp
auto loadResourceData(Resource& resource) -> void
{
    // Open resource file
    File* file = File::open(getResourcePath(resource.id));
    if(!file) {
        log_error("Failed to open resource file");
        return;
    }
    
    // Read resource header
    ResourceHeader header;
    file->read(&header, sizeof(header));
    
    // Allocate memory
    resource.data = allocateMemory(header.size);
    if(!resource.data) {
        file->close();
        return;
    }
    
    // Read resource data
    if(header.compressed) {
        // Decompress data
        decompressResource(file, resource.data, header.size);
    } else {
        // Read raw data
        file->read(resource.data, header.size);
    }
    
    resource.size = header.size;
    resource.compressed = header.compressed;
    file->close();
}
```

## ByteKiller Decompression

### Compression Algorithm

Another World uses the ByteKiller compression algorithm for efficient data storage:

```cpp
class ByteKiller {
public:
    static auto decompress(const uint8_t* input, uint8_t* output, size_t outputSize) -> size_t;
    static auto getDecompressedSize(const uint8_t* input) -> size_t;
};
```

### Decompression Process

```cpp
auto decompressResource(File* file, uint8_t* output, size_t outputSize) -> void
{
    // Read compressed data
    uint8_t* compressed = allocateMemory(file->tell());
    file->read(compressed, file->tell());
    
    // Decompress
    size_t decompressedSize = ByteKiller::decompress(compressed, output, outputSize);
    
    // Free compressed data
    freeMemory(compressed);
}
```

## String Management

### String System

The game uses a string table for localized text:

```cpp
struct String {
    uint16_t id;        // String ID
    char* value;        // String value
    uint16_t length;    // String length
};
```

### String Operations

#### Get String
```cpp
auto getString(uint16_t stringId) -> const String*
{
    // Search string table
    for(int i = 0; i < _stringCount; ++i) {
        if(_strings[i].id == stringId) {
            return &_strings[i];
        }
    }
    return nullptr;
}
```

#### Load Strings
```cpp
auto loadStrings() -> void
{
    // Load string table from resources
    Resource* stringResource = getResource(RESOURCE_STRING_TABLE);
    if(stringResource) {
        parseStringTable(stringResource->data, stringResource->size);
    }
}
```

## Polygon Data Management

### Polygon Storage

Polygon data is stored in compressed format and loaded on demand:

```cpp
class Resources {
private:
    uint8_t* _segPolygon1;  // Polygon data segment 1
    uint8_t* _segPolygon2;  // Polygon data segment 2
};
```

### Polygon Operations

#### Get Polygon Data
```cpp
auto getPolygonData(int index) -> const uint8_t*
{
    switch(index) {
        case 1:
            return _segPolygon1;
        case 2:
            return _segPolygon2;
        default:
            return nullptr;
    }
}
```

#### Load Polygon Data
```cpp
auto loadPolygonData() -> void
{
    // Load polygon segments
    _segPolygon1 = loadPolygonSegment(1);
    _segPolygon2 = loadPolygonSegment(2);
}
```

## Bytecode Management

### Bytecode Storage

The VM bytecode is loaded and managed by the resource system:

```cpp
class Resources {
private:
    uint8_t* _segByteCode;  // Bytecode segment
};
```

### Bytecode Operations

#### Get Bytecode
```cpp
auto getByteCodeData() const -> const uint8_t*
{
    return _segByteCode;
}
```

#### Load Bytecode
```cpp
auto loadBytecode() -> void
{
    // Load bytecode for current part
    Resource* bytecodeResource = getResource(RESOURCE_BYTECODE);
    if(bytecodeResource) {
        _segByteCode = bytecodeResource->data;
    }
}
```

## Memory Layout

### MEMLIST.BIN Format

The game uses a memory list file to define resource layout:

```cpp
struct MemListEntry {
    uint16_t resourceId;    // Resource ID
    uint32_t offset;        // File offset
    uint32_t size;          // Resource size
    uint8_t  type;          // Resource type
    uint8_t  compressed;    // Compression flag
};
```

### Load Memory List

```cpp
auto loadMemList() -> void
{
    // Open MEMLIST.BIN
    File* file = File::open("MEMLIST.BIN");
    if(!file) {
        log_error("Failed to open MEMLIST.BIN");
        return;
    }
    
    // Read entries
    MemListEntry entry;
    while(file->read(&entry, sizeof(entry)) == sizeof(entry)) {
        // Add resource entry
        addResourceEntry(entry);
    }
    
    file->close();
}
```

## Performance Characteristics

### Memory Usage
- **Total Pool**: ~1.8MB fixed memory pool
- **Resource Cache**: ~1-2MB typical usage
- **String Table**: ~64KB for all strings
- **Polygon Data**: ~256KB for polygon segments

### Loading Performance
- **Resource Loading**: ~1-10ms per resource
- **Decompression**: ~5-50ms depending on size
- **Part Switching**: ~100-500ms for full part load
- **Memory Allocation**: O(1) constant time

## Integration with Game Systems

### Engine Interface

The resource system integrates with the main engine:

```cpp
class Resources {
    Engine& _engine;  // Reference to main engine
    
    // System access methods
    auto getResource(uint16_t id) -> Resource*;
    auto getString(uint16_t id) -> const String*;
    auto getPolygonData(int index) -> const uint8_t*;
    // ... other system calls
};
```

### VM Integration

The Virtual Machine accesses resources through the engine:

```cpp
// VM resource instructions
op_load(Thread& thread);  // Load resource
```

### Video Integration

The video system accesses graphics resources:

```cpp
// Video system resource access
auto getBitmap(uint16_t id) -> const uint8_t*;
auto getPalette(uint16_t id) -> const uint8_t*;
```

## Debugging Support

### Debug Output

```cpp
// Enable resource debugging
./another-world.bin --debug-resources

// Debug all systems
./another-world.bin --debug-all
```

### Debug Features
- **Memory Usage**: Track memory allocation
- **Resource Loading**: Monitor resource loading
- **Cache Status**: Track resource cache state
- **Performance Metrics**: Loading and allocation statistics

## Historical Context

### Innovation (1991)

Another World's resource system was sophisticated for its time:

- **Compression**: ByteKiller algorithm for efficient storage
- **Memory Management**: Fixed pool for predictable memory usage
- **Part System**: Modular game data loading
- **Cross-platform**: Identical data format across platforms

### Technical Achievements

- **Efficient Storage**: ~50% compression ratio
- **Fast Loading**: Optimized for limited hardware
- **Memory Safety**: Bounded memory usage
- **Modular Design**: Clean separation of game parts

## Modern Implementation

### Improvements

This modern implementation adds:

- **Better Error Handling**: Comprehensive error checking
- **Enhanced Debugging**: Detailed logging and debugging
- **Memory Safety**: Modern C++ memory management
- **Documentation**: Complete technical documentation

### Compatibility

The system maintains full compatibility with:
- **Original Game Data**: All original resource formats
- **Compression**: ByteKiller algorithm implementation
- **Memory Layout**: Identical memory organization

The Resource Management System provides a robust foundation for game data handling, supporting both the original game's requirements and modern development practices while maintaining full compatibility with the original game data.
