# Coding Standards

## Overview

This document outlines the coding standards and conventions used in the Another World Interpreter project. These standards ensure code consistency, readability, and maintainability across the entire codebase.

## General Principles

### Code Quality
- **Readability**: Code should be self-documenting and easy to understand
- **Consistency**: Follow established patterns and conventions
- **Maintainability**: Code should be easy to modify and extend
- **Performance**: Optimize for performance where appropriate
- **Safety**: Use safe coding practices to prevent bugs

### Modern C++ Practices
- **C++14 Standard**: Use C++14 features and idioms
- **RAII**: Resource Acquisition Is Initialization
- **Smart Pointers**: Prefer smart pointers over raw pointers
- **const Correctness**: Use const wherever appropriate
- **Exception Safety**: Write exception-safe code

## Naming Conventions

### Files and Directories

#### Source Files
- **C++ Files**: Use `.cc` extension for implementation files
- **Header Files**: Use `.h` extension for header files
- **Naming**: Use lowercase with underscores (snake_case)

**Examples**:
```
src/main.cc
src/engine.h
src/virtual_machine.cc
src/audio_system.h
```

#### Directories
- **Naming**: Use lowercase with underscores
- **Structure**: Organize by functionality

**Examples**:
```
src/
docs/
game_systems/
technical/
```

### Identifiers

#### Classes and Structs
- **Naming**: Use PascalCase (CamelCase with first letter capitalized)
- **Prefixes**: No prefixes for classes

**Examples**:
```cpp
class VirtualMachine { ... };
struct AudioSample { ... };
class SDL2Backend { ... };
```

#### Functions and Methods
- **Naming**: Use camelCase
- **Prefixes**: Use descriptive prefixes for clarity

**Examples**:
```cpp
auto processEvents() -> void;
auto getResource(uint16_t id) -> Resource*;
auto setRegister(uint8_t index, uint16_t value) -> void;
```

#### Variables
- **Naming**: Use camelCase
- **Prefixes**: Use descriptive prefixes

**Examples**:
```cpp
uint32_t currentTicks;
uint8_t* sampleData;
bool isActive;
```

#### Constants
- **Naming**: Use UPPER_CASE with underscores
- **Prefixes**: Use descriptive prefixes

**Examples**:
```cpp
static constexpr uint32_t PAGE_SIZE = 32000;
static constexpr uint8_t MAX_THREADS = 64;
static constexpr int16_t SCREEN_WIDTH = 320;
```

#### Enumerations
- **Naming**: Use PascalCase for enum names
- **Values**: Use UPPER_CASE with underscores

**Examples**:
```cpp
enum ResourceType {
    RESOURCE_BITMAP = 0,
    RESOURCE_SOUND = 1,
    RESOURCE_MUSIC = 2
};

enum LogLevel {
    LOG_DEBUG = 0x01,
    LOG_ERROR = 0x08
};
```

## Code Formatting

### Indentation
- **Style**: Use 4 spaces for indentation
- **Tabs**: Never use tabs
- **Alignment**: Align code for readability

**Example**:
```cpp
class Example {
public:
    auto processData(const uint8_t* data, size_t size) -> void {
        if(data && size > 0) {
            for(size_t i = 0; i < size; ++i) {
                processByte(data[i]);
            }
        }
    }
};
```

### Braces
- **Style**: Use Allman style (braces on separate lines)
- **Consistency**: Always use braces, even for single statements

**Example**:
```cpp
if(condition) {
    doSomething();
} else {
    doSomethingElse();
}

for(int i = 0; i < count; ++i) {
    processItem(i);
}
```

### Line Length
- **Maximum**: 100 characters per line
- **Breaking**: Break long lines at logical points
- **Indentation**: Indent continuation lines appropriately

**Example**:
```cpp
auto longFunctionName(const std::string& parameter1,
                      const std::string& parameter2,
                      const std::string& parameter3) -> void {
    // Function implementation
}
```

### Spacing
- **Operators**: Space around operators
- **Commas**: Space after commas
- **Keywords**: Space after keywords
- **Functions**: No space before parentheses

**Example**:
```cpp
if(condition1 && condition2) {
    result = value1 + value2;
    callFunction(param1, param2, param3);
}
```

## Documentation

### Comments
- **Purpose**: Explain why, not what
- **Style**: Use C++ style comments (`//`)
- **Placement**: Place comments above the code they describe

