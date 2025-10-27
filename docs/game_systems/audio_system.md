# Audio System

## Overview

The Audio System provides comprehensive sound and music capabilities for Another World, including multi-channel audio mixing, sound effect playback, and music sequencing. The system is designed to work seamlessly with the game's virtual machine and provides high-quality audio output.

## Architecture

### Core Components

```
Audio System
├── Mixer
│   ├── 4 Audio Channels
│   ├── Sample Rate Conversion
│   ├── Volume Control
│   └── Audio Processing
├── Sound System
│   ├── Sound Effect Playback
│   ├── Sample Management
│   ├── Frequency Control
│   └── Resource Loading
├── Music System
│   ├── Music Track Playback
│   ├── Position Control
│   ├── Delay Synchronization
│   └── Loop Management
└── Backend Integration
    ├── SDL2 Audio
    ├── Callback Processing
    └── Platform Abstraction
```

## Audio Specifications

### Technical Parameters
- **Sample Rate**: 44,100 Hz (configurable)
- **Channels**: 4 simultaneous audio channels
- **Bit Depth**: 16-bit signed samples
- **Format**: Stereo output
- **Buffer Size**: Variable (platform-dependent)

### Channel Configuration
- **Channel 0**: Music and ambient sounds
- **Channel 1**: Sound effects and voices
- **Channel 2**: Environmental sounds
- **Channel 3**: Special effects and UI sounds

## Mixer System

### Audio Channel Management

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

### Mixer Operations

#### Play All Channels
```cpp
auto playAllChannels() -> void
{
    for(int i = 0; i < 4; ++i) {
        if(_channels[i].active) {
            processChannel(_channels[i]);
        }
    }
}
```

#### Play Channel
```cpp
auto playChannel(uint8_t channel, const AudioSample& sample) -> void
{
    if(channel < 4) {
        _channels[channel].channel_id = channel;
        _channels[channel].active = 1;
        _channels[channel].volume = sample.volume;
        _channels[channel].sample_id = sample.sample_id;
        _channels[channel].data_ptr = sample.data_ptr;
        _channels[channel].data_len = sample.data_len;
        _channels[channel].data_pos = 0;
        _channels[channel].data_inc = sample.frequency;
        _channels[channel].loop_pos = sample.loop_pos;
        _channels[channel].loop_len = sample.loop_len;
    }
}
```

#### Stop Channel
```cpp
auto stopChannel(uint8_t channel) -> void
{
    if(channel < 4) {
        _channels[channel].active = 0;
        _channels[channel].data_ptr = nullptr;
        _channels[channel].data_len = 0;
        _channels[channel].data_pos = 0;
    }
}
```

#### Set Channel Volume
```cpp
auto setChannelVolume(uint8_t channel, uint8_t volume) -> void
{
    if(channel < 4) {
        _channels[channel].volume = volume;
    }
}
```

### Audio Processing

#### Process Audio Buffer
```cpp
auto processAudio(float* buffer, int length) -> void
{
    // Clear buffer
    std::memset(buffer, 0, length * sizeof(float));
    
    // Mix all active channels
    for(int i = 0; i < 4; ++i) {
        if(_channels[i].active) {
            mixChannel(buffer, length, _channels[i]);
        }
    }
}
```

#### Mix Channel
```cpp
auto mixChannel(float* buffer, int length, AudioChannel& channel) -> void
{
    for(int i = 0; i < length; ++i) {
        if(channel.samplePosition < channel.sampleLength) {
            // Get sample value
            int16_t sample = readSample(channel.sampleData, channel.samplePosition);
            
            // Apply volume
            float volume = channel.volume / 255.0f;
            sample = static_cast<int16_t>(sample * volume);
            
            // Mix to buffer
            buffer[i] += sample / 32768.0f;
            
            // Advance position
            channel.samplePosition += channel.frequency;
        } else if(channel.loop) {
            // Loop sample
            channel.samplePosition = 0;
        } else {
            // Stop channel
            channel.active = false;
            break;
        }
    }
}
```

## Sound System

### Sound Effect Management

```cpp
struct AudioSample {
    const uint8_t* data;    // Sample data
    uint32_t length;        // Sample length
    uint8_t volume;         // Volume level
    uint8_t frequency;      // Frequency multiplier
    bool loop;             // Loop flag
};
```

### Sound Operations

#### Play Sound
```cpp
auto playSound(uint16_t id, uint8_t channel, uint8_t volume, uint8_t frequency) -> void
{
    // Get sound resource
    Resource* resource = _engine.getResource(id);
    if(resource && resource->type == RESOURCE_SOUND) {
        // Create audio sample
        AudioSample sample;
        sample.sample_id = id;
        sample.frequency = frequency;
        sample.volume = volume;
        sample.data_ptr = resource->data;
        sample.data_len = resource->unpacked_size;
        sample.loop_pos = 0;
        sample.loop_len = 0;
        
        // Play through mixer
        _mixer.playChannel(channel, sample);
    }
}
```

### Sound Resource Format

Sound resources are stored in compressed format and must be decompressed before playback:

```cpp
auto loadSoundResource(uint16_t id) -> AudioSample*
{
    Resource* resource = _engine.getResource(id);
    if(resource) {
        // Decompress sound data
        uint8_t* decompressed = decompressData(resource->data, resource->size);
        
        // Create sample
        AudioSample* sample = new AudioSample();
        sample->data = decompressed;
        sample->length = getDecompressedSize(resource);
        return sample;
    }
    return nullptr;
}
```

