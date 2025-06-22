# Claude Memory for Racing Drone Simulation

This file contains important information about the racing drone simulation project that Claude should remember between sessions.

## Project Overview

Racing drone flight simulator with real-time sACN DMX output for lighting control integration (specifically designed for Depence lighting software).

## Architecture & Code Structure

### Modular Design (Refactored)
The codebase is organized into separate modules for maintainability:

- **`models.py`** - Data classes (`StageConfig`, `DroneState`)
- **`physics.py`** - Physics engine and drone movement (`DronePhysics`)
- **`ui.py`** - UI components (`VirtualJoystick`, `HorizontalSlider`)  
- **`controls.py`** - Input handling (`InputController`)
- **`rendering.py`** - Visualization and drawing (`DroneRenderer`)
- **`dmx.py`** - DMX/sACN output handling (`DMXController`)
- **`main.py`** - Main application orchestration (`DroneSim`)

### Key Design Patterns
- **Separation of Concerns**: Each module handles a specific responsibility
- **Dependency Injection**: Components are injected into the main `DroneSim` class
- **Event-Driven**: UI and input handling use pygame events
- **Real-time Updates**: 60 FPS physics and rendering loop

## Coordinate Systems

### Internal Coordinate System
- **X**: Left/Right (stage coordinates)
- **Y**: Back/Forth (forward/backward movement)
- **Z**: Up/Down (height)
- **Pan**: Yaw rotation (0-360°)
- **Tilt**: Pitch angle (calculated from forward movement)
- **Roll**: Roll angle (calculated from sideways movement)

### Depence DMX Coordinate Mapping
```
# Internal → Depence
X → X (Left/Right - same)
Z → Y (Up/Down - maps from internal Z)  
Y → Z (Back/Forth - maps from internal Y)

# Orientation (swapped for Depence)
Internal Tilt → Depence Pan
Internal Pan → Depence Tilt
Internal Roll → Depence Roll (+ 180° offset)
```

## Critical Physics Implementation

### Orientation-Relative Movement
The drone controls work relative to the drone's current heading, not world coordinates:

```python
# Transform control inputs relative to drone's orientation
pan_rad = math.radians(drone.pan)
drone_forward = -drone.pitch * MAX_SPEED_XY      # Inverted for correct direction
drone_right = -drone.roll_input * MAX_SPEED_XY   # Inverted for correct direction

# Transform to world coordinates
desired_vx = drone_right * math.cos(pan_rad) - drone_forward * math.sin(pan_rad)
desired_vy = drone_right * math.sin(pan_rad) + drone_forward * math.cos(pan_rad)
```

### Banking Effects (Visual Realism)
- **Tilt**: Uses drone-relative forward velocity (consistent regardless of orientation)
- **Roll**: Uses world X velocity (works correctly for visual representation)

This hybrid approach ensures:
- Forward movement → nose down tilt (always)
- Sideways movement → appropriate roll direction

## Recent Key Fixes

### 1. Grid Visualization (Fixed)
- Changed from rectangular (800x400) to square (400x400) grid
- Properly represents the cube stage structure
- Updated drone position mapping to stay within square bounds

### 2. Control Inversion Issues (Fixed)
- **Root Cause**: Controls were applied in world coordinates instead of drone-relative
- **Solution**: Transform control inputs relative to drone's current heading
- **Result**: Consistent controls regardless of drone orientation

### 3. Banking Effect Issues (Fixed)  
- **Root Cause**: Tilt/roll calculations were inconsistent with orientation changes
- **Solution**: Tilt uses drone-relative velocity, roll uses world velocity
- **Result**: Realistic banking that looks correct from all angles

## DMX Output Specification

### Channel Layout (16-bit values)
```
Base Address + 0-1:   X Position (MSB, LSB)
Base Address + 2-3:   Y Position (MSB, LSB) 
Base Address + 4-5:   Z Position (MSB, LSB)
Base Address + 6-7:   Pan (MSB, LSB)
Base Address + 8-9:   Tilt (MSB, LSB)
Base Address + 10-11: Roll (MSB, LSB)
Base Address + 12-13: Zoom/FOV (MSB, LSB)
```

### sACN Configuration
- **Protocol**: sACN (Streaming ACN)
- **Multicast**: Enabled
- **Universe Range**: 1-63999
- **Address Range**: 1-500 (uses 14 consecutive channels)

## Control Inputs

### Gamepad Mapping (PS4/Xbox compatible)
- **Left Stick X**: Yaw (rotation)
- **Left Stick Y**: Throttle (up/down) - inverted
- **Right Stick X**: Roll (left/right)
- **Right Stick Y**: Pitch (forward/back) - inverted

### Keyboard Controls
- **ESC**: Quit application
- **SPACE**: Emergency stop (zero all velocities)
- **R**: Reset position to center

### Virtual Joysticks
- Fallback when no gamepad detected
- Same mapping as physical gamepad
- Mouse/touch control

## Testing & Development Notes

### Common Test Scenarios
1. **Orientation Test**: Move forward, yaw 180°, move forward again - should be consistent
2. **Banking Test**: Move in all directions, check tilt/roll visual behavior
3. **Grid Bounds**: Ensure drone indicator stays within square grid
4. **DMX Output**: Verify coordinate transformations in Depence

### Performance Targets
- **60 FPS**: Smooth real-time operation
- **Low Latency**: Immediate response to control inputs
- **Stable sACN**: Continuous DMX output without dropouts

## Build & Run Commands

```bash
# Standard run
uv run drone-sim

# With custom DMX settings
uv run drone-sim --dmx-universe 2 --dmx-address 17

# Development/testing
python -m src.drone_sim.main --dmx-universe 1 --dmx-address 1
```

## Dependencies
- **pygame**: UI and input handling
- **numpy**: Mathematical operations
- **sacn**: sACN DMX output protocol
- **dataclasses**: Type-safe data structures
- **typing**: Type hints for better code quality

## Future Improvements
- Add bounds checking/collision detection
- Implement different flight modes
- Add recording/playback functionality  
- Support for multiple drones
- Advanced physics (wind, gravity effects)
- 3D visualization improvements