**Example**:
```cpp
// Process audio samples for the current frame
auto processAudio(float* buffer, int samples) -> void {
    // Clear buffer to prevent audio artifacts
    std::memset(buffer, 0, samples * sizeof(float));
    
    // Mix all active channels
    for(int i = 0; i < 4; ++i) {
        if(_channels[i].active) {
            mixChannel(buffer, samples, _channels[i]);
        }
    }
}
```

### Header Comments
- **Purpose**: File identification and copyright
- **Format**: Standard header format

**Example**:
```cpp
/*
 * filename.cc - Copyright (c) 2004-2025
 *
 * Gregory Montoir, Fabien Sanglard, Olivier Poncet
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
```

### Function Documentation
- **Purpose**: Document function behavior and parameters
- **Format**: Use Doxygen-style comments

**Example**:
```cpp
/**
 * @brief Processes audio samples for the current frame
 * @param buffer Audio buffer to process
 * @param samples Number of samples to process
 * @return void
 */
auto processAudio(float* buffer, int samples) -> void;
```

## Memory Management

### Smart Pointers
- **Preference**: Use smart pointers over raw pointers
- **Types**: Use `std::unique_ptr` and `std::shared_ptr` appropriately

**Example**:
```cpp
class ResourceManager {
private:
    std::unique_ptr<Resource> _resource;
    std::shared_ptr<AudioSystem> _audioSystem;
    
public:
    auto loadResource(const std::string& path) -> void {
        _resource = std::make_unique<Resource>(path);
    }
};
```

### RAII
- **Principle**: Acquire resources in constructors, release in destructors
- **Implementation**: Use RAII for all resource management

**Example**:
```cpp
class File {
private:
    FILE* _file;
    
public:
    File(const std::string& path) : _file(std::fopen(path.c_str(), "rb")) {
        if(!_file) {
            throw std::runtime_error("Failed to open file");
        }
    }
    
    ~File() {
        if(_file) {
            std::fclose(_file);
        }
    }
};
```

### Memory Safety
- **Bounds Checking**: Always check array bounds
- **Null Checks**: Check pointers before dereferencing
- **Initialization**: Initialize all variables

**Example**:
```cpp
auto processArray(const uint8_t* data, size_t size) -> void {
    if(!data || size == 0) {
        return;
    }
    
    for(size_t i = 0; i < size; ++i) {
        processByte(data[i]);
    }
}
```

## Error Handling

### Exception Safety
- **Principle**: Write exception-safe code
- **Types**: Use appropriate exception types
- **Handling**: Handle exceptions at appropriate levels

**Example**:
```cpp
auto loadResource(const std::string& path) -> std::unique_ptr<Resource> {
    try {
        auto resource = std::make_unique<Resource>(path);
        return resource;
    } catch(const std::exception& e) {
        log_error("Failed to load resource: %s", e.what());
        return nullptr;
    }
}
```

### Error Codes
- **Usage**: Use error codes for recoverable errors
- **Format**: Use consistent error code format

**Example**:
```cpp
enum ErrorCode {
    ERROR_SUCCESS = 0,
    ERROR_FILE_NOT_FOUND = 1,
    ERROR_INVALID_FORMAT = 2,
    ERROR_OUT_OF_MEMORY = 3
};

auto processFile(const std::string& path) -> ErrorCode {
    if(!std::filesystem::exists(path)) {
        return ERROR_FILE_NOT_FOUND;
    }
    
    // Process file
    return ERROR_SUCCESS;
}
```

## Performance

### Optimization
- **Profile**: Profile before optimizing
- **Target**: Optimize hot paths
- **Measure**: Measure performance improvements

**Example**:
```cpp
// Optimized version using lookup table
auto processPixel(uint8_t pixel) -> uint8_t {
    static const uint8_t lookupTable[256] = {
        // Precomputed values
    };
    
    return lookupTable[pixel];
}
```

### Memory Access
- **Locality**: Optimize for cache locality
- **Alignment**: Use appropriate alignment
- **Allocation**: Minimize dynamic allocation

**Example**:
```cpp
class OptimizedProcessor {
private:
    uint8_t _buffer[1024];  // Stack allocation
    uint8_t* _ptr;
    
public:
    OptimizedProcessor() : _ptr(_buffer) {}
    
    auto processData(const uint8_t* data, size_t size) -> void {
        // Process data in cache-friendly chunks
        const size_t chunkSize = 64;
        for(size_t i = 0; i < size; i += chunkSize) {
            size_t currentChunk = std::min(chunkSize, size - i);
            processChunk(data + i, currentChunk);
        }
    }
};
```

## Testing

