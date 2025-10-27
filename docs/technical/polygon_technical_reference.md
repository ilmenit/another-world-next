# Polygon Rendering Technical Reference

## Implementation Details

### Core Constants and Macros

```cpp
// Screen dimensions and layout
static constexpr int16_t XMIN =   0;  // Left screen boundary
static constexpr int16_t YMIN =   0;  // Top screen boundary  
static constexpr int16_t XMAX = 319;  // Right screen boundary
static constexpr int16_t YMAX = 199;  // Bottom screen boundary
static constexpr int16_t PPB  =   2;  // Pixels per byte (4-bit packed)
static constexpr int16_t BPL  = 160;  // Bytes per line (320/2)

// Fixed-point arithmetic constants
#define FIXED_POINT_SHIFT 16
#define FIXED_POINT_MULTIPLIER (1 << FIXED_POINT_SHIFT)
#define ROUND_LEFT  0x8000
#define ROUND_RIGHT 0x7fff
```

### Data Structure Definitions

```cpp
// Point structure for vertex coordinates
struct Point {
    int16_t x;  // X coordinate (-32768 to 32767)
    int16_t y;  // Y coordinate (-32768 to 32767)
};

// Polygon structure for rendering
struct Polygon {
    uint16_t bbw;        // Bounding box width
    uint16_t bbh;        // Bounding box height
    uint8_t  count;      // Number of vertices (must be even, max 50)
    Point    points[50]; // Vertex coordinates array
};

// Video page structure
struct Page {
    uint8_t id = 0;                    // Page identifier
    uint8_t data[((320 / 2) * 200)];  // Page data (32,000 bytes)
};
```

### Interpolation Table Initialization

