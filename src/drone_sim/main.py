import pygame
import numpy as np
import sacn
import sys
import argparse
from dataclasses import dataclass
from typing import Tuple, Optional, Dict
import math


# Depence coordinate system mapping
# X = stage left/right (same)
# Y = up/down (maps from Z)
# Z = back/forth (maps from Y)


@dataclass
class StageConfig:
    size: float = 20.0  # meters (cube dimensions)
    
    
@dataclass
class DroneState:
    x: float = 0.0   # meters (center)
    y: float = 0.0   # meters (center)
    z: float = 4.0   # meters (mid height)
    pan: float = 0.0  # degrees
    tilt: float = 0.0  # degrees
    roll: float = 0.0  # degrees
    fov: float = 90.0  # degrees (30-120 range)
    
    # Velocities
    vx: float = 0.0  # m/s
    vy: float = 0.0  # m/s
    vz: float = 0.0  # m/s
    v_yaw: float = 0.0  # deg/s
    
    # Control inputs (-1 to 1)
    throttle: float = 0.0
    yaw: float = 0.0
    pitch: float = 0.0
    roll_input: float = 0.0


class VirtualJoystick:
    def __init__(self, center: Tuple[int, int], radius: int, color: Tuple[int, int, int]):
        self.center = center
        self.radius = radius
        self.color = color
        self.stick_pos = list(center)
        self.dragging = False
        
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            dist = math.sqrt((mouse_pos[0] - self.center[0])**2 + 
                           (mouse_pos[1] - self.center[1])**2)
            if dist <= self.radius:
                self.dragging = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            self.stick_pos = list(self.center)
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_pos = pygame.mouse.get_pos()
            dx = mouse_pos[0] - self.center[0]
            dy = mouse_pos[1] - self.center[1]
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist > self.radius:
                dx = dx / dist * self.radius
                dy = dy / dist * self.radius
                
            self.stick_pos[0] = self.center[0] + dx
            self.stick_pos[1] = self.center[1] + dy
    
    def get_values(self) -> Tuple[float, float]:
        x = (self.stick_pos[0] - self.center[0]) / self.radius
        y = -(self.stick_pos[1] - self.center[1]) / self.radius  # Invert Y
        return x, y
    
    def draw(self, screen: pygame.Surface) -> None:
        # Draw outer circle
        pygame.draw.circle(screen, self.color, self.center, self.radius, 2)
        # Draw center cross
        pygame.draw.line(screen, self.color, 
                        (self.center[0] - 10, self.center[1]),
                        (self.center[0] + 10, self.center[1]), 1)
        pygame.draw.line(screen, self.color,
                        (self.center[0], self.center[1] - 10),
                        (self.center[0], self.center[1] + 10), 1)
        # Draw stick
        pygame.draw.circle(screen, (255, 255, 255), 
                          (int(self.stick_pos[0]), int(self.stick_pos[1])), 15)
        pygame.draw.circle(screen, self.color,
                          (int(self.stick_pos[0]), int(self.stick_pos[1])), 15, 2)


class HorizontalSlider:
    def __init__(self, x: int, y: int, width: int, height: int, min_val: float, max_val: float, initial_val: float):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False
        
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value(event.pos[0])
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value(event.pos[0])
    
    def _update_value(self, mouse_x: int) -> None:
        relative_x = mouse_x - self.rect.x
        relative_x = max(0, min(relative_x, self.rect.width))
        self.value = self.min_val + (relative_x / self.rect.width) * (self.max_val - self.min_val)
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        # Draw track
        pygame.draw.rect(screen, (60, 60, 60), self.rect)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 2)
        
        # Draw handle
        handle_x = self.rect.x + int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        handle_rect = pygame.Rect(handle_x - 5, self.rect.y - 2, 10, self.rect.height + 4)
        pygame.draw.rect(screen, (200, 200, 200), handle_rect)
        
        # Draw value
        value_text = font.render(f"FOV: {self.value:.0f}°", True, (200, 200, 200))
        screen.blit(value_text, (self.rect.x + self.rect.width + 10, self.rect.y - 2))


