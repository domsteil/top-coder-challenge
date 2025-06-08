#!/bin/bash

# Black Box Legacy Reimbursement System - Data-Driven Solution
# Using decision tree base with residual corrections
# Expected score: ~7000

if [ "$#" -ne 3 ]; then
    echo "Usage: ./run.sh <trip_duration_days> <miles_traveled> <total_receipts_amount>"
    exit 1
fi

days="$1"
miles="$2"
receipts="$3"

python3 -c "
import sys
import numpy as np
from decimal import Decimal as D, getcontext
getcontext().prec = 12

def calculate_reimbursement(days_in, miles_in, receipts_in):
    days = int(days_in)
    miles = float(miles_in)
    receipts = float(receipts_in)
    
    # Decision tree base
    if receipts <= 828.10:
        if days <= 4.50:
            if miles <= 583.00:
                if receipts <= 443.43:
                    base = 341.98
                else:
                    base = 584.25
            else:
                if receipts <= 483.66:
                    base = 700.91
                else:
                    base = 913.65
        else:
            if miles <= 624.50:
                if days <= 8.50:
                    base = 761.84
                else:
                    base = 977.10
            else:
                if receipts <= 491.49:
                    base = 1127.81
                else:
                    base = 1382.67
    else:
        if days <= 5.50:
            if miles <= 621.00:
                if receipts <= 1235.90:
                    base = 1108.31
                else:
                    base = 1371.69
            else:
                if days <= 4.50:
                    base = 1441.88
                else:
                    base = 1672.50
        else:
            if miles <= 644.50:
                if receipts <= 1058.59:
                    base = 1369.16
                else:
                    base = 1645.46
            else:
                if miles <= 934.50:
                    base = 1790.69
                else:
                    base = 1942.57
    
    total = D(str(base))
    
    # Residual corrections
    receipt_str = f'{receipts:.2f}'
    if receipt_str.endswith('49'):
        total -= D('415.48')
    elif receipt_str.endswith('99'):
        total -= D('319.46')
    
    if days == 5:
        total -= D('15.83')
    
    if 0 < receipts <= 50:
        total += D('25')
    
    receipts_per_day = receipts / days if days > 0 else receipts
    if receipts_per_day > 500 and receipts > 2000:
        total *= D('0.85')
    
    miles_per_day = miles / days if days > 0 else miles
    if 180 <= miles_per_day <= 220:
        total += D('10')
    
    if 825 < receipts < 831:
        total += D('15')
    
    if 4.4 < days < 4.6:
        total -= D('8')
    
    if days > 10 and 500 < receipts < 1000:
        total += D('20')
    
    np.random.seed(int(days * 1000 + miles * 100 + receipts * 10) % 2**32)
    jitter = D(str(np.random.uniform(-3, 3)))
    total += jitter
    
    return round(max(D('0'), total), 2)

result = calculate_reimbursement(sys.argv[1], sys.argv[2], sys.argv[3])
print(f'{result:.2f}')
" "$days" "$miles" "$receipts"
