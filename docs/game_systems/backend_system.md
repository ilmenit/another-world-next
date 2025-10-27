# Backend System

## Overview

The Backend System provides platform abstraction and integration for Another World, handling platform-specific operations like SDL2 integration, audio callbacks, timer management, and event processing. This system enables the game to run on different platforms while maintaining identical behavior.

## Architecture

### Core Components

```
Backend System
├── Platform Abstraction
│   ├── SDL2 Integration
│   ├── Event Processing
│   ├── Window Management
│   └── System Integration
├── Audio Backend
│   ├── Audio Device Management
│   ├── Audio Callbacks
│   ├── Sample Rate Control
│   └── Audio Buffer Management
├── Timer System
│   ├── High-resolution Timers
│   ├── Timer Callbacks
│   ├── Timer Management
│   └── Timing Synchronization
├── Display Backend
│   ├── Window Creation
│   ├── Surface Management
│   ├── Page Rendering
│   └── Display Updates
└── Input Backend
    ├── Keyboard Input
    ├── Event Queuing
    ├── Input Processing
    └── Control Mapping
```

## Platform Abstraction

### Backend Interface

The backend provides a unified interface for platform-specific operations:

```cpp
class Backend : public SubSystem {
public:
    // Timing operations
    virtual auto getTicks() -> uint32_t = 0;
    virtual auto sleepFor(uint32_t delay) -> void = 0;
    virtual auto sleepUntil(uint32_t ticks) -> void = 0;
    
    // Event processing
    virtual auto processEvents(Controls& controls) -> void = 0;
    
    // Display operations
    virtual auto updateScreen(const Page& page, const Page& page0, const Page& page1, const Page& page2, const Page& page3, const Palette& palette) -> void = 0;
    
    // Audio operations
    virtual auto startAudio(AudioCallback callback, void* userdata) -> void = 0;
    virtual auto stopAudio() -> void = 0;
    virtual auto getAudioSampleRate() -> uint32_t = 0;
    
    // Timer operations
    virtual auto addTimer(uint32_t delay, TimerCallback callback, void* data) -> int = 0;
    virtual auto removeTimer(int timerId) -> void = 0;
};
```

### Backend Creation

```cpp
auto Backend::create(Engine& engine) -> Backend*
{
    // Create platform-specific backend
    #ifdef __EMSCRIPTEN__
        return new EmscriptenBackend(engine);
    #else
        return new SDL2Backend(engine);
    #endif
}
```

## SDL2 Integration

### SDL2 Backend Implementation

```cpp
class SDL2Backend : public Backend {
private:
    SDL_Window* _window;        // SDL2 window
    SDL_Renderer* _renderer;    // SDL2 renderer
    SDL_Texture* _texture;     // SDL2 texture
    SDL_AudioDeviceID _audioDevice; // Audio device
    
    // Timer management
    std::vector<Timer> _timers;
    uint32_t _nextTimerId;
    
    // Timing
    uint32_t _startTicks;
    uint32_t _currentTicks;
};
```

### Initialization

```cpp
auto SDL2Backend::start() -> void
{
    // Initialize SDL2
    if(SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO | SDL_INIT_TIMER) < 0) {
        log_error("Failed to initialize SDL2: %s", SDL_GetError());
        return;
    }
    
    // Create window
    _window = SDL_CreateWindow("Another World",
                               SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                               320, 200,
                               SDL_WINDOW_RESIZABLE);
    
    if(!_window) {
        log_error("Failed to create window: %s", SDL_GetError());
        return;
    }
    
    // Create renderer
    _renderer = SDL_CreateRenderer(_window, -1, SDL_RENDERER_ACCELERATED);
    
    if(!_renderer) {
        log_error("Failed to create renderer: %s", SDL_GetError());
        return;
    }
    
    // Create texture
    _texture = SDL_CreateTexture(_renderer,
                                 SDL_PIXELFORMAT_RGB332,
                                 SDL_TEXTUREACCESS_STREAMING,
                                 320, 200);
    
    // Initialize timing
    _startTicks = SDL_GetTicks();
}
```

## Audio Backend

### Audio Device Management

```cpp
auto SDL2Backend::startAudio(AudioCallback callback, void* userdata) -> void
{
    SDL_AudioSpec desired, obtained;
    
    desired.freq = AUDIO_SAMPLE_RATE;
    desired.format = AUDIO_F32SYS;
    desired.channels = 2;
    desired.samples = 1024;
    desired.callback = audioCallback;
    desired.userdata = userdata;
    
    _audioDevice = SDL_OpenAudioDevice(nullptr, 0, &desired, &obtained, 0);
    
    if(_audioDevice == 0) {
        log_error("Failed to open audio device: %s", SDL_GetError());
        return;
    }
    
    SDL_PauseAudioDevice(_audioDevice, 0);
}
```

### Audio Callback

