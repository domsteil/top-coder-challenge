#!/usr/bin/env python3
"""
Advanced parameter optimization with finer granularity and more combinations.
"""

import json
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
    errors_over_500 = 0
    
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
        if error > D('500'):
            errors_over_500 += 1
        max_error = max(max_error, error)
    
    avg_error = total_error / len(data)
    return float(avg_error), float(max_error), float(total_error), errors_over_500

# Current optimized parameters
current_params = {
    'base_per_diem': 100,
    'mileage_tier2_rate': 0.45,
    'efficiency_min': 180,
    'efficiency_max': 220,
    
    # Short trip thresholds and rates
    'short_high_threshold': 1500,
    'short_mid_threshold': 500,
    'short_high_rate': 0.45,
    'short_mid_rate': 0.55,
    'short_low_rate': 0.40,
    
    # Medium trip thresholds and rates
    'medium_high_threshold': 1500,
    'medium_mid_threshold': 600,
    'medium_high_rate': 0.45,
    'medium_mid_rate': 0.55,
    'medium_low_rate': 0.50,
    
    # Long trip thresholds and rates
    'long_high_threshold': 1000,
    'long_mid_threshold': 500,
    'long_high_rate': 0.20,
    'long_mid_rate': 0.30,
    'long_low_rate': 0.40,
    
    # Bonuses and penalties
    'five_day_bonus': 20,
    'low_receipt_penalty': 25,
    'high_spending_threshold': 450
}

print("Advanced Parameter Optimization")
print("=" * 80)

# Evaluate current parameters
avg_err, max_err, total_err, high_errors = evaluate_parameters(current_params)
current_score = total_err / 100
print(f"Current score: {current_score:.2f} (avg error ${avg_err:.2f}, {high_errors} errors >$500)")

best_score = current_score
best_params = current_params.copy()

# Test 1: Fine-tune mileage tier 2 rate with smaller steps
print("\n1. Fine-tuning mileage tier 2 rate (0.01 increments):")
for rate in [0.43, 0.44, 0.45, 0.46, 0.47]:
    test_params = current_params.copy()
    test_params['mileage_tier2_rate'] = rate
    avg_err, max_err, total_err, high_errors = evaluate_parameters(test_params)
    score = total_err / 100
    print(f"  Rate {rate}: Score {score:.2f} (avg ${avg_err:.2f}, {high_errors} errors >$500)")
    if score < best_score:
        best_score = score
        best_params = test_params.copy()

# Test 2: Fine-tune medium trip threshold
print("\n2. Fine-tuning medium trip mid threshold:")
for threshold in [550, 575, 600, 625, 650]:
    test_params = best_params.copy()
    test_params['medium_mid_threshold'] = threshold
    avg_err, max_err, total_err, high_errors = evaluate_parameters(test_params)
    score = total_err / 100
    print(f"  Threshold ${threshold}: Score {score:.2f} (avg ${avg_err:.2f})")
    if score < best_score:
        best_score = score
        best_params = test_params.copy()

# Test 3: Explore efficiency bonus range adjustments
print("\n3. Testing efficiency bonus range adjustments:")
for min_val, max_val in [(170, 220), (175, 220), (180, 225), (185, 215)]:
    test_params = best_params.copy()
    test_params['efficiency_min'] = min_val
    test_params['efficiency_max'] = max_val
    avg_err, max_err, total_err, high_errors = evaluate_parameters(test_params)
    score = total_err / 100
    print(f"  Range {min_val}-{max_val}: Score {score:.2f} (avg ${avg_err:.2f})")
    if score < best_score:
        best_score = score
        best_params = test_params.copy()

# Test 4: Try different long trip thresholds
print("\n4. Testing long trip threshold adjustments:")
for high_thresh in [900, 950, 1000, 1050, 1100]:
    test_params = best_params.copy()
    test_params['long_high_threshold'] = high_thresh
    avg_err, max_err, total_err, high_errors = evaluate_parameters(test_params)
    score = total_err / 100
    print(f"  High threshold ${high_thresh}: Score {score:.2f} (avg ${avg_err:.2f})")
    if score < best_score:
        best_score = score
        best_params = test_params.copy()

# Test 5: Fine-tune receipt rates with 0.02 increments
print("\n5. Fine-tuning short trip mid rate:")
for rate in [0.53, 0.54, 0.55, 0.56, 0.57]:
    test_params = best_params.copy()
    test_params['short_mid_rate'] = rate
    avg_err, max_err, total_err, high_errors = evaluate_parameters(test_params)
    score = total_err / 100
    print(f"  Rate {rate}: Score {score:.2f} (avg ${avg_err:.2f})")
    if score < best_score:
        best_score = score
        best_params = test_params.copy()

# Test 6: Try adjusting low receipt penalty threshold
print("\n6. Testing low receipt penalty adjustments:")
for penalty in [20, 22, 25, 27, 30]:
    test_params = best_params.copy()
    test_params['low_receipt_penalty'] = penalty
    avg_err, max_err, total_err, high_errors = evaluate_parameters(test_params)
    score = total_err / 100
    print(f"  Penalty ${penalty}: Score {score:.2f} (avg ${avg_err:.2f})")
    if score < best_score:
        best_score = score
        best_params = test_params.copy()

# Test 7: Explore combined adjustments for high-error cases
print("\n7. Testing combined adjustments for outliers:")
# Try adding a very high receipt penalty
test_params = best_params.copy()
# This would require modifying the calculation function, so we'll skip for now

print("\n" + "=" * 80)
print(f"Best score found: {best_score:.2f}")
print(f"Improvement: {current_score - best_score:.2f} points")
print("\nOptimal parameters (changes from current):")
for key, value in best_params.items():
    if value != current_params[key]:
        print(f"  {key}: {current_params[key]} → {value}")

if best_score < current_score:
    print("\n✅ Found improvements! Consider updating run.sh with these parameters.")
else:
    print("\n✅ Current parameters are already optimal!") 