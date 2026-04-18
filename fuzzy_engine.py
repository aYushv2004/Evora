"""
fuzzy_engine.py
===============
Fuzzy-logic engine for the EV Charging Scheduler.

Defines antecedents (SOC, Price, Time), a consequent (Charge_Power),
and their triangular membership functions.
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# ──────────────────────────────────────────────
# 1.  Antecedents (inputs)
# ──────────────────────────────────────────────

# State of Charge – 0 % to 100 %
soc = ctrl.Antecedent(np.arange(0, 101, 1), 'SOC')

# Electricity price – 0 to 50 ¢/kWh (or equivalent currency unit)
price = ctrl.Antecedent(np.arange(0, 51, 1), 'Price')

# Time of day – 0 h to 24 h
time = ctrl.Antecedent(np.arange(0, 25, 1), 'Time')

# ──────────────────────────────────────────────
# 2.  Consequent (output)
# ──────────────────────────────────────────────

# Charging power – 0 kW to 22 kW
charge_power = ctrl.Consequent(np.arange(0, 23, 1), 'Charge_Power')

# ──────────────────────────────────────────────
# 3.  Membership functions  (triangular)
# ──────────────────────────────────────────────

# --- SOC: Low / Medium / High ---
soc['Low']    = fuzz.trimf(soc.universe, [0,   0,  50])
soc['Medium'] = fuzz.trimf(soc.universe, [20, 50,  80])
soc['High']   = fuzz.trimf(soc.universe, [50, 100, 100])

# --- Price: Low / Medium / High ---
price['Low']    = fuzz.trimf(price.universe, [0,   0,  25])
price['Medium'] = fuzz.trimf(price.universe, [10, 25,  40])
price['High']   = fuzz.trimf(price.universe, [25, 50,  50])

# --- Time: Short / Medium / Long  (early-morning, midday, evening/night) ---
time['Short']  = fuzz.trimf(time.universe, [0,   0,  12])
time['Medium'] = fuzz.trimf(time.universe, [6,  12,  18])
time['Long']   = fuzz.trimf(time.universe, [12, 24,  24])

# --- Charge_Power: Low / Medium / High ---
charge_power['Low']    = fuzz.trimf(charge_power.universe, [0,   0,  11])
charge_power['Medium'] = fuzz.trimf(charge_power.universe, [5,  11,  17])
charge_power['High']   = fuzz.trimf(charge_power.universe, [11, 22,  22])


# ──────────────────────────────────────────────
# 4.  Fuzzy Rules  (20 rules)
# ──────────────────────────────────────────────
# Legend
#   SOC   : Low / Medium / High   (battery level)
#   Price : Low / Medium / High   (electricity cost)
#   Time  : Short / Medium / Long (time until departure)
#   → Charge_Power : Low / Medium / High

# ── CRITICAL: Low SOC + Short Time  →  always charge hard ──
rule1  = ctrl.Rule(soc['Low']    & time['Short'],                        charge_power['High'])
rule2  = ctrl.Rule(soc['Low']    & time['Short']  & price['High'],       charge_power['High'])   # even if price is high

# ── Low SOC, more time available ──
rule3  = ctrl.Rule(soc['Low']    & time['Medium'] & price['Low'],        charge_power['High'])
rule4  = ctrl.Rule(soc['Low']    & time['Medium'] & price['Medium'],     charge_power['High'])
rule5  = ctrl.Rule(soc['Low']    & time['Medium'] & price['High'],       charge_power['Medium'])
rule6  = ctrl.Rule(soc['Low']    & time['Long']   & price['Low'],        charge_power['High'])
rule7  = ctrl.Rule(soc['Low']    & time['Long']   & price['Medium'],     charge_power['Medium'])
rule8  = ctrl.Rule(soc['Low']    & time['Long']   & price['High'],       charge_power['Low'])

# ── Medium SOC ──
rule9  = ctrl.Rule(soc['Medium'] & time['Short']  & price['Low'],        charge_power['High'])
rule10 = ctrl.Rule(soc['Medium'] & time['Short']  & price['Medium'],     charge_power['Medium'])
rule11 = ctrl.Rule(soc['Medium'] & time['Short']  & price['High'],       charge_power['Medium'])
rule12 = ctrl.Rule(soc['Medium'] & time['Medium'] & price['Low'],        charge_power['Medium'])
rule13 = ctrl.Rule(soc['Medium'] & time['Medium'] & price['Medium'],     charge_power['Medium'])
rule14 = ctrl.Rule(soc['Medium'] & time['Medium'] & price['High'],       charge_power['Low'])
rule15 = ctrl.Rule(soc['Medium'] & time['Long']   & price['Low'],        charge_power['Medium'])
rule16 = ctrl.Rule(soc['Medium'] & time['Long']   & price['Medium'],     charge_power['Low'])
rule17 = ctrl.Rule(soc['Medium'] & time['Long']   & price['High'],       charge_power['Low'])

# ── High SOC  →  conserve / top-up only if cheap ──
rule18 = ctrl.Rule(soc['High']   & price['Low'],                         charge_power['Medium'])
rule19 = ctrl.Rule(soc['High']   & price['Medium'],                      charge_power['Low'])
rule20 = ctrl.Rule(soc['High']   & price['High'],                        charge_power['Low'])

# ──────────────────────────────────────────────
# 5.  Control System & Simulation
# ──────────────────────────────────────────────

charging_ctrl = ctrl.ControlSystem([
    rule1,  rule2,  rule3,  rule4,  rule5,  rule6,
    rule7,  rule8,  rule9,  rule10, rule11, rule12,
    rule13, rule14, rule15, rule16, rule17, rule18,
    rule19, rule20,
])

charging_sim = ctrl.ControlSystemSimulation(charging_ctrl)

# ──────────────────────────────────────────────
# 6.  Public API
# ──────────────────────────────────────────────

def get_optimal_charge(soc_val: float,
                       price_val: float,
                       time_val: float) -> float:
    """
    Compute the recommended charging power using the fuzzy inference system.

    Parameters
    ----------
    soc_val   : float  –  Current state of charge (0-100 %).
    price_val : float  –  Current electricity price (0-50 ¢/kWh).
    time_val  : float  –  Time until departure (0-24 h).

    Returns
    -------
    float  –  Optimal charging power in kW (0-22).
    """
    charging_sim.input['SOC']   = soc_val
    charging_sim.input['Price'] = price_val
    charging_sim.input['Time']  = time_val

    charging_sim.compute()

    return round(charging_sim.output['Charge_Power'], 2)


# ──────────────────────────────────────────────
# 7.  Quick sanity-check when run directly
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  EV Charging Fuzzy Engine – Sanity Check")
    print("=" * 50)

    # Print variable info
    for var, label in [(soc, "SOC"), (price, "Price"),
                       (time, "Time"), (charge_power, "Charge_Power")]:
        print(f"\n  {label}:")
        print(f"    Universe  : {var.universe[0]} – {var.universe[-1]}")
        print(f"    MF terms  : {list(var.terms.keys())}")

    print(f"\n  Total rules : {len(list(charging_ctrl.rules))}")

    # Sample scenarios
    test_cases = [
        (15, 10,  2, "Low battery, cheap, leaving soon → expect HIGH"),
        (15, 45,  2, "Low battery, expensive, leaving soon → expect HIGH (emergency)"),
        (50, 10, 12, "Mid battery, cheap, plenty of time → expect MEDIUM"),
        (50, 45,  6, "Mid battery, expensive, moderate time → expect LOW"),
        (90,  5, 20, "Full battery, cheap, lots of time → expect MEDIUM (top-up)"),
        (90, 45, 20, "Full battery, expensive, lots of time → expect LOW"),
    ]

    print("\n" + "-" * 50)
    print("  Test Scenarios")
    print("-" * 50)
    for s, p, t, desc in test_cases:
        power = get_optimal_charge(s, p, t)
        print(f"\n  SOC={s:3d}%  Price={p:2d}¢  Time={t:2d}h")
        print(f"  → Charge Power = {power:5.2f} kW")
        print(f"    ({desc})")
