import json

# High-error cases
test_cases = [
    {'case': 520, 'days': 14, 'miles': 481, 'receipts': 939.99},
    {'case': 152, 'days': 4, 'miles': 69, 'receipts': 2321.49},
    {'case': 711, 'days': 5, 'miles': 516, 'receipts': 1878.49},
    {'case': 996, 'days': 1, 'miles': 1082, 'receipts': 1809.49},
    {'case': 684, 'days': 8, 'miles': 795, 'receipts': 1645.99}
]

print("Daily spending analysis for high-error cases:")
print("=" * 60)

for case in test_cases:
    daily_spending = case['receipts'] / case['days']
    print(f"Case {case['case']}: {case['days']} days, ${case['receipts']:.2f} receipts")
    print(f"  Daily spending: ${daily_spending:.2f}/day")
    print(f"  Would trigger $600/day threshold: {'YES' if daily_spending > 600 else 'NO'}")
    print() 