#!/bin/bash

# Black Box Legacy Reimbursement System - FINAL WINNING VERSION
# This script implements a multi-stage, feature-rich, hybrid calculation pipeline
# that synthesizes all discoveries for maximum accuracy.
# Target Score: < 4800

# --- 1. Input Validation ---
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <trip_duration_days> <miles_traveled> <total_receipts_amount>" >&2
    exit 1
fi

if ! [[ "$1" =~ ^[0-9]+(\.[0-9]+)?$ && "$2" =~ ^[0-9]+(\.[0-9]+)?$ && "$3" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
    echo "Error: All arguments must be numeric" >&2
    exit 1
fi

# --- 2. Execute Ultimate Python Logic ---
exec python3 -c "
import sys
import math
from decimal import Decimal as D, getcontext
getcontext().prec = 12

def calculate_reimbursement(days_in, miles_in, receipts_in):
    \"\"\"
    This definitive model uses a multi-stage pipeline to replicate the legacy system.
    It combines component calculations, feature-based adjustments, and final safeguards.
    \"\"\"
    
    # --- Convert inputs to Decimal for precision ---
    days = int(days_in)
    miles = D(str(miles_in))
    receipts = D(str(receipts_in))
    
    # --- Step 1: Calculate Base Components ---
    per_diem = D(days) * D('100')
    
    if miles <= D('100'):
        mileage = miles * D('0.58')
    elif miles <= D('400'):
        mileage = D('58') + (miles - D('100')) * D('0.48')
    else:
        mileage = D('58') + D('144') + (miles - D('400')) * D('0.35')

    rpd = receipts / D(days) if days else receipts
    if days <= 3:
        receipt_rate = D('0.55') if rpd < 120 else D('0.42')
    elif days <= 7:
        receipt_rate = D('0.60') if rpd < 140 else D('0.48')
    else:
        receipt_rate = D('0.45') if rpd < 110 else D('0.30')
    
    receipt_component = receipts * receipt_rate
    
    total = per_diem + mileage + receipt_component
    
    # --- Step 2: Apply Critical Adjustments & Penalties ---
    receipt_str = f'{receipts:.2f}'
    if receipt_str.endswith('49'):
        raw_pen = receipts * (D('0.26') + D(days) * D('0.004'))
        penalty = max(D('220'), min(D('640'), raw_pen))
        total -= penalty
    elif receipt_str.endswith('99'):
        raw_pen = receipts * (D('0.17') + D(days) * D('0.003'))
        penalty = max(D('170'), min(D('450'), raw_pen))
        total -= penalty
    else:
        total += D('5')

    # --- Step 3: Apply Feature-Based Adjustments ---
    miles_per_day = miles / D(days) if days > 0 else miles
    if D('175') <= miles_per_day <= D('212'):
        total *= D('1.10')
    
    if days == 5: total -= D('46')
    elif days >= 9: total *= D('0.84') if days < 12 else (D('0.78') if days < 15 else D('0.72'))

    if receipts < D('40'): total += D('18')
    
    # --- Step 4: Final Safeguards and Caps ---
    if days == 4 and receipts > D('1900'):
        total = min(total, D('800'))
        
    rec_cap = (D(days) * D('120')) + (miles * D('0.25')) + D('50')
    if total > rec_cap:
        total = rec_cap
    
    return round(max(D('0'), total), 2)

# --- Python Script Entry Point ---
try:
    result = calculate_reimbursement(sys.argv[1], sys.argv[2], sys.argv[3])
    print(f'{result:.2f}')
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)

" "$1" "$2" "$3" 