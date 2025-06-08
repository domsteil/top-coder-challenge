#!/usr/bin/env python3
"""
Test the self-contained RandomForest solution
"""

import json
import subprocess
import time
import numpy as np

# Load public cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

print("Testing self-contained RandomForest solution...")
print("="*60)

# Test timing first
print("\nTiming test (5 cases):")
for i in range(5):
    start = time.time()
    result = subprocess.run(
        ['./run_self_contained.sh', '3', '93', '1.42'],
        capture_output=True,
        text=True
    )
    elapsed = time.time() - start
    print(f"  Run {i+1}: {elapsed:.3f} seconds")

# Compare with original model on sample cases
print("\nComparing with original RandomForest:")
test_cases = [
    (3, 93, 1.42, 364.51),
    (1, 55, 3.60, 126.06),
    (4, 69, 2321.49, 322.00),
    (8, 795, 1645.99, 644.69),
    (1, 1082, 1809.49, 446.94)
]

for days, miles, receipts, expected in test_cases:
    # Original model
    orig_result = subprocess.run(
        ['./run.sh', str(days), str(miles), str(receipts)],
        capture_output=True,
        text=True,
        stderr=subprocess.DEVNULL
    )
    orig_pred = float(orig_result.stdout.strip().split('\n')[-1])
    
    # Self-contained model
    self_result = subprocess.run(
        ['./run_self_contained.sh', str(days), str(miles), str(receipts)],
        capture_output=True,
        text=True
    )
    self_pred = float(self_result.stdout.strip())
    
    print(f"\nCase: {days}d, {miles}mi, ${receipts:.2f} (Expected: ${expected:.2f})")
    print(f"  Original RF:     ${orig_pred:.2f}")
    print(f"  Self-contained:  ${self_pred:.2f}")
    print(f"  Match: {'✅' if abs(orig_pred - self_pred) < 0.01 else '❌'}")

# Full evaluation
print("\n" + "="*60)
print("Running full evaluation on 1000 cases...")
print("="*60)

total_error = 0
errors = []
mismatches = 0

for i, case in enumerate(data):
    if i % 100 == 0:
        print(f"Progress: {i}/1000...")
    
    result = subprocess.run(
        ['./run_self_contained.sh', 
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

mae = total_error / len(data)
score = mae * 100

print(f"\n✅ Self-Contained RandomForest Results:")
print(f"  MAE: ${mae:.2f}")
print(f"  Score: {score:.0f}")
print(f"  Max error: ${max(errors):.2f}")
print(f"  Errors > $100: {sum(1 for e in errors if e > 100)}")

# Error distribution
errors_array = np.array(errors)
print(f"\nError distribution:")
print(f"  25th percentile: ${np.percentile(errors_array, 25):.2f}")
print(f"  50th percentile: ${np.percentile(errors_array, 50):.2f}")
print(f"  75th percentile: ${np.percentile(errors_array, 75):.2f}")
print(f"  90th percentile: ${np.percentile(errors_array, 90):.2f}")

print(f"\n🎯 Comparison with original:")
print(f"  Original RandomForest:     Score 5363.90 (MAE $52.64)")
print(f"  Self-contained version:    Score {score:.0f} (MAE ${mae:.2f})")
print(f"  Difference:                {abs(5363.90 - score):.0f} points")

if abs(score - 5363.90) < 10:
    print("\n✅ SUCCESS! Self-contained version matches original performance!")
    print("   Ready to submit as run.sh") 