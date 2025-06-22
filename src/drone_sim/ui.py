"""
UI components for the racing drone simulation.

Contains virtual joysticks, sliders, and other interactive UI elements.
"""

import pygame
import math
from typing import Tuple


class VirtualJoystick:
    """Virtual on-screen joystick for touch/mouse control."""
    
    def __init__(self, center: Tuple[int, int], radius: int, color: Tuple[int, int, int]):
        self.center = center
        self.radius = radius
        self.color = color
        self.stick_pos = list(center)
        self.is_dragging = False
        self.dead_zone = 0.1
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the joystick.
        
        Args:
            event: Pygame event to process
            
        Returns:
            True if event was handled, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                distance = math.sqrt((event.pos[0] - self.center[0])**2 + 
                                   (event.pos[1] - self.center[1])**2)
                if distance <= self.radius:
                    self.is_dragging = True
                    self.stick_pos = list(event.pos)
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging:
                self.is_dragging = False
                self.stick_pos = list(self.center)
                return True
        
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            # Constrain to circle
            dx = event.pos[0] - self.center[0]
            dy = event.pos[1] - self.center[1]
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance <= self.radius:
                self.stick_pos = list(event.pos)
            else:
                # Clamp to circle edge
                angle = math.atan2(dy, dx)
                self.stick_pos[0] = self.center[0] + math.cos(angle) * self.radius
                self.stick_pos[1] = self.center[1] + math.sin(angle) * self.radius
            return True
        
        return False
    
    def get_values(self) -> Tuple[float, float]:
        """
        Get normalized joystick values.
        
        Returns:
            Tuple of (x, y) values in range [-1, 1]
        """
        dx = self.stick_pos[0] - self.center[0]
        dy = self.stick_pos[1] - self.center[1]
        
        # Normalize to [-1, 1] range
        x = dx / self.radius
        y = -dy / self.radius  # Invert Y axis
        
        # Apply dead zone
        if abs(x) < self.dead_zone:
            x = 0.0
        if abs(y) < self.dead_zone:
            y = 0.0
        
        return (x, y)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the virtual joystick on screen."""
        # Draw outer circle
        pygame.draw.circle(screen, self.color, self.center, self.radius, 3)
        
        # Draw stick position
        pygame.draw.circle(screen, (255, 255, 255), self.stick_pos, 15)
        pygame.draw.circle(screen, self.color, self.stick_pos, 15, 2)


class HorizontalSlider:
    """Horizontal slider for adjusting values."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 min_val: float, max_val: float, initial_val: float):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.dragging = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the slider.
        
        Args:
            event: Pygame event to process
            
        Returns:
            True if event was handled, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value(event.pos[0])
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
                return True
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value(event.pos[0])
            return True
        
        return False
    
    def _update_value(self, mouse_x: int) -> None:
        """Update slider value based on mouse position."""
        rel_x = mouse_x - self.rect.x
        rel_x = max(0, min(self.rect.width, rel_x))
        ratio = rel_x / self.rect.width
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
    
    def get_value(self) -> float:
        """Get current slider value."""
        return self.val
    
    def set_value(self, value: float) -> None:
        """Set slider value."""
        self.val = max(self.min_val, min(self.max_val, value))
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the slider on screen."""
        # Draw track
        pygame.draw.rect(screen, (100, 100, 100), self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
        
        # Draw handle
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + ratio * self.rect.width
        handle_rect = pygame.Rect(handle_x - 10, self.rect.y - 5, 20, self.rect.height + 10)
        pygame.draw.rect(screen, (255, 255, 255), handle_rect)
        pygame.draw.rect(screen, (150, 150, 150), handle_rect, 2)