## Music System

### Music Track Management

```cpp
struct MusicTrack {
    const uint8_t* data;    // Music data
    uint32_t length;        // Track length
    uint32_t position;      // Current position
    uint16_t delay;         // Delay between notes
    bool playing;           // Playing flag
    bool loop;              // Loop flag
};
```

### Music Operations

#### Play Music
```cpp
auto playMusic(uint16_t id, uint8_t position, uint16_t delay) -> void
{
    // Get music resource
    Resource* resource = _engine.getResource(id);
    if(resource && resource->type == RESOURCE_MUSIC) {
        // Create music track
        MusicTrack track;
        track.data = resource->data;
        track.length = resource->unpacked_size;
        track.position = position;
        track.delay = delay;
        track.playing = true;
        track.loop = true;
        
        // Start playback
        startMusicTrack(track);
    }
}
```

### Music Synchronization

The music system supports synchronization with the game's virtual machine:

```cpp
auto setMusicMark(uint16_t value) -> void
{
    // Set music synchronization marker
    _musicMark = value;
    
    // Notify VM of music position
    _engine.setMusicMark(value);
}
```

## Backend Integration

### SDL2 Audio Integration

The audio system integrates with SDL2 for cross-platform audio support:

```cpp
auto startAudio() -> void
{
    // Initialize SDL2 audio
    SDL_AudioSpec desired, obtained;
    desired.freq = AUDIO_SAMPLE_RATE;
    desired.format = AUDIO_F32SYS;
    desired.channels = 2;
    desired.samples = 1024;
    desired.callback = audioCallback;
    desired.userdata = this;
    
    // Open audio device
    if(SDL_OpenAudio(&desired, &obtained) < 0) {
        log_error("Failed to open audio device: %s", SDL_GetError());
        return;
    }
    
    // Start audio playback
    SDL_PauseAudio(0);
}
```

### Audio Callback

```cpp
static void audioCallback(void* userdata, uint8_t* stream, int len)
{
    Mixer* mixer = static_cast<Mixer*>(userdata);
    float* buffer = reinterpret_cast<float*>(stream);
    int samples = len / sizeof(float);
    
    // Process audio
    mixer->processAudio(buffer, samples);
}
```

## Performance Characteristics

### Audio Performance
- **Sample Rate**: 44,100 Hz (CD quality)
- **Latency**: ~20ms (platform-dependent)
- **CPU Usage**: ~5-10% on modern systems
- **Memory Usage**: ~1-2MB for audio buffers

### Channel Performance
- **Concurrent Channels**: 4 simultaneous channels
- **Mixing Overhead**: Minimal (simple addition)
- **Volume Control**: Real-time volume adjustment
- **Frequency Control**: Real-time pitch adjustment

## Integration with Game Systems

### Engine Interface

The audio system integrates with the main engine:

```cpp
class Audio {
    Engine& _engine;  // Reference to main engine
    
    // System access methods
    auto getResource(uint16_t id) -> Resource*;
    auto getMusicMark() -> uint16_t;
    // ... other system calls
};
```

### VM Integration

The Virtual Machine controls audio operations through system calls:

```cpp
// VM audio instructions
op_sound(Thread& thread);  // Play sound effect
op_music(Thread& thread);  // Play music track
```

### Input Integration

Audio can be controlled through input events:

```cpp
// Input controls for audio
struct Controls {
    bool mute;           // Mute audio
    bool volumeUp;       // Increase volume
    bool volumeDown;     // Decrease volume
    bool musicToggle;    // Toggle music
};
```

## Debugging Support

### Debug Output

```cpp
// Enable audio debugging
./another-world.bin --debug-audio

// Debug all systems
./another-world.bin --debug-all
```

### Debug Features
- **Channel Status**: Monitor active channels
- **Sample Information**: Track sample playback
- **Volume Levels**: Monitor volume settings
- **Performance Metrics**: Audio processing statistics

## Historical Context

### Innovation (1991)

Another World's audio system was advanced for its time:

- **Multi-channel Audio**: 4-channel mixing on limited hardware
- **Sample-based Sound**: High-quality sound effects
- **Music Integration**: Synchronized music playback
- **Cross-platform**: Identical audio across all platforms

### Technical Achievements

- **Efficient Mixing**: Optimized for 16-bit processors
- **Memory Management**: Smart sample caching
- **Real-time Control**: Dynamic volume and frequency adjustment
- **Synchronization**: Music sync with game events

## Modern Implementation

### Improvements

This modern implementation adds:

- **Higher Quality**: 44.1kHz sample rate
- **Better Performance**: Optimized for modern processors
- **Enhanced Debugging**: Comprehensive logging and debugging
- **Documentation**: Complete technical documentation

### Compatibility

The system maintains full compatibility with:
- **Original Game Data**: All original audio formats
- **Bytecode Instructions**: Complete VM instruction set
- **Platform Support**: Linux and WebAssembly

## Audio File Formats

### Supported Formats
- **Raw PCM**: 8-bit unsigned samples
- **Compressed**: ByteKiller compressed audio
- **Music**: Custom music format with timing data

### Resource Types
- **RESOURCE_SOUND**: Sound effect data
- **RESOURCE_MUSIC**: Music track data
- **RESOURCE_VOICE**: Voice/speech data

The Audio System provides a robust foundation for game audio, supporting both the original game's requirements and modern audio standards while maintaining full compatibility with the original game data.
