# Polygon Drawing Algorithm

## Overview

The Another World interpreter uses a sophisticated polygon rendering system that combines vector graphics with efficient scanline filling algorithms. This system is designed for real-time character animation and background rendering on limited hardware.

## Architecture

### Data Structures

#### Polygon Structure
```cpp
struct Polygon {
    uint16_t bbw;        // Bounding box width
    uint16_t bbh;        // Bounding box height  
    uint8_t  count;      // Number of vertices (must be even)
    Point    points[50]; // Vertex coordinates (max 50 points)
};
```

#### Point Structure
```cpp
struct Point {
    int16_t x;  // X coordinate
    int16_t y;  // Y coordinate
};
```

### Screen Constants
```cpp
static constexpr int16_t XMIN =   0;  // Left screen boundary
static constexpr int16_t YMIN =   0;  // Top screen boundary
static constexpr int16_t XMAX = 319;  // Right screen boundary
static constexpr int16_t YMAX = 199;  // Bottom screen boundary
static constexpr int16_t PPB  =   2;  // Pixels per byte (4-bit packed)
static constexpr int16_t BPL  = 160;  // Bytes per line (320/2)
```

## Algorithm Components

### 1. Polygon Data Parsing (`renderPolygons`)

The polygon data is stored in a compressed format and parsed from a buffer:

```cpp
auto read_and_fill_polygon_single = [&]() -> void {
    _polygon.bbw   = static_cast<uint16_t>(data.fetchByte()) * zoom / 64;
    _polygon.bbh   = static_cast<uint16_t>(data.fetchByte()) * zoom / 64;
    _polygon.count = static_cast<uint8_t>(data.fetchByte());
    
    // Validate vertex count
    assert(((_polygon.count & 1) == 0) && (_polygon.count < countof(_polygon.points)));
    
    // Read vertex coordinates
    int index = -1;
    const int count = _polygon.count;
    for(auto& point : _polygon.points) {
        if(++index >= count) break;
        point.x = static_cast<uint16_t>(data.fetchByte()) * zoom / 64;
        point.y = static_cast<uint16_t>(data.fetchByte()) * zoom / 64;
    }
    renderPolygon(_polygon, position, zoom, color);
};
```

**Key Features:**
- **Zoom Scaling**: All coordinates are scaled by `zoom/64` for smooth scaling
- **Even Vertex Count**: Polygons must have an even number of vertices
- **Bounding Box**: Used for efficient clipping and optimization

### 2. Scanline Polygon Filling (`fill_polygon`)

The core algorithm uses a **dual-edge scanline filling** technique:

```cpp
auto fill_polygon = [&]() -> void {
    // Calculate bounding box
    const auto half_bbw = (full_bbw / 2);
    const auto half_bbh = (full_bbh / 2);
    const int16_t x1 = (position.x - half_bbw);
    const int16_t x2 = (position.x + half_bbw);
    const int16_t y1 = (position.y - half_bbh);
    const int16_t y2 = (position.y + half_bbh);
    
    // Early clipping test
    if((x1 > XMAX) || (x2 < XMIN) || (y1 > YMAX) || (y2 < YMIN)) {
        return;
    }
    
    // Dual-edge scanline algorithm
    auto p1 = &polygon.points[0];        // Left edge pointer
    auto p2 = &polygon.points[count-1];  // Right edge pointer
    int32_t xa = static_cast<int32_t>(x1 + p1->x) << 16;  // Fixed-point left X
    int32_t xb = static_cast<int32_t>(x1 + p2->x) << 16;  // Fixed-point right X
    int32_t yl = y1;  // Current scanline
    
    while(count != 0) {
        int32_t dy = 0;
        const int32_t step1 = calc_step(*p1, *(p1 + 1), 0, dy);  // Left edge step
        const int32_t step2 = calc_step(*p2, *(p2 - 1), 0, dy);  // Right edge step
        
        // Round to nearest pixel
        xa = (xa & 0xffff0000) | 0x8000;
        xb = (xb & 0xffff0000) | 0x7fff;
        
        if(dy != 0) {
            do {
                draw_line((xa >> 16), (xb >> 16), yl);  // Draw scanline
                xa += step1;  // Advance left edge
                xb += step2;  // Advance right edge
                ++yl;         // Next scanline
            } while(--dy != 0);
        }
        ++p1; --count;  // Advance left edge pointer
        --p2; --count;  // Advance right edge pointer
    }
};
```