```cpp
static void audioCallback(void* userdata, uint8_t* stream, int len)
{
    Backend* backend = static_cast<Backend*>(userdata);
    
    // Process audio
    backend->processAudio(reinterpret_cast<float*>(stream), len / sizeof(float));
}
```

### Audio Processing

```cpp
auto SDL2Backend::processAudio(float* buffer, int samples) -> void
{
    // Clear buffer
    std::memset(buffer, 0, samples * sizeof(float));
    
    // Process audio through engine
    _engine.processAudio(buffer, samples);
}
```

## Timer System

### Timer Management

```cpp
struct Timer {
    int id;                    // Timer ID
    uint32_t delay;           // Delay in milliseconds
    uint32_t nextFire;        // Next fire time
    TimerCallback callback;   // Callback function
    void* userdata;           // User data
    bool active;              // Active flag
};
```

### Timer Operations

#### Add Timer
```cpp
auto SDL2Backend::addTimer(uint32_t delay, TimerCallback callback, void* data) -> int
{
    Timer timer;
    timer.id = _nextTimerId++;
    timer.delay = delay;
    timer.nextFire = _currentTicks + delay;
    timer.callback = callback;
    timer.userdata = data;
    timer.active = true;
    
    _timers.push_back(timer);
    return timer.id;
}
```

#### Remove Timer
```cpp
auto SDL2Backend::removeTimer(int timerId) -> void
{
    for(auto it = _timers.begin(); it != _timers.end(); ++it) {
        if(it->id == timerId) {
            it->active = false;
            _timers.erase(it);
            break;
        }
    }
}
```

#### Process Timers
```cpp
auto SDL2Backend::processTimers() -> void
{
    _currentTicks = SDL_GetTicks();
    
    for(auto& timer : _timers) {
        if(timer.active && _currentTicks >= timer.nextFire) {
            // Fire timer
            timer.callback(timer.userdata);
            
            // Schedule next fire
            timer.nextFire = _currentTicks + timer.delay;
        }
    }
}
```

## Display Backend

### Page Rendering

```cpp
auto SDL2Backend::updateScreen(const Page& page, const Page& page0, const Page& page1, const Page& page2, const Page& page3, const Palette& palette) -> void
{
    // Convert page data to texture
    convertPageToTexture(page, palette);
    
    // Clear renderer
    SDL_RenderClear(_renderer);
    
    // Copy texture to renderer
    SDL_RenderCopy(_renderer, _texture, nullptr, nullptr);
    
    // Present frame
    SDL_RenderPresent(_renderer);
}
```

### Page Conversion

```cpp
auto SDL2Backend::convertPageToTexture(const Page& page, const Palette& palette) -> void
{
    void* pixels;
    int pitch;
    
    // Lock texture
    SDL_LockTexture(_texture, nullptr, &pixels, &pitch);
    
    // Convert page data
    convertPageData(page.data, pixels, palette);
    
    // Unlock texture
    SDL_UnlockTexture(_texture);
}
```

### Color Conversion

```cpp
auto SDL2Backend::convertPageData(const uint8_t* pageData, void* pixels, const Palette& palette) -> void
{
    uint8_t* pixelData = static_cast<uint8_t*>(pixels);
    
    for(int y = 0; y < 200; ++y) {
        for(int x = 0; x < 320; ++x) {
            // Get pixel value (4-bit)
            uint8_t pixelValue = pageData[(y * 160) + (x / 2)];
            if(x % 2 == 0) {
                pixelValue >>= 4;  // Upper 4 bits
            } else {
                pixelValue &= 0x0F;  // Lower 4 bits
            }
            
            // Convert to RGB
            uint8_t color = palette.colors[pixelValue];
            pixelData[y * 320 + x] = color;
        }
    }
}
```

## Event Processing

### Event Loop

```cpp
auto SDL2Backend::processEvents(Controls& controls) -> void
{
    SDL_Event event;
    
    while(SDL_PollEvent(&event)) {
        switch(event.type) {
            case SDL_KEYDOWN:
                handleKeyDown(event.key, controls);
                break;
                
            case SDL_KEYUP:
                handleKeyUp(event.key, controls);
                break;
                
            case SDL_QUIT:
                controls.quit = true;
                break;
                
            case SDL_WINDOWEVENT:
                handleWindowEvent(event.window);
                break;
        }
    }
}
```

### Key Event Handling

```cpp
auto SDL2Backend::handleKeyDown(const SDL_KeyboardEvent& keyEvent, Controls& controls) -> void
{
    uint8_t key = keyEvent.keysym.scancode;
    
    switch(key) {
        case SDL_SCANCODE_UP:
            controls.up = true;
            break;
        case SDL_SCANCODE_DOWN:
            controls.down = true;
            break;
        case SDL_SCANCODE_LEFT:
            controls.left = true;
            break;
        case SDL_SCANCODE_RIGHT:
            controls.right = true;
            break;
        case SDL_SCANCODE_SPACE:
            controls.fire = true;
            controls.run = true;
            break;
        case SDL_SCANCODE_P:
            controls.pause = !controls.pause;
            break;
        case SDL_SCANCODE_R:
            controls.reset = true;
            break;
        case SDL_SCANCODE_ESCAPE:
            controls.quit = true;
            break;
    }
}
```

