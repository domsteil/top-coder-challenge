#!/usr/bin/env python3
"""
Ultra-advanced parameter optimization with multi-parameter search, outlier analysis, and random exploration.
"""

import json
import random
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

def evaluate_parameters(params, data=None):
    """
    Evaluate a parameter set against all public cases.
    """
    if data is None:
        with open('public_cases.json', 'r') as f:
            data = json.load(f)
    
    total_error = D('0')
    max_error = D('0')
    errors_over_500 = 0
    high_error_cases = []
    
    for i, case in enumerate(data):
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
            high_error_cases.append({
                'index': i,
                'days': case['input']['trip_duration_days'],
                'miles': case['input']['miles_traveled'],
                'receipts': case['input']['total_receipts_amount'],
                'expected': float(expected),
                'calculated': float(calculated),
                'error': float(error)
            })
        max_error = max(max_error, error)
    
    avg_error = total_error / len(data)
    return float(avg_error), float(max_error), float(total_error), errors_over_500, high_error_cases

# Load data once
with open('public_cases.json', 'r') as f:
    data = json.load(f)

# Current best parameters from previous optimization
current_params = {
    'base_per_diem': 100,
    'mileage_tier2_rate': 0.43,
    'efficiency_min': 185,
    'efficiency_max': 215,
    
    # Short trip thresholds and rates
    'short_high_threshold': 1500,
    'short_mid_threshold': 500,
    'short_high_rate': 0.45,
    'short_mid_rate': 0.57,
    'short_low_rate': 0.40,
    
    # Medium trip thresholds and rates
    'medium_high_threshold': 1500,
    'medium_mid_threshold': 650,
    'medium_high_rate': 0.45,
    'medium_mid_rate': 0.55,
    'medium_low_rate': 0.50,
    
    # Long trip thresholds and rates
    'long_high_threshold': 1100,
    'long_mid_threshold': 500,
    'long_high_rate': 0.20,
    'long_mid_rate': 0.30,
    'long_low_rate': 0.40,
    
    # Bonuses and penalties
    'five_day_bonus': 20,
    'low_receipt_penalty': 20,
    'high_spending_threshold': 450
}

print("Ultra-Advanced Parameter Optimization")
print("=" * 80)

# Evaluate current parameters
avg_err, max_err, total_err, high_errors, high_error_cases = evaluate_parameters(current_params, data)
current_score = total_err / 100
print(f"Current score: {current_score:.2f} (avg error ${avg_err:.2f}, {high_errors} errors >$500)")

best_score = current_score
best_params = current_params.copy()

# Test 1: Ultra-fine mileage tier 2 rate (0.005 increments)
print("\n1. Ultra-fine mileage tier 2 rate tuning:")
for rate in [0.425, 0.430, 0.435, 0.440, 0.445]:
    test_params = current_params.copy()
    test_params['mileage_tier2_rate'] = rate
    avg_err, max_err, total_err, high_errors, _ = evaluate_parameters(test_params, data)
    score = total_err / 100
    print(f"  Rate {rate}: Score {score:.2f} (avg ${avg_err:.2f}, {high_errors} errors >$500)")
    if score < best_score:
        best_score = score
        best_params = test_params.copy()

# Test 2: Multi-parameter grid search
print("\n2. Multi-parameter grid search (promising combinations):")
param_combinations = [
    {'mileage_tier2_rate': 0.44, 'medium_mid_threshold': 625},
    {'mileage_tier2_rate': 0.44, 'short_mid_rate': 0.56},
    {'mileage_tier2_rate': 0.435, 'short_mid_rate': 0.565},
    {'efficiency_min': 175, 'efficiency_max': 225, 'mileage_tier2_rate': 0.44},
    {'medium_mid_threshold': 675, 'medium_mid_rate': 0.54},
    {'short_mid_rate': 0.58, 'short_mid_threshold': 475},
    {'long_high_threshold': 1050, 'long_high_rate': 0.22},
]

for combo in param_combinations:
    test_params = best_params.copy()
    test_params.update(combo)
    avg_err, max_err, total_err, high_errors, _ = evaluate_parameters(test_params, data)
    score = total_err / 100
    combo_str = ', '.join(f"{k}={v}" for k, v in combo.items())
    print(f"  {combo_str}: Score {score:.2f}")
    if score < best_score:
        best_score = score
        best_params = test_params.copy()

