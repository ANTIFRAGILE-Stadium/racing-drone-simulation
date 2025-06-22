"""
Physics engine for drone simulation.

Handles drone movement, physics calculations, and realistic flight dynamics.
"""

import math
import numpy as np
from .models import DroneState


class DronePhysics:
    """Physics engine for realistic drone flight simulation."""
    
    # Physics constants
    MAX_SPEED_XY = 8.0       # m/s (maximum horizontal speed)
    MAX_SPEED_Z = 5.0        # m/s (maximum vertical speed)
    MAX_YAW_RATE = 180.0     # deg/s (maximum yaw rotation rate)
    ACCELERATION = 15.0      # m/s^2 (horizontal acceleration)
    Z_ACCELERATION = 10.0    # m/s^2 (vertical acceleration)
    YAW_ACCELERATION = 360.0 # deg/s^2 (yaw acceleration)
    DRAG_COEFFICIENT = 3.0   # Air resistance factor
    
    def update_physics(self, drone: DroneState, dt: float) -> None:
        """
        Update drone physics for one timestep.
        
        Args:
            drone: DroneState object to update
            dt: Time delta in seconds
        """
        # Transform roll/pitch inputs relative to drone's current heading
        pan_rad = math.radians(drone.pan)
        
        # Roll and pitch relative to drone's orientation
        # Invert both to match expected control directions in Depence
        drone_forward = -drone.pitch * self.MAX_SPEED_XY
        drone_right = -drone.roll_input * self.MAX_SPEED_XY
        
        # Transform to world coordinates
        desired_vx = drone_right * math.cos(pan_rad) - drone_forward * math.sin(pan_rad)
        desired_vy = drone_right * math.sin(pan_rad) + drone_forward * math.cos(pan_rad)
        desired_vz = drone.throttle * self.MAX_SPEED_Z
        desired_v_yaw = drone.yaw * self.MAX_YAW_RATE
        
        # Apply acceleration towards desired velocities
        drone.vx += (desired_vx - drone.vx) * self.ACCELERATION * dt / self.MAX_SPEED_XY
        drone.vy += (desired_vy - drone.vy) * self.ACCELERATION * dt / self.MAX_SPEED_XY
        drone.vz += (desired_vz - drone.vz) * self.Z_ACCELERATION * dt / self.MAX_SPEED_Z
        drone.v_yaw += (desired_v_yaw - drone.v_yaw) * self.YAW_ACCELERATION * dt / self.MAX_YAW_RATE
        
        # Apply drag when no input
        if abs(drone.roll_input) < 0.1:
            drone.vx *= (1.0 - self.DRAG_COEFFICIENT * dt)
        if abs(drone.pitch) < 0.1:
            drone.vy *= (1.0 - self.DRAG_COEFFICIENT * dt)
        if abs(drone.throttle) < 0.1:
            drone.vz *= (1.0 - self.DRAG_COEFFICIENT * dt)
        if abs(drone.yaw) < 0.1:
            drone.v_yaw *= (1.0 - self.DRAG_COEFFICIENT * dt)
        
        # Update positions based on velocities
        drone.x += drone.vx * dt
        drone.y += drone.vy * dt
        drone.z += drone.vz * dt
        drone.pan += drone.v_yaw * dt
        
        # Update tilt and roll based on velocity (banking effect)
        # Tilt: drone-relative forward velocity, Roll: world X velocity
        pan_rad = math.radians(drone.pan)
        drone_forward_vel = -drone.vx * math.sin(pan_rad) + drone.vy * math.cos(pan_rad)
        
        drone.tilt = np.clip(-drone_forward_vel / self.MAX_SPEED_XY * 30.0, -30, 30)  # Forward motion = nose down
        drone.roll = np.clip(-drone.vx / self.MAX_SPEED_XY * 30.0, -30, 30)          # Right motion = roll right
        
        # Normalize pan to 0-360
        drone.pan = drone.pan % 360
    
    def emergency_stop(self, drone: DroneState) -> None:
        """Immediately stop all drone movement."""
        drone.vx = 0.0
        drone.vy = 0.0
        drone.vz = 0.0
        drone.v_yaw = 0.0
    
    def reset_position(self, drone: DroneState) -> None:
        """Reset drone to initial position and state."""
        drone.x = 0.0
        drone.y = 0.0
        drone.z = 4.0
        drone.pan = 0.0
        drone.tilt = 0.0
        drone.roll = 0.0
        drone.vx = 0.0
        drone.vy = 0.0
        drone.vz = 0.0
        drone.v_yaw = 0.0