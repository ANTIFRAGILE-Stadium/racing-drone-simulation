"""
Rendering and visualization for the racing drone simulation.

Handles all drawing operations including drone visualization, grid, and UI.
"""

import pygame
import math
from .models import DroneState, StageConfig
from .ui import VirtualJoystick, HorizontalSlider


class DroneRenderer:
    """Handles all rendering operations for the drone simulation."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
    
    def draw_stage_grid(self, stage_config: StageConfig) -> None:
        """
        Draw the stage bounds and grid.
        
        Args:
            stage_config: Stage configuration object
        """
        # Draw stage bounds (square)
        stage_size = 400  # Square size in pixels
        stage_x = 440     # Center X position  
        stage_y = 220     # Center Y position
        stage_rect = pygame.Rect(stage_x - stage_size//2, stage_y - stage_size//2, 
                                stage_size, stage_size)
        pygame.draw.rect(self.screen, (60, 60, 60), stage_rect, 2)
        
        # Draw grid (square)
        grid_divisions = 5
        for i in range(grid_divisions + 1):
            # Vertical lines
            x = stage_x - stage_size//2 + i * (stage_size // grid_divisions)
            pygame.draw.line(self.screen, (40, 40, 40), 
                           (x, stage_y - stage_size//2), 
                           (x, stage_y + stage_size//2), 1)
            
            # Horizontal lines  
            y = stage_y - stage_size//2 + i * (stage_size // grid_divisions)
            pygame.draw.line(self.screen, (40, 40, 40), 
                           (stage_x - stage_size//2, y), 
                           (stage_x + stage_size//2, y), 1)
    
    def draw_drone(self, drone: DroneState, stage_config: StageConfig) -> None:
        """
        Draw the drone indicator on the stage grid.
        
        Args:
            drone: Current drone state
            stage_config: Stage configuration
        """
        # Map to square grid (400x400 centered at 440,220)
        stage_size = 400
        stage_x = 440
        stage_y = 220
        
        # Normalize coordinates from -stage.size/2 to +stage.size/2 range to 0-1
        normalized_x = (drone.x + stage_config.size/2) / stage_config.size
        normalized_y = (drone.y + stage_config.size/2) / stage_config.size
        
        screen_x = int(stage_x - stage_size//2 + normalized_x * stage_size)
        screen_y = int(stage_y - stage_size//2 + (1 - normalized_y) * stage_size)
        
        # Draw drone as circle with size based on height
        size = int(20 + (drone.z / stage_config.size) * 20)
        pygame.draw.circle(self.screen, (255, 100, 100), (screen_x, screen_y), size)
        
        # Draw direction indicator
        dir_x = int(screen_x + math.cos(math.radians(drone.pan - 90)) * size)
        dir_y = int(screen_y + math.sin(math.radians(drone.pan - 90)) * size)
        pygame.draw.line(self.screen, (255, 255, 255), (screen_x, screen_y), (dir_x, dir_y), 3)
    
    def draw_ui(self, drone: DroneState, stage_config: StageConfig, 
                left_stick: VirtualJoystick, right_stick: VirtualJoystick,
                fov_slider: HorizontalSlider, use_gamepad: bool,
                sacn_universe: int, dmx_address: int, sacn_active: bool) -> None:
        """
        Draw the complete UI including drone, controls, and status information.
        
        Args:
            drone: Current drone state
            stage_config: Stage configuration
            left_stick: Left virtual joystick
            right_stick: Right virtual joystick
            fov_slider: FOV control slider
            use_gamepad: Whether gamepad is being used
            sacn_universe: sACN universe number
            dmx_address: Base DMX address
            sacn_active: Whether sACN output is active
        """
        # Clear screen
        self.screen.fill((30, 30, 30))
        
        # Draw stage and drone
        self.draw_stage_grid(stage_config)
        self.draw_drone(drone, stage_config)
        
        # Draw virtual joysticks (if not using gamepad)
        if not use_gamepad:
            left_stick.draw(self.screen)
            right_stick.draw(self.screen)
        
        # Draw FOV slider
        fov_slider.draw(self.screen, self.font_small)
        
        # Draw control labels
        left_text = self.font_small.render("Throttle / Yaw", True, (150, 150, 150))
        self.screen.blit(left_text, (150, 620))
        
        right_text = self.font_small.render("Pitch / Roll", True, (150, 150, 150))
        self.screen.blit(right_text, (1040, 620))
        
        # Draw status information
        self._draw_status_info(drone, sacn_universe, dmx_address, use_gamepad)
        
        # Draw help text
        self._draw_help_text()
        
        # Draw sACN indicator
        self._draw_sacn_indicator(sacn_active)
    
    def _draw_status_info(self, drone: DroneState, sacn_universe: int, 
                         dmx_address: int, use_gamepad: bool) -> None:
        """Draw status information panel."""
        y_pos = 450
        status_items = [
            f"Position: X={drone.x:.1f}m Y={drone.y:.1f}m Z={drone.z:.1f}m",
            f"Velocity: X={drone.vx:.1f}m/s Y={drone.vy:.1f}m/s Z={drone.vz:.1f}m/s",
            f"Orientation: Pan={drone.pan:.0f}° Tilt={drone.tilt:.0f}° Roll={drone.roll:.0f}° FOV={drone.fov:.0f}°",
            f"Controls: Throttle={drone.throttle:.2f} Yaw={drone.yaw:.2f} Pitch={drone.pitch:.2f} Roll={drone.roll_input:.2f}",
            f"sACN: Universe {sacn_universe} @ Ch{dmx_address + 1}-{dmx_address + 13} - Multicast",
            f"Coordinate System: DEPENCE (X=L/R, Y=U/D, Z=B/F)",
            f"Controller: {'Gamepad' if use_gamepad else 'Virtual Joysticks'}"
        ]
        
        for item in status_items:
            text = self.font.render(item, True, (200, 200, 200))
            self.screen.blit(text, (240, y_pos))
            y_pos += 30
    
    def _draw_help_text(self) -> None:
        """Draw help/controls text."""
        help_text = [
            "ESC: Quit | SPACE: Emergency Stop | R: Reset Position",
            "DMX Output: X=Stage L/R, Y=Up/Down, Z=Back/Forth, Pan/Tilt swapped for Depence"
        ]
        y_pos = 680
        for line in help_text:
            text = self.font_small.render(line, True, (120, 120, 120))
            self.screen.blit(text, (240, y_pos))
            y_pos += 20
    
    def _draw_sacn_indicator(self, sacn_active: bool) -> None:
        """Draw sACN status indicator."""
        indicator_color = (0, 255, 0) if sacn_active else (255, 0, 0)
        pygame.draw.circle(self.screen, indicator_color, (1240, 40), 10)
        sacn_text = self.font_small.render("sACN", True, (200, 200, 200))
        self.screen.blit(sacn_text, (1200, 55))