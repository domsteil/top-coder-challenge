#!/usr/bin/env python3
"""
Analyze decision tree errors to improve the model
"""

import json
import numpy as np
from decimal import Decimal as D

# Load public cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

def get_base_amount(days, miles, receipts):
    """Current decision tree logic"""
    if receipts <= 828.10:
        if days <= 4.50:
            if miles <= 583.00:
                if receipts <= 443.43:
                    return 341.98
                else:  # receipts > 443.43
                    return 584.25
            else:  # miles > 583.00
                if receipts <= 483.66:
                    return 700.91
                else:  # receipts > 483.66
                    return 913.65
        else:  # days > 4.50
            if miles <= 624.50:
                if days <= 8.50:
                    return 761.84
                else:  # days > 8.50
                    return 977.10
            else:  # miles > 624.50
                if receipts <= 491.49:
                    return 1127.81
                else:  # receipts > 491.49
                    return 1382.67
    else:  # receipts > 828.10
        if days <= 5.50:
            if miles <= 621.00:
                if receipts <= 1235.90:
                    return 1108.31
                else:  # receipts > 1235.90
                    return 1371.69
            else:  # miles > 621.00
                if days <= 4.50:
                    return 1441.88
                else:  # days > 4.50
                    return 1672.50
        else:  # days > 5.50
            if miles <= 644.50:
                if receipts <= 1058.59:
                    return 1369.16
                else:  # receipts > 1058.59
                    return 1645.46
            else:  # miles > 644.50
                if miles <= 934.50:
                    return 1790.69
                else:  # miles > 934.50
                    return 1942.57

# Analyze which bucket each case falls into
buckets = {}
for i, case in enumerate(data):
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    expected = case['expected_output']
    
    base = get_base_amount(days, miles, receipts)
    
    # Create bucket key
    bucket_key = f"base_{base}"
    if bucket_key not in buckets:
        buckets[bucket_key] = []
    
    buckets[bucket_key].append({
        'case_id': i,
        'days': days,
        'miles': miles,
        'receipts': receipts,
        'expected': expected,
        'base': base,
        'error_before_corrections': abs(expected - base)
    })

# Analyze each bucket
print("DECISION TREE BUCKET ANALYSIS:")
print("="*80)

for bucket_key in sorted(buckets.keys()):
    cases = buckets[bucket_key]
    base_value = cases[0]['base']
    
    print(f"\nBucket: {bucket_key} (Base value: ${base_value:.2f})")
    print(f"Number of cases: {len(cases)}")
    
    # Calculate statistics
    expected_values = [c['expected'] for c in cases]
    errors = [c['error_before_corrections'] for c in cases]
    
    print(f"Expected values: min=${min(expected_values):.2f}, max=${max(expected_values):.2f}, mean=${np.mean(expected_values):.2f}")
    print(f"Errors: min=${min(errors):.2f}, max=${max(errors):.2f}, mean=${np.mean(errors):.2f}")
    
    # Show cases with large errors
    large_errors = [c for c in cases if c['error_before_corrections'] > 200]
    if large_errors:
        print(f"Cases with error > $200: {len(large_errors)}")
        for c in large_errors[:3]:  # Show first 3
            print(f"  Case {c['case_id']}: {c['days']}d, {c['miles']}mi, ${c['receipts']:.2f} → "
                  f"Expected: ${c['expected']:.2f}, Base: ${c['base']:.2f}, Error: ${c['error_before_corrections']:.2f}")

# Find problematic cases
print("\n" + "="*80)
print("MOST PROBLEMATIC CASES:")
print("="*80)

all_cases = []
for bucket_cases in buckets.values():
    all_cases.extend(bucket_cases)

all_cases.sort(key=lambda x: x['error_before_corrections'], reverse=True)

print("\nTop 10 cases with highest base error:")
for i, c in enumerate(all_cases[:10]):
    print(f"{i+1}. Case {c['case_id']}: {c['days']}d, {c['miles']}mi, ${c['receipts']:.2f}")
    print(f"   Expected: ${c['expected']:.2f}, Base: ${c['base']:.2f}, Error: ${c['error_before_corrections']:.2f}")
    
    # Check for patterns
    receipt_str = f"{c['receipts']:.2f}"
    if receipt_str.endswith('49') or receipt_str.endswith('99'):
        print(f"   → Has .49/.99 ending!")

# Analyze specific problematic case
print("\n" + "="*80)
print("ANALYZING CASE 1 (1d, 55mi, $3.60):")
print("="*80)
print("Expected: $126.06")
print("Decision tree path:")
print("  receipts (3.60) <= 828.10? YES")
print("  days (1) <= 4.50? YES")
print("  miles (55) <= 583.00? YES")
print("  receipts (3.60) <= 443.43? YES")
print("  → Base value: $341.98")
print("  → Error before corrections: $215.92")
print("\nThis suggests the decision tree is too coarse for low-value cases!") 