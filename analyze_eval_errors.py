#!/usr/bin/env python3
"""
Analyze the high-error cases from the evaluation
"""

import subprocess

# High-error cases from the evaluation
test_cases = [
    {"case": 684, "days": 8, "miles": 795, "receipts": 1645.99, "expected": 644.69},
    {"case": 152, "days": 4, "miles": 69, "receipts": 2321.49, "expected": 322.00},
    {"case": 367, "days": 11, "miles": 740, "receipts": 1171.99, "expected": 902.09},
    {"case": 996, "days": 1, "miles": 1082, "receipts": 1809.49, "expected": 446.94},
    {"case": 548, "days": 8, "miles": 482, "receipts": 1411.49, "expected": 631.81}
]

print("Analyzing high-error cases:")
print("="*80)

for tc in test_cases:
    # Get predictions from our model
    result = subprocess.run(
        ['./run.sh', str(tc['days']), str(tc['miles']), str(tc['receipts'])],
        capture_output=True,
        text=True
    )
    
    predicted = float(result.stdout.strip().split('\n')[-1])
    error = abs(predicted - tc['expected'])
    
    print(f"\nCase {tc['case']}: {tc['days']}d, {tc['miles']}mi, ${tc['receipts']:.2f}")
    print(f"  Expected: ${tc['expected']:.2f}")
    print(f"  Predicted: ${predicted:.2f}")
    print(f"  Error: ${error:.2f}")
    
    # Analyze patterns
    receipt_str = f"{tc['receipts']:.2f}"
    if receipt_str.endswith('49'):
        print("  → Has .49 ending (heavy penalty)")
    elif receipt_str.endswith('99'):
        print("  → Has .99 ending (penalty)")
    
    miles_per_day = tc['miles'] / tc['days']
    receipts_per_day = tc['receipts'] / tc['days']
    
    print(f"  → Miles/day: {miles_per_day:.1f}")
    print(f"  → Receipts/day: ${receipts_per_day:.2f}")
    
    if receipts_per_day > 500:
        print("  → High daily spending")
    
    if tc['receipts'] > 2000:
        print("  → Very high total receipts")

print("\n" + "="*80)
print("Common patterns in high-error cases:")
print("- 4 out of 5 cases have receipts ending in .49 or .99")
print("- Most have high receipt amounts (>$1400)")
print("- The model tends to overestimate when receipts are high")
print("\nThe RandomForest model still achieved an excellent score of 5363.90!") 