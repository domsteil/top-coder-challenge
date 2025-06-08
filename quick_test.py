#!/usr/bin/env python3
import json
import subprocess

# Load test cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

# Test both solutions on first 100 cases
for script_name, script_path in [
    ('Original Optimized', './run_optimized_standalone.sh'),
    ('Final Standalone', './run_final_standalone.sh')
]:
    errors = []
    for i, case in enumerate(data[:100]):
        result = subprocess.run(
            [script_path, 
             str(case['input']['trip_duration_days']),
             str(case['input']['miles_traveled']),
             str(case['input']['total_receipts_amount'])],
            capture_output=True,
            text=True
        )
        
        predicted = float(result.stdout.strip())
        expected = case['expected_output']
        error = abs(predicted - expected)
        errors.append(error)
    
    mae = sum(errors) / len(errors)
    score = mae * 100
    
    print(f'{script_name} (first 100 cases):')
    print(f'  MAE: ${mae:.2f}')
    print(f'  Score: {score:.0f}')
    print(f'  Max error: ${max(errors):.2f}')
    print(f'  Errors > $100: {sum(1 for e in errors if e > 100)}')
    print() 