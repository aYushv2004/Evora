/**
 * app.js — Evora frontend logic
 * Light Mode Only.
 */

function debounce(fn, ms) {
    let t;
    return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
}

const $ = (s) => document.querySelector(s);
const socSlider   = $('#soc-slider');
const priceSlider = $('#price-slider');
const timeSlider  = $('#time-slider');

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
    $('#metric-price').textContent = priceSlider.value + '$';
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
    return {
        lines: ['#059669', '#7c3aed', '#f472b6'],
        text:  '#4b5563',
        grid:  'rgba(0,0,0,0.06)',
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
                             font: { family: 'Inter', size: 12, weight: '500' } },
                    legend: { labels: { color: c.text,
                              font: { family: 'Inter', size: 11 }, boxWidth: 10 } },
                },
                scales: {
                    x: { grid: { color: c.grid }, ticks: { color: c.text, font: { size: 10 } } },
                    y: { grid: { color: c.grid }, ticks: { color: c.text, font: { size: 10 } },
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
const form = document.getElementById('contactForm');
const submitBtn = document.getElementById('submitBtn');

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    formData.append("access_key", "71864be5-9511-4e5b-8235-0fb77d6896a3");

    const originalText = submitBtn.textContent;

    submitBtn.textContent = "Sending...";
    submitBtn.disabled = true;

    try {
        const response = await fetch("https://api.web3forms.com/submit", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            alert("Success! Your message has been sent.");
            form.reset();
        } else {
            alert("Error: " + data.message);
        }

    } catch (error) {
        alert("Something went wrong. Please try again.");
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
});

/* ── Init ── */
updateDisplays();
compute();
