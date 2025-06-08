#!/usr/bin/env python3
"""
Parameter optimization for the best-performing reimbursement model.
Focuses on high-impact parameters identified in the analysis.
"""

import json
import subprocess
from decimal import Decimal as D, getcontext
from itertools import product
import sys

getcontext().prec = 12

def calculate_reimbursement_with_params(days_in, miles_in, receipts_in, params):
    """
    Calculate reimbursement with custom parameters for testing.
    """
    days = int(days_in)
    miles = D(str(miles_in))
    receipts = D(str(receipts_in))
    
    # Unpack parameters
    p = params
    
    # Base per diem
    per_diem = days * D(str(p['base_per_diem']))
    
    # Tiered mileage
    if miles <= D('100'):
        mileage = miles * D('0.58')
    else:
        mileage = (D('100') * D('0.58')) + ((miles - D('100')) * D(str(p['mileage_tier2_rate'])))
    
    # Mileage efficiency bonus
    miles_per_day = miles / days if days > 0 else miles
    if D(str(p['efficiency_min'])) <= miles_per_day <= D(str(p['efficiency_max'])):
        mileage *= D('1.15')
    
    # Receipt component with variable rates
    if days <= 3:  # Short trips
        if receipts > D(str(p['short_high_threshold'])):
            receipt_rate = D(str(p['short_high_rate']))
        elif receipts > D(str(p['short_mid_threshold'])):
            receipt_rate = D(str(p['short_mid_rate']))
        else:
            receipt_rate = D(str(p['short_low_rate']))
    elif days <= 7:  # Medium trips
        if receipts > D(str(p['medium_high_threshold'])):
            receipt_rate = D(str(p['medium_high_rate']))
        elif receipts > D(str(p['medium_mid_threshold'])):
            receipt_rate = D(str(p['medium_mid_rate']))
        else:
            receipt_rate = D(str(p['medium_low_rate']))
    else:  # Long trips
        if receipts > D(str(p['long_high_threshold'])):
            receipt_rate = D(str(p['long_high_rate']))
        elif receipts > D(str(p['long_mid_threshold'])):
            receipt_rate = D(str(p['long_mid_rate']))
        else:
            receipt_rate = D(str(p['long_low_rate']))
    
    receipt_component = receipts * receipt_rate
    
    # Bonuses and penalties
    if days == 5:
        per_diem += D(str(p['five_day_bonus']))
    
    if D('0') < receipts <= D('50'):
        per_diem -= D(str(p['low_receipt_penalty']))
    
    daily_spending = receipts / days if days > 0 else receipts
    if daily_spending > D(str(p['high_spending_threshold'])):
        per_diem *= D('0.5')
    
    per_diem = max(D('0'), per_diem)
    
    # Rounding bug bonus
    receipt_str = f'{receipts:.2f}'
    if receipt_str.endswith(('49', '99')):
        receipt_component += D('5.01')
    
    total = per_diem + mileage + receipt_component
    return round(max(D('0'), total), 2)

def evaluate_parameters(params):
    """
    Evaluate a parameter set against all public cases.
    """
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    total_error = D('0')
    max_error = D('0')
    
    # data is a list, not a dict with 'cases' key
    for case in data:
        expected = D(str(case['expected_output']))
        calculated = calculate_reimbursement_with_params(
            case['input']['trip_duration_days'],
            case['input']['miles_traveled'],
            case['input']['total_receipts_amount'],
            params
        )
        
        error = abs(expected - calculated)
        total_error += error
        max_error = max(max_error, error)
    
    avg_error = total_error / len(data)
    return float(avg_error), float(max_error), float(total_error)

# Current best parameters
base_params = {
    'base_per_diem': 100,
    'mileage_tier2_rate': 0.48,
    'efficiency_min': 180,
    'efficiency_max': 220,
    
    # Short trip thresholds and rates
    'short_high_threshold': 1500,
    'short_mid_threshold': 500,
    'short_high_rate': 0.45,
    'short_mid_rate': 0.50,
    'short_low_rate': 0.40,
    
    # Medium trip thresholds and rates
    'medium_high_threshold': 1500,
    'medium_mid_threshold': 500,
    'medium_high_rate': 0.45,
    'medium_mid_rate': 0.60,
    'medium_low_rate': 0.50,
    
    # Long trip thresholds and rates
    'long_high_threshold': 1000,
    'long_mid_threshold': 500,
    'long_high_rate': 0.20,
    'long_mid_rate': 0.30,
    'long_low_rate': 0.40,
    
    # Bonuses and penalties
    'five_day_bonus': 25,
    'low_receipt_penalty': 25,
    'high_spending_threshold': 500
}

