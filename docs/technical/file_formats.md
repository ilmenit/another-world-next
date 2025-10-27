# File Formats

## Overview

This document describes the file formats used by Another World, including game data files, resource formats, and configuration files. Understanding these formats is essential for data extraction, modification, and compatibility.

## Game Data Files

### BANK Files (BANK01-BANK0D)

**Purpose**: Compressed game resource banks containing all game assets.

**Format**:
```
[Header: 16 bytes]
[Compressed Data: Variable]

Header Structure:
- Magic: 4 bytes ("BANK")
- Version: 4 bytes
- Compressed Size: 4 bytes
- Decompressed Size: 4 bytes

Compressed Data:
- ByteKiller compressed data
- Contains multiple resources
```

**Decompression**:
```cpp
auto decompressBank(const uint8_t* bankData) -> uint8_t* {
    // Read header
    uint32_t compressedSize = readUint32(bankData + 8);
    uint32_t decompressedSize = readUint32(bankData + 12);
    
    // Decompress data
    uint8_t* decompressed = new uint8_t[decompressedSize];
    ByteKiller::decompress(bankData + 16, decompressed, decompressedSize);
    
    return decompressed;
}
```

### MEMLIST.BIN

**Purpose**: Memory layout file defining resource locations and properties.

**Format**:
```
[Entry Count: 4 bytes]
[Entries: Variable]

Entry Structure (16 bytes):
- Resource ID: 2 bytes
- File Offset: 4 bytes
- Resource Size: 4 bytes
- Resource Type: 1 byte
- Compression Flag: 1 byte
- Reserved: 4 bytes
```

**Structure**:
```cpp
struct MemListEntry {
    uint16_t resourceId;    // Resource identifier
    uint32_t offset;        // File offset
    uint32_t size;          // Resource size
    uint8_t  type;          // Resource type
    uint8_t  compressed;    // Compression flag
    uint8_t  reserved[4];   // Reserved bytes
};
```

### CONFIG Files

#### CONFIG.dat
**Purpose**: Game configuration and settings.

**Format**:
```
[Configuration Data: Variable]
- Game settings
- Default values
- System parameters
```

#### CONFIG.lng
**Purpose**: Language configuration and localization.

**Format**:
```
[Language Data: Variable]
- String table
- Localization settings
- Language-specific data
```

### VOL Files (VOL.1-VOL.end)

**Purpose**: Game volume files containing level/scene data.

**Format**:
```
[Volume Header: 32 bytes]
[Volume Data: Variable]

Volume Header:
- Magic: 4 bytes ("VOL ")
- Version: 4 bytes
- Data Size: 4 bytes
- Entry Count: 4 bytes
- Reserved: 16 bytes

Volume Data:
- Compressed level data
- Resource references
- Game logic data
```

### MUSIC

**Purpose**: Music data file containing all game music tracks.

**Format**:
```
[Music Header: 16 bytes]
[Track Data: Variable]

Music Header:
- Magic: 4 bytes ("MUSC")
- Track Count: 4 bytes
- Data Size: 4 bytes
- Reserved: 4 bytes

Track Data:
- Compressed music data
- Timing information
- Instrument data
```

### LOGO

**Purpose**: Logo graphics data.

**Format**:
```
[Logo Header: 16 bytes]
[Logo Data: Variable]

Logo Header:
- Magic: 4 bytes ("LOGO")
- Width: 2 bytes
- Height: 2 bytes
- Data Size: 4 bytes
- Reserved: 4 bytes

Logo Data:
- Compressed bitmap data
- Palette information
```

### TABVOL.bin

**Purpose**: Volume table for audio processing.

**Format**:
```
[Volume Table: 256 bytes]
- Volume levels (0-255)
- Audio processing data
```

## Resource Formats

### Bitmap Resources

**Purpose**: Graphics data for sprites, backgrounds, and UI elements.

