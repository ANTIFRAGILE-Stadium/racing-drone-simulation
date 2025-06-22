# Racing Drone Simulator

A Python-based racing drone flight simulator that outputs position and orientation data via DMX protocols (sACN only for now) for integration with lighting visualization software including Depence, Unreal Engine, and other virtual environments.

## Features

- **Realistic Flight Physics**: Orientation-relative controls with realistic banking effects
- **Gamepad Support**: Auto-detects PS4/Xbox controllers with fallback to virtual joysticks
- **Real-time sACN Output**: Streams DMX data compatible with Depence and other lighting software
- **14-channel DMX Mapping** (Depence coordinate system):
  - Channels 1-2: X Position (16-bit) - Stage Left/Right
  - Channels 3-4: Y Position (16-bit) - Up/Down (maps from Z)
  - Channels 5-6: Z Position (16-bit) - Back/Forth (maps from Y)
  - Channels 7-8: Pan (16-bit) - Swapped with Tilt for Depence
  - Channels 9-10: Tilt (16-bit) - Swapped with Pan for Depence
  - Channels 11-12: Roll (16-bit)
  - Channels 13-14: Zoom/FOV (16-bit)
- **Square Grid Visualization**: Accurate representation of 20m cube stage
- **Modular Architecture**: Clean separation of physics, rendering, controls, and DMX output
- **Interactive Controls**:
  - FOV slider (30°-120°)
  - Emergency stop and position reset
  - Real-time status display

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
- **Dimensions**: 20m × 20m × 20m cube
- **Origin**: Center of cube at ground level
- **Units**: Meters for position, degrees for rotation

### DMX Protocol
- **Protocol**: sACN (E1.31) multicast
- **Data Format**: 16-bit for position/rotation, 8-bit for FOV
- **Refresh Rate**: 60 Hz
- **Universe**: Configurable (default: 0)

## Development

### Project Structure
```
src/drone_sim/
├── main.py         # Main application orchestration
├── models.py       # Data structures (DroneState, StageConfig)
├── physics.py      # Physics engine and drone movement
├── ui.py          # UI components (joysticks, sliders)
├── controls.py    # Input handling (gamepad, keyboard)
├── rendering.py   # Visualization and drawing
└── dmx.py         # DMX/sACN output handling
```

### Key Features
- **Modular Design**: Each component has a single responsibility
- **Type Safety**: Full type hints throughout the codebase
- **Real-time Performance**: 60 FPS physics and rendering
- **Cross-platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.11+
- Dependencies managed by uv (see pyproject.toml)
- Network connectivity for DMX output
- Optional: USB gamepad for enhanced control

