#!/usr/bin/env python3
"""Test the balanced standalone solution"""

import json
import subprocess
import time

# Load test cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

# Test first 10 cases
print('Testing balanced standalone solution:')
print('='*60)
total_error = 0

for i in range(10):
    case = data[i]
    result = subprocess.run(
        ['./run_balanced_standalone.sh', 
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

print(f'\nAverage error for first 10 cases: ${total_error/10:.2f}')

# Full evaluation
print('\n' + '='*60)
print('Running full evaluation on 1000 cases...')
print('='*60)

total_error = 0
errors = []
start_time = time.time()

for i, case in enumerate(data):
    if i % 100 == 0:
        print(f'Progress: {i}/1000...')
    
    result = subprocess.run(
        ['./run_balanced_standalone.sh', 
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

elapsed = time.time() - start_time
mae = total_error / len(data)
score = mae * 100

print(f"\n✅ Balanced Standalone Results:")
print(f"  MAE: ${mae:.2f}")
print(f"  Score: {score:.0f}")
print(f"  Max error: ${max(errors):.2f}")
print(f"  Errors > $100: {sum(1 for e in errors if e > 100)}")
print(f"  Time: {elapsed:.1f} seconds")

print(f"\n🎯 Comparison:")
print(f"  Original optimized standalone:  Score 7800 (MAE $78)")
print(f"  Balanced standalone:            Score {score:.0f} (MAE ${mae:.2f})")
print(f"  Improvement:                    {7800 - score:.0f} points")

# Compare with RandomForest
print(f"\n📊 Full comparison:")
print(f"  RandomForest (self-contained):  Score 5364 (MAE $52.64)")
print(f"  Original optimized standalone:  Score 7800 (MAE $78.00)")
print(f"  Balanced standalone:            Score {score:.0f} (MAE ${mae:.2f})")
print(f"  Gap to RandomForest:            {score - 5364:.0f} points") 