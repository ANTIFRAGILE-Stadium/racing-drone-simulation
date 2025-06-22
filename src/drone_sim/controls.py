"""
Input handling for the racing drone simulation.

Manages gamepad input, virtual joysticks, and keyboard controls.
"""

import pygame
from typing import Optional
from .models import DroneState
from .ui import VirtualJoystick


class InputController:
    """Handles all input sources for drone control."""
    
    def __init__(self):
        self.gamepad: Optional[pygame.joystick.Joystick] = None
        self._initialize_gamepad()
    
    def _initialize_gamepad(self) -> None:
        """Initialize gamepad if available."""
        try:
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                self.gamepad = pygame.joystick.Joystick(0)
                self.gamepad.init()
                print(f"Connected to controller: {self.gamepad.get_name()}")
        except Exception as e:
            print(f"Controller initialization failed: {e}")
            print("Continuing with virtual joysticks...")
    
    def update_controls(self, drone: DroneState, left_stick: VirtualJoystick, 
                       right_stick: VirtualJoystick) -> None:
        """
        Update drone control inputs from available input sources.
        
        Args:
            drone: DroneState object to update
            left_stick: Left virtual joystick (throttle/yaw)
            right_stick: Right virtual joystick (pitch/roll)
        """
        if self.gamepad:
            try:
                # Use physical gamepad
                drone.yaw = self.gamepad.get_axis(0)          # Left stick X
                drone.throttle = -self.gamepad.get_axis(1)    # Left stick Y (inverted)
                drone.roll_input = self.gamepad.get_axis(2)   # Right stick X
                drone.pitch = -self.gamepad.get_axis(3)       # Right stick Y (inverted)
            except (pygame.error, SystemError) as e:
                print(f"Controller read error: {e}")
                self.gamepad = None
        else:
            # Use virtual joysticks
            yaw, throttle = left_stick.get_values()
            roll, pitch = right_stick.get_values()
            drone.yaw = yaw
            drone.throttle = throttle
            drone.roll_input = roll
            drone.pitch = pitch
    
    def handle_keyboard(self, event: pygame.event.Event, drone: DroneState, 
                       physics_engine) -> bool:
        """
        Handle keyboard input events.
        
        Args:
            event: Pygame keyboard event
            drone: DroneState object
            physics_engine: Physics engine for emergency stop/reset
            
        Returns:
            True if app should quit, False otherwise
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True
            elif event.key == pygame.K_SPACE:
                # Emergency stop
                physics_engine.emergency_stop(drone)
            elif event.key == pygame.K_r:
                # Reset position
                physics_engine.reset_position(drone)
        
        return False
    
    def is_gamepad_connected(self) -> bool:
        """Check if gamepad is currently connected."""
        return self.gamepad is not None