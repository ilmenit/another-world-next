# Debugging Guide

## Overview

This guide provides comprehensive information on debugging the Another World Interpreter, including debugging tools, techniques, and common issues. Effective debugging is essential for development, maintenance, and troubleshooting.

## Debugging Tools

### Built-in Debugging

#### Debug Flags
The interpreter supports various debug flags for subsystem-specific debugging:

```bash
# Debug specific subsystems
./another-world.bin --debug-engine
./another-world.bin --debug-video
./another-world.bin --debug-audio
./another-world.bin --debug-vm
./another-world.bin --debug-resources
./another-world.bin --debug-input
./another-world.bin --debug-backend

# Debug all subsystems
./another-world.bin --debug-all

# Quiet mode (disable all debug output)
./another-world.bin --quiet
```

#### Debug Output
Debug output is controlled by the logger system:

```cpp
// Enable debug output
g_logger_mask |= LOG_DEBUG;

// Enable specific subsystem debugging
g_logger_mask |= SYS_ENGINE;
g_logger_mask |= SYS_VIDEO;
g_logger_mask |= SYS_AUDIO;
```

### External Debugging Tools

#### GDB (GNU Debugger)
**Purpose**: Source-level debugging for Linux builds

**Usage**:
```bash
# Compile with debug symbols
make -f Makefile.linux CXXFLAGS="-std=c++14 -O0 -g -Wall"

# Start debugging session
gdb ./bin/another-world.bin

# Set breakpoints
(gdb) break main
(gdb) break VirtualMachine::run
(gdb) break Video::drawPolygons

# Run with arguments
(gdb) run --debug-vm

# Debug commands
(gdb) step
(gdb) next
(gdb) continue
(gdb) print variable_name
(gdb) backtrace
```

#### Valgrind
**Purpose**: Memory debugging and profiling

**Usage**:
```bash
# Memory leak detection
valgrind --leak-check=full ./bin/another-world.bin

# Memory error detection
valgrind --tool=memcheck ./bin/another-world.bin

# Performance profiling
valgrind --tool=callgrind ./bin/another-world.bin
```

#### AddressSanitizer
**Purpose**: Memory error detection

**Usage**:
```bash
# Compile with AddressSanitizer
make -f Makefile.linux CXXFLAGS="-std=c++14 -O0 -g -Wall -fsanitize=address"

# Run with sanitizer
./bin/another-world.bin
```

## Debugging Techniques

### Logging and Tracing

#### Logger System
The logger system provides comprehensive debugging capabilities:

```cpp
// Debug macros
#ifndef NDEBUG
#define LOG_DEBUG(format, ...) log_debug(SYS_VM, format, ##__VA_ARGS__)
#else
#define LOG_DEBUG(format, ...) do {} while(0)
#endif

// Usage examples
LOG_DEBUG("Starting VM execution");
LOG_DEBUG("Register %d = 0x%04x", index, value);
LOG_DEBUG("Thread %d state: %d", threadId, state);
```

#### Instruction Tracing
Enable instruction tracing for VM debugging:

```cpp
auto VirtualMachine::executeInstruction(Thread& thread) -> void {
    LOG_DEBUG("PC: 0x%04x, Opcode: 0x%02x", thread.current_pc, thread.opcode);
    
    switch(thread.opcode) {
        case OP_SETR:
            LOG_DEBUG("SETR reg=%d, value=%d", reg, value);
            op_setr(thread);
            break;
        case OP_JUMP:
            LOG_DEBUG("JUMP address=0x%04x", address);
            op_jump(thread);
            break;
        // ... other instructions
    }
}
```

#### Performance Profiling
Monitor performance metrics:

```cpp
class PerformanceProfiler {
private:
    uint32_t _frameCount;
    uint32_t _totalTime;
    uint32_t _vmTime;
    uint32_t _videoTime;
    uint32_t _audioTime;
    
public:
    auto startFrame() -> void {
        _frameStart = getTicks();
    }
    
    auto endFrame() -> void {
        _frameTime = getTicks() - _frameStart;
        _totalTime += _frameTime;
        _frameCount++;
        
        if(_frameCount % 60 == 0) {
            log_debug("Average frame time: %d ms", _totalTime / _frameCount);
        }
    }
};
```

### Memory Debugging

#### Memory Pool Monitoring
Monitor memory pool usage:

```cpp
auto Resources::getMemoryUsage() -> void {
    size_t used = _bufptr - _buffer;
    size_t total = _bufend - _buffer;
    float percentage = (float)used / total * 100.0f;
    
    LOG_DEBUG("Memory usage: %zu/%zu bytes (%.1f%%)", used, total, percentage);
}
```

#### Resource Tracking
Track resource loading and usage:

