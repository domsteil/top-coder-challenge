#!/usr/bin/env python3
"""
Phase 2: Re-encode regression weights as explicit deterministic rules
Based on the shocking discoveries from Phase 1 regression
"""

import json
import numpy as np
from decimal import Decimal as D, getcontext
getcontext().prec = 12

def calculate_reimbursement_v2(days_in, miles_in, receipts_in):
    """
    New model based on regression insights:
    - Rounding .49/.99 is a PENALTY, not bonus
    - 5-day trips get PENALIZED
    - Low receipts get BONUS
    - Strong logarithmic receipt handling
    """
    
    days = int(days_in)
    miles = D(str(miles_in))
    receipts = D(str(receipts_in))
    
    # Start with intercept from regression
    total = D('711.32')
    
    # --- 1. Per Diem Component ---
    # Regression showed $64.94/day
    total += days * D('64.94')
    
    # --- 2. Mileage Component ---
    # Tier 1: 0-100 miles at $0.824/mile
    tier1_miles = min(miles, D('100'))
    total += tier1_miles * D('0.824')
    
    # Tier 2: 101-400 miles at $0.490/mile
    if miles > D('100'):
        tier2_miles = min(miles - D('100'), D('300'))
        total += tier2_miles * D('0.490')
    
    # Tier 3: 401+ miles at $0.434/mile
    if miles > D('400'):
        tier3_miles = miles - D('400')
        total += tier3_miles * D('0.434')
    
    # --- 3. Receipt Component ---
    # Strong negative log component: -387.56 * log(receipts+1)
    if receipts > 0:
        log_receipts = float(np.log1p(float(receipts)))
        total -= D(str(387.56 * log_receipts))
    
    # Linear receipt component: -0.8008 * receipts
    total -= receipts * D('0.8008')
    
    # Sqrt component: +111.99 * sqrt(receipts)
    if receipts > 0:
        sqrt_receipts = float(np.sqrt(float(receipts)))
        total += D(str(111.99 * sqrt_receipts))
    
    # --- 4. Special Adjustments ---
    
    # 5-day PENALTY: -$46.24
    if days == 5:
        total -= D('46.24')
    
    # Low receipt BONUS: +$44.52
    if D('0') < receipts <= D('50'):
        total += D('44.52')
    
    # Rounding bug PENALTY: -$472.73
    receipt_str = f'{receipts:.2f}'
    if receipt_str.endswith(('49', '99')):
        total -= D('472.73')
    
    # High daily spending penalty: -$54.64
    daily_spending = receipts / days if days > 0 else receipts
    if daily_spending > D('450'):
        total -= D('54.64')
    
    # Very high daily spending adjustment: +$35.59 (partially offsets the above)
    if daily_spending > D('500'):
        total += D('35.59')
    
    # Extreme receipts penalty: -$139.33
    if receipts > D('2000'):
        total -= D('139.33')
    
    # Trip type adjustments
    if days <= 3:  # Short trip
        total -= D('16.38')
    elif 3 < days <= 7:  # Medium trip
        total += D('62.90')
    else:  # Long trip
        total -= D('46.52')
    
    # Efficiency bonus
    miles_per_day = miles / days if days > 0 else miles
    if D('180') <= miles_per_day <= D('220'):
        total += D('14.75')
    
    # Narrow efficiency penalty (overlaps with above)
    if D('185') <= miles_per_day <= D('215'):
        total -= D('18.51')
    
    return round(max(D('0'), total), 2)

# Test on public cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

total_error = D('0')
errors = []

for i, case in enumerate(data):
    expected = D(str(case['expected_output']))
    calculated = calculate_reimbursement_v2(
        case['input']['trip_duration_days'],
        case['input']['miles_traveled'],
        case['input']['total_receipts_amount']
    )
    
    error = abs(expected - calculated)
    total_error += error
    errors.append(float(error))
    
    if i < 5:  # Show first few examples
        print(f"Case {i}: {case['input']['trip_duration_days']}d, "
              f"{case['input']['miles_traveled']}mi, "
              f"${case['input']['total_receipts_amount']:.2f} → "
              f"Expected: ${expected}, Got: ${calculated}, Error: ${error}")

mae = float(total_error) / len(data)
print(f"\nPhase 2 MAE: ${mae:.2f}")
print(f"Max error: ${max(errors):.2f}")
print(f"Errors > $100: {sum(1 for e in errors if e > 100)}")
print(f"Errors > $500: {sum(1 for e in errors if e > 500)}")

# Analyze remaining errors
high_errors = [(i, errors[i]) for i in range(len(errors)) if errors[i] > 200]
high_errors.sort(key=lambda x: x[1], reverse=True)

print(f"\nTop 5 highest errors:")
for idx, err in high_errors[:5]:
    case = data[idx]
    print(f"  Case {idx}: {case['input']['trip_duration_days']}d, "
          f"{case['input']['miles_traveled']}mi, "
          f"${case['input']['total_receipts_amount']:.2f} - Error: ${err:.2f}")

print("\n✅ Phase 2 complete!")
print("   The regression-based rules are performing well but need refinement.")
print("   Next: Use decision trees in Phase 3 to capture non-linear patterns") 