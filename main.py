import shutil
import time
import os
import sys
import math
from typing import List, Tuple, Generator

TORUS_RADIUS = 2.0
TUBE_RADIUS = 1.0
THETA_SPACING = 0.07
PHI_SPACING = 0.02
FRAME_DELAY = 0.03
DEPTH_OFFSET = 5.0

SHADES = ".,-~:;=!*#$@"
NUM_SHADES = len(SHADES)

SCALE_X = 30
SCALE_Y = 15


def clear_screen() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def frange(start: float, stop: float, step: float) -> Generator[float, None, None]:
    count = int((stop - start) / step)
    for i in range(count):
        yield start + i * step


def compute_point(theta: float, phi: float, rotation_x: float, rotation_z: float) -> Tuple[int, int, float, int]:
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    cos_phi = math.cos(phi)
    sin_phi = math.sin(phi)

    cos_rot_x = math.cos(rotation_x)
    sin_rot_x = math.sin(rotation_x)
    cos_rot_z = math.cos(rotation_z)
    sin_rot_z = math.sin(rotation_z)

    circle_x = TORUS_RADIUS + TUBE_RADIUS * cos_theta
    circle_y = TUBE_RADIUS * sin_theta

    x = (circle_x * (cos_rot_z * cos_phi + sin_rot_x * sin_rot_z * sin_phi)
         - circle_y * cos_rot_x * sin_rot_z)
    y = (circle_x * (sin_rot_z * cos_phi - sin_rot_x * cos_rot_z * sin_phi)
         + circle_y * cos_rot_x * cos_rot_z)
    z = (cos_rot_x * circle_x * sin_phi + circle_y * sin_rot_x + DEPTH_OFFSET)

    ooz = 1 / z

    x_screen = int(HALF_WIDTH + SCALE_X * ooz * x)
    y_screen = int(HALF_HEIGHT - SCALE_Y * ooz * y)

    luminance = (cos_phi * cos_theta * sin_rot_z
                 - cos_rot_x * cos_theta * sin_phi
                 - sin_rot_x * sin_theta
                 + cos_rot_z * (cos_rot_x * sin_theta - cos_theta * sin_rot_x * sin_phi))
    luminance_index = int((luminance + 1.5) / 3 * (NUM_SHADES - 1))
    luminance_index = max(0, min(luminance_index, NUM_SHADES - 1))

    return x_screen, y_screen, ooz, luminance_index


def render_frame(rotation_x: float, rotation_z: float, width: int, height: int) -> List[str]:
    output = [' '] * (width * height)
    zbuffer = [0.0] * (width * height)

    for theta in frange(0, 2 * math.pi, THETA_SPACING):
        for phi in frange(0, 2 * math.pi, PHI_SPACING):
            x_screen, y_screen, depth, luminance_index = compute_point(theta, phi, rotation_x, rotation_z)

            if 0 <= x_screen < width and 0 <= y_screen < height:
                idx = x_screen + y_screen * width
                if depth > zbuffer[idx]:
                    zbuffer[idx] = depth
                    output[idx] = SHADES[luminance_index]

    return output


def main() -> None:
    global HALF_WIDTH, HALF_HEIGHT

    terminal_size = shutil.get_terminal_size((80, 40))
    width, height = terminal_size.columns, terminal_size.lines
    HALF_WIDTH = width / 2
    HALF_HEIGHT = height / 2

    rotation_x = 0.0
    rotation_z = 0.0

    try:
        while True:
            frame = render_frame(rotation_x, rotation_z, width, height)
            clear_screen()
            print(''.join(frame))
            time.sleep(FRAME_DELAY)

            rotation_x += 0.07
            rotation_z += 0.03
    except KeyboardInterrupt:
        clear_screen()
        sys.exit(0)


if __name__ == "__main__":
    main()
