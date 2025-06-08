#!/bin/bash

# Black Box Legacy Reimbursement System - Aggressive Penalty Version
# Focus on strong penalties for .49/.99 receipt endings

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <trip_duration_days> <miles_traveled> <total_receipts_amount>" >&2
    exit 1
fi

if ! [[ "$1" =~ ^[0-9]+\.?[0-9]*$ ]] || ! [[ "$2" =~ ^[0-9]+\.?[0-9]*$ ]] || ! [[ "$3" =~ ^[0-9]+\.?[0-9]*$ ]]; then
    echo "Error: All arguments must be numeric" >&2
    exit 1
fi

python3 -c "
import sys
import math
from decimal import Decimal as D, getcontext
getcontext().prec = 12

def calculate_reimbursement(days_in, miles_in, receipts_in):
    days = int(days_in)
    miles = float(miles_in)
    receipts = float(receipts_in)
    
    # Initialize base amount
    total = D('0')
    
    # === COMPONENT 1: Base Per Diem ===
    per_diem = D('100')
    total += per_diem * D(str(days))
    
    # === COMPONENT 2: Mileage Reimbursement ===
    if miles <= 100:
        total += D(str(miles * 0.58))
    elif miles <= 400:
        total += D('58') + D(str((miles - 100) * 0.419))
    else:
        total += D('58') + D('125.7') + D(str((miles - 400) * 0.35))
    
    # === COMPONENT 3: Receipt Processing ===
    if receipts > 0:
        # Base receipt rate varies by trip length
        if days <= 2:
            receipt_rate = 0.55 if receipts <= 500 else 0.45
        elif days <= 4:
            receipt_rate = 0.50 if receipts <= 600 else 0.40
        elif days <= 7:
            receipt_rate = 0.45 if receipts <= 800 else 0.35
        else:
            receipt_rate = 0.40 if receipts <= 1000 else 0.30
        
        receipt_value = D(str(receipts * receipt_rate))
        total += receipt_value
    
    # === CRITICAL: Receipt ending penalties ===
    # Based on test cases, these need to be MUCH stronger
    receipt_str = f'{receipts:.2f}'
    if receipt_str.endswith('49') or receipt_str.endswith('99'):
        # Calculate expected ratio based on total input
        total_input = days + miles + receipts
        
        # These cases typically result in very low reimbursement ratios
        # Apply a percentage-based reduction to achieve target ratios
        if receipt_str.endswith('49'):
            # .49 cases get the most severe penalty
            # Target ratio around 0.15-0.20
            total *= D('0.25')  # Reduce to 25% of calculated value
        else:
            # .99 cases get moderate penalty
            # Target ratio around 0.25-0.35
            total *= D('0.40')  # Reduce to 40% of calculated value
    
    # === OTHER ADJUSTMENTS ===
    miles_per_day = miles / days if days > 0 else miles
    receipts_per_day = receipts / days if days > 0 else receipts
    
    # Efficiency bonus (only if not .49/.99)
    if not (receipt_str.endswith('49') or receipt_str.endswith('99')):
        if 175 <= miles_per_day <= 212:
            total *= D('1.10')
        elif miles_per_day > 300:
            total *= D('0.95')
    
    # Day-specific adjustments (reduced impact for .49/.99 cases)
    if not (receipt_str.endswith('49') or receipt_str.endswith('99')):
        if days == 5:
            total -= D('46')
        elif days in [2, 3]:
            total += D('15')
        elif days == 1:
            total += D('10')
        elif days >= 10:
            total -= D('25')
    
    # High spending penalty (only if not already penalized)
    if not (receipt_str.endswith('49') or receipt_str.endswith('99')):
        if receipts_per_day > 500:
            total *= D('0.85')
    
    # Low receipt bonus
    if receipts_per_day < 100 and receipts > 0:
        if not (receipt_str.endswith('49') or receipt_str.endswith('99')):
            total += D('44')
    
    # Feature interactions (reduced for .49/.99)
    if not (receipt_str.endswith('49') or receipt_str.endswith('99')):
        total_input = days + miles + receipts
        if total_input > 2000:
            total += D(str((total_input - 2000) * 0.01))
    
    # Final bounds
    if total > D('2500'):
        total = D('2500') + (total - D('2500')) * D('0.7')
    elif total < D('50'):
        total = D('50')
    
    return round(max(D('0'), total), 2)

result = calculate_reimbursement(sys.argv[1], sys.argv[2], sys.argv[3])
print(f'{result:.2f}')
" "$1" "$2" "$3" 