```cpp
auto Resources::loadResource(uint16_t resourceId) -> void {
    LOG_DEBUG("Loading resource %d", resourceId);
    
    Resource* resource = getResource(resourceId);
    if(resource) {
        LOG_DEBUG("Resource %d: type=%d, size=%d, compressed=%s", 
                  resourceId, resource->type, resource->size, 
                  resource->compressed ? "yes" : "no");
    }
}
```

### Audio Debugging

#### Audio Channel Monitoring
Monitor audio channel states:

```cpp
auto Audio::debugChannels() -> void {
    for(int i = 0; i < 4; ++i) {
        if(_channels[i].active) {
            LOG_DEBUG("Channel %d: active, volume=%d, frequency=%d, position=%d/%d", 
                      i, _channels[i].volume, _channels[i].frequency,
                      _channels[i].samplePosition, _channels[i].sampleLength);
        }
    }
}
```

#### Audio Buffer Analysis
Analyze audio buffer content:

```cpp
auto Audio::analyzeBuffer(const float* buffer, int samples) -> void {
    float min = 0.0f, max = 0.0f, sum = 0.0f;
    
    for(int i = 0; i < samples; ++i) {
        min = std::min(min, buffer[i]);
        max = std::max(max, buffer[i]);
        sum += std::abs(buffer[i]);
    }
    
    float average = sum / samples;
    LOG_DEBUG("Audio buffer: min=%.3f, max=%.3f, avg=%.3f", min, max, average);
}
```

### Video Debugging

#### Page State Monitoring
Monitor video page states:

```cpp
auto Video::debugPages() -> void {
    for(int i = 0; i < 4; ++i) {
        LOG_DEBUG("Page %d: dirty=%s, size=%d", 
                  i, _pages[i].dirty ? "yes" : "no", PAGE_SIZE);
    }
}
```

#### Polygon Rendering Debug
Debug polygon rendering:

```cpp
auto Video::debugPolygon(const Polygon& polygon) -> void {
    LOG_DEBUG("Polygon: points=%d, color=0x%04x, filled=%s", 
              polygon.pointCount, polygon.color, 
              polygon.filled ? "yes" : "no");
    
    for(int i = 0; i < polygon.pointCount; ++i) {
        LOG_DEBUG("  Point %d: (%d, %d)", i, polygon.points[i].x, polygon.points[i].y);
    }
}
```

## Common Issues and Solutions

### Memory Issues

#### Memory Leaks
**Symptoms**: Increasing memory usage over time
**Debugging**:
```bash
# Use Valgrind to detect leaks
valgrind --leak-check=full ./bin/another-world.bin

# Use AddressSanitizer
make -f Makefile.linux CXXFLAGS="-fsanitize=address"
./bin/another-world.bin
```

**Solutions**:
- Use smart pointers
- Implement RAII
- Check resource cleanup

#### Buffer Overflows
**Symptoms**: Crashes, corrupted data
**Debugging**:
```bash
# Use AddressSanitizer
make -f Makefile.linux CXXFLAGS="-fsanitize=address"
./bin/another-world.bin
```

**Solutions**:
- Add bounds checking
- Use safe array access
- Validate input data

### Audio Issues

#### Audio Dropouts
**Symptoms**: Audio stuttering, gaps in playback
**Debugging**:
```cpp
// Monitor audio buffer underruns
auto Audio::checkBufferUnderrun() -> void {
    if(_bufferUnderrun) {
        LOG_DEBUG("Audio buffer underrun detected");
        _bufferUnderrun = false;
    }
}
```

**Solutions**:
- Increase buffer size
- Optimize audio processing
- Check timing synchronization

#### Audio Distortion
**Symptoms**: Crackling, distortion in audio
**Debugging**:
```cpp
// Check for clipping
auto Audio::checkClipping(const float* buffer, int samples) -> void {
    for(int i = 0; i < samples; ++i) {
        if(std::abs(buffer[i]) > 1.0f) {
            LOG_DEBUG("Audio clipping detected at sample %d", i);
        }
    }
}
```

**Solutions**:
- Reduce volume levels
- Check sample rate conversion
- Validate audio data

### Video Issues

#### Rendering Artifacts
**Symptoms**: Visual glitches, corrupted graphics
**Debugging**:
```cpp
// Validate page data
auto Video::validatePage(const Page& page) -> void {
    for(int i = 0; i < PAGE_SIZE; ++i) {
        if(page.data[i] > 15) {
            LOG_DEBUG("Invalid pixel value %d at offset %d", page.data[i], i);
        }
    }
}
```

**Solutions**:
- Check page bounds
- Validate palette data
- Verify polygon data

#### Performance Issues
**Symptoms**: Low frame rate, stuttering
**Debugging**:
```cpp
// Profile rendering performance
auto Video::profileRendering() -> void {
    uint32_t start = getTicks();
    renderFrame();
    uint32_t end = getTicks();
    
    LOG_DEBUG("Rendering time: %d ms", end - start);
}
```

**Solutions**:
- Optimize rendering algorithms
- Reduce polygon complexity
- Use efficient data structures

