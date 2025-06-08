#!/usr/bin/env python3
import json
import numpy as np

# High-error cases from the evaluation
high_error_cases = [
    {'id': 169, 'days': 7, 'miles': 948, 'receipts': 657.17, 'expected': 1578.97, 'got': 1513.05, 'error': 65.92},
    {'id': 463, 'days': 11, 'miles': 667, 'receipts': 2221.67, 'expected': 1872.89, 'got': 1809.03, 'error': 63.86},
    {'id': 33, 'days': 5, 'miles': 262, 'receipts': 1173.79, 'expected': 1485.59, 'got': 1421.81, 'error': 63.78},
    {'id': 572, 'days': 10, 'miles': 797, 'receipts': 1706.73, 'expected': 1724.42, 'got': 1785.78, 'error': -61.36},
    {'id': 830, 'days': 12, 'miles': 601, 'receipts': 2166.56, 'expected': 1918.46, 'got': 1858.43, 'error': 60.03}
]

print("High-error case analysis:")
print("="*60)

# Analyze receipt endings
print("\nReceipt endings:")
for c in high_error_cases:
    ending = f"{c['receipts']:.2f}"[-2:]
    print(f"  Case {c['id']}: receipts end in .{ending}, error: ${c['error']:.2f}")

# Analyze receipts per day
print("\nReceipts per day:")
for c in high_error_cases:
    rpd = c['receipts'] / c['days']
    print(f"  Case {c['id']}: ${rpd:.2f}/day, error: ${c['error']:.2f}")

# Analyze miles per day
print("\nMiles per day:")
for c in high_error_cases:
    mpd = c['miles'] / c['days']
    print(f"  Case {c['id']}: {mpd:.2f} miles/day, error: ${c['error']:.2f}")

# Check if model is consistently under-predicting
print("\nPrediction bias:")
under_predictions = sum(1 for c in high_error_cases if c['error'] > 0)
print(f"  Under-predictions: {under_predictions}/5")
print(f"  Over-predictions: {5 - under_predictions}/5")

# Load all public cases to find similar patterns
with open('public_cases.json', 'r') as f:
    all_cases = json.load(f)

# Find cases with similar characteristics
print("\n" + "="*60)
print("IMPROVEMENT STRATEGIES:")
print("="*60)

print("\n1. Pattern-specific corrections:")
print("   - Most errors are under-predictions (4/5)")
print("   - Consider adding a small positive bias (+$5-10)")

print("\n2. Feature engineering opportunities:")
print("   - Add interaction: days * receipts_per_day")
print("   - Add: is_weekend_trip (2-3 days)")
print("   - Add: receipt_volatility (std dev of daily spending)")

print("\n3. Model ensemble:")
print("   - Train separate models for different trip lengths")
print("   - Use weighted average based on confidence")

print("\n4. Post-processing rules:")
# Check for specific patterns in high-error cases
for c in high_error_cases:
    if c['receipts'] > 2000 and c['days'] >= 10:
        print(f"   - High receipts + long trip: add correction")
    if c['miles'] / c['days'] > 130:
        print(f"   - High miles/day: may need adjustment") 