print("Testing parameter variations...")
print("=" * 80)

# Test 1: Adjust medium trip mid threshold (highest impact expected)
print("\n1. Testing medium trip mid threshold adjustments:")
best_score = float('inf')
best_params = base_params.copy()

for threshold in [400, 450, 500, 550, 600]:
    test_params = base_params.copy()
    test_params['medium_mid_threshold'] = threshold
    avg_err, max_err, total_err = evaluate_parameters(test_params)
    score = total_err / 100  # Convert to score format
    print(f"  Threshold ${threshold}: Score {score:.2f} (avg error ${avg_err:.2f})")
    if score < best_score:
        best_score = score
        best_params = test_params.copy()

# Test 2: Adjust medium trip mid rate
print("\n2. Testing medium trip mid rate adjustments:")
for rate in [0.55, 0.58, 0.60, 0.62, 0.65]:
    test_params = best_params.copy()
    test_params['medium_mid_rate'] = rate
    avg_err, max_err, total_err = evaluate_parameters(test_params)
    score = total_err / 100
    print(f"  Rate {rate}: Score {score:.2f} (avg error ${avg_err:.2f})")
    if score < best_score:
        best_score = score
        best_params = test_params.copy()

# Test 3: Adjust high spending threshold
print("\n3. Testing high spending threshold adjustments:")
for threshold in [450, 475, 500, 525, 550]:
    test_params = best_params.copy()
    test_params['high_spending_threshold'] = threshold
    avg_err, max_err, total_err = evaluate_parameters(test_params)
    score = total_err / 100
    print(f"  Threshold ${threshold}: Score {score:.2f} (avg error ${avg_err:.2f})")
    if score < best_score:
        best_score = score
        best_params = test_params.copy()

# Test 4: Adjust five-day bonus
print("\n4. Testing five-day bonus adjustments:")
for bonus in [20, 22, 25, 27, 30]:
    test_params = best_params.copy()
    test_params['five_day_bonus'] = bonus
    avg_err, max_err, total_err = evaluate_parameters(test_params)
    score = total_err / 100
    print(f"  Bonus ${bonus}: Score {score:.2f} (avg error ${avg_err:.2f})")
    if score < best_score:
        best_score = score
        best_params = test_params.copy()

# Test 5: Fine-tune short trip rates
print("\n5. Testing short trip mid rate adjustments:")
for rate in [0.45, 0.48, 0.50, 0.52, 0.55]:
    test_params = best_params.copy()
    test_params['short_mid_rate'] = rate
    avg_err, max_err, total_err = evaluate_parameters(test_params)
    score = total_err / 100
    print(f"  Rate {rate}: Score {score:.2f} (avg error ${avg_err:.2f})")
    if score < best_score:
        best_score = score
        best_params = test_params.copy()

# Test 6: Mileage tier 2 rate
print("\n6. Testing mileage tier 2 rate adjustments:")
for rate in [0.45, 0.46, 0.48, 0.50, 0.52]:
    test_params = best_params.copy()
    test_params['mileage_tier2_rate'] = rate
    avg_err, max_err, total_err = evaluate_parameters(test_params)
    score = total_err / 100
    print(f"  Rate {rate}: Score {score:.2f} (avg error ${avg_err:.2f})")
    if score < best_score:
        best_score = score
        best_params = test_params.copy()

print("\n" + "=" * 80)
print(f"Best score found: {best_score:.2f}")
print("\nOptimal parameters (changes from baseline):")
for key, value in best_params.items():
    if value != base_params[key]:
        print(f"  {key}: {base_params[key]} → {value}")

# Generate optimized run.sh if improvements found
if best_score < 186.25:  # Current score is ~18625
    print("\n✅ Found improvements! Generating optimized run.sh...")
    # Would generate the file here
else:
    print("\n❌ No improvements found. Current parameters are already optimal.") 