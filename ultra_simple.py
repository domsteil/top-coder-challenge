#!/usr/bin/env python3
"""
Ultra Simple Solution - What if it's simpler than we think?
"""

import sys
from decimal import Decimal as D, getcontext
getcontext().prec = 12

def calculate_reimbursement(days, miles, receipts):
    receipt_str = f"{receipts:.2f}"
    
    # For .49/.99: It's JUST a percentage of total
    if receipt_str.endswith("49"):
        total = days + miles + receipts
        # Simple formula: lower receipts = higher percentage
        percentage = 0.50 - (receipts / 5000)  # Decreases as receipts increase
        return round(total * max(0.14, percentage), 2)
    
    elif receipt_str.endswith("99"):
        total = days + miles + receipts
        percentage = 0.65 - (receipts / 6000)
        return round(total * max(0.26, percentage), 2)
    
    else:
        # For normal: Simple components
        result = 0
        
        # Per diem: $95/day base
        result += days * 95
        
        # Mileage: Simple flat rate
        result += miles * 0.50
        
        # Receipts: 55% base rate
        result += receipts * 0.55
        
        # One key adjustment: 5-day penalty
        if days == 5:
            result -= 46
        
        # Efficiency bonus
        if 175 <= miles/days <= 212:
            result *= 1.08
        
        return round(result, 2)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 simple.py <days> <miles> <receipts>")
        sys.exit(1)
    
    days = int(sys.argv[1])
    miles = float(sys.argv[2])
    receipts = float(sys.argv[3])
    
    print(f"{calculate_reimbursement(days, miles, receipts):.2f}") 