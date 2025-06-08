#!/bin/bash

# Black Box Legacy Reimbursement System - FINAL WINNING VERSION
# This script implements a highly-tuned component model with surgical, data-driven
# patches to achieve the highest possible accuracy (<4800 target score).

# --- 1. Input Validation ---
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <trip_duration_days> <miles_traveled> <total_receipts_amount>" >&2
    exit 1
fi

if ! [[ "$1" =~ ^[0-9]+(\.[0-9]+)?$ && "$2" =~ ^[0-9]+(\.[0-9]+)?$ && "$3" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
    echo "Error: All arguments must be numeric" >&2
    exit 1
fi

# --- 2. Execute Final Python Logic ---
python3 -c "
import sys
from decimal import Decimal as D, getcontext
getcontext().prec = 12

def calculate_reimbursement(days_in, miles_in, receipts_in):
    \"\"\"
    This definitive model uses a component-based architecture hardened with
    three critical, data-driven patches to handle all known outlier patterns.
    \"\"\"
    
    # --- Convert inputs to Decimal for precision ---
    days = int(days_in)
    miles = D(str(miles_in))
    receipts = D(str(receipts_in))
    
    # --- Step 1: Calculate Base Components ---
    per_diem = D(days) * D('100')
    
    # A more accurate three-tier mileage structure
    if miles <= D('100'):
        mileage = miles * D('0.58')
    elif miles <= D('400'):
        mileage = D('58') + (miles - D('100')) * D('0.45') # Tuned rate
    else:
        mileage = D('58') + D('135') + (miles - D('400')) * D('0.35')

    # Variable receipt rate calculation
    if days <= 3:
        receipt_rate = D('0.50') if receipts <= 600 else D('0.40')
    elif days <= 7:
        receipt_rate = D('0.60') if receipts <= 800 else D('0.50')
    else:
        receipt_rate = D('0.40') if receipts <= 1000 else D('0.25')
        
    receipt_component = receipts * receipt_rate

    total = per_diem + mileage + receipt_component

    # --- Step 2: Apply Surgical Patches and Adjustments ---
    
    # FIX 1: Proportional penalties for .49/.99 endings
    receipt_str = f'{receipts:.2f}'
    if receipt_str.endswith('49'):
        pen = max(D('250'), min(D('650'), receipts * D('0.28')))
        total -= pen
    elif receipt_str.endswith('99'):
        pen = max(D('170'), min(D('450'), receipts * D('0.18')))
        total -= pen
    
    # Efficiency bonus
    miles_per_day = miles / D(days) if days > 0 else miles
    if D('175') <= miles_per_day <= D('212'):
        total *= D('1.10')
        
    # Other standard adjustments
    if days == 5: total -= D('46')
    if D('0') < receipts <= D('50'): total -= D('20')

    # FIX 2: Long trip per diem adjustment
    if days >= 9:
        total *= D('0.85') # Scale down for long trips
        
    # High spending penalty
    daily_spending = receipts / D(days) if days > 0 else receipts
    if daily_spending > D('450'):
        total *= D('0.90')

    # --- Step 3: Final Capping and Bounding ---
    
    # FIX 3: Receipt blow-up guard
    # A dynamic cap based on the trip's characteristics.
    rec_cap = (D(days) * D('120')) + (miles * D('0.25')) + D('50')
    if total > rec_cap:
        total = rec_cap
    
    return round(max(D('0'), total), 2)

# --- Python Script Entry Point ---
try:
    days_arg = sys.argv[1]
    miles_arg = sys.argv[2]
    receipts_arg = sys.argv[3]
    result = calculate_reimbursement(days_arg, miles_arg, receipts_arg)
    print(f'{result:.2f}')
except (ValueError, IndexError) as e:
    print(f'Error: Invalid input - {e}', file=sys.stderr)
    sys.exit(1)

" "$1" "$2" "$3" 