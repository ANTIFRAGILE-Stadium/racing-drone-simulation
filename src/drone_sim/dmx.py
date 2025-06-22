"""
DMX/sACN output handling for the racing drone simulation.

Manages sACN communication and coordinate system transformations for Depence.
"""

import sacn
from .models import DroneState, StageConfig


class DMXController:
    """Handles DMX output via sACN for lighting control integration."""
    
    def __init__(self, universe: int = 1, dmx_address: int = 1):
        """
        Initialize DMX controller.
        
        Args:
            universe: sACN universe number (1-63999)
            dmx_address: Base DMX address (1-based, converted to 0-based internally)
        """
        self.sacn_universe = universe
        self.dmx_address = dmx_address - 1  # Convert to 0-based index for array
        
        # Initialize sACN sender
        self.sacn_sender = sacn.sACNsender()
        self.sacn_sender.start()
        self.sacn_sender.activate_output(self.sacn_universe)
        self.sacn_sender[self.sacn_universe].multicast = True
    
    def send_dmx_data(self, drone: DroneState, stage_config: StageConfig) -> None:
        """
        Send current drone state as DMX data via sACN.
        
        Transforms coordinates from internal system to Depence coordinate system:
        - Internal X → Depence X (stage left/right)
        - Internal Z → Depence Y (up/down) 
        - Internal Y → Depence Z (back/forth)
        - Internal tilt → Depence pan (swapped)
        - Internal pan → Depence tilt (swapped)
        
        Args:
            drone: Current drone state
            stage_config: Stage configuration for coordinate normalization
        """
        # Convert to DMX values (0-65535 for 16-bit)
        dmx_data = [0] * 512
        
        # Position mapping for Depence: X=left/right, Y=up/down, Z=back/forth
        # Normalize to 0-1 range using stage size as reference (but no bounds enforcement)
        x_norm = (drone.x + stage_config.size/2) / stage_config.size    # Center at stage center
        y_norm = drone.z / stage_config.size                            # 0 = ground, 1 = top
        z_norm = (drone.y + stage_config.size/2) / stage_config.size    # Center at stage center
        
        # Clamp to 0-1 for DMX output only
        x_norm = max(0, min(1, x_norm))
        y_norm = max(0, min(1, y_norm))
        z_norm = max(0, min(1, z_norm))
        
        x_dmx = int(x_norm * 65535)      # X -> X (stage left/right)
        y_dmx = int(y_norm * 65535)      # Z -> Y (up/down)
        z_dmx = int(z_norm * 65535)      # Y -> Z (back/forth)
        
        # Orientation (16-bit values) - swapped for Depence
        # In Depence: Pan and Tilt are swapped
        pan_dmx = int(((drone.tilt + 90) / 180.0) * 65535)    # Tilt -> Pan (swapped)
        tilt_dmx = int((drone.pan / 360.0) * 65535)           # Pan -> Tilt (swapped)
        roll_dmx = int(((drone.roll + 180) / 360.0) * 65535)  # Roll + 180° to fix upside down
        
        # FOV/Zoom (16-bit)
        zoom_dmx = int(((120 - drone.fov) / 90.0) * 65535)    # Invert FOV for zoom
        
        # Set DMX channels (using dmx_address as offset)
        base = self.dmx_address
        dmx_data[base + 0] = x_dmx >> 8        # X MSB
        dmx_data[base + 1] = x_dmx & 0xFF      # X LSB
        dmx_data[base + 2] = y_dmx >> 8        # Y MSB  
        dmx_data[base + 3] = y_dmx & 0xFF      # Y LSB
        dmx_data[base + 4] = z_dmx >> 8        # Z MSB
        dmx_data[base + 5] = z_dmx & 0xFF      # Z LSB
        dmx_data[base + 6] = pan_dmx >> 8      # Pan MSB
        dmx_data[base + 7] = pan_dmx & 0xFF    # Pan LSB
        dmx_data[base + 8] = tilt_dmx >> 8     # Tilt MSB
        dmx_data[base + 9] = tilt_dmx & 0xFF   # Tilt LSB
        dmx_data[base + 10] = roll_dmx >> 8    # Roll MSB
        dmx_data[base + 11] = roll_dmx & 0xFF  # Roll LSB
        dmx_data[base + 12] = zoom_dmx >> 8    # Zoom MSB
        dmx_data[base + 13] = zoom_dmx & 0xFF  # Zoom LSB
        
        # Send DMX data
        self.sacn_sender[self.sacn_universe].dmx_data = dmx_data
    
    def is_active(self) -> bool:
        """Check if sACN output is currently active."""
        return bool(self.sacn_sender.get_active_outputs())
    
    def stop(self) -> None:
        """Stop sACN sender and clean up."""
        self.sacn_sender.stop()
    
    def get_universe(self) -> int:
        """Get current sACN universe number."""
        return self.sacn_universe
    
    def get_dmx_address(self) -> int:
        """Get current DMX base address (1-based)."""
        return self.dmx_address + 1