**Algorithm Characteristics:**
- **Fixed-Point Arithmetic**: Uses 16.16 fixed-point for sub-pixel accuracy
- **Dual-Edge Tracking**: Maintains left and right edges simultaneously
- **Edge Stepping**: Calculates step values for smooth edge interpolation
- **Scanline Filling**: Draws horizontal lines between edges

### 3. Edge Step Calculation (`calc_step`)

```cpp
auto calc_step = [&](const Point& p1, const Point& p2, int32_t dx, int32_t& dy) -> int32_t {
    dx = p2.x - p1.x;
    dy = p2.y - p1.y;
    return dx * _interpolate[dy] * 4;
};
```

**Mathematical Explanation:**
- `dx` is the horizontal distance between two points
- `dy` is the vertical distance between two points  
- `dx/dy` gives the slope of the edge
- `dx * (0x4000/dy) * 4` provides the step size per scanline in fixed-point
- The `* 4` factor provides additional precision for smooth edges
- Special case: when `dy = 0`, `_interpolate[0] = 0x4000` prevents division by zero

**Interpolation Table:**
The `_interpolate` array contains pre-calculated values for efficient division:
```cpp
auto init_interpolate = [&]() -> void {
    int index = 0;
    for(auto& value : _interpolate) {
        if(index == 0) {
            value = 0x4000;
        }
        else {
            value = 0x4000 / index;
        }
        ++index;
    }
};
```

### 4. Line Rendering Modes

The system supports three different line rendering modes based on color value:

#### Plain Rendering (`render_line_plain`)
- **Usage**: `color < 0x10` (solid colors 0-15)
- **Operation**: Direct color fill
- **Pixel Format**: 4-bit packed (2 pixels per byte)

```cpp
auto render_line_plain = +[](Page* dst, Page* src, int16_t x1, int16_t x2, int16_t yl, uint8_t color, uint32_t* pixelCount) -> void {
    uint16_t offset = (yl * BPL) + (x1 / PPB);
    uint8_t* dstptr = &dst->data[offset];
    uint16_t width = (x2 / PPB) - (x1 / PPB) + 1;
    
    // Handle odd pixel alignment
    uint8_t mask1 = 0, mask2 = 0;
    if((x1 & 1) != 0) {
        mask1 = 0xf0;  // Preserve left nibble
        --width;
    }
    if((x2 & 1) == 0) {
        mask2 = 0x0f;  // Preserve right nibble
        --width;
    }
    
    // Duplicate color to both nibbles
    color = ((color & 0x0f) << 4) | ((color & 0x0f) << 0);
    
    // Render with masks
    if(mask1 != 0) {
        *dstptr = (*dstptr & mask1) | (color & 0x0f);
        ++dstptr;
    }
    while(width--) {
        *dstptr = color;
        ++dstptr;
    }
    if(mask2 != 0) {
        *dstptr = (*dstptr & mask2) | (color & 0xf0);
        ++dstptr;
    }
    
    *pixelCount += (x2 - x1 + 1);  // Count pixels
};
```

#### Video Copy Rendering (`render_line_vcopy`)
- **Usage**: `color > 0x10` (video copy operations)
- **Operation**: Copies from source page to destination
- **Purpose**: Background compositing and effects

```cpp
auto render_line_vcopy = +[](Page* dst, Page* src, int16_t x1, int16_t x2, int16_t yl, uint8_t color, uint32_t* pixelCount) -> void {
    uint8_t* dstptr = &dst->data[offset];
    uint8_t* srcptr = &src->data[offset];
    
    // Similar masking logic as plain rendering
    // Copies source pixels to destination
    while(width--) {
        *dstptr++ = *srcptr++;
    }
    
    *pixelCount += (x2 - x1 + 1);
};
```

#### Blend Rendering (`render_line_blend`)
- **Usage**: `color == 0x10` (special blend mode)
- **Operation**: Applies blending effects
- **Masks**: Uses different masks (`0xf7`, `0x7f`) for blending

