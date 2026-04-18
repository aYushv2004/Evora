"""
server.py
=========
Flask API backend for the EV Charging Scheduler.
Serves the frontend static files and provides the fuzzy inference API.
"""

from flask import Flask, jsonify, request, send_from_directory
from fuzzy_engine import (
    get_optimal_charge,
    soc, price, time, charge_power,
)

app = Flask(__name__, static_folder='frontend', static_url_path='')


@app.route('/')
def index():
    """Serve the main frontend page."""
    return send_from_directory('frontend', 'index.html')


@app.route('/api/compute', methods=['POST'])
def compute():
    """Compute optimal charging power from fuzzy inputs."""
    data = request.json
    soc_val = float(data.get('soc', 50))
    price_val = float(data.get('price', 25))
    time_val = float(data.get('time', 12))

    power = get_optimal_charge(soc_val, price_val, time_val)

    if power <= 7.5:
        tier = 'eco'
    elif power <= 15:
        tier = 'balanced'
    else:
        tier = 'rapid'

    return jsonify({
        'power': power,
        'tier': tier,
        'inputs': {'soc': soc_val, 'price': price_val, 'time': time_val},
    })


@app.route('/api/membership')
def membership():
    """Return membership function data for chart visualization."""
    result = {}
    for var, name in [(soc, 'soc'), (price, 'price'),
                       (time, 'time'), (charge_power, 'charge_power')]:
        result[name] = {
            'universe': var.universe.tolist(),
            'terms': {},
        }
        for term_name in var.terms:
            result[name]['terms'][term_name] = var[term_name].mf.tolist()
    return jsonify(result)


if __name__ == '__main__':
    print('=' * 50)
    print('  Evora — Server')
    print('=' * 50)
    print('\n  Open  http://localhost:5000  in your browser\n')
    app.run(debug=True, port=5000)
