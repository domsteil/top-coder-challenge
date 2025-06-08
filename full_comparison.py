#!/usr/bin/env python3
"""Full comparison between original optimized and final standalone solutions"""

import json
import subprocess
import time

# Load test cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

print('Full evaluation on 1000 cases')
print('='*60)

# Test both solutions
for script_name, script_path in [
    ('Original Optimized', './run_optimized_standalone.sh'),
    ('Final Standalone', './run_final_standalone.sh')
]:
    print(f'\nTesting {script_name}...')
    total_error = 0
    errors = []
    start_time = time.time()
    
    for i, case in enumerate(data):
        if i % 200 == 0:
            print(f'  Progress: {i}/1000...')
        
        result = subprocess.run(
            [script_path, 
             str(case['input']['trip_duration_days']),
             str(case['input']['miles_traveled']),
             str(case['input']['total_receipts_amount'])],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"  Error on case {i}: {result.stderr}")
            continue
        
        predicted = float(result.stdout.strip())
        expected = case['expected_output']
        error = abs(predicted - expected)
        
        total_error += error
        errors.append(error)
    
    elapsed = time.time() - start_time
    mae = total_error / len(data)
    score = mae * 100
    
    print(f"\n✅ {script_name} Results:")
    print(f"  MAE: ${mae:.2f}")
    print(f"  Score: {score:.0f}")
    print(f"  Max error: ${max(errors):.2f}")
    print(f"  Errors > $100: {sum(1 for e in errors if e > 100)}")
    print(f"  Time: {elapsed:.1f} seconds")

print("\n" + "="*60)
print("Summary:")
print("  Original optimized standalone claimed: Score 7800 (MAE $78)")
print("  Actual scores shown above")
print("\n  Best available:")
print("  RandomForest (self-contained): Score 5364 (MAE $52.64)") 