/**
 * Core Torus Logic (Math Engine)
 * Unified for both Browser and Terminal
 */

export const CONFIG = {
    TORUS_RADIUS: 2,
    TUBE_RADIUS: 1,
    SHADES: ".,-~:;=!*#$@",
    SCALE_X: 30,
    SCALE_Y: 15,
    DEPTH_OFFSET: 5,
    COLORS: [
        "\x1b[38;5;22m", "\x1b[38;5;28m", "\x1b[38;5;34m",
        "\x1b[38;5;40m", "\x1b[38;5;46m", "\x1b[38;5;82m",
        "\x1b[38;5;118m", "\x1b[38;5;154m"
    ]
};

export function computeFrame(width, height, rotationX, rotationZ, useColors = false) {
    const output = Array(width * height).fill(' ');
    const zbuffer = Array(width * height).fill(0);

    for (let theta = 0; theta < 2 * Math.PI; theta += 0.07) {
        for (let phi = 0; phi < 2 * Math.PI; phi += 0.02) {
            const cosTheta = Math.cos(theta);
            const sinTheta = Math.sin(theta);
            const cosPhi = Math.cos(phi);
            const sinPhi = Math.sin(phi);
            const cosRotX = Math.cos(rotationX);
            const sinRotX = Math.sin(rotationX);
            const cosRotZ = Math.cos(rotationZ);
            const sinRotZ = Math.sin(rotationZ);

            const circleX = CONFIG.TORUS_RADIUS + CONFIG.TUBE_RADIUS * cosTheta;
            const circleY = CONFIG.TUBE_RADIUS * sinTheta;

            const x = (circleX * (cosRotZ * cosPhi + sinRotX * sinRotZ * sinPhi) - circleY * cosRotX * sinRotZ);
            const y = (circleX * (sinRotZ * cosPhi - sinRotX * cosRotZ * sinPhi) + circleY * cosRotX * cosRotZ);
            const z = (cosRotX * circleX * sinPhi + circleY * sinRotX + CONFIG.DEPTH_OFFSET);
            const ooz = 1 / z;

            const x_screen = Math.floor(width / 2 + CONFIG.SCALE_X * ooz * x);
            const y_screen = Math.floor(height / 2 - CONFIG.SCALE_Y * ooz * y);

            const luminance = cosPhi * cosTheta * sinRotZ - cosRotX * cosTheta * sinPhi - sinRotX * sinTheta + cosRotZ * (cosRotX * sinTheta - cosTheta * sinRotX * sinPhi);
            let luminanceIndex = Math.floor(((luminance + 1.5) / 3) * (CONFIG.SHADES.length - 1));
            luminanceIndex = Math.max(0, Math.min(luminanceIndex, CONFIG.SHADES.length - 1));

            if (x_screen >= 0 && x_screen < width && y_screen >= 0 && y_screen < height) {
                const idx = x_screen + y_screen * width;
                if (ooz > zbuffer[idx]) {
                    zbuffer[idx] = ooz;
                    let char = CONFIG.SHADES[luminanceIndex];
                    
                    if (useColors) {
                        const colorIdx = Math.floor((luminanceIndex / (CONFIG.SHADES.length - 1)) * (CONFIG.COLORS.length - 1));
                        const color = CONFIG.COLORS[colorIdx];
                        output[idx] = `${color}${char}\x1b[0m`;
                    } else {
                        output[idx] = char;
                    }
                }
            }
        }
    }
    
    return output;
}
