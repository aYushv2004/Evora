/**
 * app.js — Evora frontend logic
 */

function debounce(fn, ms) {
    let t;
    return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
}

const $ = (s) => document.querySelector(s);
const socSlider   = $('#soc-slider');
const priceSlider = $('#price-slider');
const timeSlider  = $('#time-slider');

/* ── Theme ── */
const themeBtn  = $('#themeToggle');
const themeIcon = themeBtn.querySelector('.theme-icon');

function setTheme(theme) {
    document.documentElement.dataset.theme = theme;
    themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    localStorage.setItem('evora-theme', theme);
    if (Object.keys(charts).length) createCharts();
}

themeBtn.addEventListener('click', () => {
    setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
});

const saved = localStorage.getItem('evora-theme');
if (saved) setTheme(saved);

/* ── Mobile menu ── */
const hamburger = $('#hamburger');
const navLinks  = $('#navLinks');
hamburger.addEventListener('click', () => navLinks.classList.toggle('open'));
navLinks.querySelectorAll('.nav-link').forEach(l =>
    l.addEventListener('click', () => navLinks.classList.remove('open'))
);

/* ── Scroll-based active nav ── */
const sections = document.querySelectorAll('section[id]');
const allLinks = document.querySelectorAll('.nav-link');
window.addEventListener('scroll', () => {
    let cur = '';
    sections.forEach(s => { if (scrollY >= s.offsetTop - 120) cur = s.id; });
    allLinks.forEach(l => l.classList.toggle('active', l.getAttribute('href') === '#' + cur));
}, { passive: true });

/* ── Slider fill ── */
function fillSlider(slider) {
    const pct = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
    slider.style.background =
        `linear-gradient(to right, var(--slider-fill) ${pct}%, var(--slider-track) ${pct}%)`;
}

/* ── Display + Compute ── */
function updateDisplays() {
    $('#soc-value').textContent   = socSlider.value;
    $('#price-value').textContent = priceSlider.value;
    $('#time-value').textContent  = timeSlider.value;
    $('#metric-soc').textContent   = socSlider.value + '%';
    $('#metric-price').textContent = priceSlider.value + '¢';
    $('#metric-time').textContent  = timeSlider.value + 'h';
    [socSlider, priceSlider, timeSlider].forEach(fillSlider);
}

async function compute() {
    try {
        const res = await fetch('/api/compute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                soc:   +socSlider.value,
                price: +priceSlider.value,
                time:  +timeSlider.value,
            }),
        });
        const d = await res.json();
        $('#result-power').textContent = d.power.toFixed(1);
        $('#metric-power').textContent = d.power.toFixed(1);
        const badge = $('#result-badge');
        badge.textContent = d.tier.toUpperCase();
        badge.className   = 'result-badge badge-' + d.tier;
    } catch (e) {
        console.error('Compute error:', e);
    }
}

const debouncedCompute = debounce(compute, 80);
[socSlider, priceSlider, timeSlider].forEach(s => {
    s.addEventListener('input', () => { updateDisplays(); debouncedCompute(); });
});

/* ── Charts ── */
let membershipData = null;
let charts = {};

function chartColors() {
    const dk = document.documentElement.dataset.theme === 'dark';
    return {
        lines: [dk ? '#34d399' : '#059669', dk ? '#a78bfa' : '#7c3aed', '#f472b6'],
        text:  dk ? '#666' : '#888',
        grid:  dk ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.05)',
    };
}

function createCharts() {
    if (!membershipData) return;
    const c = chartColors();
    const keys   = ['soc', 'price', 'time', 'charge_power'];
    const ids    = ['chart-soc', 'chart-price', 'chart-time', 'chart-power'];
    const titles = ['SOC (%)', 'Tariff (¢/kWh)', 'Time (h)', 'Power (kW)'];

    keys.forEach((key, i) => {
        if (charts[key]) charts[key].destroy();
        const d = membershipData[key];
        charts[key] = new Chart(document.getElementById(ids[i]).getContext('2d'), {
            type: 'line',
            data: {
                labels: d.universe,
                datasets: Object.entries(d.terms).map(([name, vals], j) => ({
                    label: name, data: vals,
                    borderColor: c.lines[j % 3],
                    backgroundColor: c.lines[j % 3] + '0a',
                    fill: true, borderWidth: 1.5, pointRadius: 0, tension: 0.1,
                })),
            },
            options: {
                responsive: true, maintainAspectRatio: true,
                animation: { duration: 300 },
                plugins: {
                    title: { display: true, text: titles[i], color: c.text,
                             font: { family: 'Inter', size: 11, weight: '500' } },
                    legend: { labels: { color: c.text,
                              font: { family: 'Inter', size: 10 }, boxWidth: 10 } },
                },
                scales: {
                    x: { grid: { color: c.grid }, ticks: { color: c.text, font: { size: 9 } } },
                    y: { grid: { color: c.grid }, ticks: { color: c.text, font: { size: 9 } },
                         min: -0.05, max: 1.1 },
                },
            },
        });
    });
}

async function loadMembership() {
    const res = await fetch('/api/membership');
    membershipData = await res.json();
    createCharts();
}

/* Charts toggle */
let chartsOpen = false;
$('#chartsToggle').addEventListener('click', () => {
    chartsOpen = !chartsOpen;
    $('#chartsGrid').style.display = chartsOpen ? 'grid' : 'none';
    $('#toggleIcon').textContent   = chartsOpen ? '▾' : '▸';
    if (chartsOpen && !membershipData) loadMembership();
});

/* ── Contact form ── */
$('#contactForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const btn = $('#submitBtn');
    btn.textContent = '✓ Sent'; btn.disabled = true;
    setTimeout(() => { btn.textContent = 'Send Message'; btn.disabled = false; e.target.reset(); }, 2000);
});

/* ── Init ── */
updateDisplays();
compute();
