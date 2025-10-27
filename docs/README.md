# Another World Interpreter Documentation

This directory contains comprehensive documentation for the Another World Bytecode Interpreter project.

## Overview

The Another World Interpreter is a modern C++ reimplementation of Eric Chahi's classic 1991 game "Another World" (also known as "Out of This World"). This project is a fork of Fabien Sanglard's implementation, which itself was based on Gregory Montoir's original reverse-engineered virtual machine.

## Documentation Structure

### Core Documentation
- **[Project Overview](project_overview.md)** - High-level project description and goals
- **[Project Structure](project_structure.md)** - Detailed file and directory organization
- **[Build Process](development/build_process.md)** - Compilation and build instructions

### Game Systems
- **[Virtual Machine](game_systems/virtual_machine.md)** - Core bytecode interpreter and execution engine
- **[Video System](game_systems/video_system.md)** - Polygon rendering and page-based graphics
- **[Audio System](game_systems/audio_system.md)** - Sound effects and music playback
- **[Resource Management](game_systems/resource_management.md)** - Game data loading and management
- **[Input System](game_systems/input_system.md)** - Player input handling and controls
- **[Backend System](game_systems/backend_system.md)** - Platform abstraction layer

### Technical Documentation
- **[Architecture Overview](architecture/architecture_overview.md)** - System architecture and design patterns
- **[Data Structures](technical/data_structures.md)** - Core data types and structures
- **[Bytecode Reference](technical/bytecode_reference.md)** - Virtual machine instruction set
- **[File Formats](technical/file_formats.md)** - Game data file specifications

### Development
- **[Coding Standards](development/coding_standards.md)** - Code style and conventions
- **[Debugging Guide](development/debugging_guide.md)** - Debugging tools and techniques
- **[Platform Support](development/platform_support.md)** - Linux, WASM, and other platforms

## About Another World

Another World (known as "Out of This World" in North America) is a groundbreaking action-adventure game created by Eric Chahi in 1991. The game was notable for:

- **Revolutionary Graphics**: Used polygon-based rendering for smooth character animations
- **Cinematic Presentation**: Featured cinematic cutscenes and dramatic storytelling
- **Virtual Machine Architecture**: Used a custom bytecode interpreter for cross-platform compatibility
- **Minimalist Design**: Focused on atmosphere and storytelling over complex mechanics

## Technical Innovation

The original game's technical achievements include:

- Custom virtual machine for cross-platform bytecode execution
- Polygon-based character animation system
- Sophisticated resource management and compression
- Multi-threaded game logic execution
- Page-based graphics system for smooth scrolling

## Project Goals

This interpreter aims to:

1. **Preserve Gaming History**: Maintain compatibility with the original game data
2. **Educational Value**: Provide a clean, readable implementation for learning
3. **Cross-Platform Support**: Run on modern systems including web browsers
4. **Code Quality**: Demonstrate modern C++ practices and clean architecture

## Quick Start

1. **Build the Project**: See [Build Process](development/build_process.md)
2. **Obtain Game Data**: Copy original game files to `share/another-world/`
3. **Run**: Execute `./bin/another-world.bin` (Linux) or open `bin/another-world.html` (WASM)

## Contributing

This project follows the GNU General Public License v2.0. Contributions are welcome for:

- Bug fixes and improvements
- Additional platform support
- Documentation enhancements
- Performance optimizations

## Resources

- [Eric Chahi's Official Website](https://www.anotherworld.fr/)
- [Fabien Sanglard's Code Review](https://fabiensanglard.net/anotherWorld_code_review/)
- [Gregory Montoir's Original Implementation](https://github.com/cyxx/rawgl)
- [Play Online](https://www.emaxilde.net/assets/games/another-world/another-world.html)

## License

This project is licensed under the GNU General Public License v2.0. See the [COPYING](../COPYING) file for details.

---

*This documentation is maintained as part of the Another World Interpreter project.*