**Format**:
```
[Bitmap Header: 16 bytes]
[Bitmap Data: Variable]

Bitmap Header:
- Width: 2 bytes
- Height: 2 bytes
- Color Depth: 1 byte
- Compression: 1 byte
- Data Size: 4 bytes
- Reserved: 6 bytes

Bitmap Data:
- Compressed bitmap data
- Palette information
```

**Structure**:
```cpp
struct BitmapHeader {
    uint16_t width;         // Bitmap width
    uint16_t height;        // Bitmap height
    uint8_t  colorDepth;    // Color depth (4 bits)
    uint8_t  compressed;    // Compression flag
    uint32_t dataSize;      // Data size
    uint8_t  reserved[6];   // Reserved bytes
};
```

### Palette Resources

**Purpose**: Color palette data for graphics.

**Format**:
```
[Palette Data: 16 bytes]
- 16 colors, 1 byte each
- RGB332 format (3 bits red, 3 bits green, 2 bits blue)
```

**Structure**:
```cpp
struct Palette {
    uint8_t colors[16];  // 16 colors
};
```

### Sound Resources

**Purpose**: Audio data for sound effects.

**Format**:
```
[Sound Header: 16 bytes]
[Sound Data: Variable]

Sound Header:
- Sample Rate: 4 bytes
- Sample Count: 4 bytes
- Channels: 1 byte
- Bit Depth: 1 byte
- Compression: 1 byte
- Reserved: 5 bytes

Sound Data:
- Compressed audio data
- PCM samples
```

**Structure**:
```cpp
struct SoundHeader {
    uint32_t sampleRate;    // Sample rate (Hz)
    uint32_t sampleCount;   // Number of samples
    uint8_t  channels;      // Channel count
    uint8_t  bitDepth;      // Bit depth
    uint8_t  compressed;    // Compression flag
    uint8_t  reserved[5];  // Reserved bytes
};
```

### Music Resources

**Purpose**: Music track data.

**Format**:
```
[Music Header: 16 bytes]
[Music Data: Variable]

Music Header:
- Track Length: 4 bytes
- Tempo: 2 bytes
- Channels: 1 byte
- Compression: 1 byte
- Reserved: 8 bytes

Music Data:
- Compressed music data
- MIDI-like data
- Timing information
```

### String Resources

**Purpose**: Text strings for localization.

**Format**:
```
[String Header: 8 bytes]
[String Data: Variable]

String Header:
- String ID: 2 bytes
- Length: 2 bytes
- Encoding: 1 byte
- Reserved: 3 bytes

String Data:
- Text data
- Null-terminated strings
```

### Polygon Resources

**Purpose**: Vector graphics data for character animation.

**Format**:
```
[Polygon Header: 16 bytes]
[Polygon Data: Variable]

Polygon Header:
- Point Count: 2 bytes
- Color: 2 bytes
- Flags: 2 bytes
- Data Size: 4 bytes
- Reserved: 6 bytes

Polygon Data:
- Point coordinates
- Animation data
- Transformation data
```

## Compression Formats

### ByteKiller Compression

**Purpose**: Primary compression algorithm used throughout the game.

**Algorithm**:
1. **LZ77-style compression**: Find repeated sequences
2. **Huffman coding**: Encode frequent patterns
3. **Run-length encoding**: Compress repeated bytes

**Decompression**:
```cpp
auto ByteKiller::decompress(const uint8_t* input, uint8_t* output, size_t outputSize) -> size_t {
    size_t inputPos = 0;
    size_t outputPos = 0;
    
    while(outputPos < outputSize) {
        uint8_t control = input[inputPos++];
        
        if(control & 0x80) {
            // Literal byte
            output[outputPos++] = control & 0x7F;
        } else {
            // Compressed sequence
            uint8_t length = control & 0x0F;
            uint8_t offset = input[inputPos++];
            
            // Copy sequence
            for(int i = 0; i < length; ++i) {
                output[outputPos++] = output[outputPos - offset];
            }
        }
    }
    
    return outputPos;
}
```