### VM Issues

#### Infinite Loops
**Symptoms**: Game freezes, high CPU usage
**Debugging**:
```cpp
// Add loop detection
auto VirtualMachine::detectInfiniteLoop(Thread& thread) -> void {
    static uint32_t lastPC = 0;
    static uint32_t loopCount = 0;
    
    if(thread.current_pc == lastPC) {
        loopCount++;
        if(loopCount > 1000) {
            LOG_DEBUG("Infinite loop detected at PC 0x%04x", thread.current_pc);
            thread.current_state = THREAD_HALTED;
        }
    } else {
        loopCount = 0;
    }
    
    lastPC = thread.current_pc;
}
```

**Solutions**:
- Add loop detection
- Implement timeout mechanisms
- Validate bytecode

#### Register Corruption
**Symptoms**: Incorrect game behavior, crashes
**Debugging**:
```cpp
// Monitor register changes
auto VirtualMachine::monitorRegister(uint8_t index) -> void {
    static uint16_t lastValue = 0;
    uint16_t currentValue = _registers[index].u;
    
    if(currentValue != lastValue) {
        LOG_DEBUG("Register %d changed: 0x%04x -> 0x%04x", 
                  index, lastValue, currentValue);
        lastValue = currentValue;
    }
}
```

**Solutions**:
- Add register validation
- Check instruction implementation
- Validate memory access

## Debugging Workflow

### Step-by-Step Debugging Process

1. **Reproduce the Issue**
   - Identify the exact conditions that cause the problem
   - Create a minimal test case if possible
   - Document the expected vs. actual behavior

2. **Enable Debugging**
   - Use appropriate debug flags
   - Enable logging for relevant subsystems
   - Set up breakpoints if using a debugger

3. **Analyze the Output**
   - Review debug logs for errors or anomalies
   - Look for patterns in the behavior
   - Identify the root cause

4. **Implement a Fix**
   - Make minimal changes to fix the issue
   - Test the fix thoroughly
   - Ensure no regressions

5. **Verify the Solution**
   - Test under various conditions
   - Verify performance impact
   - Document the fix

### Debugging Checklist

- [ ] Issue is reproducible
- [ ] Debug output is enabled
- [ ] Logs are analyzed
- [ ] Root cause is identified
- [ ] Fix is implemented
- [ ] Fix is tested
- [ ] No regressions introduced
- [ ] Documentation is updated

## Performance Debugging

### Profiling Tools

#### CPU Profiling
```bash
# Use gprof for CPU profiling
make -f Makefile.linux CXXFLAGS="-std=c++14 -O2 -g -pg"
./bin/another-world.bin
gprof ./bin/another-world.bin gmon.out > profile.txt
```

#### Memory Profiling
```bash
# Use Valgrind for memory profiling
valgrind --tool=massif ./bin/another-world.bin
ms_print massif.out.* > memory_profile.txt
```

#### Call Graph Analysis
```bash
# Use callgrind for call graph analysis
valgrind --tool=callgrind ./bin/another-world.bin
callgrind_annotate callgrind.out.* > callgraph.txt
```

### Performance Metrics

#### Frame Rate Monitoring
```cpp
class FrameRateMonitor {
private:
    uint32_t _frameCount;
    uint32_t _lastTime;
    float _fps;
    
public:
    auto update() -> void {
        _frameCount++;
        uint32_t currentTime = getTicks();
        
        if(currentTime - _lastTime >= 1000) {
            _fps = _frameCount * 1000.0f / (currentTime - _lastTime);
            LOG_DEBUG("FPS: %.1f", _fps);
            _frameCount = 0;
            _lastTime = currentTime;
        }
    }
};
```

#### Memory Usage Monitoring
```cpp
auto monitorMemoryUsage() -> void {
    size_t used = _bufptr - _buffer;
    size_t total = _bufend - _buffer;
    float percentage = (float)used / total * 100.0f;
    
    LOG_DEBUG("Memory: %zu/%zu bytes (%.1f%%)", used, total, percentage);
}
```

## Debugging Best Practices

### General Principles
- **Start Simple**: Begin with basic debugging techniques
- **Use Tools**: Leverage available debugging tools
- **Document Issues**: Keep detailed records of problems and solutions
- **Test Thoroughly**: Verify fixes under various conditions

### Code Quality
- **Add Assertions**: Use assertions to catch errors early
- **Validate Input**: Check all input data for validity
- **Handle Errors**: Implement proper error handling
- **Use Logging**: Add comprehensive logging

### Maintenance
- **Regular Testing**: Test regularly during development
- **Monitor Performance**: Keep track of performance metrics
- **Update Documentation**: Keep debugging documentation current
- **Share Knowledge**: Document solutions for future reference

This debugging guide provides comprehensive information for troubleshooting the Another World Interpreter, enabling effective problem identification and resolution.
