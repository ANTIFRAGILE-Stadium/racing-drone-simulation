import argparse
from dataclasses import dataclass
from typing import Tuple


@dataclass
class DMXCameraChannels:
    """DMX channel mapping for camera control (13 channels total)"""
    position_x: Tuple[int, int]  # 16-bit (coarse, fine)
    position_y: Tuple[int, int]  # 16-bit (coarse, fine)
    position_z: Tuple[int, int]  # 16-bit (coarse, fine)
    rotation_x: Tuple[int, int]  # 16-bit (coarse, fine)
    rotation_y: Tuple[int, int]  # 16-bit (coarse, fine)
    rotation_z: Tuple[int, int]  # 16-bit (coarse, fine)
    fov: int  # 8-bit

    @classmethod
    def from_start_address(cls, start_addr: int) -> 'DMXCameraChannels':
        """Create channel mapping from start address"""
        return cls(
            position_x=(start_addr, start_addr + 1),
            position_y=(start_addr + 2, start_addr + 3),
            position_z=(start_addr + 4, start_addr + 5),
            rotation_x=(start_addr + 6, start_addr + 7),
            rotation_y=(start_addr + 8, start_addr + 9),
            rotation_z=(start_addr + 10, start_addr + 11),
            fov=start_addr + 12
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Racing drone simulation with DMX camera control"
    )
    parser.add_argument(
        "--dmx-address", 
        type=int, 
        default=1,
        help="Starting DMX address for camera control (default: 1)"
    )
    parser.add_argument(
        "--dmx-universe", 
        type=int, 
        default=0,
        help="DMX universe (default: 0)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Create camera channel mapping
    camera_channels = DMXCameraChannels.from_start_address(args.dmx_address)
    
    print(f"Racing Drone Simulation")
    print(f"DMX Universe: {args.dmx_universe}")
    print(f"DMX Start Address: {args.dmx_address}")
    print(f"Camera channel mapping:")
    print(f"  Position X: channels {camera_channels.position_x[0]}-{camera_channels.position_x[1]}")
    print(f"  Position Y: channels {camera_channels.position_y[0]}-{camera_channels.position_y[1]}")
    print(f"  Position Z: channels {camera_channels.position_z[0]}-{camera_channels.position_z[1]}")
    print(f"  Rotation X: channels {camera_channels.rotation_x[0]}-{camera_channels.rotation_x[1]}")
    print(f"  Rotation Y: channels {camera_channels.rotation_y[0]}-{camera_channels.rotation_y[1]}")
    print(f"  Rotation Z: channels {camera_channels.rotation_z[0]}-{camera_channels.rotation_z[1]}")
    print(f"  FOV: channel {camera_channels.fov}")


if __name__ == "__main__":
    main()