```cpp
// Pre-calculated division table for efficient edge stepping
uint16_t _interpolate[0x400];  // 1024 entries

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

**Mathematical Foundation:**
- The interpolation table provides `0x4000/dy` values in fixed-point format
- This eliminates expensive division operations during edge stepping
- Each entry represents the reciprocal of `dy` scaled by `0x4000`
- Special case: `_interpolate[0] = 0x4000` prevents division by zero

### Edge Step Calculation Algorithm

```cpp
auto calc_step = [&](const Point& p1, const Point& p2, int32_t dx, int32_t& dy) -> int32_t {
    dx = p2.x - p1.x;  // X difference
    dy = p2.y - p1.y;  // Y difference
    
    // Return: dx * (0x4000/dy) * 4 in fixed-point
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

### Scanline Filling Algorithm

```cpp
auto fill_polygon = [&]() -> void {
    // Calculate bounding box coordinates
    const auto half_bbw = (full_bbw / 2);
    const auto half_bbh = (full_bbh / 2);
    const int16_t x1 = (position.x - half_bbw);
    const int16_t x2 = (position.x + half_bbw);
    const int16_t y1 = (position.y - half_bbh);
    const int16_t y2 = (position.y + half_bbh);
    
    // Early clipping test
    if((x1 > XMAX) || (x2 < XMIN) || (y1 > YMAX) || (y2 < YMIN)) {
        return;  // Polygon completely off-screen
    }
    
    // Special case: single pixel
    if(count == 4) {
        if(((full_bbw == 1) && (full_bbh <= 1)) ||
           ((full_bbh == 1) && (full_bbw <= 1))) {
            draw_point(position.x, position.y);
            return;
        }
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
        
        // Round to nearest pixel (fixed-point to integer conversion)
        xa = (xa & 0xffff0000) | ROUND_LEFT;   // Round left edge up
        xb = (xb & 0xffff0000) | ROUND_RIGHT;  // Round right edge down
        
        if(dy != 0) {
            do {
                // Draw horizontal line between edges
                draw_line((xa >> 16), (xb >> 16), yl);
                
                // Advance edges to next scanline
                xa += step1;  // Left edge step
                xb += step2;  // Right edge step
                ++yl;         // Next scanline
            } while(--dy != 0);
        } else {
            // Horizontal edge - just advance positions
            xa += step1;
            xb += step2;
        }
        
        // Advance edge pointers
        ++p1; --count;  // Move left pointer forward
        --p2; --count;  // Move right pointer backward
    }
};
```

### Line Rendering Implementation

#### Plain Color Rendering
```cpp
auto render_line_plain = +[](Page* dst, Page* src, int16_t x1, int16_t x2, int16_t yl, uint8_t color, uint32_t* pixelCount) -> void {
    // Calculate memory offset
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
    
    // Render with proper masking
    if(mask1 != 0) {
        *dstptr = (*dstptr & mask1) | (color & 0x0f);
        ++dstptr;
    }
    while(width--) {
        *dstptr = color;  // Write complete byte (2 pixels)
        ++dstptr;
    }
    if(mask2 != 0) {
        *dstptr = (*dstptr & mask2) | (color & 0xf0);
        ++dstptr;
    }
    
    // Count pixels for analytics
    *pixelCount += (x2 - x1 + 1);
};
```

#### Video Copy Rendering
```cpp
auto render_line_vcopy = +[](Page* dst, Page* src, int16_t x1, int16_t x2, int16_t yl, uint8_t color, uint32_t* pixelCount) -> void {
    uint16_t offset = (yl * BPL) + (x1 / PPB);
    uint8_t* dstptr = &dst->data[offset];
    uint8_t* srcptr = &src->data[offset];
    uint16_t width = (x2 / PPB) - (x1 / PPB) + 1;
    
    // Handle odd pixel alignment
    uint8_t mask1 = 0, mask2 = 0;
    if((x1 & 1) != 0) {
        mask1 = 0xf0;
        --width;
    }
    if((x2 & 1) == 0) {
        mask2 = 0x0f;
        --width;
    }
    
    // Copy with proper masking
    if(mask1 != 0) {
        *dstptr = (*dstptr & mask1) | (*srcptr & 0x0f);
        ++dstptr;
        ++srcptr;
    }
    while(width--) {
        *dstptr++ = *srcptr++;  // Copy complete bytes
    }
    if(mask2 != 0) {
        *dstptr = (*dstptr & mask2) | (*srcptr & 0xf0);
        ++dstptr;
        ++srcptr;
    }
    
    *pixelCount += (x2 - x1 + 1);
};
```

#### Blend Rendering
```cpp
auto render_line_blend = +[](Page* dst, Page* src, int16_t x1, int16_t x2, int16_t yl, uint8_t color, uint32_t* pixelCount) -> void {
    uint16_t offset = (yl * BPL) + (x1 / PPB);
    uint8_t* dstptr = &dst->data[offset];
    uint16_t width = (x2 / PPB) - (x1 / PPB) + 1;
    
    // Special blend masks
    uint8_t mask1 = 0, mask2 = 0;
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
    if(mask2 != 0) {
        *dstptr = (*dstptr & mask2) | 0x80;
        ++dstptr;
    }
    
    *pixelCount += (x2 - x1 + 1);
};
```

### Polygon Data Parsing

```cpp
auto read_and_fill_polygon_single = [&]() -> void {
    // Read polygon header
    _polygon.bbw = static_cast<uint16_t>(data.fetchByte()) * zoom / 64;
    _polygon.bbh = static_cast<uint16_t>(data.fetchByte()) * zoom / 64;
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
    
    // Render the polygon
    renderPolygon(_polygon, position, zoom, color);
};
```

### Hierarchical Polygon Support

```cpp
auto read_and_fill_polygon_hierarchy = [&]() {
    // Read parent offset
    Point parent_position(position);
    const uint16_t parent_x = static_cast<uint16_t>(data.fetchByte());
    const uint16_t parent_y = static_cast<uint16_t>(data.fetchByte());
    parent_position.x -= (parent_x * zoom) / 64;
    parent_position.y -= (parent_y * zoom) / 64;
    
    // Read child count
    int children = data.fetchByte() + 1;
    
    // Process each child
    do {
        Point child_position(parent_position);
        const uint8_t* child_buffer = buffer;
        uint16_t child_offset = data.fetchWordBE();
        uint16_t child_x = static_cast<uint16_t>(data.fetchByte());
        uint16_t child_y = static_cast<uint16_t>(data.fetchByte());
        uint16_t child_zoom = zoom;
        uint8_t child_color = 0xff;
        
        // Apply child offset
        child_position.x += (child_x * zoom) / 64;
        child_position.y += (child_y * zoom) / 64;
        
        // Handle child color override
        if(child_offset & 0x8000) {
            child_color = (data.fetchWordBE() >> 8) & 0x7f;
        }
        child_offset &= 0x7fff;
        child_offset *= 2;
        
        // Recursively render child
        renderPolygons(child_buffer, child_offset, child_position, child_zoom, child_color);
    } while(--children != 0);
};
```

## Performance Analysis

### Time Complexity
- **Polygon Parsing**: O(n) where n = vertex count
- **Bounding Box Calculation**: O(1)
- **Early Clipping**: O(1)
- **Scanline Filling**: O(h) where h = polygon height
- **Pixel Rendering**: O(w) where w = average scanline width
- **Overall**: O(n + h×w)

### Space Complexity
- **Additional Memory**: O(1) - in-place rendering only
- **Stack Usage**: Minimal - only temporary variables
- **Frame Buffer**: Direct modification of existing buffer

### Memory Access Patterns
- **Sequential Access**: Scanline-by-scanline rendering
- **Cache Friendly**: Linear memory access pattern
- **4-bit Packed**: Reduces memory bandwidth by 50%

### Optimization Techniques
1. **Early Clipping**: Quick rejection of off-screen polygons
2. **Fixed-Point Arithmetic**: Eliminates floating-point operations
3. **Pre-calculated Tables**: Interpolation table for efficient division
4. **Dual-Edge Tracking**: Simultaneous left/right edge processing
5. **Mask-based Rendering**: Efficient odd-pixel alignment handling

## Error Handling and Edge Cases

### Input Validation
```cpp
// Validate vertex count
assert(((_polygon.count & 1) == 0) && (_polygon.count < countof(_polygon.points)));

// Check for degenerate polygons
if(count == 4 && ((full_bbw == 1) && (full_bbh <= 1)) || 
                 ((full_bbh == 1) && (full_bbw <= 1))) {
    // Handle as single pixel
}
```

### Boundary Conditions
- **Screen Clipping**: Automatic clipping to screen boundaries
- **Odd Pixel Alignment**: Proper handling of non-byte-aligned pixels
- **Zero-Area Polygons**: Handled gracefully with early exit
- **Overflow Protection**: Fixed-point arithmetic prevents overflow

### Robustness Features
- **Null Pointer Checks**: Buffer validation before processing
- **Range Validation**: Coordinate bounds checking
- **Memory Safety**: Stack-based temporary variables only
- **Graceful Degradation**: Fallback to single pixel for edge cases

This technical reference provides the complete implementation details needed to understand, modify, or port the Another World polygon rendering algorithm to other platforms, including the 6502 Atari 800 target system.
