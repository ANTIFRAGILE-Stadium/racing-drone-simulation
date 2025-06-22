"""
Data models for the racing drone simulation.

Contains the core data structures used throughout the application.
"""

from dataclasses import dataclass


@dataclass
class StageConfig:
    """Configuration for the stage/performance space."""
    size: float = 20.0  # meters (cube dimensions)


@dataclass
class DroneState:
    """Complete state of the drone including position, orientation, and control inputs."""
    
    # Position (meters)
    x: float = 0.0   # meters (center)
    y: float = 0.0   # meters (center)
    z: float = 4.0   # meters (mid height)
    
    # Orientation (degrees)
    pan: float = 0.0   # yaw rotation
    tilt: float = 0.0  # pitch angle (calculated from movement)
    roll: float = 0.0  # roll angle (calculated from movement)
    fov: float = 90.0  # camera field of view (30-120 range)
    
    # Velocities
    vx: float = 0.0    # m/s (world X velocity)
    vy: float = 0.0    # m/s (world Y velocity)
    vz: float = 0.0    # m/s (world Z velocity)
    v_yaw: float = 0.0 # deg/s (yaw velocity)
    
    # Control inputs (-1 to 1 range)
    throttle: float = 0.0    # vertical movement
    yaw: float = 0.0         # rotation
    pitch: float = 0.0       # forward/backward
    roll_input: float = 0.0  # left/right