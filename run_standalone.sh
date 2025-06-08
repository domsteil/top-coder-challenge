#!/bin/bash

# Black Box Legacy Reimbursement System - Self-Contained Solution
# Ultra-optimized model with score ~17209
# All logic embedded - no external dependencies

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
from decimal import Decimal as D, getcontext
getcontext().prec = 12

def calculate_reimbursement(days_in, miles_in, receipts_in):
    days = int(days_in)
    miles = D(str(miles_in))
    receipts = D(str(receipts_in))
    
    # Base per diem
    per_diem = days * D('100')
    
    # Tiered mileage
    if miles <= D('100'):
        mileage = miles * D('0.58')
    else:
        mileage = (D('100') * D('0.58')) + ((miles - D('100')) * D('0.419'))
    
    # Efficiency bonus
    miles_per_day = miles / days if days > 0 else miles
    if D('175') <= miles_per_day <= D('212'):
        mileage *= D('1.15')
    
    # Receipt component
    if days <= 3:
        if receipts > D('1500'):
            receipt_rate = D('0.45')
        elif receipts > D('475'):
            receipt_rate = D('0.58')
        else:
            receipt_rate = D('0.40')
    elif days <= 7:
        if receipts > D('1500'):
            receipt_rate = D('0.45')
        elif receipts > D('694'):
            receipt_rate = D('0.55')
        else:
            receipt_rate = D('0.50')
    else:
        if receipts > D('1154'):
            receipt_rate = D('0.20')
        elif receipts > D('500'):
            receipt_rate = D('0.30')
        else:
            receipt_rate = D('0.40')
    
    receipt_component = receipts * receipt_rate
    
    # Adjustments
    if days == 5:
        per_diem += D('19')
    
    if D('0') < receipts <= D('50'):
        per_diem -= D('20')
    
    daily_spending = receipts / days if days > 0 else receipts
    if daily_spending > D('450'):
        per_diem *= D('0.5')
    
    per_diem = max(D('0'), per_diem)
    
    receipt_str = f'{receipts:.2f}'
    if receipt_str.endswith(('49', '99')):
        receipt_component += D('5.01')
    
    total = per_diem + mileage + receipt_component
    return round(max(D('0'), total), 2)

result = calculate_reimbursement(sys.argv[1], sys.argv[2], sys.argv[3])
print(f'{result:.2f}')
" "$1" "$2" "$3" 