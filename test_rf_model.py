#!/usr/bin/env python3
"""
Test the RandomForest model solution
"""

import json
import subprocess
from decimal import Decimal as D
import numpy as np

# Load public cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

total_error = D('0')
errors = []

print("Testing RandomForest model...")
print("Sample results:")

for i, case in enumerate(data):
    # Run the shell script
    result = subprocess.run(
        ['./run.sh', 
         str(case['input']['trip_duration_days']),
         str(case['input']['miles_traveled']),
         str(case['input']['total_receipts_amount'])],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error on case {i}: {result.stderr}")
        continue
    
    # Extract the numeric value from output (ignore warnings)
    output_lines = result.stdout.strip().split('\n')
    calculated = D(output_lines[-1])  # Last line should be the number
    
    expected = D(str(case['expected_output']))
    error = abs(expected - calculated)
    total_error += error
    errors.append(float(error))
    
    # Show first 10 cases
    if i < 10:
        print(f"Case {i}: {case['input']['trip_duration_days']}d, "
              f"{case['input']['miles_traveled']}mi, "
              f"${case['input']['total_receipts_amount']:.2f} → "
              f"Expected: ${expected}, Got: ${calculated}, Error: ${error:.2f}")

mae = float(total_error) / len(data)
print(f"\n{'='*60}")
print(f"RANDOMFOREST MODEL RESULTS:")
print(f"{'='*60}")
print(f"Mean Absolute Error: ${mae:.2f}")
print(f"Expected Score: {int(mae * 100)}")
print(f"Max error: ${max(errors):.2f}")
print(f"Errors > $100: {sum(1 for e in errors if e > 100)}")
print(f"Errors > $50: {sum(1 for e in errors if e > 50)}")

# Error distribution
errors_array = np.array(errors)
print(f"\nError distribution:")
print(f"  10th percentile: ${np.percentile(errors_array, 10):.2f}")
print(f"  25th percentile: ${np.percentile(errors_array, 25):.2f}")
print(f"  50th percentile (median): ${np.percentile(errors_array, 50):.2f}")
print(f"  75th percentile: ${np.percentile(errors_array, 75):.2f}")
print(f"  90th percentile: ${np.percentile(errors_array, 90):.2f}")

# Compare to previous models
print(f"\nComparison:")
print(f"  Ultra-optimized model: Score 17209 (MAE ~$172)")
print(f"  Decision tree model: Score 13161 (MAE ~$132)")
print(f"  RandomForest model: Score {int(mae * 100)} (MAE ${mae:.2f})")

if mae < 70:
    print("\n✅ SUCCESS! Achieved target MAE < $70!")
    print(f"   This should win the competition with score ~{int(mae * 100)}!")
else:
    print(f"\n📊 Still ${mae - 70:.2f} away from the $70 target") 