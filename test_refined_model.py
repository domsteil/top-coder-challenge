import subprocess
import json

# High-error cases from the best model
test_cases = [
    {'case': 520, 'days': 14, 'miles': 481, 'receipts': 939.99, 'expected': 877.17},
    {'case': 152, 'days': 4, 'miles': 69, 'receipts': 2321.49, 'expected': 322.00},
    {'case': 711, 'days': 5, 'miles': 516, 'receipts': 1878.49, 'expected': 669.85},
    {'case': 996, 'days': 1, 'miles': 1082, 'receipts': 1809.49, 'expected': 446.94},
    {'case': 684, 'days': 8, 'miles': 795, 'receipts': 1645.99, 'expected': 644.69}
]

print("Testing refined model on high-error cases:")
print("=" * 80)

total_error = 0
for case in test_cases:
    # Run the model
    result = subprocess.run(
        ['./run.sh', str(case['days']), str(case['miles']), f"{case['receipts']:.2f}"],
        capture_output=True,
        text=True
    )
    
    got = float(result.stdout.strip())
    error = abs(got - case['expected'])
    total_error += error
    
    print(f"\nCase {case['case']}: {case['days']} days, {case['miles']} miles, ${case['receipts']:.2f} receipts")
    print(f"  Expected: ${case['expected']:.2f}")
    print(f"  Got: ${got:.2f}")
    print(f"  Error: ${error:.2f} ({'IMPROVED' if error < 900 else 'STILL HIGH'})")

print(f"\n\nTotal error on these 5 cases: ${total_error:.2f}")
print(f"Average error: ${total_error/5:.2f}")

# Now test on all public cases
print("\n\nTesting on all public cases...")
with open('public_cases.json', 'r') as f:
    public_cases = json.load(f)

total_error = 0
errors = []

for i, case in enumerate(public_cases):
    result = subprocess.run(
        ['./run.sh', 
         str(case['input']['trip_duration_days']), 
         str(case['input']['miles_traveled']), 
         f"{case['input']['total_receipts_amount']:.2f}"],
        capture_output=True,
        text=True
    )
    
    got = float(result.stdout.strip())
    expected = case['expected_output']
    error = abs(got - expected)
    total_error += error
    errors.append(error)
    
    if i % 100 == 0:
        print(f"Processed {i} cases...")

print(f"\nTotal error: ${total_error:.2f}")
print(f"Average error: ${total_error/len(public_cases):.2f}")
print(f"Max error: ${max(errors):.2f}")
print(f"Cases with error > $100: {sum(1 for e in errors if e > 100)}")
print(f"Cases with error > $500: {sum(1 for e in errors if e > 500)}") 