class DroneSim:
    def __init__(self, universe: int = 1, dmx_address: int = 1):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Racing Drone Simulator - sACN Output")
        self.clock = pygame.time.Clock()
        
        self.stage = StageConfig()
        self.drone = DroneState()
        
        # Virtual joysticks
        self.left_stick = VirtualJoystick((200, 520), 80, (100, 200, 100))
        self.right_stick = VirtualJoystick((1080, 520), 80, (100, 100, 200))
        
        # FOV slider
        self.fov_slider = HorizontalSlider(440, 640, 400, 20, 30, 120, self.drone.fov)
        
        # sACN setup
        self.sacn_universe = universe
        self.dmx_address = dmx_address - 1  # Convert to 0-based index for array
        self.sacn_sender = sacn.sACNsender()
        self.sacn_sender.start()
        self.sacn_sender.activate_output(self.sacn_universe)
        self.sacn_sender[self.sacn_universe].multicast = True
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Gamepad
        self.gamepad = None
        try:
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                self.gamepad = pygame.joystick.Joystick(0)
                self.gamepad.init()
                print(f"Connected to controller: {self.gamepad.get_name()}")
        except Exception as e:
            print(f"Controller initialization failed: {e}")
            print("Continuing with virtual joysticks...")
            self.gamepad = None
        
        self.running = True
        self.emergency_stop = False
        
    def handle_events(self):
        try:
            events = pygame.event.get()
        except (SystemError, pygame.error) as e:
            # Controller disconnection can cause pygame.event.get() to fail
            print(f"Event handling error (likely controller issue): {e}")
            # Try to reset controller
            self.gamepad = None
            # Clear event queue a different way
            pygame.event.clear()
            return
            
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.emergency_stop = True
                elif event.key == pygame.K_r:
                    self.reset_drone()
            
            # Handle virtual joysticks if no gamepad
            if not self.gamepad:
                self.left_stick.handle_event(event)
                self.right_stick.handle_event(event)
            
            # Handle FOV slider
            self.fov_slider.handle_event(event)
    
    def update_controls(self):
        # Update FOV from slider
        self.drone.fov = self.fov_slider.value
        
        if self.emergency_stop:
            self.drone.throttle = 0
            self.drone.yaw = 0
            self.drone.pitch = 0
            self.drone.roll_input = 0
            # Also zero out velocities for emergency stop
            self.drone.vx = 0
            self.drone.vy = 0
            self.drone.vz = 0
            self.drone.v_yaw = 0
            self.emergency_stop = False
            return
        
        if self.gamepad:
            try:
                # Use physical gamepad
                self.drone.yaw = self.gamepad.get_axis(0)  # Left stick X
                self.drone.throttle = -self.gamepad.get_axis(1)  # Left stick Y (inverted)
                self.drone.roll_input = self.gamepad.get_axis(2)  # Right stick X
                self.drone.pitch = -self.gamepad.get_axis(3)  # Right stick Y (inverted)
            except (pygame.error, SystemError) as e:
                print(f"Controller read error: {e}")
                self.gamepad = None
        else:
            # Use virtual joysticks
            yaw, throttle = self.left_stick.get_values()
            roll, pitch = self.right_stick.get_values()
            self.drone.yaw = yaw
            self.drone.throttle = throttle
            self.drone.roll_input = roll
            self.drone.pitch = pitch
    
    def update_physics(self, dt: float):
        # Physics constants
        MAX_SPEED_XY = 8.0  # m/s
        MAX_SPEED_Z = 5.0   # m/s
        MAX_YAW_RATE = 180.0  # deg/s
        ACCELERATION = 15.0  # m/s^2
        Z_ACCELERATION = 10.0  # m/s^2
        YAW_ACCELERATION = 360.0  # deg/s^2
        DRAG_COEFFICIENT = 3.0  # Higher = more drag
        
        # Calculate desired velocities based on stick input
        desired_vx = self.drone.roll_input * MAX_SPEED_XY
        desired_vy = self.drone.pitch * MAX_SPEED_XY
        desired_vz = self.drone.throttle * MAX_SPEED_Z
        desired_v_yaw = self.drone.yaw * MAX_YAW_RATE
        
        # Apply acceleration towards desired velocities
        self.drone.vx += (desired_vx - self.drone.vx) * ACCELERATION * dt / MAX_SPEED_XY
        self.drone.vy += (desired_vy - self.drone.vy) * ACCELERATION * dt / MAX_SPEED_XY
        self.drone.vz += (desired_vz - self.drone.vz) * Z_ACCELERATION * dt / MAX_SPEED_Z
        self.drone.v_yaw += (desired_v_yaw - self.drone.v_yaw) * YAW_ACCELERATION * dt / MAX_YAW_RATE
        
        # Apply drag when no input
        if abs(self.drone.roll_input) < 0.1:
            self.drone.vx *= (1.0 - DRAG_COEFFICIENT * dt)
        if abs(self.drone.pitch) < 0.1:
            self.drone.vy *= (1.0 - DRAG_COEFFICIENT * dt)
        if abs(self.drone.throttle) < 0.1:
            self.drone.vz *= (1.0 - DRAG_COEFFICIENT * dt)
        if abs(self.drone.yaw) < 0.1:
            self.drone.v_yaw *= (1.0 - DRAG_COEFFICIENT * dt)
        
        # Update positions based on velocities
        self.drone.x += self.drone.vx * dt
        self.drone.y += self.drone.vy * dt
        self.drone.z += self.drone.vz * dt
        self.drone.pan += self.drone.v_yaw * dt
        
        # Update tilt and roll based on velocity (banking effect)
        self.drone.tilt = np.clip(self.drone.vy / MAX_SPEED_XY * 30.0, -30, 30)
        self.drone.roll = np.clip(self.drone.vx / MAX_SPEED_XY * 30.0, -30, 30)
        
        # No bounds - drone can move freely in all directions
        
        # Normalize pan to 0-360
        self.drone.pan = self.drone.pan % 360
    
    def send_sacn(self):
        # Convert to DMX values (0-65535 for 16-bit)
        dmx_data = [0] * 512
        
        # Position mapping for Depence: X=left/right, Y=up/down, Z=back/forth
        # Normalize to 0-1 range using stage size as reference (but no bounds enforcement)
        x_norm = (self.drone.x + self.stage.size/2) / self.stage.size    # Center at stage center
        y_norm = self.drone.z / self.stage.size                          # 0 = ground, 1 = top
        z_norm = (self.drone.y + self.stage.size/2) / self.stage.size    # Center at stage center
        
        # Clamp to 0-1 for DMX output only
        x_norm = max(0, min(1, x_norm))
        y_norm = max(0, min(1, y_norm))
        z_norm = max(0, min(1, z_norm))
        
        x_dmx = int(x_norm * 65535)      # X -> X (stage left/right)
        y_dmx = int(y_norm * 65535)      # Z -> Y (up/down)
        z_dmx = int(z_norm * 65535)      # Y -> Z (back/forth)
        
        # Orientation (16-bit values) - swapped for Depence
        # In Depence: Pan and Tilt are swapped
        pan_dmx = int(((self.drone.tilt + 90) / 180.0) * 65535)    # Tilt -> Pan (swapped)
        tilt_dmx = int((self.drone.pan / 360.0) * 65535)           # Pan -> Tilt (swapped)
        roll_dmx = int(((self.drone.roll + 180) / 360.0) * 65535)  # Roll + 180° to fix upside down
        
        # Set DMX channels (using dmx_address as offset)
        base = self.dmx_address
        dmx_data[base + 0] = x_dmx >> 8  # X MSB
        dmx_data[base + 1] = x_dmx & 0xFF  # X LSB
        dmx_data[base + 2] = y_dmx >> 8  # Y MSB
        dmx_data[base + 3] = y_dmx & 0xFF  # Y LSB
        dmx_data[base + 4] = z_dmx >> 8  # Z MSB
        dmx_data[base + 5] = z_dmx & 0xFF  # Z LSB
        dmx_data[base + 6] = pan_dmx >> 8  # Pan MSB
        dmx_data[base + 7] = pan_dmx & 0xFF  # Pan LSB
        dmx_data[base + 8] = tilt_dmx >> 8  # Tilt MSB
        dmx_data[base + 9] = tilt_dmx & 0xFF  # Tilt LSB
        dmx_data[base + 10] = roll_dmx >> 8  # Roll MSB
        dmx_data[base + 11] = roll_dmx & 0xFF  # Roll LSB
        
        # FOV (8-bit value)
        fov_dmx = int((self.drone.fov - 30) / 90.0 * 255)  # 30-120 degrees -> 0-255
        dmx_data[base + 12] = fov_dmx
        
        # Send data
        self.sacn_sender[self.sacn_universe].dmx_data = dmx_data
    
    def reset_drone(self):
        self.drone = DroneState()
    
    def draw_drone(self):
        # Convert stage coordinates to screen coordinates
        screen_x = int((self.drone.x / self.stage.size) * 800) + 240
        screen_y = int((1 - self.drone.y / self.stage.size) * 400) + 20
        
        # Draw drone as circle with size based on height
        size = int(20 + (self.drone.z / self.stage.size) * 20)
        pygame.draw.circle(self.screen, (255, 100, 100), (screen_x, screen_y), size)
        
        # Draw direction indicator
        dir_x = int(screen_x + math.cos(math.radians(self.drone.pan - 90)) * size)
        dir_y = int(screen_y + math.sin(math.radians(self.drone.pan - 90)) * size)
        pygame.draw.line(self.screen, (255, 255, 255), (screen_x, screen_y), (dir_x, dir_y), 3)
    
    def draw_ui(self):
        # Clear screen
        self.screen.fill((30, 30, 30))
        
        # Draw stage bounds
        stage_rect = pygame.Rect(240, 20, 800, 400)
        pygame.draw.rect(self.screen, (60, 60, 60), stage_rect, 2)
        
        # Draw grid
        for i in range(5):
            x = 240 + i * 200
            pygame.draw.line(self.screen, (40, 40, 40), (x, 20), (x, 420), 1)
        for i in range(3):
            y = 20 + i * 133
            pygame.draw.line(self.screen, (40, 40, 40), (240, y), (1040, y), 1)
        
        # Draw drone
        self.draw_drone()
        
        # Draw virtual joysticks
        if not self.gamepad:
            self.left_stick.draw(self.screen)
            self.right_stick.draw(self.screen)
        
        # Draw FOV slider
        self.fov_slider.draw(self.screen, self.font_small)
        
        # Draw labels
        left_text = self.font_small.render("Throttle / Yaw", True, (150, 150, 150))
        self.screen.blit(left_text, (150, 620))
        
        right_text = self.font_small.render("Pitch / Roll", True, (150, 150, 150))
        self.screen.blit(right_text, (1040, 620))
        
        # Draw status info
        y_pos = 450
        status_items = [
            f"Position: X={self.drone.x:.1f}m Y={self.drone.y:.1f}m Z={self.drone.z:.1f}m",
            f"Velocity: X={self.drone.vx:.1f}m/s Y={self.drone.vy:.1f}m/s Z={self.drone.vz:.1f}m/s",
            f"Orientation: Pan={self.drone.pan:.0f}° Tilt={self.drone.tilt:.0f}° Roll={self.drone.roll:.0f}° FOV={self.drone.fov:.0f}°",
            f"Controls: Throttle={self.drone.throttle:.2f} Yaw={self.drone.yaw:.2f} Pitch={self.drone.pitch:.2f} Roll={self.drone.roll_input:.2f}",
            f"sACN: Universe {self.sacn_universe} @ Ch{self.dmx_address + 1}-{self.dmx_address + 13} - Multicast",
            f"Coordinate System: DEPENCE (X=L/R, Y=U/D, Z=B/F)",
            f"Controller: {'Gamepad' if self.gamepad else 'Virtual Joysticks'}"
        ]
        
        for item in status_items:
            text = self.font.render(item, True, (200, 200, 200))
            self.screen.blit(text, (240, y_pos))
            y_pos += 30
        
        # Draw controls help            
        help_text = [
            "ESC: Quit | SPACE: Emergency Stop | R: Reset Position",
            "DMX Output: X=Stage L/R, Y=Up/Down, Z=Back/Forth, Pan/Tilt swapped for Depence"
        ]
        y_pos = 680
        for line in help_text:
            text = self.font_small.render(line, True, (120, 120, 120))
            self.screen.blit(text, (240, y_pos))
            y_pos += 20
        
        # Draw sACN indicator
        indicator_color = (0, 255, 0) if self.sacn_sender.get_active_outputs() else (255, 0, 0)
        pygame.draw.circle(self.screen, indicator_color, (1240, 40), 10)
        sacn_text = self.font_small.render("sACN", True, (200, 200, 200))
        self.screen.blit(sacn_text, (1200, 55))
    
    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update_controls()
            self.update_physics(dt)
            self.send_sacn()
            self.draw_ui()
            
            pygame.display.flip()
        
        # Cleanup
        self.sacn_sender.stop()
        pygame.quit()


def main():
    parser = argparse.ArgumentParser(description="Racing Drone Simulator with sACN Output (Depence format)")
    parser.add_argument(
        "--dmx-universe",
        type=int,
        default=1,
        help="DMX universe number (default: 1)"
    )
    parser.add_argument(
        "--dmx-address",
        type=int,
        default=1,
        help="Starting DMX address for drone data (default: 1)"
    )
    
    args = parser.parse_args()
    
    sim = DroneSim(universe=args.dmx_universe, dmx_address=args.dmx_address)
    sim.run()


if __name__ == "__main__":
    main()