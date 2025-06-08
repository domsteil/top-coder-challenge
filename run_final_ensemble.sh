#!/bin/bash

# Black Box Legacy Reimbursement System - Final Competition-Winning Version
# This script implements a weighted ensemble of two distinct models: a complex,
# feature-rich component model and a simple, ratio-based model. The ensemble weights
# are adjusted based on the input data to achieve maximum accuracy.
# Target Score: < 4000

# --- 1. Input Validation ---
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <trip_duration_days> <miles_traveled> <total_receipts_amount>" >&2
    exit 1
fi

if ! [[ "$1" =~ ^[0-9]+(\.[0-9]+)?$ && "$2" =~ ^[0-9]+(\.[0-9]+)?$ && "$3" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
    echo "Error: All arguments must be numeric" >&2
    exit 1
fi

# --- 2. Execute Ensembled Python Logic ---
exec python3 -c '
import sys
import math
from decimal import Decimal as D, getcontext
getcontext().prec = 12

def calculate_component_model(days, miles, receipts):
    # This is the highly-tuned, feature-rich component model.
    total = D("0")
    per_diem = D("100") * D(days)
    
    # Tiered Mileage
    if miles <= 100: mileage = D(miles * 0.58)
    elif miles <= 400: mileage = D("58") + D((miles - 100) * 0.419)
    else: mileage = D("58") + D("125.7") + D((miles - 400) * 0.35)
    
    # Variable Rate Receipts
    if days <= 2: receipt_rate = 0.55 if receipts <= 500 else 0.45
    elif days <= 4: receipt_rate = 0.50 if receipts <= 600 else 0.40
    elif days <= 7: receipt_rate = 0.45 if receipts <= 800 else 0.35
    else: receipt_rate = 0.40 if receipts <= 1000 else 0.30
    receipt_component = D(receipts * receipt_rate)
    
    total = per_diem + mileage + receipt_component
    
    # Adjustments
    receipt_str = f"{receipts:.2f}"
    if receipt_str.endswith("49"): total -= D("472")
    elif receipt_str.endswith("99"): total -= D("319")
    else: total += D("5")
    
    miles_per_day = miles / days if days > 0 else miles
    if 175 <= miles_per_day <= 212: total *= D("1.10")
    
    if days == 5: total -= D("46")
    elif days >= 10: total -= D("25")
    
    return total

def calculate_ratio_model(days, miles, receipts):
    # This is the simple, elegant ratio-based model.
    total_input = D(days + miles + receipts)
    receipt_str = f"{receipts:.2f}"
    
    # Determine Ratio
    if receipt_str.endswith("49"):
        base_ratio = 0.22 if receipts > 1000 else 0.30
    elif receipt_str.endswith("99"):
        base_ratio = 0.35 if receipts > 1000 else 0.45
    else:
        base_ratio = 0.60 if receipts > 1000 else 0.70
        
    # Adjust Ratio
    miles_per_day = miles / days if days > 0 else miles
    if 180 <= miles_per_day <= 210: base_ratio *= 1.08
    if days == 5: base_ratio *= 0.94
    
    base_reimbursement = total_input * D(base_ratio)
    
    # Minimum Guarantee
    minimum = D(days * 50) + (D(miles) * D("0.25"))
    return max(base_reimbursement, minimum)

def calculate_reimbursement(days_in, miles_in, receipts_in):
    try:
        days = int(days_in)
        miles = float(miles_in)
        receipts = float(receipts_in)
        
        # Get predictions from both models
        component_pred = calculate_component_model(days, miles, receipts)
        ratio_pred = calculate_ratio_model(days, miles, receipts)
        
        # --- Context-Aware Ensemble Weighting ---
        receipt_str = f"{receipts:.2f}"
        if receipt_str.endswith("49") or receipt_str.endswith("99"):
            # Trust the aggressive ratio model more for punitive cases
            final_total = ratio_pred * D("0.9") + component_pred * D("0.1")
        else:
            # Balance both approaches for normal cases
            final_total = component_pred * D("0.7") + ratio_pred * D("0.3")
            
        # Final safety cap
        if final_total > D("2500"):
            final_total = D("2500") + (final_total - D("2500")) * D("0.5")
            
        return round(max(D("0"), final_total), 2)
        
    except (ValueError, TypeError, ZeroDivisionError) as e:
        print(f"Error: Invalid input - {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    result = calculate_reimbursement(sys.argv[1], sys.argv[2], sys.argv[3])
    print(f"{result:.2f}")

' "$1" "$2" "$3" 