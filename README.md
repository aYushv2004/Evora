# ⚡ EV Charging Scheduler

A fuzzy-logic powered smart charging recommendation system for Electric Vehicles, built with **scikit-fuzzy** and **Streamlit**.

## 📖 Overview

This project uses a **Mamdani-type fuzzy inference system** to determine the optimal charging power (0–22 kW) for an electric vehicle based on three input parameters:

| Input              | Range       | Description                              |
|--------------------|-------------|------------------------------------------|
| **SOC**            | 0 – 100 %   | Current battery state of charge          |
| **Electricity Price** | 0 – 50 $/kWh | Current grid electricity cost          |
| **Departure Time** | 0 – 24 h    | Hours until the EV is needed             |

The system outputs a **Charge Power** value (0–22 kW) classified into three tiers:
- 🟢 **ECO MODE** (≤ 7.5 kW) — Slow, cost-efficient charging
- 🟡 **BALANCED** (≤ 15 kW) — Moderate charging speed
- 🔴 **FAST CHARGE** (> 15 kW) — Maximum speed, urgent scenarios

## 🏗️ Architecture

```
Fuzzy Projects/
├── fuzzy_engine.py      # Core fuzzy logic engine (antecedents, rules, API)
├── app.py               # Streamlit web interface
├── tests/
│   ├── __init__.py
│   └── test_fuzzy_engine.py   # Unit tests for the engine
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

The project follows a **modular architecture**:
- **`fuzzy_engine.py`** — Contains all fuzzy logic: 3 antecedents, 1 consequent, 18 rules, and the `get_optimal_charge()` API function.
- **`app.py`** — Streamlit UI that imports from the engine and provides an interactive dashboard.

## 🔧 Fuzzy Logic Details

### Membership Functions (Triangular)

- **SOC**: Low [0,0,50], Medium [20,50,80], High [50,100,100]
- **Price**: Low [0,0,25], Medium [10,25,40], High [25,50,50]
- **Time**: Short [0,0,12], Medium [6,12,18], Long [12,24,24]
- **Charge Power**: Low [0,0,11], Medium [5,11,17], High [11,22,22]

### Rule Base (18 Rules)

The rule base covers emergency scenarios (low SOC + short time → always charge hard), cost-optimization (high SOC + expensive → minimal charging), and balanced scenarios in between.

## 🚀 Setup & Run

### Prerequisites
- Python 3.8+

### Installation

```bash
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### Running the Engine Sanity Check

```bash
python fuzzy_engine.py
```

### Running Unit Tests

```bash
python -m pytest tests/ -v
```

## 📦 Dependencies

| Package        | Purpose                              |
|----------------|--------------------------------------|
| scikit-fuzzy   | Fuzzy logic inference engine         |
| numpy          | Numerical array operations           |
| matplotlib     | Membership function visualization    |
| streamlit      | Interactive web dashboard            |

## 📝 License

This project was created for educational purposes.
