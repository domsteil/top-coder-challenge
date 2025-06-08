#!/usr/bin/env python3
"""
Generate test results CSV from public cases for ratio analysis
"""

import json
import csv
import subprocess

# Load public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Open CSV file for writing
with open('test_results.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['days', 'miles', 'receipts', 'expected', 'predicted', 'error'])
    
    print("Generating test results...")
    for i, case in enumerate(cases):
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Run current solution to get prediction
        result = subprocess.run(
            ['./run.sh', str(days), str(miles), str(receipts)],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            predicted = float(result.stdout.strip())
            error = predicted - expected
            
            writer.writerow([days, miles, receipts, expected, predicted, error])
        
        if i % 100 == 0:
            print(f"Processed {i}/{len(cases)} cases...")
    
    print(f"Generated test_results.csv with {len(cases)} cases") 