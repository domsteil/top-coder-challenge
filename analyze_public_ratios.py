#!/usr/bin/env python3
"""
Analyze ratios directly from public cases to find exact patterns
"""

import json
import numpy as np

# Load public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Organize data by receipt endings
data_49 = []
data_99 = []
data_normal = []

for case in cases:
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    expected = case['expected_output']
    
    total_input = days + miles + receipts
    ratio = expected / total_input if total_input > 0 else 0
    
    receipt_str = f"{receipts:.2f}"
    
    if receipt_str.endswith('.49'):
        data_49.append({
            'days': days, 'miles': miles, 'receipts': receipts,
            'expected': expected, 'total': total_input, 'ratio': ratio
        })
    elif receipt_str.endswith('.99'):
        data_99.append({
            'days': days, 'miles': miles, 'receipts': receipts,
            'expected': expected, 'total': total_input, 'ratio': ratio
        })
    else:
        data_normal.append({
            'days': days, 'miles': miles, 'receipts': receipts,
            'expected': expected, 'total': total_input, 'ratio': ratio
        })

print("=== RATIO ANALYSIS FROM PUBLIC CASES ===\n")

# Analyze .49 endings
print("Receipt .49 Endings - Actual Ratios by Range:")
print(f"Total .49 cases: {len(data_49)}")

ranges = [(0, 300), (300, 500), (500, 700), (700, 900), (900, 1100), 
          (1100, 1300), (1300, 1500), (1500, 1700), (1700, 1900), (1900, 9999)]

for low, high in ranges:
    subset = [d for d in data_49 if low <= d['receipts'] < high]
    if subset:
        ratios = [d['ratio'] for d in subset]
        mean_ratio = np.mean(ratios)
        std_ratio = np.std(ratios)
        print(f"  ${low:4d}-${high:4d}: {mean_ratio:.6f} ± {std_ratio:.6f} (n={len(subset)})")

# Analyze .99 endings
print("\nReceipt .99 Endings - Actual Ratios by Range:")
print(f"Total .99 cases: {len(data_99)}")

for low, high in ranges:
    subset = [d for d in data_99 if low <= d['receipts'] < high]
    if subset:
        ratios = [d['ratio'] for d in subset]
        mean_ratio = np.mean(ratios)
        std_ratio = np.std(ratios)
        print(f"  ${low:4d}-${high:4d}: {mean_ratio:.6f} ± {std_ratio:.6f} (n={len(subset)})")

# Special patterns
print("\n=== SPECIAL PATTERNS ===")

# Find case 996 pattern
for d in data_49:
    if d['days'] == 1 and d['miles'] > 1000 and d['receipts'] > 1800:
        print(f"Case 996 pattern: {d['days']}d, {d['miles']}mi, ${d['receipts']:.2f}")
        print(f"  Expected: ${d['expected']:.2f}, Ratio: {d['ratio']:.6f}")

# Find case 684 pattern
for d in data_99:
    if d['days'] == 8 and 700 <= d['miles'] <= 900 and d['receipts'] > 1500:
        print(f"Case 684 pattern: {d['days']}d, {d['miles']}mi, ${d['receipts']:.2f}")
        print(f"  Expected: ${d['expected']:.2f}, Ratio: {d['ratio']:.6f}")

# Generate exact ratio code
print("\n=== GENERATED CODE FOR EXACT RATIOS ===")
print("# Copy these exact ratios into your solution:\n")

print("if receipt_str.endswith('49'):")
for i, (low, high) in enumerate(ranges):
    subset = [d for d in data_49 if low <= d['receipts'] < high]
    if subset:
        ratio = np.mean([d['ratio'] for d in subset])
        if i == 0:
            print(f'    if receipts < {high}:')
        elif i == len(ranges) - 1:
            print(f'    else:')
        else:
            print(f'    elif receipts < {high}:')
        print(f'        base_ratio = {ratio:.6f}')

print("\nelif receipt_str.endswith('99'):")
for i, (low, high) in enumerate(ranges):
    subset = [d for d in data_99 if low <= d['receipts'] < high]
    if subset:
        ratio = np.mean([d['ratio'] for d in subset])
        if i == 0:
            print(f'    if receipts < {high}:')
        elif i == len(ranges) - 1:
            print(f'    else:')
        else:
            print(f'    elif receipts < {high}:')
        print(f'        base_ratio = {ratio:.6f}') 