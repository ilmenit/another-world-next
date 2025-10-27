# Polygon Rendering Algorithm Flowchart

## High-Level Algorithm Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Polygon Rendering Pipeline                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. Parse Polygon Data from Buffer                              │
│    - Read bounding box (bbw, bbh)                              │
│    - Read vertex count                                         │
│    - Read vertex coordinates (x,y pairs)                      │
│    - Apply zoom scaling (coord * zoom / 64)                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Calculate Bounding Box                                      │
│    - half_bbw = bbw / 2                                        │
│    - half_bbh = bbh / 2                                        │
│    - x1 = position.x - half_bbw                                │
│    - x2 = position.x + half_bbw                                │
│    - y1 = position.y - half_bbh                                │
│    - y2 = position.y + half_bbh                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Early Clipping Test                                         │
│    if (x1 > XMAX || x2 < XMIN || y1 > YMAX || y2 < YMIN)      │
│        return; // Polygon completely off-screen               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Special Case: Single Point                                  │
│    if (count == 4 && (bbw <= 1 || bbh <= 1))                  │
│        draw_point(position.x, position.y);                    │
│        return;                                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Dual-Edge Scanline Algorithm                               │
│    - p1 = &points[0]           (left edge pointer)            │
│    - p2 = &points[count-1]     (right edge pointer)           │
│    - xa = (x1 + p1->x) << 16   (fixed-point left X)           │
│    - xb = (x1 + p2->x) << 16   (fixed-point right X)         │
│    - yl = y1                   (current scanline)            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Main Scanline Loop                                          │
│    while (count != 0) {                                        │
│        dy = 0;                                                 │
│        step1 = calc_step(*p1, *(p1+1), 0, dy);                │
│        step2 = calc_step(*p2, *(p2-1), 0, dy);                │
│        xa = (xa & 0xffff0000) | 0x8000;  // Round left        │
│        xb = (xb & 0xffff0000) | 0x7fff;  // Round right       │
│        if (dy != 0) {                                          │
│            do {                                                 │
│                draw_line((xa>>16), (xb>>16), yl);             │
│                xa += step1;                                     │
│                xb += step2;                                     │
│                ++yl;                                           │
│            } while (--dy != 0);                                │
│        }                                                       │
│        ++p1; --count;  // Advance left edge                    │
│        --p2; --count;  // Advance right edge                   │
│    }                                                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Line Rendering (per scanline)                               │
│    - Choose rendering mode based on color:                     │
│      * color < 0x10:  render_line_plain (solid fill)          │
│      * color > 0x10:  render_line_vcopy (video copy)          │
│      * color = 0x10:  render_line_blend (blend mode)         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. Pixel-Level Rendering                                       │
│    - Calculate byte offset: offset = (yl * BPL) + (x1 / PPB)  │
│    - Handle odd pixel alignment with masks                     │
│    - Render pixels in 4-bit packed format                     │
│    - Count pixels for analytics                               │
└─────────────────────────────────────────────────────────────────┘
```

## Edge Step Calculation

```
┌─────────────────────────────────────────────────────────────────┐
│                    calc_step Function                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Input: Point p1, Point p2, int32_t dx, int32_t& dy            │
│                                                                 │
│ dx = p2.x - p1.x;                                              │
│ dy = p2.y - p1.y;                                              │
│                                                                 │
│ return dx * _interpolate[dy] * 4;                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Interpolation Table (_interpolate)                            │
│                                                                 │
│ _interpolate[i] = 0x4000 / i (with special case for i=0)        │
│                                                                 │
│ This provides efficient division for edge stepping            │
└─────────────────────────────────────────────────────────────────┘
```

## Line Rendering Modes

```
┌─────────────────────────────────────────────────────────────────┐
│                    Line Rendering Decision Tree                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    color value                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│   color < 0x10          │ │   color > 0x10          │ │   color = 0x10          │
│                         │ │                         │ │                         │
│ render_line_plain       │ │ render_line_vcopy       │ │ render_line_blend       │
│                         │ │                         │ │                         │
│ • Solid color fill      │ │ • Video copy operation  │ │ • Special blend mode    │
│ • Direct pixel write    │ │ • Source to dest copy   │ │ • Blending effects      │
│ • Color duplication     │ │ • Background compositing│ │ • Different masks       │
│ • Standard masks        │ │ • Standard masks       │ │ • 0xf7, 0x7f masks     │
└─────────────────────────┘ └─────────────────────────┘ └─────────────────────────┘
```

## Memory Layout and Pixel Format

```
┌─────────────────────────────────────────────────────────────────┐
│                    4-bit Packed Pixel Format                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Screen Layout: 320x200 pixels                                  │
│                                                                 │
│ • 2 pixels per byte (4 bits each)                             │
│ • BPL (Bytes Per Line) = 160                                   │
│ • PPB (Pixels Per Byte) = 2                                    │
│                                                                 │
│ Byte Layout:                                                   │
│ ┌─────────────┬─────────────┐                                  │
│ │ Pixel N+1   │ Pixel N     │                                  │
│ │ (bits 7-4)  │ (bits 3-0)  │                                  │
│ └─────────────┴─────────────┘                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Odd Pixel Alignment Handling                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Left Edge (x1 & 1 != 0):                                      │
│ • mask1 = 0xf0 (preserve left nibble)                         │
│ • Write only right nibble                                      │
│ • Decrement width                                              │
│                                                                 │
│ Right Edge (x2 & 1 == 0):                                     │
│ • mask2 = 0x0f (preserve right nibble)                        │
│ • Write only left nibble                                       │
│ • Decrement width                                              │
│                                                                 │
│ Middle Bytes:                                                  │
│ • Write complete bytes (2 pixels each)                        │
└─────────────────────────────────────────────────────────────────┘
```

## Performance Characteristics

```
┌─────────────────────────────────────────────────────────────────┐
│                    Algorithm Complexity                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Time Complexity:                                               │
│ • Polygon parsing: O(n) where n = vertex count                │
│ • Scanline filling: O(h) where h = polygon height             │
│ • Pixel rendering: O(w) where w = scanline width              │
│ • Overall: O(n + h*w)                                         │
│                                                                 │
│ Space Complexity:                                              │
│ • O(1) additional space (in-place rendering)                  │
│ • Stack-based temporary variables only                        │
│                                                                 │
│ Memory Access Pattern:                                         │
│ • Sequential scanline access (cache-friendly)                 │
│ • 4-bit packed format (memory efficient)                      │
│ • Direct frame buffer modification                             │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Points

```
┌─────────────────────────────────────────────────────────────────┐
│                    System Integration                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Virtual Machine Integration:                                   │
│ • POLY1/POLY2 opcodes trigger polygon rendering                │
│ • Position, zoom, color passed from VM                         │
│ • Polygon data loaded from resource buffers                     │
│                                                                 │
│ Analytics Integration:                                          │
│ • LOG_POLYGON_DRAW: Logs polygon parameters                    │
│ • Pixel counting: Real pixel count per polygon                 │
│ • Frame statistics: Per-frame polygon metrics                   │
│                                                                 │
│ Resource Management:                                            │
│ • Polygon data stored in compressed format                     │
│ • Hierarchical polygon support                                 │
│ • Dynamic loading from game resources                          │
└─────────────────────────────────────────────────────────────────┘
```

This comprehensive documentation provides a complete understanding of the Another World polygon rendering algorithm, including its mathematical foundations, implementation details, and performance characteristics. The algorithm represents a sophisticated balance between visual quality and computational efficiency, making it well-suited for real-time animation on limited hardware platforms.