### Unit Testing
- **Coverage**: Aim for high test coverage
- **Isolation**: Test units in isolation
- **Mocking**: Use mocks for dependencies

**Example**:
```cpp
class TestAudioSystem {
public:
    auto testPlaySound() -> void {
        AudioSystem audio;
        auto result = audio.playSound(1, 0, 128, 1);
        assert(result == true);
    }
    
    auto testVolumeControl() -> void {
        AudioSystem audio;
        audio.setVolume(0, 64);
        assert(audio.getVolume(0) == 64);
    }
};
```

### Integration Testing
- **Scope**: Test system integration
- **Data**: Use realistic test data
- **Environment**: Test in target environment

**Example**:
```cpp
class TestGameIntegration {
public:
    auto testGameLoop() -> void {
        Engine engine("test_data");
        engine.start();
        
        // Simulate game loop
        for(int i = 0; i < 100; ++i) {
            engine.processFrame();
        }
        
        engine.stop();
    }
};
```

## Build System

### Makefiles
- **Structure**: Use consistent Makefile structure
- **Variables**: Use descriptive variable names
- **Targets**: Use standard target names

**Example**:
```makefile
# Compiler settings
CXX = g++
CXXFLAGS = -std=c++14 -O2 -Wall -Wextra

# Source files
SOURCES = src/main.cc src/engine.cc src/vm.cc
OBJECTS = $(SOURCES:.cc=.o)

# Default target
all: $(TARGET)

# Build target
$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $@ $^

# Clean target
clean:
	rm -f $(OBJECTS) $(TARGET)
```

### CMake (Alternative)
- **Structure**: Use modern CMake practices
- **Targets**: Use target-based approach
- **Options**: Use options for configuration

**Example**:
```cmake
cmake_minimum_required(VERSION 3.10)
project(AnotherWorld)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Options
option(BUILD_WASM "Build WebAssembly version" OFF)
option(ENABLE_DEBUG "Enable debug build" OFF)

# Source files
set(SOURCES
    src/main.cc
    src/engine.cc
    src/vm.cc
)

# Create executable
add_executable(another-world ${SOURCES})

# Link libraries
target_link_libraries(another-world SDL2 z)
```

## Version Control

### Git Workflow
- **Branches**: Use feature branches
- **Commits**: Write descriptive commit messages
- **History**: Keep clean commit history

**Example**:
```bash
# Feature branch
git checkout -b feature/audio-improvements

# Commit with descriptive message
git commit -m "Add multi-channel audio mixing

- Implement 4-channel audio mixer
- Add volume control per channel
- Optimize audio processing performance"

# Merge to main
git checkout main
git merge feature/audio-improvements
```

### Commit Messages
- **Format**: Use conventional commit format
- **Description**: Write clear, descriptive messages
- **Scope**: Include affected components

**Example**:
```
feat(audio): add multi-channel audio mixing

- Implement 4-channel audio mixer
- Add volume control per channel
- Optimize audio processing performance

Closes #123
```

## Code Review

### Review Process
- **Checklist**: Use review checklist
- **Focus**: Focus on code quality and correctness
- **Feedback**: Provide constructive feedback

### Review Checklist
- [ ] Code follows naming conventions
- [ ] Code is properly formatted
- [ ] Documentation is complete
- [ ] Error handling is appropriate
- [ ] Performance is acceptable
- [ ] Tests are included
- [ ] Security considerations are addressed

## Tools and Utilities

### Code Formatting
- **clang-format**: Use clang-format for consistent formatting
- **Configuration**: Use project-specific configuration

**Example**:
```yaml
# .clang-format
BasedOnStyle: LLVM
IndentWidth: 4
TabWidth: 4
UseTab: Never
ColumnLimit: 100
BreakBeforeBraces: Allman
```

### Static Analysis
- **clang-tidy**: Use clang-tidy for static analysis
- **Configuration**: Use project-specific rules

**Example**:
```yaml
# .clang-tidy
Checks: >
  -*,readability-*,performance-*,modernize-*
HeaderFilterRegex: '.*'
```

### Documentation
- **Doxygen**: Use Doxygen for API documentation
- **Configuration**: Use project-specific configuration

**Example**:
```doxygen
# Doxyfile
PROJECT_NAME = "Another World Interpreter"
INPUT = src/
OUTPUT_DIRECTORY = docs/
GENERATE_HTML = YES
GENERATE_LATEX = NO
```

These coding standards ensure consistency, readability, and maintainability across the Another World Interpreter project, enabling effective collaboration and long-term maintenance.
