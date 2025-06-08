#!/usr/bin/env python3
"""
Test the optimized standalone solution
"""

import json
import subprocess
import numpy as np

# Load public cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

print("Testing optimized standalone solution...")
print("="*60)

# Test on sample cases first
test_cases = [
    {"idx": 0, "days": 3, "miles": 93, "receipts": 1.42, "expected": 364.51},
    {"idx": 1, "days": 1, "miles": 55, "receipts": 3.60, "expected": 126.06},
    {"idx": 151, "days": 4, "miles": 69, "receipts": 2321.49, "expected": 322.00},
    {"idx": 683, "days": 8, "miles": 795, "receipts": 1645.99, "expected": 644.69},
    {"idx": 995, "days": 1, "miles": 1082, "receipts": 1809.49, "expected": 446.94}
]

print("\nSample test cases:")
for tc in test_cases:
    result = subprocess.run(
        ['./run_optimized_standalone.sh', 
         str(tc['days']), 
         str(tc['miles']), 
         str(tc['receipts'])],
        capture_output=True,
        text=True
    )
    
    predicted = float(result.stdout.strip())
    error = abs(predicted - tc['expected'])
    
    print(f"\nCase {tc['idx']}: {tc['days']}d, {tc['miles']}mi, ${tc['receipts']:.2f}")
    print(f"  Expected:  ${tc['expected']:.2f}")
    print(f"  Predicted: ${predicted:.2f}")
    print(f"  Error:     ${error:.2f}")

# Full evaluation
print("\n" + "="*60)
print("Running full evaluation on 1000 cases...")
print("="*60)

total_error = 0
errors = []
high_errors = []

for i, case in enumerate(data):
    if i % 100 == 0:
        print(f"Progress: {i}/1000...")
    
    result = subprocess.run(
        ['./run_optimized_standalone.sh', 
         str(case['input']['trip_duration_days']),
         str(case['input']['miles_traveled']),
         str(case['input']['total_receipts_amount'])],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error on case {i}: {result.stderr}")
        continue
    
    predicted = float(result.stdout.strip())
    expected = case['expected_output']
    error = abs(predicted - expected)
    
    total_error += error
    errors.append(error)
    
    if error > 500:
        high_errors.append({
            'idx': i,
            'days': case['input']['trip_duration_days'],
            'miles': case['input']['miles_traveled'],
            'receipts': case['input']['total_receipts_amount'],
            'expected': expected,
            'predicted': predicted,
            'error': error
        })

mae = total_error / len(data)
score = mae * 100

print(f"\n✅ Optimized Standalone Results:")
print(f"  MAE: ${mae:.2f}")
print(f"  Score: {score:.0f}")
print(f"  Max error: ${max(errors):.2f}")
print(f"  Errors > $100: {sum(1 for e in errors if e > 100)}")
print(f"  Errors > $500: {sum(1 for e in errors if e > 500)}")

# Error distribution
errors_array = np.array(errors)
print(f"\nError distribution:")
print(f"  25th percentile: ${np.percentile(errors_array, 25):.2f}")
print(f"  50th percentile: ${np.percentile(errors_array, 50):.2f}")
print(f"  75th percentile: ${np.percentile(errors_array, 75):.2f}")
print(f"  90th percentile: ${np.percentile(errors_array, 90):.2f}")

print(f"\nComparison:")
print(f"  RandomForest (external):     Score 5363.90")
print(f"  Decision Tree (current):     Score 13161")
print(f"  Ultra-optimized:             Score 17209")
print(f"  Optimized Standalone:        Score {score:.0f}")

if high_errors:
    print(f"\nHigh error cases (> $500):")
    for he in high_errors[:5]:
        print(f"  Case {he['idx']}: {he['days']}d, {he['miles']}mi, ${he['receipts']:.2f}")
        print(f"    Expected: ${he['expected']:.2f}, Got: ${he['predicted']:.2f}, Error: ${he['error']:.2f}") 