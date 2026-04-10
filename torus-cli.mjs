#!/usr/bin/env node

/**
 * Torus CLI - Single Unified Version
 * Runs the torus in terminal using Node.js
 */

import { computeFrame } from './assets/js/engine.js';
import readline from 'readline';

const FRAME_RATE = 60;
let rotationX = 0;
let rotationZ = 0;
let lastTime = Date.now();

function getTerminalSize() {
    return {
        width: process.stdout.columns || 80,
        height: process.stdout.rows || 40
    };
}

function render() {
    const now = Date.now();
    const delta = (now - lastTime) / 1000;
    lastTime = now;

    rotationX += 0.07 * delta * 30;
    rotationZ += 0.03 * delta * 30;

    const { width, height } = getTerminalSize();
    const output = computeFrame(width, height, rotationX, rotationZ, true);

    let frame = "\x1b[H"; // Move cursor to top-left
    for (let i = 0; i < output.length; i++) {
        frame += output[i];
        if ((i + 1) % width === 0) frame += "\n";
    }

    process.stdout.write(frame);
}

// Initial clear screen
process.stdout.write("\x1b[2J");

const interval = setInterval(render, 1000 / FRAME_RATE);

// Handle exit
process.on('SIGINT', () => {
    clearInterval(interval);
    process.stdout.write("\x1b[0m\x1b[H\x1b[J"); // Reset colors and clear
    process.exit(0);
});

// Hide cursor
process.stdout.write("\x1b[?25l");
process.on('exit', () => process.stdout.write("\x1b[?25h")); // Show cursor on exit