## Configuration Formats

### Build Configuration

**Purpose**: Build-time configuration options.

**Format**:
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

### Runtime Configuration

**Purpose**: Runtime configuration and settings.

**Format**:
```
[Config Section: Variable]
- Key-value pairs
- System settings
- User preferences
```

## Platform-Specific Formats

### Linux Format

**Purpose**: Native Linux executable format.

**Format**:
```
[ELF Header]
[Program Headers]
[Code Sections]
[Data Sections]
[Symbol Table]
[String Table]
```

### WebAssembly Format

**Purpose**: WebAssembly binary format.

**Format**:
```
[WASM Header]
[Type Section]
[Import Section]
[Function Section]
[Table Section]
[Memory Section]
[Global Section]
[Export Section]
[Code Section]
[Data Section]
```

## File Validation

### Magic Numbers

Each file type has a unique magic number for identification:

```cpp
enum FileMagic {
    BANK_MAGIC = 0x4B4E4142,  // "BANK"
    VOL_MAGIC  = 0x204C4F56,  // "VOL "
    MUSC_MAGIC = 0x4353554D,  // "MUSC"
    LOGO_MAGIC = 0x4F474F4C,  // "LOGO"
};
```

### File Validation

```cpp
auto validateFile(const uint8_t* data, size_t size) -> bool {
    if(size < 4) return false;
    
    uint32_t magic = readUint32(data);
    
    switch(magic) {
        case BANK_MAGIC:
            return validateBankFile(data, size);
        case VOL_MAGIC:
            return validateVolumeFile(data, size);
        case MUSC_MAGIC:
            return validateMusicFile(data, size);
        case LOGO_MAGIC:
            return validateLogoFile(data, size);
        default:
            return false;
    }
}
```

## Data Extraction

### Resource Extraction

```cpp
auto extractResource(const std::string& bankFile, uint16_t resourceId) -> uint8_t* {
    // Load bank file
    uint8_t* bankData = loadFile(bankFile);
    
    // Decompress bank
    uint8_t* decompressed = decompressBank(bankData);
    
    // Find resource
    MemListEntry* entry = findResource(decompressed, resourceId);
    
    if(entry) {
        // Extract resource data
        uint8_t* resourceData = new uint8_t[entry->size];
        std::memcpy(resourceData, decompressed + entry->offset, entry->size);
        
        return resourceData;
    }
    
    return nullptr;
}
```

### Data Modification

```cpp
auto modifyResource(uint8_t* resourceData, size_t size, const Modification& mod) -> void {
    switch(mod.type) {
        case MODIFY_PALETTE:
            modifyPalette(resourceData, mod.palette);
            break;
        case MODIFY_SOUND:
            modifySound(resourceData, mod.sound);
            break;
        case MODIFY_STRING:
            modifyString(resourceData, mod.string);
            break;
    }
}
```

## Compatibility

### Cross-Platform Compatibility

All file formats are designed for cross-platform compatibility:

- **Endianness**: Little-endian format
- **Alignment**: 4-byte alignment
- **Size**: Fixed-size structures
- **Encoding**: ASCII text encoding

### Version Compatibility

The system supports multiple file format versions:

```cpp
enum FileVersion {
    VERSION_1_0 = 0x0100,  // Original version
    VERSION_1_1 = 0x0101,  // Enhanced version
    VERSION_2_0 = 0x0200   // Modern version
};
```

## Tools and Utilities

### File Analysis Tools

- **Hex Editor**: For binary file analysis
- **Resource Extractor**: For extracting game resources
- **Compression Tool**: For compressing/decompressing data
- **Format Validator**: For validating file formats

### Development Tools

- **Resource Packer**: For creating resource files
- **Format Converter**: For converting between formats
- **Debug Tools**: For analyzing file structures
- **Documentation Generator**: For generating format documentation

This file format reference provides a comprehensive guide to understanding and working with Another World's data formats, enabling data extraction, modification, and compatibility analysis.
