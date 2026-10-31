"""Assumption-based monthly sales scenario calculator. NOT a trained prediction.

Usage:
 python forecast.py --adults 5000 --capture-low .05 --capture-base .10 --capture-high .15 --monthly-spend 60
Inputs must be validated independently before using results to make investment decisions.
"""
import argparse

def estimate(adults, capture, spend):
    if adults <= 0 or not (0 <= capture <= 1) or spend <= 0:
        raise ValueError("invalid assumptions")
    return round(adults * capture * spend)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--adults", type=int, required=True, help="Verified age-21+ trade-area population")
    p.add_argument("--capture-low", type=float, required=True)
    p.add_argument("--capture-base", type=float, required=True)
    p.add_argument("--capture-high", type=float, required=True)
    p.add_argument("--monthly-spend", type=float, required=True)
    a = p.parse_args()
    rates = [a.capture_low, a.capture_base, a.capture_high]
    if rates != sorted(rates):
        raise ValueError("Capture rates must be ascending")
    values = [estimate(a.adults, c, a.monthly_spend) for c in rates]
    print("LOW: ${:,}/month\nBASE: ${:,}/month\nHIGH: ${:,}/month".format(*values))
    print("ASSUMPTION-BASED SCENARIOS; NOT TRAINED PREDICTIONS")

if __name__ == "__main__":
    main()
