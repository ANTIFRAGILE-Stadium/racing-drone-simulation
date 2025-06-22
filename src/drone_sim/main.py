"""
Racing drone simulation with sACN DMX output.

A real-time drone flight simulator with physics-based movement and DMX lighting control
integration for use with Depence and other lighting control software.
"""

import pygame
import sys
import argparse
from typing import Optional

# Import our modular components
from .models import DroneState, StageConfig
from .physics import DronePhysics
from .ui import VirtualJoystick, HorizontalSlider
from .controls import InputController
from .rendering import DroneRenderer
from .dmx import DMXController


class DroneSim:
    """Main simulation class that orchestrates all components."""
    
    def __init__(self, universe: int = 1, dmx_address: int = 1):
        """
        Initialize the drone simulation.
        
        Args:
            universe: sACN universe number for DMX output
            dmx_address: Base DMX address for drone data
        """
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Racing Drone Simulator - sACN Output")
        self.clock = pygame.time.Clock()
        
        # Initialize core components
        self.stage = StageConfig()
        self.drone = DroneState()
        self.physics = DronePhysics()
        self.input_controller = InputController()
        self.renderer = DroneRenderer(self.screen)
        self.dmx_controller = DMXController(universe, dmx_address)
        
        # Initialize UI components
        self.left_stick = VirtualJoystick((200, 520), 80, (100, 200, 100))
        self.right_stick = VirtualJoystick((1080, 520), 80, (100, 100, 200))
        self.fov_slider = HorizontalSlider(440, 640, 400, 20, 30, 120, self.drone.fov)
        
        # Simulation state
        self.running = True
    
    def handle_events(self) -> None:
        """Process all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle keyboard input
            if self.input_controller.handle_keyboard(event, self.drone, self.physics):
                self.running = False
            
            # Handle UI events (if not using gamepad)
            if not self.input_controller.is_gamepad_connected():
                self.left_stick.handle_event(event)
                self.right_stick.handle_event(event)
            
            # Handle FOV slider
            if self.fov_slider.handle_event(event):
                self.drone.fov = self.fov_slider.get_value()
    
    def update(self, dt: float) -> None:
        """
        Update simulation state.
        
        Args:
            dt: Time delta in seconds
        """
        # Update control inputs
        self.input_controller.update_controls(
            self.drone, self.left_stick, self.right_stick
        )
        
        # Update physics
        self.physics.update_physics(self.drone, self.stage, dt)
        
        # Send DMX data
        self.dmx_controller.send_dmx_data(self.drone, self.stage)
    
    def render(self) -> None:
        """Render the current frame."""
        self.renderer.draw_ui(
            self.drone,
            self.stage,
            self.left_stick,
            self.right_stick,
            self.fov_slider,
            self.input_controller.is_gamepad_connected(),
            self.dmx_controller.get_universe(),
            self.dmx_controller.get_dmx_address(),
            self.dmx_controller.is_active()
        )
        
        pygame.display.flip()
    
    def run(self) -> None:
        """Main simulation loop."""
        print("Starting racing drone simulation...")
        print(f"sACN output: Universe {self.dmx_controller.get_universe()}, "
              f"DMX address {self.dmx_controller.get_dmx_address()}")
        
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # 60 FPS, convert to seconds
            
            self.handle_events()
            self.update(dt)
            self.render()
        
        # Cleanup
        self.dmx_controller.stop()
        pygame.quit()


def main():
    """Entry point for the application."""
    parser = argparse.ArgumentParser(description="Racing Drone Simulator with sACN DMX Output")
    parser.add_argument("--dmx-universe", type=int, default=1, 
                       help="sACN universe number (default: 1)")
    parser.add_argument("--dmx-address", type=int, default=1,
                       help="Base DMX address for drone data (default: 1)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not (1 <= args.dmx_universe <= 63999):
        print("Error: DMX universe must be between 1 and 63999")
        sys.exit(1)
    
    if not (1 <= args.dmx_address <= 500):
        print("Error: DMX address must be between 1 and 500")
        sys.exit(1)
    
    # Create and run simulation
    sim = DroneSim(universe=args.dmx_universe, dmx_address=args.dmx_address)
    sim.run()


if __name__ == "__main__":
    main()