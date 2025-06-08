#!/bin/bash

# Black Box Legacy Reimbursement System - Optimized Version
# Using decision tree with residual corrections
# Expected score: ~7000

# Validate arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <trip_duration_days> <miles_traveled> <total_receipts_amount>" >&2
    exit 1
fi

# Input validation
if ! [[ "$1" =~ ^[0-9]+\.?[0-9]*$ ]] || ! [[ "$2" =~ ^[0-9]+\.?[0-9]*$ ]] || ! [[ "$3" =~ ^[0-9]+\.?[0-9]*$ ]]; then
    echo "Error: All arguments must be numeric" >&2
    exit 1
fi

exec python3 -c '
import sys
from decimal import Decimal as D, getcontext
import random

getcontext().prec = 12

# Decision tree lookup table for better performance
TREE_RULES = [
    # (receipts_max, days_max, miles_max, receipts_min, base_value)
    (828.10, 4.50, 583.00, 0, 443.43, 341.98),
    (828.10, 4.50, 583.00, 443.43, float("inf"), 584.25),
    (828.10, 4.50, float("inf"), 0, 483.66, 700.91),
    (828.10, 4.50, float("inf"), 483.66, float("inf"), 913.65),
    (828.10, 8.50, 624.50, 0, float("inf"), 761.84),
    (828.10, float("inf"), 624.50, 0, float("inf"), 977.10),
    (828.10, float("inf"), float("inf"), 0, 491.49, 1127.81),
    (828.10, float("inf"), float("inf"), 491.49, float("inf"), 1382.67),
    (float("inf"), 5.50, 621.00, 828.10, 1235.90, 1108.31),
    (float("inf"), 5.50, 621.00, 1235.90, float("inf"), 1371.69),
    (float("inf"), 4.50, float("inf"), 828.10, float("inf"), 1441.88),
    (float("inf"), 5.50, float("inf"), 828.10, float("inf"), 1672.50),
    (float("inf"), float("inf"), 644.50, 828.10, 1058.59, 1369.16),
    (float("inf"), float("inf"), 644.50, 1058.59, float("inf"), 1645.46),
    (float("inf"), float("inf"), 934.50, 828.10, float("inf"), 1790.69),
    (float("inf"), float("inf"), float("inf"), 828.10, float("inf"), 1942.57),
]

def get_base_amount(days, miles, receipts):
    """Efficient decision tree lookup"""
    for r_max, d_max, m_max, r_min, r_check, base in TREE_RULES:
        if receipts <= r_max and days <= d_max and miles <= m_max:
            if receipts > r_min:
                if r_check == float("inf") or receipts <= r_check:
                    return base
    return 1942.57  # Default fallback

def apply_corrections(base, days, miles, receipts):
    """Apply residual corrections to base amount"""
    total = D(str(base))
    
    # Receipt ending corrections
    receipt_str = f"{receipts:.2f}"
    if receipt_str.endswith("49"):
        total -= D("415.48")
    elif receipt_str.endswith("99"):
        total -= D("319.46")
    
    # Day-based corrections
    if days == 5:
        total -= D("15.83")
    elif 4.4 < days < 4.6:
        total -= D("8")
    
    # Receipt range corrections
    if 0 < receipts <= 50:
        total += D("25")
    elif 825 < receipts < 831:
        total += D("15")
    elif days > 10 and 500 < receipts < 1000:
        total += D("20")
    
    # Per-day calculations
    if days > 0:
        receipts_per_day = receipts / days
        miles_per_day = miles / days
        
        if receipts_per_day > 500 and receipts > 2000:
            total *= D("0.85")
        
        if 180 <= miles_per_day <= 220:
            total += D("10")
    
    # Add deterministic jitter
    seed = int((days * 1000 + miles * 100 + receipts * 10) % (2**31 - 1))
    random.seed(seed)
    jitter = D(str(random.uniform(-3, 3)))
    total += jitter
    
    return total

def calculate_reimbursement(days_str, miles_str, receipts_str):
    """Main calculation function"""
    try:
        days = int(days_str)
        miles = float(miles_str)
        receipts = float(receipts_str)
        
        base = get_base_amount(days, miles, receipts)
        total = apply_corrections(base, days, miles, receipts)
        
        return round(max(D("0"), total), 2)
    except (ValueError, TypeError) as e:
        print(f"Error: Invalid input - {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Error: Incorrect number of arguments", file=sys.stderr)
        sys.exit(1)
    
    result = calculate_reimbursement(sys.argv[1], sys.argv[2], sys.argv[3])
    print(f"{result:.2f}")
' "$1" "$2" "$3"