```cpp
auto render_line_blend = +[](Page* dst, Page* src, int16_t x1, int16_t x2, int16_t yl, uint8_t color, uint32_t* pixelCount) -> void {
    // Special blending masks
    if((x1 & 1) != 0) {
        mask1 = 0xf7;  // Different blend mask
        --width;
    }
    if((x2 & 1) == 0) {
        mask2 = 0x7f;  // Different blend mask
        --width;
    }
    
    // Apply blending operations
    if(mask1 != 0) {
        *dstptr = (*dstptr & mask1) | 0x08;
        ++dstptr;
    }
    while(width--) {
        *dstptr = (*dstptr | 0x88);  // Blend operation
        ++dstptr;
    }
    
    *pixelCount += (x2 - x1 + 1);
};
```

## Performance Optimizations

### 1. Early Clipping
- **Bounding Box Test**: Quick rejection of off-screen polygons
- **Point Optimization**: Single-pixel polygons handled specially
- **Screen Boundary Checks**: Per-line clipping in `draw_line`

### 2. Fixed-Point Arithmetic
- **Sub-pixel Accuracy**: 16.16 fixed-point prevents aliasing
- **Efficient Division**: Pre-calculated interpolation table
- **Rounding**: Proper rounding with `0x8000` and `0x7fff`

### 3. Memory Layout
- **4-bit Packed Format**: 2 pixels per byte for memory efficiency
- **Byte-aligned Operations**: Optimized for 8-bit processors
- **Mask-based Rendering**: Handles odd pixel alignments efficiently

## Usage Patterns

### Character Animation
- **Small Polygons**: Character body parts (4-6 vertices)
- **Frequent Updates**: Real-time animation with smooth scaling
- **Color Variations**: Different colors for different body parts

### Background Elements
- **Larger Polygons**: Background objects and scenery
- **Static Elements**: Less frequent updates
- **Blend Effects**: Special effects and compositing

## Data Format

### Polygon Buffer Format
```
[Polygon Type Byte]
- Bit 7-6: Type flags (0xC0 = single polygon)
- Bit 5-0: Color or flags

[Single Polygon Data]
- Byte 1: Bounding box width
- Byte 2: Bounding box height  
- Byte 3: Vertex count
- Bytes 4+: Vertex coordinates (x,y pairs)

[Hierarchical Polygon Data]
- Byte 1: Parent X offset
- Byte 2: Parent Y offset
- Byte 3: Child count + 1
- For each child:
  - Word: Child offset (with flags)
  - Byte: Child X offset
  - Byte: Child Y offset
  - Optional: Child color (if offset bit 15 set)
```

## Integration with Analytics

The polygon rendering system includes comprehensive analytics:

```cpp
// Log polygon drawing
LOG_POLYGON_DRAW(position.x, position.y, zoom, color, polygon.count);

// Count actual pixels drawn
uint32_t pixelsDrawn = 0;
*pixelCount += (x2 - x1 + 1);  // In each line renderer

// Log final pixel count
ANALYTICS.logPixelsDrawn(pixelsDrawn);
```

This provides detailed metrics for:
- **Polygon Operations**: Position, zoom, color, vertex count
- **Pixel Counts**: Real pixel counts per polygon and per frame
- **Performance Analysis**: Essential for 6502 Atari 800 porting

## Technical Notes

### Coordinate System
- **Origin**: Top-left corner (0,0)
- **Units**: Pixels (320x200 resolution)
- **Scaling**: Zoom factor applied to all coordinates
- **Clipping**: Screen boundaries enforced

### Edge Cases
- **Single Points**: Handled as special case for efficiency
- **Degenerate Polygons**: Zero-area polygons are clipped
- **Odd Alignments**: Proper handling of non-byte-aligned pixels
- **Boundary Conditions**: Careful edge pixel handling

### Memory Efficiency
- **Packed Format**: 4-bit pixels reduce memory usage by 50%
- **In-place Rendering**: Direct modification of frame buffer
- **Minimal Allocation**: Stack-based temporary variables only

This polygon rendering system represents a sophisticated balance between visual quality, performance, and memory efficiency, making it well-suited for real-time animation on limited hardware platforms.
