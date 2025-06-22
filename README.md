# Racing Drone Simulator

A Python-based racing drone flight simulator that outputs position and orientation data via DMX protocols (sACN only for now) for integration with lighting visualization software including Depence, Unreal Engine, and other virtual environments.

## Features

- **Virtual Joysticks**: On-screen controls for development (automatically switches to gamepad when connected)
- **Real-time sACN Output**: Streams DMX data that can be received by lighting consoles like grandMA3 or Depence
- **13-channel DMX Mapping** (compatible with Depence camera channels):
  - Channels 1-2: X Position (16-bit)
  - Channels 3-4: Y Position (16-bit)
  - Channels 5-6: Z Position (16-bit)
  - Channels 7-8: Rotation X (16-bit)
  - Channels 9-10: Rotation Y (16-bit)
  - Channels 11-12: Rotation Z (16-bit)
  - Channel 13: FOV (8-bit)
- **Stage Coordinate System**: 20m x 15m x 8m virtual stage
- **FOV Control**: Interactive slider for field of view adjustment (30°-120°)
- **Command Line Arguments**: Configurable DMX start address and universe
- **Keyboard Controls**:
  - ESC: Quit
  - SPACE: Emergency Stop
  - R: Reset Position

## Installation

```bash
# Clone the repository
git clone https://github.com/ANTIFRAGILE-Stadium/racing-drone-simulation
cd racing-drone-simulation

# Install dependencies with uv
uv sync

# Run the simulator
uv run drone-sim
```

## Usage

### Basic Usage
```bash
# Run with default settings (DMX address 1, universe 0)
uv run drone-sim

# Specify custom DMX settings
uv run drone-sim --dmx-address 100 --dmx-universe 2
```

### Controls
1. **Flight Control**: Use mouse to drag the virtual joysticks:
   - Left stick: Throttle (up/down) and Yaw (rotation)
   - Right stick: Pitch (forward/back) and Roll (left/right)
2. **FOV Control**: Drag the horizontal slider to adjust camera field of view
3. **DMX Output**: Simulator automatically outputs sACN data (multicast)
4. **Lighting Software**: Configure your visualization software to receive DMX data on the specified universe

### Integration with Lighting Software
- **Depence**: Use the DMX camera channels for virtual camera control
- **grandMA3**: Record DMX data for playback

## Technical Details

### Stage Coordinate System
- **Dimensions**: 20m (width) × 15m (depth) × 8m (height)
- **Origin**: Front-left corner at ground level
- **Units**: Meters for position, degrees for rotation

### DMX Protocol
- **Protocol**: sACN (E1.31) multicast
- **Data Format**: 16-bit for position/rotation, 8-bit for FOV
- **Refresh Rate**: 60 Hz
- **Universe**: Configurable (default: 0)

## Development

Project structure:
- `main.py`: Command-line interface and argument parsing
- `src/drone_sim/main.py`: Core simulator application
- Uses pygame for graphics and input handling
- Uses sacn library for DMX streaming
- Modular design for easy extension and integration

## Requirements

- Python 3.11+
- Dependencies managed by uv (see pyproject.toml)
- Network connectivity for DMX output
- Optional: USB gamepad for enhanced control

