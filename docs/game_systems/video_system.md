# Video System

## Overview

The Video System is responsible for all graphics rendering in Another World, including polygon-based character animation, page-based graphics management, and bitmap drawing. This system implements the revolutionary polygon rendering technique that made Another World visually distinctive in 1991.

## Architecture

### Core Components

```
Video System
├── Page Management
│   ├── 4 Video Pages (320×200 each)
│   ├── Page Selection and Switching
│   └── Page Copying and Scrolling
├── Palette System
│   ├── 32 Color Palettes
│   ├── Palette Selection
│   └── Color Interpolation
├── Polygon Rendering
│   ├── Vector-based Graphics
│   ├── Smooth Character Animation
│   └── Zoom and Scaling
├── Bitmap Drawing
│   ├── Sprite Rendering
│   ├── Background Graphics
│   └── Text Rendering
└── Display Management
    ├── Screen Updates
    ├── Fade Effects
    └── Page Transitions
```

## Video Specifications

### Display Properties
- **Resolution**: 320×200 pixels
- **Color Depth**: 4 bits per pixel (16 colors)
- **Pixels per Byte**: 2 pixels per byte
- **Bytes per Line**: 160 bytes
- **Total Page Size**: 32,000 bytes (320×200×4/8)

### Page System

The video system uses a page-based architecture with 4 video pages:

```cpp
static constexpr uint8_t VIDEO_PAGE0 = 0x00;  // Background page
static constexpr uint8_t VIDEO_PAGE1 = 0x01;  // Foreground page
static constexpr uint8_t VIDEO_PAGE2 = 0x02;  // Working page
static constexpr uint8_t VIDEO_PAGE3 = 0x03;  // Buffer page
static constexpr uint8_t VIDEO_PAGEV = 0xfe;  // Visible page
static constexpr uint8_t VIDEO_PAGEI = 0xff;  // Invalid page
```

### Coordinate System
- **X Range**: 0-319 (left to right)
- **Y Range**: 0-199 (top to bottom)
- **Origin**: Top-left corner (0,0)

## Page Management

### Page Operations

#### Select Page
```cpp
auto selectPage(uint8_t dst) -> void
{
    // Set active drawing page
    _currentPage = getPage(dst);
}
```

#### Fill Page
```cpp
auto fillPage(uint8_t dst, uint8_t color) -> void
{
    Page* page = getPage(dst);
    std::fill(page->data, page->data + PAGE_SIZE, color);
}
```

#### Copy Page
```cpp
auto copyPage(uint8_t dst, uint8_t src, int16_t vscroll) -> void
{
    Page* destPage = getPage(dst);
    Page* srcPage = getPage(src);
    
    if(vscroll == 0) {
        // Direct copy
        std::memcpy(destPage->data, srcPage->data, PAGE_SIZE);
    } else {
        // Scrolled copy
        copyPageWithScroll(destPage, srcPage, vscroll);
    }
}
```

#### Show Page
```cpp
auto showPage(uint8_t src) -> void
{
    // Display specified page on screen
    _backend->updateScreen(*getPage(src), _pages[0], _pages[1], _pages[2], _pages[3], *_palette);
}
```

### Page Data Structure

```cpp
struct Page {
    uint8_t data[PAGE_SIZE];  // 32,000 bytes
    bool dirty;              // Needs update flag
};
```

## Palette System

### Palette Management

The video system supports 32 different color palettes:

```cpp
struct Palette {
    uint8_t colors[16];  // 16 colors per palette
};
```

### Palette Operations

#### Set Palettes
```cpp
auto setPalettes(const uint8_t* palettes, uint8_t mode) -> void
{
    // Load palette data
    for(int i = 0; i < 32; ++i) {
        std::memcpy(_palettes[i].colors, palettes + (i * 16), 16);
    }
    _paletteMode = mode;
}
```

#### Select Palette
```cpp
auto selectPalette(uint8_t palette) -> void
{
    if(palette < 32) {
        _palette = &_palettes[palette];
    }
}
```

### Color Interpolation

The system includes color interpolation for smooth transitions:

```cpp
uint16_t _interpolate[0x400];  // Interpolation lookup table
```

## Polygon Rendering

### Polygon System

Another World's most distinctive feature is its polygon-based character animation system:

```cpp
struct Polygon {
    uint16_t pointCount;     // Number of vertices
    Point points[16];        // Vertex coordinates
    uint16_t color;          // Fill color
    bool filled;             // Filled or wireframe
};
```

### Polygon Drawing

#### Draw Polygons
```cpp
auto drawPolygons(const uint8_t* buffer, uint16_t offset, const Point& position, uint16_t zoom) -> void
{
    // Parse polygon data from buffer
    uint32_t dataOffset = offset;
    
    while(dataOffset < bufferSize) {
        Polygon polygon = parsePolygon(buffer, dataOffset);
        
        // Apply position and zoom
        transformPolygon(polygon, position, zoom);
        
        // Render polygon
        renderPolygon(polygon, position, zoom, polygon.color);
        
        dataOffset += polygonSize(polygon);
    }
}
```

#### Render Polygon
```cpp
auto renderPolygon(const Polygon& polygon, const Point& position, uint16_t zoom, uint16_t color) -> void
{
    if(polygon.filled) {
        // Fill polygon using scanline algorithm
        fillPolygon(polygon, color);
    } else {
        // Draw wireframe
        drawPolygonWireframe(polygon, color);
    }
}
```

