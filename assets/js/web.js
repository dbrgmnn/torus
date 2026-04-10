import { computeFrame } from './engine.js';

const asciiElement = document.getElementById('ascii');
const timerElement = document.getElementById('timer');
const visitsElement = document.getElementById('visits');

let width = Math.floor(window.innerWidth / 8);
let height = Math.floor(window.innerHeight / 16);

window.addEventListener('resize', () => {
    width = Math.floor(window.innerWidth / 8);
    height = Math.floor(window.innerHeight / 16);
});

let rotationX = 0;
let rotationZ = 0;
let lastTime = performance.now();

function renderFrame(now) {
    const delta = (now - lastTime) / 1000;
    lastTime = now;

    rotationX += 0.035 * delta * 60;
    rotationZ += 0.015 * delta * 60;

    const output = computeFrame(width, height, rotationX, rotationZ, false);
    
    let rendered = "";
    for (let i = 0; i < output.length; i++) {
        rendered += output[i];
        if ((i + 1) % width === 0) rendered += "\n";
    }
    asciiElement.textContent = rendered;

    requestAnimationFrame(renderFrame);
}

// Timer Logic
const startTime = new Date('2025-11-04T00:00:00Z').getTime();
function updateTimer() {
    const elapsed = Date.now() - startTime;
    const days = Math.floor(elapsed / 86400000);
    const hours = Math.floor((elapsed % 86400000) / 3600000);
    const minutes = Math.floor((elapsed % 3600000) / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    timerElement.textContent = `${days}d ${String(hours).padStart(2,'0')}:${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`;
}

// Visit Counter Logic
const PROXY = "https://visit-counter.dmtrbrgmnn.workers.dev/";
async function updateVisits() {
    try {
        let data;
        if (!localStorage.getItem('visited')) {
            const res = await fetch(PROXY, { method: 'POST', mode: 'cors' });
            data = await res.json();
            localStorage.setItem('visited', 'true');
        } else {
            const res = await fetch(PROXY, { mode: 'cors' });
            data = await res.json();
        }
        visitsElement.textContent = data.value;
    } catch (e) {
        console.error("Error counter:", e);
        visitsElement.textContent = "—";
    }
}

export function init() {
    requestAnimationFrame(renderFrame);
    updateTimer();
    updateVisits();

    setInterval(updateTimer, 50);
    setInterval(updateVisits, 3000);
}