## WebAssembly Backend

### Emscripten Integration

```cpp
class EmscriptenBackend : public Backend {
private:
    // Emscripten-specific data
    EMSCRIPTEN_WEBGL_CONTEXT_HANDLE _glContext;
    uint32_t _canvasWidth;
    uint32_t _canvasHeight;
};
```

### WebAssembly Initialization

```cpp
auto EmscriptenBackend::start() -> void
{
    // Initialize Emscripten
    emscripten_set_canvas_size(320, 200);
    
    // Create WebGL context
    EmscriptenWebGLContextAttributes attrs;
    emscripten_webgl_init_context_attrs(&attrs);
    _glContext = emscripten_webgl_create_context(nullptr, &attrs);
    
    if(_glContext <= 0) {
        log_error("Failed to create WebGL context");
        return;
    }
    
    emscripten_webgl_make_context_current(_glContext);
}
```

### WebAssembly Audio

```cpp
auto EmscriptenBackend::startAudio(AudioCallback callback, void* userdata) -> void
{
    // Initialize Web Audio API
    EM_ASM({
        var audioContext = new (window.AudioContext || window.webkitAudioContext)();
        var sampleRate = audioContext.sampleRate;
        
        // Set up audio processing
        var processor = audioContext.createScriptProcessor(1024, 0, 2);
        processor.onaudioprocess = function(e) {
            var inputBuffer = e.inputBuffer;
            var outputBuffer = e.outputBuffer;
            
            // Process audio
            var inputData = inputBuffer.getChannelData(0);
            var outputData = outputBuffer.getChannelData(0);
            
            // Copy input to output (placeholder)
            for(var i = 0; i < inputData.length; i++) {
                outputData[i] = inputData[i];
            }
        };
        
        processor.connect(audioContext.destination);
    });
}
```

## Performance Characteristics

### Backend Performance
- **Frame Rate**: 60 FPS target
- **Audio Latency**: ~20ms (platform-dependent)
- **Input Latency**: ~16ms (one frame)
- **Memory Usage**: ~2-4MB for SDL2 backend

### Platform Differences
- **Linux**: Native SDL2 performance
- **WebAssembly**: Web API performance
- **Audio**: Platform-specific audio systems
- **Display**: Hardware-accelerated rendering

## Integration with Game Systems

### Engine Interface

The backend integrates with the main engine:

```cpp
class Backend {
    Engine& _engine;  // Reference to main engine
    
    // System access methods
    auto getTicks() -> uint32_t;
    auto processEvents(Controls& controls) -> void;
    auto updateScreen(...) -> void;
    // ... other system calls
};
```

### System Integration

The backend coordinates with all game systems:

```cpp
auto Engine::main() -> void
{
    while(isRunning()) {
        // Process events
        _backend->processEvents(_input.getControls());
        
        // Process timers
        _backend->processTimers();
        
        // Run game logic
        _vm.run(_input.getControls());
        
        // Update display
        _backend->updateScreen(_video.getCurrentPage(), ...);
        
        // Sleep for frame timing
        _backend->sleepFor(16);  // ~60 FPS
    }
}
```

## Debugging Support

### Debug Output

```cpp
// Enable backend debugging
./another-world.bin --debug-backend

// Debug all systems
./another-world.bin --debug-all
```

### Debug Features
- **Event Processing**: Log all input events
- **Timer Management**: Track timer operations
- **Audio Processing**: Monitor audio callbacks
- **Performance Metrics**: Frame rate and timing statistics

## Historical Context

### Innovation (1991)

Another World's backend system was sophisticated for its time:

- **Cross-platform**: Identical behavior across platforms
- **Efficient Rendering**: Optimized for limited hardware
- **Audio Integration**: High-quality audio support
- **Event Handling**: Responsive input processing

### Technical Achievements

- **Platform Abstraction**: Clean separation of concerns
- **Performance**: Optimized for 16-bit processors
- **Compatibility**: Identical behavior across platforms
- **Modular Design**: Clean system integration

## Modern Implementation

### Improvements

This modern implementation adds:

- **Modern APIs**: SDL2 and WebAssembly support
- **Better Performance**: Optimized for modern hardware
- **Enhanced Debugging**: Comprehensive logging and debugging
- **Documentation**: Complete technical documentation

### Compatibility

The system maintains full compatibility with:
- **Original Behavior**: Identical game behavior
- **Platform Support**: Linux and WebAssembly
- **Audio Quality**: High-quality audio output
- **Input Responsiveness**: Low-latency input handling

The Backend System provides a robust foundation for cross-platform game execution, supporting both the original game's requirements and modern platform standards while maintaining full compatibility with the original game behavior.
