#!/bin/bash

# Black Box Legacy Reimbursement System - FINAL TUNED VERSION
# Applies 6 surgical tweaks to achieve score < 4800 (target: ~4370)

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <trip_duration_days> <miles_traveled> <total_receipts_amount>" >&2
    exit 1
fi

if ! [[ "$1" =~ ^[0-9]+(\.[0-9]+)?$ && "$2" =~ ^[0-9]+(\.[0-9]+)?$ && "$3" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
    echo "Error: All arguments must be numeric" >&2
    exit 1
fi

python3 -c "
import sys
from decimal import Decimal as D, getcontext
getcontext().prec = 12

def calculate_reimbursement(days_in, miles_in, receipts_in):
    # Convert inputs to Decimal for precision
    days = int(days_in)
    miles = D(str(miles_in))
    receipts = D(str(receipts_in))
    
    # === Step 1: Calculate Base Components ===
    per_diem = D(days) * D('100')
    
    # FIX 1: Better mileage tier-2 rate (0.48 instead of 0.45)
    if miles <= D('100'):
        mileage = miles * D('0.58')
    elif miles <= D('400'):
        mileage = D('58') + (miles - D('100')) * D('0.48')  # Changed from 0.45
    else:
        mileage = D('58') + D('144') + (miles - D('400')) * D('0.35')  # 300 * 0.48 = 144

    # FIX 2: Adaptive receipt-rate based on receipts/days
    rpd = receipts / D(days) if days else receipts
    if days <= 3:
        receipt_rate = D('0.55') if rpd < 120 else D('0.42')
    elif days <= 7:
        receipt_rate = D('0.60') if rpd < 140 else D('0.48')
    else:
        receipt_rate = D('0.45') if rpd < 110 else D('0.30')
        
    receipt_component = receipts * receipt_rate

    total = per_diem + mileage + receipt_component

    # === Step 2: Apply Adjustments ===
    
    # FIX 3: Scale .49/.99 penalties by days as well
    receipt_str = f'{receipts:.2f}'
    if receipt_str.endswith('49'):
        raw = receipts * (D('0.26') + D(days) * D('0.004'))  # 0.26-0.34
        pen = max(D('220'), min(D('640'), raw))
        total -= pen
    elif receipt_str.endswith('99'):
        raw = receipts * (D('0.17') + D(days) * D('0.003'))  # 0.17-0.25
        pen = max(D('170'), min(D('450'), raw))
        total -= pen
    
    # Efficiency bonus
    miles_per_day = miles / D(days) if days > 0 else miles
    if D('175') <= miles_per_day <= D('212'):
        total *= D('1.10')
        
    # Standard adjustments
    if days == 5: 
        total -= D('46')
    
    # FIX 6: Tiny bonus for really cheap trips
    if receipts < 40:
        total += D('18')
    
    # Low receipt penalty (adjusted threshold)
    if D('40') <= receipts <= D('50'):
        total -= D('20')

    # FIX 4: Piece-wise linear long-trip scaler
    if days >= 15:
        total *= D('0.72')
    elif days >= 12:
        total *= D('0.78')
    elif days >= 9:
        total *= D('0.84')
        
    # High spending penalty
    daily_spending = receipts / D(days) if days > 0 else receipts
    if daily_spending > D('450'):
        total *= D('0.90')

    # === Step 3: Final Capping ===
    
    # FIX 5: Special cap for 4-day monsters
    if days == 4 and receipts > D('1900'):
        total = min(total, D('800'))
    
    # General receipt blow-up guard
    rec_cap = (D(days) * D('120')) + (miles * D('0.25')) + D('50')
    if total > rec_cap:
        total = rec_cap
    
    return round(max(D('0'), total), 2)

# Python Script Entry Point
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