import json

# High-error cases from optimized rules evaluation
high_error_cases = [
    {"case": 684, "days": 8, "miles": 795, "receipts": 1645.99, "expected": 644.69, "got": 1587.95, "error": 943.26},
    {"case": 152, "days": 4, "miles": 69, "receipts": 2321.49, "expected": 322.00, "got": 1151.82, "error": 829.82},
    {"case": 367, "days": 11, "miles": 740, "receipts": 1171.99, "expected": 902.09, "got": 1692.63, "error": 790.54},
    {"case": 996, "days": 1, "miles": 1082, "receipts": 1809.49, "expected": 446.94, "got": 1175.16, "error": 728.22},
    {"case": 548, "days": 8, "miles": 482, "receipts": 1411.49, "expected": 631.81, "got": 1335.14, "error": 703.33}
]

print("Analysis of High-Error Cases:")
print("=" * 80)

for case in high_error_cases:
    days = case['days']
    miles = case['miles']
    receipts = case['receipts']
    expected = case['expected']
    got = case['got']
    error = case['error']
    
    # Calculate metrics
    miles_per_day = miles / days
    receipts_per_day = receipts / days
    total_input = days + miles + receipts
    expected_ratio = expected / total_input
    got_ratio = got / total_input
    
    print(f"\nCase {case['case']}:")
    print(f"  Input: {days} days, {miles} miles, ${receipts:.2f} receipts")
    print(f"  Expected: ${expected:.2f} (ratio: {expected_ratio:.3f})")
    print(f"  Got: ${got:.2f} (ratio: {got_ratio:.3f})")
    print(f"  Error: ${error:.2f}")
    print(f"  Miles/day: {miles_per_day:.1f}")
    print(f"  Receipts/day: ${receipts_per_day:.2f}")
    
    # Check receipt endings
    receipt_str = f"{receipts:.2f}"
    if receipt_str.endswith('49'):
        print(f"  ⚠️  Receipt ends in .49 - should be HEAVILY penalized")
        print(f"  💡 Expected ratio suggests penalty of ~{(1 - expected_ratio/got_ratio)*100:.0f}%")
    elif receipt_str.endswith('99'):
        print(f"  ⚠️  Receipt ends in .99 - should be MODERATELY penalized")
        print(f"  💡 Expected ratio suggests penalty of ~{(1 - expected_ratio/got_ratio)*100:.0f}%")

print("\n\nKey Insights:")
print("=" * 80)
print("All high-error cases have .49 or .99 receipt endings")
print("The optimized rules are not penalizing these cases enough")
print("We need stronger penalties for .49/.99 endings, especially for high receipt amounts") 