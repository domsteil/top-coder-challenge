#!/usr/bin/env python3
"""
Test the optimized GradientBoosting model
"""

import json
import subprocess
from decimal import Decimal as D
import numpy as np

# Load public cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

# Test on a subset first
print("Testing optimized model on sample cases:")
test_indices = [0, 1, 2, 151, 683, 995]  # Include some high-error cases

for i in test_indices:
    case = data[i]
    
    # Test both models
    result_rf = subprocess.run(
        ['./run.sh', 
         str(case['input']['trip_duration_days']),
         str(case['input']['miles_traveled']),
         str(case['input']['total_receipts_amount'])],
        capture_output=True,
        text=True
    )
    
    result_opt = subprocess.run(
        ['./run_optimized.sh', 
         str(case['input']['trip_duration_days']),
         str(case['input']['miles_traveled']),
         str(case['input']['total_receipts_amount'])],
        capture_output=True,
        text=True
    )
    
    rf_pred = float(result_rf.stdout.strip().split('\n')[-1])
    opt_pred = float(result_opt.stdout.strip())
    expected = case['expected_output']
    
    rf_error = abs(rf_pred - expected)
    opt_error = abs(opt_pred - expected)
    
    print(f"\nCase {i}: {case['input']['trip_duration_days']}d, "
          f"{case['input']['miles_traveled']}mi, "
          f"${case['input']['total_receipts_amount']:.2f}")
    print(f"  Expected:        ${expected:.2f}")
    print(f"  RandomForest:    ${rf_pred:.2f} (error: ${rf_error:.2f})")
    print(f"  GradientBoost:   ${opt_pred:.2f} (error: ${opt_error:.2f})")
    print(f"  Improvement:     ${rf_error - opt_error:.2f}")

# Full evaluation
print("\n" + "="*60)
print("Running full evaluation on 1000 cases...")
print("="*60)

total_rf_error = 0
total_opt_error = 0
improvements = 0

for i, case in enumerate(data):
    if i % 100 == 0:
        print(f"Progress: {i}/1000...")
    
    result_opt = subprocess.run(
        ['./run_optimized.sh', 
         str(case['input']['trip_duration_days']),
         str(case['input']['miles_traveled']),
         str(case['input']['total_receipts_amount'])],
        capture_output=True,
        text=True
    )
    
    opt_pred = float(result_opt.stdout.strip())
    expected = case['expected_output']
    opt_error = abs(opt_pred - expected)
    
    total_opt_error += opt_error
    
    # Compare with known RF performance
    rf_avg_error = 52.64
    if opt_error < rf_avg_error:
        improvements += 1

opt_mae = total_opt_error / len(data)
opt_score = opt_mae * 100

print(f"\n✅ Optimized Model Results:")
print(f"  MAE: ${opt_mae:.2f}")
print(f"  Score: {opt_score:.0f}")
print(f"  Cases improved vs RF average: {improvements}/{len(data)} ({improvements/len(data)*100:.1f}%)")

print(f"\nComparison:")
print(f"  RandomForest:     Score 5363.90 (MAE $52.64)")
print(f"  GradientBoost:    Score {opt_score:.0f} (MAE ${opt_mae:.2f})")
print(f"  Improvement:      {5363.90 - opt_score:.0f} points") 