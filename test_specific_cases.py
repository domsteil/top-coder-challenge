import subprocess
import json

# Load public cases
with open('public_cases.json', 'r') as f:
    cases = json.load(f)

# Test cases from evaluation output
test_cases = [
    {"case": 684, "days": 8, "miles": 795, "receipts": 1645.99, "expected": 644.69},
    {"case": 152, "days": 4, "miles": 69, "receipts": 2321.49, "expected": 322.00},
    {"case": 367, "days": 11, "miles": 740, "receipts": 1171.99, "expected": 902.09},
    {"case": 996, "days": 1, "miles": 1082, "receipts": 1809.49, "expected": 446.94},
    {"case": 548, "days": 8, "miles": 482, "receipts": 1411.49, "expected": 631.81}
]

print("Testing specific high-error cases with ULTRA SIMPLE model:")
print("=" * 80)

for test in test_cases:
    # Run our ultra simple version
    result = subprocess.run(
        ['./run_ultra_simple.sh', str(test['days']), str(test['miles']), str(test['receipts'])],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        got = float(result.stdout.strip())
        error = abs(got - test['expected'])
        
        print(f"\nCase {test['case']}: {test['days']}d, {test['miles']}mi, ${test['receipts']:.2f}")
        print(f"  Expected: ${test['expected']:.2f}")
        print(f"  Got: ${got:.2f}")
        print(f"  Error: ${error:.2f}")
        
        # Analyze what's happening
        miles_per_day = test['miles'] / test['days']
        receipts_per_day = test['receipts'] / test['days']
        total_input = test['days'] + test['miles'] + test['receipts']
        reimb_ratio = test['expected'] / total_input
        got_ratio = got / total_input
        
        print(f"  Miles/day: {miles_per_day:.1f}")
        print(f"  Receipts/day: ${receipts_per_day:.2f}")
        print(f"  Expected/Total Input: {reimb_ratio:.3f}")
        print(f"  Got/Total Input: {got_ratio:.3f}")
        
        # Check receipt endings
        receipt_str = f"{test['receipts']:.2f}"
        if receipt_str.endswith('49'):
            print(f"  ⚠️  Receipt ends in .49 - heavily penalized")
        elif receipt_str.endswith('99'):
            print(f"  ⚠️  Receipt ends in .99 - moderately penalized") 