# Test 3: Analyze high-error patterns
print("\n3. Analyzing high-error case patterns:")
_, _, _, _, current_high_errors = evaluate_parameters(best_params, data)
if current_high_errors:
    avg_days = sum(c['days'] for c in current_high_errors) / len(current_high_errors)
    avg_miles = sum(c['miles'] for c in current_high_errors) / len(current_high_errors)
    avg_receipts = sum(c['receipts'] for c in current_high_errors) / len(current_high_errors)
    print(f"  High-error cases ({len(current_high_errors)} total):")
    print(f"    Average: {avg_days:.1f} days, {avg_miles:.0f} miles, ${avg_receipts:.2f} receipts")
    
    # Show top 3 worst cases
    worst_cases = sorted(current_high_errors, key=lambda x: x['error'], reverse=True)[:3]
    print("  Top 3 worst cases:")
    for case in worst_cases:
        print(f"    Case {case['index']}: {case['days']}d, {case['miles']}mi, ${case['receipts']:.2f} - Error: ${case['error']:.2f}")

# Test 4: Random parameter exploration
print("\n4. Random parameter search (20 iterations):")
random.seed(42)  # For reproducibility
best_random_score = best_score
best_random_params = None

for i in range(20):
    test_params = best_params.copy()
    
    # Randomly adjust 2-3 parameters
    num_params = random.choice([2, 3])
    params_to_adjust = random.sample([
        ('mileage_tier2_rate', 0.42, 0.46),
        ('medium_mid_threshold', 600, 700),
        ('short_mid_rate', 0.54, 0.60),
        ('high_spending_threshold', 425, 475),
        ('efficiency_min', 175, 190),
        ('efficiency_max', 210, 225),
        ('long_high_threshold', 1000, 1200),
        ('five_day_bonus', 15, 25),
    ], k=num_params)
    
    for param, min_val, max_val in params_to_adjust:
        if isinstance(min_val, int):
            test_params[param] = random.randint(min_val, max_val)
        else:
            test_params[param] = round(random.uniform(min_val, max_val), 3)
    
    avg_err, max_err, total_err, high_errors, _ = evaluate_parameters(test_params, data)
    score = total_err / 100
    
    if score < best_random_score:
        print(f"  🎯 Iteration {i+1}: New best! Score: {score:.2f} (avg ${avg_err:.2f})")
        best_random_score = score
        best_random_params = test_params.copy()
        if score < best_score:
            best_score = score
            best_params = test_params.copy()

# Test 5: Fine-tune around best found parameters
if best_score < current_score:
    print("\n5. Fine-tuning around best parameters:")
    # Fine-tune the most impactful parameter
    if best_params['mileage_tier2_rate'] != current_params['mileage_tier2_rate']:
        center = best_params['mileage_tier2_rate']
        for delta in [-0.01, -0.005, 0, 0.005, 0.01]:
            test_params = best_params.copy()
            test_params['mileage_tier2_rate'] = round(center + delta, 3)
            avg_err, max_err, total_err, high_errors, _ = evaluate_parameters(test_params, data)
            score = total_err / 100
            print(f"  Mileage rate {test_params['mileage_tier2_rate']}: Score {score:.2f}")
            if score < best_score:
                best_score = score
                best_params = test_params.copy()

print("\n" + "=" * 80)
print(f"Best score found: {best_score:.2f}")
print(f"Improvement: {current_score - best_score:.2f} points")
print("\nOptimal parameters (changes from current):")
changes = []
for key, value in best_params.items():
    if value != current_params[key]:
        changes.append(f"  {key}: {current_params[key]} → {value}")
        
if changes:
    for change in sorted(changes):
        print(change)
    print("\n✅ Found improvements! Update run.sh with these parameters.")
else:
    print("\n✅ Current parameters are already optimal!")

# Generate update code if improvements found
if best_score < current_score - 1:  # Only if meaningful improvement
    print("\n📝 Update code for run.sh:")
    print("Replace the following values:")
    if best_params['mileage_tier2_rate'] != current_params['mileage_tier2_rate']:
        print(f"  D('0.43') → D('{best_params['mileage_tier2_rate']}')")
    if best_params['short_mid_rate'] != current_params['short_mid_rate']:
        print(f"  receipt_rate = D('0.57') → D('{best_params['short_mid_rate']}')")
    # Add more as needed 