### Polygon Types

The system supports two polygon rendering modes:

#### Type 1 Polygons
- **Usage**: Character bodies and main objects
- **Features**: Filled polygons with solid colors
- **Performance**: Optimized for character animation

#### Type 2 Polygons
- **Usage**: Background elements and effects
- **Features**: Wireframe or special effects
- **Performance**: Optimized for background rendering

## Bitmap Drawing

### Bitmap Operations

#### Draw Bitmap
```cpp
auto drawBitmap(const uint8_t* bitmap) -> void
{
    // Parse bitmap header
    uint16_t width = readUint16(bitmap);
    uint16_t height = readUint16(bitmap + 2);
    uint16_t x = readUint16(bitmap + 4);
    uint16_t y = readUint16(bitmap + 6);
    
    // Draw bitmap data
    drawBitmapData(bitmap + 8, x, y, width, height);
}
```

#### Draw String
```cpp
auto drawString(uint16_t id, uint16_t x, uint16_t y, uint8_t color) -> void
{
    const char* string = _engine.getString(id);
    if(string) {
        renderString(string, x, y, color);
    }
}
```

### Font System

The system includes a built-in 8×8 pixel font:

```cpp
struct Font {
    static const uint8_t data[96][8];  // ASCII characters
};
```

#### Render String
```cpp
auto renderString(const char* string, uint16_t x, uint16_t y, uint8_t color) -> void
{
    uint16_t currentX = x;
    
    for(const char* c = string; *c; ++c) {
        if(*c >= 32 && *c < 128) {
            // Render character
            renderCharacter(*c - 32, currentX, y, color);
            currentX += 8;  // Character width
        }
    }
}
```

## Display Management

### Screen Updates

The video system coordinates with the backend for screen updates:

```cpp
auto updateScreen(const Page& page, const Page& page0, const Page& page1, const Page& page2, const Page& page3, const Palette& palette) -> void
{
    // Convert page data to screen format
    convertPageToScreen(page, palette);
    
    // Update display
    _backend->presentFrame();
}
```

### Fade Effects

The system supports screen fade effects:

```cpp
auto fadeEffect(uint8_t type, uint16_t duration) -> void
{
    switch(type) {
        case FADE_IN:
            fadeIn(duration);
            break;
        case FADE_OUT:
            fadeOut(duration);
            break;
        case FADE_CROSS:
            crossFade(duration);
            break;
    }
}
```

## Performance Characteristics

### Rendering Performance
- **Polygon Rendering**: ~100-1000 polygons per frame
- **Page Operations**: Very fast (memory copy operations)
- **Bitmap Drawing**: ~10-100 bitmaps per frame
- **Text Rendering**: ~50-200 characters per frame

### Memory Usage
- **Page Storage**: 128KB (4 × 32KB pages)
- **Palette Storage**: 512 bytes (32 × 16 colors)
- **Polygon Buffer**: ~1KB per polygon
- **Font Data**: 768 bytes (96 × 8 bytes)

## Integration with Game Systems

### Engine Interface

The video system integrates with the main engine:

```cpp
class Video {
    Engine& _engine;  // Reference to main engine
    
    // System access methods
    auto getString(uint16_t id) -> const char*;
    auto getResource(uint16_t id) -> Resource*;
    // ... other system calls
};
```

### VM Integration

The Virtual Machine controls video operations through system calls:

```cpp
// VM video instructions
op_page(Thread& thread);    // Page operations
op_fill(Thread& thread);    // Fill page
op_copy(Thread& thread);    // Copy page
op_show(Thread& thread);    // Show page
op_print(Thread& thread);   // Print text
op_poly1(Thread& thread);   // Draw polygon type 1
op_poly2(Thread& thread);   // Draw polygon type 2
```

## Historical Context

### Innovation (1991)

Another World's video system was revolutionary for its time:

- **Polygon Characters**: First game to use polygon-based character animation
- **Smooth Animation**: 60 FPS character movement
- **Cinematic Quality**: Movie-like visual presentation
- **Cross-platform**: Identical graphics across all platforms

### Technical Achievements

- **Efficient Rendering**: Optimized for 16-bit processors
- **Memory Management**: Smart page-based graphics system
- **Color Interpolation**: Smooth color transitions
- **Scalable Graphics**: Zoom and scaling support

## Debugging Support

### Debug Output

```cpp
// Enable video debugging
./another-world.bin --debug-video

// Debug all systems
./another-world.bin --debug-all
```

### Debug Features
- **Page Operations**: Log all page manipulations
- **Polygon Rendering**: Track polygon drawing operations
- **Palette Changes**: Monitor palette selections
- **Performance Metrics**: Frame rate and rendering statistics

## Modern Implementation

### Improvements

This modern implementation adds:

- **Clean Architecture**: Modular, maintainable code
- **Better Performance**: Optimized for modern processors
- **Enhanced Debugging**: Comprehensive logging and debugging
- **Documentation**: Complete technical documentation

### Compatibility

The system maintains full compatibility with:
- **Original Game Data**: All original graphics formats
- **Bytecode Instructions**: Complete VM instruction set
- **Display Modes**: All original video modes

The Video System represents one of the most innovative graphics systems in gaming history, demonstrating sophisticated polygon rendering techniques that were years ahead of their time.
