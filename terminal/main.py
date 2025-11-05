import sys
import math
import time
import shutil
from typing import List

TORUS_RADIUS = 2.0
TUBE_RADIUS = 1.0
THETA_SPACING = 0.07
PHI_SPACING = 0.02
DEPTH_OFFSET = 5.0
FRAME_RATE = 60

SHADES = ".,-~:;=!*#$@"
COLORS = [
    "\033[38;5;22m", "\033[38;5;28m", "\033[38;5;34m",
    "\033[38;5;40m", "\033[38;5;46m", "\033[38;5;82m",
    "\033[38;5;118m", "\033[38;5;154m"
]

SCALE_X = 30
SCALE_Y = 15


def compute_point(theta: float, phi: float, rot_x: float, rot_z: float, hw: float, hh: float):
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    cos_p, sin_p = math.cos(phi), math.sin(phi)
    cos_x, sin_x = math.cos(rot_x), math.sin(rot_x)
    cos_z, sin_z = math.cos(rot_z), math.sin(rot_z)

    circle_x = TORUS_RADIUS + TUBE_RADIUS * cos_t
    circle_y = TUBE_RADIUS * sin_t

    x = circle_x * (cos_z * cos_p + sin_x * sin_z * sin_p) - circle_y * cos_x * sin_z
    y = circle_x * (sin_z * cos_p - sin_x * cos_z * sin_p) + circle_y * cos_x * cos_z
    z = cos_x * circle_x * sin_p + circle_y * sin_x + DEPTH_OFFSET

    ooz = 1 / z
    x_screen = int(hw + SCALE_X * ooz * x)
    y_screen = int(hh - SCALE_Y * ooz * y)

    lum = cos_p * cos_t * sin_z - cos_x * cos_t * sin_p - sin_x * sin_t + cos_z * (cos_x * sin_t - cos_t * sin_x * sin_p)
    lum_index = max(0, min(int((lum + 1.5) / 3 * (len(SHADES) - 1)), len(SHADES) - 1))
    return x_screen, y_screen, ooz, lum_index


def render_frame(rot_x: float, rot_z: float, width: int, height: int, hw: float, hh: float,
                 thetas: List[float], phis: List[float]) -> str:
    output = [' '] * (width * height)
    zbuf = [0.0] * (width * height)

    for theta in thetas:
        for phi in phis:
            x, y, depth, lum_idx = compute_point(theta, phi, rot_x, rot_z, hw, hh)
            if 0 <= x < width and 0 <= y < height:
                idx = x + y * width
                if depth > zbuf[idx]:
                    zbuf[idx] = depth
                    color = COLORS[int(lum_idx / (len(SHADES) - 1) * (len(COLORS) - 1))]
                    output[idx] = f"{color}{SHADES[lum_idx]}"

    frame = "\033[H" + ''.join(
        ''.join(output[i * width:(i + 1) * width]) + "\033[0m\n"
        for i in range(height)
    )
    return frame


def main():
    width, height = shutil.get_terminal_size((80, 40))
    hw, hh = width / 2, height / 2

    thetas = [i * THETA_SPACING for i in range(int(2 * math.pi / THETA_SPACING))]
    phis = [i * PHI_SPACING for i in range(int(2 * math.pi / PHI_SPACING))]

    rot_x = rot_z = 0.0
    prev_time = time.perf_counter()

    try:
        print("\033[2J")
        while True:
            new_width, new_height = shutil.get_terminal_size((80, 40))
            if (new_width, new_height) != (width, height):
                width, height = new_width, new_height
                hw, hh = width / 2, height / 2

            now = time.perf_counter()
            delta = now - prev_time
            prev_time = now

            sys.stdout.write(render_frame(rot_x, rot_z, width, height, hw, hh, thetas, phis))
            sys.stdout.flush()

            rot_x += 0.07 * delta * 30
            rot_z += 0.03 * delta * 30

            time.sleep(max(0.0, 1.0 / FRAME_RATE - (time.perf_counter() - now)))

    except KeyboardInterrupt:
        print("\033[0m\033[H\033[J")
        sys.exit(0)


if __name__ == "__main__":
    main()
