#!/usr/bin/env python3
"""Test the ultimate competition standalone solution"""

import json
import subprocess
import time
import numpy as np

# Load test cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

# Test first 20 cases to see performance
print('Testing ultimate competition solution:')
print('='*60)
total_error = 0

for i in range(20):
    case = data[i]
    result = subprocess.run(
        ['./run_ultimate.sh', 
         str(case['input']['trip_duration_days']),
         str(case['input']['miles_traveled']),
         str(case['input']['total_receipts_amount'])],
        capture_output=True,
        text=True
    )
    
    predicted = float(result.stdout.strip())
    expected = case['expected_output']
    error = abs(predicted - expected)
    total_error += error
    
    print(f'Case {i}: {case["input"]["trip_duration_days"]}d, {case["input"]["miles_traveled"]}mi, ${case["input"]["total_receipts_amount"]:.2f}')
    print(f'  Expected: ${expected:.2f}, Predicted: ${predicted:.2f}, Error: ${error:.2f}')

print(f'\nAverage error for first 20 cases: ${total_error/20:.2f}')

# Test on specific high-error cases from eval.sh
print('\n' + '='*60)
print('Testing specific high-error cases:')
print('='*60)

# High error cases from the RandomForest eval
test_cases = [
    (684, 8, 795, 1645.99, 644.69),  # Expected error with RF
    (152, 4, 69, 2321.49, 322.00),
    (996, 1, 1082, 1809.49, 446.94),
    (694, 1, 1112, 2011.44, 1423.85),
    (627, 4, 1113, 2103.82, 1695.08),
    (471, 4, 1194, 2250.51, 1691.15),
    (219, 4, 1124, 2177.18, 1567.43),
    (701, 4, 1180, 1948.55, 1565.16)
]

for case_num, days, miles, receipts, expected in test_cases:
    result = subprocess.run(
        ['./run_ultimate.sh', str(days), str(miles), str(receipts)],
        capture_output=True,
        text=True
    )
    
    predicted = float(result.stdout.strip())
    error = abs(predicted - expected)
    
    print(f'\nCase {case_num}: {days}d, {miles}mi, ${receipts:.2f}')
    print(f'  Expected: ${expected:.2f}')
    print(f'  Predicted: ${predicted:.2f}')
    print(f'  Error: ${error:.2f}')

# Full evaluation
print('\n' + '='*60)
print('Running full evaluation on 1000 cases...')
print('='*60)

total_error = 0
errors = []
exact_matches = 0
close_matches = 0
start_time = time.time()

for i, case in enumerate(data):
    if i % 200 == 0:
        print(f'Progress: {i}/1000...')
    
    result = subprocess.run(
        ['./run_ultimate.sh', 
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
    
    if error < 0.01:
        exact_matches += 1
    if error < 1.00:
        close_matches += 1

elapsed = time.time() - start_time
mae = total_error / len(data)
score = mae * 100

# Calculate percentiles
errors_array = np.array(errors)
percentiles = [25, 50, 75, 90, 95, 99]

print(f"\n✅ Ultimate Competition Results:")
print(f"  MAE: ${mae:.2f}")
print(f"  Score: {score:.0f}")
print(f"  Max error: ${max(errors):.2f}")
print(f"  Exact matches (±$0.01): {exact_matches} ({exact_matches/10:.1f}%)")
print(f"  Close matches (±$1.00): {close_matches} ({close_matches/10:.1f}%)")
print(f"  Errors > $100: {sum(1 for e in errors if e > 100)}")
print(f"  Time: {elapsed:.1f} seconds")

print(f"\nError distribution:")
for p in percentiles:
    print(f"  {p}th percentile: ${np.percentile(errors_array, p):.2f}")

print(f"\n🎯 Comparison:")
print(f"  RandomForest:              Score 5378 (MAE $52.78)")
print(f"  Original standalone:       Score 11719 (MAE $117.19)")
print(f"  Ultra-optimized:           Score 15508 (MAE $155.08)")
print(f"  Ultimate competition:      Score {score:.0f} (MAE ${mae:.2f})")

# Find worst predictions
worst_indices = np.argsort(errors)[-10:][::-1]
print(f"\n❌ Worst predictions:")
for idx in worst_indices[:5]:
    case = data[idx]
    print(f"  Case {idx}: {case['input']['trip_duration_days']}d, "
          f"{case['input']['miles_traveled']}mi, ${case['input']['total_receipts_amount']:.2f}")
    print(f"    Error: ${errors[idx]:.2f}") 